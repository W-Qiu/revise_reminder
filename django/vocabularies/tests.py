from django.test import TestCase
from .models import Vocab
from users.models import CustomUser


class VocabTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create(email="hello@world.com")
        Vocab.objects.create(word="international",
                             interpretations=[""],
                             examples=[""],
                             owner_id=1)
        Vocab.objects.create(word="a phrase",
                             interpretations=["n. something is here",
                                              ""],
                             examples=["I am an example", ""],
                             owner_id=1)
        Vocab.objects.create(word="another phrase",
                             interpretations=["",
                                              "n. something is here"],
                             examples=["", "I am an example"],
                             owner_id=1)

    def test_vocab_attr(self):
        international = Vocab.objects.get(word="international")
        self.assertEqual(international.word, 'international')
        self.assertEqual(international.interpretations, [''])
        self.assertEqual(international.examples, [''])
        self.assertEqual(international.__str__(), 'international')

        a_phrase = Vocab.objects.get(word="a phrase")
        self.assertEqual(a_phrase.word, 'a phrase')
        self.assertEqual(a_phrase.interpretations, [
                         'n. something is here', ''])
        self.assertEqual(a_phrase.examples, ['I am an example', ''])
        self.assertEqual(a_phrase.__str__(), 'a phrase')

        another_phrase = Vocab.objects.get(word="another phrase")
        self.assertEqual(another_phrase.word, 'another phrase')
        self.assertEqual(another_phrase.interpretations, [
                         '', 'n. something is here'])
        self.assertEqual(another_phrase.examples, ['', 'I am an example'])
        self.assertEqual(another_phrase.__str__(), 'another phrase')
