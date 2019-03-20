import json, requests
# from time import sleep
# from nltk import *
from textblob import TextBlob

with open('cleaned_file.csv', mode='r', encoding='UTF-8', errors='strict', buffering=1) as f:
    lines = f.readlines()

nouns = list()

with open('read input.csv', mode='w', encoding='UTF-8', errors='strict', buffering=1) as f:
    
    f.write('Read input\n')
    
    for line in lines:
        f.write( line.strip() + '\n')

for line in lines:
    blob = TextBlob(line)
    nouns.append(" ".join( blob.noun_phrases ))


with open('only nouns.csv', mode='a', encoding='UTF-8', errors='strict', buffering=1) as f:
    
    f.write('\nOnly nouns\n')
    
    for i in nouns:
        f.write( i + '\n')