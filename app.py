import requests, re, pymongo
# from bson import ObjectId
from flask import Flask, jsonify, request, render_template

MONGO_URI = "mongodb://suryaxanden:xyzzyspoonshift1!@ds137605.mlab.com:37605/ner_vals"
key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

client = pymongo.MongoClient(MONGO_URI, connectTimeoutMS = 30000)
db = client['ner_vals']
entities_found = db.entities_found

# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)

def preProcessing(q):
    # remove multiple spaces
    q = re.sub(r"\s\s+", ' ', q, 0, re.MULTILINE)

    # remove weird symbols
    q = re.sub(r"[^ \w+\s?]", ' ', q, 0, re.MULTILINE)
    
    # replace space with +
    q = re.sub(r"\s", '+', q, 0, re.MULTILINE)

    return q

def remove_redundancy(q):
    try:
        ids = [ i['_id'] for i in entities_found.find({ "entity_name" : {'$regex' : '.*{}.*'.format(q), '$options' : 'i'} })]
        try:
            _ = entities_found.delete_many({'_id': {'$in' : ids[1:]} })
        except Exception as e:            
            print(e)
            return

    except Exception as e:
        print(e)
        return

def find_in_db(q,key,entities_found):
    result = entities_found.find_one({ "entity_name" : {'$regex' : '.*{}.*'.format(q), '$options' : 'i'} })
    if result:
        # status found in db
        return result
    else:
        make_API_call(q,key,entities_found)

def make_API_call(q,key,entities_found):
    
    q = preProcessing(q)

    # PLACES_API_URL = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&fields=name,place_id&input={}&key={}'.format(q,key)
    PLACES_API_URL = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&fields=name,place_id&input={}&key={}'.format(q,key)

    try:
        PLACES_API_RESPONSE = requests.get(PLACES_API_URL)
        PLACES_API_DATA = PLACES_API_RESPONSE.json()
        entity_name = PLACES_API_DATA['candidates'][0]['name']
        place_id = PLACES_API_DATA['candidates'][0]['place_id']

        if not (entity_name and place_id):
            print("Retry")
            return

    except IndexError:
        print("0 results found in PLACES API RESPONSE")
        return

    except Exception as e:
        print("Error in Places API call! => [{}]".format(e))
        return

    # DETAILS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}&fields=address_component,scope,type'.format(key,place_id)
    DETAILS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}&fields=type'.format(key,place_id)

    try:
        DETAILS_API_RESPONSE = requests.get(DETAILS_API_URL)
        DETAILS_API_DATA = DETAILS_API_RESPONSE.json()        
        entity_type_total = DETAILS_API_DATA['result']['types']

        # insert code to classify entity based on its types
        entity_classification = ""
        
        # add to db
        try:
            entities_found.insert_one({ "_id": place_id, "entity_name" : entity_name, "entity_type_total" : entity_type_total, "entity_classification" : entity_classification })
            
            # return status as successfully inserted
            return { "_id": place_id, "entity_name" : entity_name, "entity_type_total" : entity_type_total, "entity_classification" : entity_classification }

        except pymongo.errors.DuplicateKeyError:
            print("Record already exists")
            # return status as exists
            return

        except Exception as e:
            print(e)
            # return status as exception in db ins
            return 

    except IndexError:
        print("0 results found in DETAILS API RESPONSE")
        return

    except Exception as e:        
        print("Error in Details API call! => [{}]".format(e))        
        return

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    if request.args.get("q"): 
        q = request.args.get("q")
        API_response = find_in_db(q,key,entities_found)
        if API_response:
            return jsonify(API_response)
        else:
            return render_template('error.html', msg = "API call has failed", issue = "" )
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80,debug=True,threaded=True)