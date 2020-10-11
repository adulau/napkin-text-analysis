#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import spacy
import argparse
import sys
import simplejson as json
from tabulate import tabulate
import cld3

parser = argparse.ArgumentParser(description="Extract statistical analysis of text")
parser.add_argument('-v', help="verbose output")
parser.add_argument('-f', help="file to analyse")
parser.add_argument('-t', help="maximum value for the top list (default is 100) -1 is no limit", default=100)
parser.add_argument('-s', help="display the overall statistics (default is False)", default=False,  action='store_true')
parser.add_argument('-o', help="output format (default is csv), json, readable", default="csv")
parser.add_argument('-l', help="language used for the analysis (default is en)", default="en")
parser.add_argument('--verbatim', help="Don't use the lemmatized form, use verbatim. (default is the lematized form)", default=False, action='store_true')
parser.add_argument('--no-flushdb', help="Don't flush the redisdb, useful when you want to process multiple files and aggregate the results. (by default the redis database is flushed at each run)", default=False, action='store_true')
parser.add_argument('--binary', help="set output in binary instead of UTF-8 (default)", default=False, action='store_true')
parser.add_argument('--analysis', help="Limit output to a specific analysis (verb, noun, hashtag, mention, digit, url, oov, labels, punct). (Default is all analysis are displayed)", default='all')
parser.add_argument('--disable-parser', help="disable parser component in Spacy", default=False, action='store_true')
parser.add_argument('--disable-tagger', help="disable tagger component in Spacy", default=False, action='store_true')

args = parser.parse_args()
if args.f is None:
    parser.print_help()
    sys.exit()

if not args.binary:
    redisdb = redis.Redis(host="localhost", port=6380, db=5, encoding='utf-8', decode_responses=True)
else:
    redisdb = redis.Redis(host="localhost", port=6380, db=5)

try:
    redisdb.ping()
except:
    print("Redis database on port 6380 is not running...", file=sys.stderr)
    sys.exit()

if not args.no_flushdb:
    redisdb.flushdb()

disable = []
if args.disable_parser:
    disable.append("parser")
if args.disable_tagger:
    disable.append("tagger")

if args.l == "fr":
    nlp = spacy.load("fr_core_news_md", disable=disable)
elif args.l == "en":
    nlp = spacy.load("en_core_web_md", disable=disable)
else:
    sys.exit("Language not supported")

nlp.max_length = 2000000

with open(args.f, 'r') as file:
    text = file.read()

detect_lang = cld3.get_language(text)
if detect_lang[0] != args.l:
    sys.exit("Language detected ({}) is different than the NLP used ({})".format(detect_lang[0], args.l))

doc = nlp(text)

analysis = ["verb", "noun", "hashtag", "mention",
            "digit", "url", "oov", "labels",
            "punct"]

redisdb.hset("stats", "token", doc.__len__())

for token in doc:
        if token.pos_ == "VERB" and not token.is_oov and len(token) > 1:
            if not args.verbatim:
                redisdb.zincrby("verb", 1, token.lemma_)
            else:
                redisdb.zincrby("verb", 1, token.text)
            redisdb.hincrby("stats", "verb", 1)
            continue
        if token.pos_ == "NOUN" and not token.is_oov and len(token) > 1:
            if not args.verbatim:
                redisdb.zincrby("noun", 1, token.lemma_)
            else:
                redisdb.zincrby("noun", 1, token.text)
            redisdb.hincrby("stats", "noun", 1)
            continue
        if token.pos_ == "PUNCT" and not token.is_oov:
            redisdb.zincrby("punct", 1, value)
            redisdb.hincrby("stats", "punct", 1)
            continue

        if token.is_oov:
            value = "{}".format(token)
            if value.startswith('#'):
                redisdb.zincrby("hashtag", 1, value[1:])
                redisdb.hincrby("stats", "hashtag", 1)
                continue
            if value.startswith('@'):
                redisdb.zincrby("mention", 1, value[1:])
                redisdb.hincrby("stats", "mention", 1)
                continue
            if token.is_digit:
                redisdb.zincrby("digit", 1, value)
                redisdb.hincrby("stats", "digit", 1)
                continue
            if token.is_space:
                redisdb.hincrby("stats", "space", 1)
                continue
            if token.like_url:
                redisdb.zincrby("url", 1, value)
                redisdb.hincrby("stats", "url", 1)
                continue
            if token.like_email:
                redisdb.zincrby("email", 1, value)
                redisdb.hincrby("stats", "email", 1)
                continue
            redisdb.zincrby("oov", 1, value)
            redisdb.hincrby("stats", "oov", 1)


for entity in doc.ents:
        redisdb.zincrby("labels", 1, entity.label_)

if args.o == "json":
    output_json = {"format":"napkin"}
for anal in analysis:
        if args.analysis == "all" or args.analysis == anal:
            pass
        else:
            continue
        if args.o == "readable":
            previous_value = None
        x = redisdb.zrevrange(anal, 1, args.t, withscores=True, score_cast_func=int)
        if args.o == "csv":
            print()
        elif args.o == "readable":
            header = ["\033[1mTop {} of {}\033[0m".format(args.t, anal)]
            readable_table = []
        elif args.o == "json":
            output_json.update({anal:[]})
        for a in x:
            if args.o == "csv":
                print("{},{},{}".format(anal,a[0],a[1]))
            elif args.o == "readable":
                if previous_value is None:
                    previous_value = a[1]
                elif previous_value == a[1]:
                    readable_table.append(["{}".format(a[0])])
                elif a[1] < previous_value:
                    previous_value = a[1]
                    readable_table.append(["{} occurences".format(a[1])])
                    readable_table.append(["{}".format(a[0])])
            elif args.o == "json":
                output_json[anal].append(a)
        if args.o == "readable":
            print(tabulate(readable_table, header, tablefmt="fancy_grid"))
        if args.o == "csv":
            print("#")

if args.s:
    print(redisdb.hgetall('stats'))
if args.o == "json":
    print(json.dumps(output_json))
