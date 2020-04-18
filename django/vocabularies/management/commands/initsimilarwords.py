from django.core.management.base import BaseCommand

from vocabularies.models import Vocab
from users.models import CustomUser

from nltk import edit_distance as ED
from redis import Redis

import os


class Command(BaseCommand):
    help = "update similar words on Redis server."

    def handle(self, *args, **options):
        r = Redis(host=os.environ.get("REDIS_SERVICE_SERVICE_HOST"))
        user_ids = CustomUser.objects.values_list("id",
                                                  flat=True)
        for user_id in user_ids:
            words = Vocab.objects.filter(owner_id=user_id)
            memo = {}  # ED(A, B) = ED(B, A)
            for word in words:
                set_name = f"user:{str(user_id)}:{word.word}"
                d = {}  # the sorted set and mappings in Redis
                for target in words:
                    if f"{word.word}-{target.word}" in memo:
                        e_d = memo[f"{word.word}-{target.word}"]
                    else:
                        e_d = ED(word.word, target.word)
                        if e_d > 3:
                            continue
                        memo[f"{target.word}-{word.word}"] = e_d
                    key = f"{target.word}:{str(target.id)}"
                    d[key] = e_d
                r.zadd(set_name, d)
