from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.timezone import now

from users.models import CustomUser


class Vocab(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    interpretations = ArrayField(models.TextField(null=True), null=True)
    examples = ArrayField(models.TextField(null=True), null=True)

    last_test_result = models.BooleanField(null=True, default=True)
    remember_count = models.IntegerField(default=0)
    forget_count = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_test = models.DateTimeField(default=now())

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'word'], name='unique_word_per_user'),
        ]

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        self.word = self.word.lower()
        return super().save(*args, **kwargs)
