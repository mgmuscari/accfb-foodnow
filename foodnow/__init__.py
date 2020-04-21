import psycogreen.gevent
import spacy

nlp_en = spacy.load("en_core_web_sm")
nlp_es = spacy.load("es_core_news_sm")

psycogreen.gevent.patch_psycopg()
