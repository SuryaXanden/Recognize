import requests, re, pymongo
# from bson import ObjectId
from flask import Flask, jsonify, request, render_template

MONGO_URI = "mongodb://suryaxanden:xyzzyspoonshift1!@ds137605.mlab.com:37605/ner_vals"
key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

client = pymongo.MongoClient(MONGO_URI, connectTimeoutMS = 30000)
db = client['ner_vals']
entities_found = db.entities_found

# try:

ids = [ i['_id'] for i in entities_found.find({ "entity_name" : {'$regex' : '.*abc.*', '$options' : 'i'} })]

print(ids)

q = entities_found.delete_many({'_id': {'$in' : ids[1:]} })

ids = [ i['_id'] for i in entities_found.find({ "entity_name" : {'$regex' : '.*abc.*', '$options' : 'i'} })]
print(ids)

# for i in entities_found.find({ "entity_name" : {'$regex' : '.*abc.*', '$options' : 'i'} }):
    # 

# except pymongo.errors.DuplicateKeyError:
    # print("Already Exists")

# except Exception as e:
    # print(e)
