# napkin-text-analysis

Napkin is a Python tool to produce statistical analysis of a text.

Analysis features are :

- Verbs frequency
- Nouns frequency
- Digit frequency
- Labels frequency such as (Person, organisation, product, location) as defined in spacy.io [named entities](https://spacy.io/api/annotation#named-entities)
- URL frequency
- Email frequency
- Mention frequency (everything prefixed with an @ symbol)
- Out-Of-Vocabulary (OOV) word frequency meaning any words outside English dictionary

Verbs and nouns are in their lemmatized form by default but the option `--verbatim` allows to keep the original inflection.

Intermediate results are stored in a Redis database to allow the analysis of multiple text files.

# requirements

- Python >= 3.6
- spacy.io
- redis (a redis server running on port 6380)

# how to use napkin

~~~~
usage: napkin.py [-h] [-v V] [-f F] [-t T] [-s] [-o O] [-l L] [--verbatim]
                 [--no-flushdb] [--binary]

Extract statistical analysis of text

optional arguments:
  -h, --help    show this help message and exit
  -v V          verbose output
  -f F          file to analyse
  -t T          maximum value for the top list (default is 100) -1 is no limit
  -s            display the overall statistics (default is False)
  -o O          output format (default is csv), json, readable
  -l L          language used for the analysis (default is en)
  --verbatim    Don't use the lemmatized form, use verbatim. (default is the
                lematized form)
  --no-flushdb  Don't flush the redisdb, useful when you want to process
                multiple files and aggregate the results. (by default the
                redis database is flushed at each run)
  --binary      Output response in binary instead of UTF-8 (default)
~~~~

# example usage of napkin

A sample file "The Prince, by Nicoló Machiavelli" is included to test napkin.

`python3 napkin.py -f ../samples/the-prince.txt`

Example output:

~~~~
# Top 100 of verb:napkin
b'can',137.0
b'make',116.0
b'may',106.0
b'would',102.0
b'must',97.0
b'take',86.0
b'have',73.0
b'see',72.0
b'become',62.0
b'find',61.0
b'know',59.0
b'should',54.0
b'keep',53.0
b'give',53.0
b'hold',51.0
b'say',50.0
b'wish',48.0
b'could',48.0
b'fear',46.0
b'maintain',45.0
b'think',42.0
b'use',40.0
b'consider',40.0
b'come',40.0
b'lose',37.0
b'live',35.0
b'follow',33.0
b'do',33.0
b'remain',32.0
b'gain',31.0
b'avoid',31.0
b'arise',31.0
b'speak',29.0
...
# Top 100 of noun:napkin
b'man',120.0
b'state',108.0
b'people',90.0
b'one',90.0
b'time',85.0
b'work',83.0
b'other',82.0
b'thing',71.0
b'way',60.0
b'order',57.0
b'fortune',49.0
b'army',45.0
b'force',44.0
b'arm',44.0
b'soldier',43.0
b'subject',42.0
b'power',41.0
b'difficulty',39.0
b'law',34.0
b'reputation',33.0
b'position',33.0
b'enemy',33.0
b'war',32.0
b'kingdom',32.0
b'cause',31.0
b'possession',29.0
b'action',29.0
b'ruler',28.0
b'rule',28.0
b'example',28.0
b'hand',27.0
b'friend',27.0
b'country',27.0
b'king',26.0
b'case',26.0
...
# Top 100 of digit:napkin
b'84116',1.0
b'750175',1.0
b'6221541',1.0
b'57037',1.0
b'55901',1.0
#
# Top 100 of url:napking
#
# Top 100 of oov:napkin
b'Fermo',7.0
b'Vitelli',6.0
b'Pertinax',6.0
b'Orsinis',6.0
b'Colonnas',6.0
b'Bentivogli',6.0
b'Agathocles',6.0
b'Oliverotto',5.0
b'C\xc3\xa6sar',5.0
...
# Top 100 of labels:napkin
b'GPE',305.0
b'CARDINAL',197.0
b'ORG',189.0
b'NORP',131.0
b'ORDINAL',72.0
b'DATE',44.0
b'LAW',30.0
b'LOC',18.0
b'PRODUCT',9.0
b'LANGUAGE',5.0
b'WORK_OF_ART',4.0
b'QUANTITY',4.0
b'TIME',3.0
b'FAC',3.0
b'MONEY',2.0
b'PERCENT',1.0
b'EVENT',1.0

~~~~

# LICENSE

napkin is free software under the AGPLv3 license.

~~~~
Copyright (C) 2020 Alexandre Dulaunoy
Copyright (C) 2020 Pauline Bourmeau
~~~~
