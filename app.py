import requests, re, pymongo
from flask import Flask, jsonify, request, render_template

MONGO_URI = "mongodb://suryaxanden:xyzzyspoonshift1!@ds137605.mlab.com:37605/ner_vals"
key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

client = pymongo.MongoClient(MONGO_URI)
db = client['ner_vals']
entities_found = db.entities_found

def preProcessing(q):
    # remove multiple spaces
    q = re.sub(r"\s\s+", ' ', q, 0, re.MULTILINE)

    # remove weird symbols
    q = re.sub(r"[^ \w+\s?]", ' ', q, 0, re.MULTILINE)
    
    # replace space with +
    q = re.sub(r"\s", '+', q, 0, re.MULTILINE)

    return q

def responder(error, status, entity_name, entity_classification):
    my_response = dict()
    my_response['error'] = error
    my_response['status'] = status

    data = dict()

    data['entity_name'] = entity_name
    data['entity_classification'] = entity_classification

    my_response['data'] = data
    return my_response

'''
# Ask
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
'''

def find_in_db(q, key, entities_found):
    item = re.compile(".*{}.*".format(q), re.IGNORECASE)
    try:            
        results = entities_found.find({ "entity_name" : item })
        if results:
            return responder(False, "Found in the database", results[0]['entity_name'], results[0]['entity_classification'])
        else:
            return make_API_call(q, key, entities_found)
    except Exception as e:
        return responder(True, "Exception has occoured in Recognize : {}".format(e), '', '')

def make_API_call(q, key, entities_found):
    PLACES_API_URL = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&fields=name,place_id&input={}&key={}'.format(q, key)

    try:
        PLACES_API_RESPONSE = requests.get(PLACES_API_URL)
        PLACES_API_DATA = PLACES_API_RESPONSE.json()
        entity_name = PLACES_API_DATA['candidates'][0]['name']
        place_id = PLACES_API_DATA['candidates'][0]['place_id']

        if not (entity_name and place_id):
            return responder(True, "Retry", '', '')

    except IndexError:
        return responder(False, "Places API returned no results", '', '')

    except Exception as e:
        return responder(True, "Exception has occoured in Places API call : {}".format(e), '', '')

    DETAILS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}&fields=type'.format(key, place_id)

    try:
        DETAILS_API_RESPONSE = requests.get(DETAILS_API_URL)
        DETAILS_API_DATA = DETAILS_API_RESPONSE.json()        
        entity_type_total = DETAILS_API_DATA['result']['types']

        # insert code to classify entity based on its types
        entity_classification = ""
        
        # add to db
        try:
            entities_found.insert_one({ "_id": place_id, "entity_name" : entity_name, "entity_classification" : entity_classification })

            return responder(False, "Database updated with 1 new record", entity_name, entity_classification)

        except pymongo.errors.DuplicateKeyError:
            results = entities_found.find({ "entity_name" : q })
            if results:
                return responder(False, "Record already exists in the database", results[0]['entity_name'], results[0]['entity_classification'])
            else:
                return responder(True, "Exception in pymongo call", '', '')

        except Exception as e:
            return responder(True, "Pymongo Exception : {}".format(e), '', '')

    except IndexError:
        return responder(False, "Details API returned no results", '', '')

    except Exception as e:        
        return responder(True, "Exception has occoured in Details API call : {}".format(e), '', '')

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    if request.args.get("q") and request.args.get("x"):
        x = request.args.get("x")

        if x != "1CE15CS145":
            return render_template('error.html', msg = "Unauthorized API call")

        # QUERY keyword
        q = request.args.get("q")

        q = preProcessing(q)

        API_response = find_in_db(q, key, entities_found)

        if API_response:
            return jsonify(API_response)

        else:
            return render_template('error.html', msg = "API call has failed")

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)