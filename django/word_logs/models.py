from django.db import models
from datetime import datetime

from vocabularies.models import Vocab

class WordLog(models.Model):
    word_id = models.ForeignKey(Vocab, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    log = models.TextField()

    def __str__(self):
        return self.log