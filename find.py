import requests, re, pymongo
# from bson import ObjectId
from flask import Flask, jsonify, request, render_template

MONGO_URI = "mongodb://suryaxanden:xyzzyspoonshift1!@ds137605.mlab.com:37605/ner_vals"
key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

client = pymongo.MongoClient(MONGO_URI) #, connectTimeoutMS = 30000)
db = client['ner_vals']
entities_found = db.entities_found
# q = ''
# item = re.compile(".*{}.*".format(q),re.IGNORECASE)
# q = entities_found.find_one({'entity_name': item})
# print(q)

q = "mc donalds india"
item = re.compile(".*{}.*".format(q),re.IGNORECASE)
results = entities_found.find({ "entity_name" : item })
if results:
    print(False, "Found in the database",results[0]['entity_name'],results[0]['entity_classification'])