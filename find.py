import requests, re, pymongo, json
from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource
# from collections import *

MONGO_URI = "mongodb://suryaxanden:xyzzyspoonshift1!@ds137605.mlab.com:37605/ner_vals"
Google_Places_API_key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

client = pymongo.MongoClient(MONGO_URI)
db = client['ner_vals']
database = db.entities_found

def Text_Preprocessing(text_blob):
    # remove multiple spaces and remove weird symbols and remove space and remove numbers
    text_blob = re.sub(r"[^a-zA-Z]", '', text_blob, 0, re.MULTILINE)
    return text_blob.lower()

results = database.find()
if results:
    Flask_db_copy = [{ "entity_name" : result['entity_name'], "entity_classification" : result['entity_classification'] } for result in results]

queriedString = input("Search string: ")

queriedString = Text_Preprocessing(queriedString)

for collection in Flask_db_copy:
    pp = collection['entity_name']
    pp = Text_Preprocessing(pp)
    if queriedString in pp:
        print(collection)
        break