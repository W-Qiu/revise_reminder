from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch

from vocabularies.models import Vocab
from users.models import CustomUser


es = Elasticsearch()
index = 'vocab'
index_mapping = {
    'mappings': {
        'properties': {
            "id": {
                "type": "integer"
            },
            "word": {
                "type": "completion",
                "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                }
            },
            "owner_id": {
                "type": "integer"
            },
            "date_created": {
                "type": "date"
            }
        }}
}


class Command(BaseCommand):
    help = "Initialize Elasticsearch index based on existing data."

    def handle(self, *args, **options):
        # create the index if missing
        if not es.indices.exists(index):
            es.indices.create(index=index, body=index_mapping)

        # index every word
        user_ids = CustomUser.objects.values_list("id",
                                                  flat=True)
        for user_id in user_ids:
            word_objs = Vocab.objects.filter(owner_id=user_id)
            for word_obj in word_objs:
                body = {
                    "word": word_obj.word,
                    "owner_id": word_obj.owner_id,
                    "date_created": word_obj.date_created
                }
                es.index(index, body, id=word_obj.id, refresh=True)
