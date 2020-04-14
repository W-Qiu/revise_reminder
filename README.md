# Revise Reminder (Docker - 1.2.0)

## What is it?
A web project based on Python and Django framework. Its core idea is to ultilize Ebbinghaus Forgetting Curve to help user revise learning, right now as an initial step, I implemented it on vocabularies. Users are able to add vocab on their own along with examples and interpretations. Other functionalities include:
* Word Logs for each vocab that users type to reminder themselves e.g. hints, words they got confused.
* Users define their own daily target, which is reset daily at midnight
* Similar looking words are automatically displayed next to the current word
* Fetch images from search engines using the word as a keyword (Need to set up API)
* Pronunciation generated by a TTS model by [Mozilla](https://github.com/mozilla/TTS)

![Image 1](https://github.com/W-Qiu/revise_reminder_docker/blob/master/screenshots/1.png)

#### Ebbinghaus Forgetting Curve Implementation
Each vocab has two counts associated with it:
* remember_count
* forget_count
They along with timestamp are used to determine revising priorities, see the detail algorithm in vocab models.

## Django Structure
The Django project contains three Apps (what Django calls its modular components):
* users
* vocabularies
* word logs

## Core Components and Libraries
* spaCy
  * used to calculate word vector similarities to pick highlights in examples because a lemma can have many forms, a simple edit-distance algorithm doesn't cut it.
* nltk
  * used to calculate edit distance to find similar-looking vocabs
* Redis
  * DB for similar words because RDBMS is too slow for dynamic situations, similar words change due to editing/adding/deleting
* PostgreSQL
  * for all other DBs
* Nginx
* Mozilla TTS model

## Usage
* Download TTS model from [here](https://drive.google.com/open?id=1otOqpixEsHf7SbOZIcttv3O7pG0EadDx), put it in tts/checkpoint/, rename it to 'best_model.pth.tar'
* Build images in each folder
* Change the environment variables in db-env-public and django-env-public
* /postgresql contains some test data, execute the file in the container
```bash
docker-compose -f docker-compose-public.yml
```
* See ManualInitialization for the parts that require manual operations

# To-do
* [✓]Pronunciation (TTS) 
* Mobile-friendly version
* Authentication for Nginx serving media files
* Crobjob to clean audio files against DB

# Caution
This project is for causal usage, I did not take extra discretion against abuse and attack, especially regarding submitted data cleaning so bugs are present.

# Credit, License etc.
Personal project by W. Qiu.

MIT license, so help yourself.