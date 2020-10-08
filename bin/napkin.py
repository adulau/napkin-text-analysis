#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import spacy
from spacy_langdetect import LanguageDetector
import argparse
import sys
import simplejson as json

parser = argparse.ArgumentParser(description="Extract statistical analysis of text")
parser.add_argument('-v', help="verbose output")
parser.add_argument('-f', help="file to analyse")
parser.add_argument('-t', help="maximum value for the top list (default is 100) -1 is no limit", default=100)
parser.add_argument('-s', help="display the overall statistics (default is False)", default=False,  action='store_true')
parser.add_argument('-o', help="output format (default is csv), json", default="csv")
parser.add_argument('-l', help="language used for the analysis (default is en)", default="en")
parser.add_argument('--verbatim', help="Don't use the lemmatized form, use verbatim. (default is the lematized form)", default=False, action='store_true')

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

if args.l == "fr":
    nlp = spacy.load("fr_core_news_md")
else:
    nlp = spacy.load("en_core_web_md")

nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)

nlp.max_length = 2000000

with open(args.f, 'r') as file:
    text = file.read()

doc = nlp(text)

analysis = ["verb:napkin", "noun:napkin", "hashtag:napkin", "mention:napkin",
            "digit:napkin", "url:napking", "oov:napkin", "labels:napkin",
            "punct:napkin"]

redisdb.hset("stats", "token", doc.__len__())

for token in doc:
        if token.pos_ == "VERB" and not token.is_oov:
            if not args.verbatim:
                redisdb.zincrby("verb:napkin", 1, token.lemma_)
            else:
                redisdb.zincrby("verb:napkin", 1, token.text)
            redisdb.hincrby("stats", "verb:napkin", 1)
            continue
        if token.pos_ == "NOUN" and not token.is_oov:
            if not args.verbatim:
                redisdb.zincrby("noun:napkin", 1, token.lemma_)
            else:
                redisdb.zincrby("noun:napkin", 1, token.text)
            redisdb.hincrby("stats", "noun:napkin", 1)
            continue

        if token.is_oov:
            value = "{}".format(token)
            if value.startswith('#'):
                redisdb.zincrby("hashtag:napkin", 1, value[1:])
                redisdb.hincrby("stats", "hashtag:napkin", 1)
                continue
            if value.startswith('@'):
                redisdb.zincrby("mention:napkin", 1, value[1:])
                redisdb.hincrby("stats", "mention:napkin", 1)
                continue
            if token.is_digit:
                redisdb.zincrby("digit:napkin", 1, value)
                redisdb.hincrby("stats", "digit:napkin", 1)
                continue
            if token.is_space:
                redisdb.hincrby("stats", "space:napkin", 1)
                continue
            if token.like_url:
                redisdb.zincrby("url:napkin", 1, value)
                redisdb.hincrby("stats", "url:napkin", 1)
                continue
            if token.like_email:
                redisdb.zincrby("email:napkin", 1, value)
                redisdb.hincrby("stats", "email:napkin", 1)
                continue
            if token.is_punct:
                redisdb.zincrby("punct:napkin", 1, value)
                redisdb.hincrby("stats", "punct:napkin", 1)
                continue

            redisdb.zincrby("oov:napkin", 1, value)
            redisdb.hincrby("stats", "oov:napkin", 1)


for entity in doc.ents:
        redisdb.zincrby("labels:napkin", 1, entity.label_)

if args.o == "json":
    output_json = {"format":"napkin"}
for anal in analysis:
        x = redisdb.zrevrange(anal, 1, args.t, withscores=True)
        if args.o == "csv":
            print ("# Top {} of {}".format(args.t, anal))
        elif args.o == "json":
            output_json.update({anal:[]})
        for a in x:
            if args.o == "csv":
                print ("{},{}".format(a[0],a[1]))
            elif args.o == "json":
                output_json[anal].append(a)
        if args.o == "csv":
            print ("#")

if args.s:
    print (redisdb.hgetall('stats'))
if args.o == "json":
    print(json.dumps(output_json))
