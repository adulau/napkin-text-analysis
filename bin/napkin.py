#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import spacy
from spacy_langdetect import LanguageDetector
import argparse
import sys

parser = argparse.ArgumentParser(description="Extract statistical analysis of text")
parser.add_argument('-v', help="verbose output")
parser.add_argument('-f', help="file to analyse")
parser.add_argument('-t', help="maximum value for the top list (default is 100) -1 is no limit", default=100)
parser.add_argument('-o', help="output format (default is csv)", default="csv")
args = parser.parse_args()
if args.f is None:
    parser.print_help()
    sys.exit()

redisdb = redis.Redis(host="localhost", port=6380, db=5)

try:
    redisdb.flushdb()
except:
    print("Redis database on port 6380 is not running...", file=sys.stderr)
    sys.exit()

nlp = spacy.load("en_core_web_md")
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)

nlp.max_length = 2000000

with open(args.f, 'r') as file:
    text = file.read()

doc = nlp(text)

analysis = ["verb:napkin", "noun:napkin", "hashtag:napkin", "mention:napkin", "digit:napkin", "url:napking", "oov:napkin", "labels:napkin"]

for token in doc:
        if token.pos_ == "VERB" and not token.is_oov:
            redisdb.zincrby("verb:napkin", 1, token.lemma_)
            continue
        if token.pos_ == "NOUN" and not token.is_oov:
            redisdb.zincrby("noun:napkin", 1, token.lemma_)
            continue

        if token.is_oov:
            value = "{}".format(token)
            if value.startswith('#'):
                redisdb.zincrby("hashtag:napkin", 1, value[1:])
                continue
            if value.startswith('@'):
                redisdb.zincrby("mention:napkin", 1, value[1:])
                continue
            if token.is_digit:
                redisdb.zincrby("digit:napkin", 1, value)
                continue
            if token.is_space:
                continue
            if token.like_url:
                redisdb.zincrby("url:napkin", 1, value)
                continue
            if token.like_email:
                redisdb.zincrby("email:napkin", 1, value)
                continue
            redisdb.zincrby("oov:napkin", 1, value)


for entity in doc.ents:
        redisdb.zincrby("labels:napkin", 1, entity.label_)

for anal in analysis:
        x = redisdb.zrevrange(anal, 1, args.t, withscores=True)
        print ("# Top {} of {}".format(args.t, anal))
        for a in x:
            if args.o == "csv":
                print ("{},{}".format(a[0],a[1]))
        print ("#")

