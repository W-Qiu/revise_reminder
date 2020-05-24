from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.shortcuts import redirect

from concurrent.futures import ThreadPoolExecutor
from elasticsearch import Elasticsearch
from math import floor
from nltk import edit_distance as ED
from redis import Redis
import os
import re
import socket

from .models import Vocab
from revise_reminder.settings import NLP
from users.models import CustomUser
from word_logs.models import WordLog
from .bing_search import search_img


"""
# Global Init and variables
"""
nlp = NLP().nlp  # NLP model, initialized in settings.py
es = Elasticsearch([os.environ.get("ES_SERVICE_SERVICE_HOST")])
index = 'vocab'


"""
# Helpers
"""


def dictfetchone(cursor):
    """convert SQL result to dict instead of a list."""
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return result[0]


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return result


def clean_data(L):
    """clean list data, strip white space and reject empty string."""
    i = len(L) - 1
    while i >= 0:
        L[i] = L[i].strip()
        if L[i] == '':
            del L[i]
        i -= 1
    return L


def highlight(word_object):
    """pick words/phrases to highlight"""
    picks = []

    # make sure both None and empty list are checked
    # word_object['examples'] = [''], which is True in boolean
    if word_object['examples']:
        examples = word_object['examples']
        word = word_object['word']
        word_token = nlp(word)

        for example in examples:
            # if a phrase
            if len(word_token) > 1:
                similarity = []
                doc = nlp(example)

                # example < phrase
                if len(doc) < len(word_token):
                    picks.append("")
                    continue

                for i in range(len(doc) - len(word_token) + 1):
                    span = doc[i:i+len(word_token)]
                    similarity.append(word_token.similarity(span))
                max_value = max(similarity)
                max_index = similarity.index(max_value)
                pick = doc[max_index:max_index+len(word_token)]
                picks.append(pick)

            # if a single word
            else:
                doc = nlp(example)
                similarity = [word_token.similarity(token) for token in doc]
                max_value = max(similarity)
                max_index = similarity.index(max_value)
                pick = doc[max_index].text
                picks.append(pick)
    return picks


def getSimilarWords(user_id, word):
    """Fetch similar words from Redis server."""
    similar_words = []
    r = Redis(host=os.environ.get("REDIS_SERVICE_SERVICE_HOST"))
    key = f"user:{str(user_id)}:{word}"
    redis_result = r.zrange(key, 1, 3)  # TOP 3, 0 is word itself
    for pair in redis_result:
        pair = pair.decode("utf-8").split(":")
        d = {"word": pair[0],
             "id": pair[1]}
        similar_words.append(d)
    return similar_words


def addSimilarWords(user_id, word):
    r = Redis(host=os.environ.get("REDIS_SERVICE_SERVICE_HOST"))
    words = Vocab.objects.filter(owner_id=user_id)
    new_word = words.filter(word=word)[0]
    new_set_name = f"user:{str(user_id)}:{new_word.word}"
    d = {}
    for target in words:
        # new word's edit against other words
        e_d = ED(new_word.word, target.word)
        if e_d > 3:
            continue
        key = f"{target.word}:{str(target.id)}"
        d[key] = e_d

        # update existing words against new word
        this_set_name = f"user:{str(user_id)}:{target.word}"
        mapping = {f"{new_word.word}:{str(new_word.id)}": e_d}
        r.zadd(this_set_name, mapping)
    r.zadd(new_set_name, d)


def delSimilarWords(user_id, word, word_id):
    r = Redis(host=os.environ.get("REDIS_SERVICE_SERVICE_HOST"))

    # delete field of this word in other words
    key = f"user:{str(user_id)}:{word}"
    field = f"{word}:{str(word_id)}"
    words = r.zrange(key, 0, -1)
    for w in words:
        w = w.decode("utf-8").split(":")[0]
        set_name = f"user:{str(user_id)}:{w}"
        r.zrem(set_name, field)

    # delete this word's own sorted set
    r.delete(key)


def updateAudio(word):
    """Signal TTS server to update audio files."""

    # TCP connection to TTS server
    server_addr = (os.environ.get("TTS_SERVICE_SERVICE_HOST"),
                   int(os.environ.get("TTS_SERVICE_SERVICE_PORT")))
    sock = socket.create_connection(server_addr)

    sock.send(str.encode(word))
    response = sock.recv(1024)
    print(f"Updated audio file {word}.wav - {response.decode()}")
    sock.close()


def updateElasticSearch(word_obj):
    body = {
        "word": word_obj.word,
        "owner_id": word_obj.owner_id,
        "date_created": word_obj.date_created
    }
    try:
        response = es.index(index, body, id=word_obj.id, refresh=True)
        print(response)
    except:
        pass


"""
# All the views
"""


def direct(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')


class HomeView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "vocabularies/home.html"

    def get_context_data(self, **kwargs):
        # initializing
        context = super().get_context_data(**kwargs)

        user_id = self.request.user.id
        revise_strategy = self.request.user.revise_strategy

        today_target = self.request.user.preset_target
        today_progress = self.request.user.today_progress

        user_info = {'today_target': today_target,
                     'today_progress': today_progress}
        context['user_info'] = user_info

        """
        # SQL commands for 'by last test date' revise strategy
        # get_word_SQL:     fetch one word
        #                   (not just the word itself, all columns)
        # SQL commands for 'forgeting curve' revise strategy
        # order by: forgetting curve function R = exp(-t/1+S)
        #           R = Retrievability, t = Time, S = Stability
        #           t = log(EXTRACT(EPOCH FROM 
        #                   (current_timestamp-date_last_test)))
        #           S = 0.2 * forget_count + 0.8 * remember_count
        #           small S -> high rank
        """
        get_word_SQL_S1 = 'SELECT * FROM vocabularies_vocab \
                        ORDER BY date_last_test DESC \
                        LIMIT 1 OFFSET %s'

        get_word_SQL_S2 = 'SELECT * FROM vocabularies_vocab             \
                           ORDER BY exp(-log(EXTRACT(EPOCH FROM         \
                                    (current_timestamp-date_last_test)))\
                                    / (1 + 0.2 * forget_count +         \
                                        0.8 * remember_count))          \
                           LIMIT 1'

        # main logic
        word_count = Vocab.objects.filter(owner_id=user_id).count()
        if word_count != 0 and today_target > today_progress:
            with connection.cursor() as cursor:
                if revise_strategy == 'by last test date':
                    cursor.execute(get_word_SQL_S1, [today_progress])
                elif revise_strategy == 'forgetting curve':
                    cursor.execute(get_word_SQL_S2)
                word = dictfetchone(cursor)

                # get logs
                logs = WordLog.objects.filter(word_id=word['id'])

                # get highlighted
                context['picks'] = highlight(word)
                context['num_picks'] = len(highlight(word))

            context['word'] = word
            context['logs'] = logs
            context['similar_words'] = getSimilarWords(user_id,
                                                       word['word'])

        elif word_count == 0:
            context['no_word'] = True
        else:
            context['completed'] = True
        return context

# class WordImagesView(LoginRequiredMixin, View):
#     login_url = '/login/'

#     def get(self, request):
#         user_id = self.request.user.id
#         word_id = self.request.GET['word_id']

#         word_object = Vocab.objects.get(id=word_id)
#         word = word_object.word
#         owner_id = word_object.owner_id
#         if user_id != owner_id:
#             raise PermissionDenied

#         # img_urls = search_img(word)
#         # return HttpResponse(img_urls)
#         return HttpResponse('not now')


class YesView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "vocabularies/home.html"

    def post(self, request, *args, **kwargs):
        word_id = self.request.POST.get('word_id')
        user_id = self.request.user.id
        owner_id = Vocab.objects.get(id=word_id).owner_id
        if user_id != owner_id:
            raise PermissionDenied

        update_word_SQL = 'UPDATE vocabularies_vocab \
                            SET last_test_result=TRUE, \
                                remember_count=remember_count+1, \
                                date_last_test=NOW() \
                                WHERE id=%s'

        update_user_SQL = 'UPDATE users_customuser \
                            SET today_progress=today_progress+1 \
                            WHERE id=%s'

        with connection.cursor() as cursor:
            cursor.execute(update_word_SQL, [word_id])
            cursor.execute(update_user_SQL, [user_id])

        return redirect('home')


class NoView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "vocabularies/home.html"

    def post(self, request, *args, **kwargs):
        word_id = self.request.POST.get('word_id')
        user_id = self.request.user.id
        owner_id = Vocab.objects.get(id=word_id).owner_id
        if user_id != owner_id:
            raise PermissionDenied

        update_word_SQL = 'UPDATE vocabularies_vocab \
                            SET last_test_result=FALSE, \
                                forget_count=forget_count+1, \
                                date_last_test=NOW() \
                                WHERE id=%s'

        update_user_SQL = 'UPDATE users_customuser \
                            SET today_progress=today_progress+1 \
                            WHERE id=%s'

        with connection.cursor() as cursor:
            cursor.execute(update_word_SQL, [word_id])
            cursor.execute(update_user_SQL, [user_id])

        return redirect('home')


class NewWordView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "vocabularies/home.html"

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        word = self.request.POST.get('word').lower().strip()
        if word:
            interpretations = self.request.POST.getlist('interpretations')
            examples = self.request.POST.getlist('examples')

            interpretations = clean_data(interpretations)
            examples = clean_data(examples)

            new_word = Vocab(word=word,
                             interpretations=interpretations,
                             examples=examples,
                             owner_id=user_id)
            try:
                new_word.save()
            except IntegrityError:
                messages.warning(request, f'Duplicated word')
                return redirect('home')
            else:  # update similar_words on Redis and audio file
                with ThreadPoolExecutor(max_workers=3) as executor:
                    executor.submit(addSimilarWords(user_id, word))
                    executor.submit(updateAudio(word))
                    executor.submit(updateElasticSearch(new_word))
        else:
            messages.warning(request, f'Word is empty')
        return redirect('home')


class DeleteWordView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "vocabularies/home.html"

    def post(self, request, *args, **kwargs):
        word_id = self.request.POST.get('word_id')
        user_id = self.request.user.id
        word = Vocab.objects.get(id=word_id)
        if user_id != word.owner_id:
            raise PermissionDenied

        delSimilarWords(user_id, word.word, word.id)
        try:
            es.delete(index, word.id)
        except:
            pass
        word.delete()

        return redirect('home')


class AllWordsView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Vocab
    template_name = "vocabularies/all_user_words.html"
    context_object_name = "words"

    def get_queryset(self):
        user_id = self.request.user.id
        return Vocab.objects.filter(owner_id=user_id)


class SearchWordView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Vocab
    template_name = "vocabularies/search_result.html"
    context_object_name = "words"

    def get_queryset(self):
        user_id = self.request.user.id
        query = self.request.GET.get('query')
        # query = re.sub('[^a-zA-Z -"]', '', query.lower())
        return Vocab.objects.filter(Q(word__icontains=query) |
                                    Q(examples__icontains=query) |
                                    Q(interpretations__icontains=query),
                                    owner_id=user_id).order_by('-date_created')


class SingleWordView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "vocabularies/single_word.html"

    def get_context_data(self, **kwargs):
        user_id = self.request.user.id
        word_id = self.request.GET['id']
        word = Vocab.objects.get(id__exact=word_id)
        owner_id = word.owner_id
        if user_id != owner_id:
            raise PermissionDenied

        context = super().get_context_data(**kwargs)

        # Django queryset result is an object, not a dict
        context['picks'] = highlight(word.__dict__)
        context['num_picks'] = len(highlight(word.__dict__))
        context['word'] = word
        context['similar_words'] = getSimilarWords(user_id, word.word)
        context['logs'] = WordLog.objects.filter(word_id=word_id)

        return context

    # deal with edits
    def post(self, request, *args, **kwargs):
        word_id = self.request.POST.get('word_id')
        user_id = self.request.user.id
        word = Vocab.objects.get(id=word_id)
        if user_id != word.owner_id:
            raise PermissionDenied

        # clean data
        new_word = self.request.POST.get('word')
        old_word = word.word
        interpretations = clean_data(
            self.request.POST.getlist('interpretation'))
        examples = clean_data(self.request.POST.getlist('example'))

        # update
        word.word = new_word
        word.examples = examples
        word.interpretations = interpretations
        word.save()

        # update similar words on Redis server and audio file
        if old_word != new_word:
            delSimilarWords(user_id, old_word, word_id)
            addSimilarWords(user_id, new_word)
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(updateAudio(new_word))
                executor.submit(updateElasticSearch(word))

        return redirect(request.META.get('HTTP_REFERER', 'home'))
