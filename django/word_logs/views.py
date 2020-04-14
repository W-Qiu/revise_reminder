from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.db import connection
from django.shortcuts import redirect

from .models import WordLog
from vocabularies.models import Vocab


class AddWordLog(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "vocabularies/home.html"

    def post(self, request, *args, **kwargs):
        word_id = self.request.POST.get('word_id')
        log = self.request.POST.get('log').strip()
        if log != "":
            word = Vocab.objects.get(id=word_id)
            log = WordLog(word_id=word, log=log)
            try:
                log.save()
            except:
                messages.warning(self.request, "DB error")
            else:
                messages.success(self.request, "A new entry has been logged")
        return redirect('home')
