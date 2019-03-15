import requests, re, pymongo
# from bson import ObjectId
from flask import Flask, jsonify, request, render_template

MONGO_URI = "mongodb://suryaxanden:xyzzyspoonshift1!@ds137605.mlab.com:37605/ner_vals"
key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

client = pymongo.MongoClient(MONGO_URI, connectTimeoutMS = 30000)
db = client['ner_vals']
entities_found = db.entities_found

try:
    ins = entities_found.insert_one({ "_id": 130, "entity_name" : "abc", "entity_type_total" : "bank maybe", "entity_classification" : "bank" })
    print(ins)

except pymongo.errors.DuplicateKeyError:
    print("Already Exists")

except Exception as e:
    print(e)
