import requests, re, pymongo, json
from flask import Flask, jsonify, request

MONGO_URI = "mongodb://suryaxanden:xyzzyspoonshift1!@ds137605.mlab.com:37605/ner_vals"
Google_Places_API_key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

client = pymongo.MongoClient(MONGO_URI)
db = client['ner_vals']
database = db.entities_found

def make_response_JSON(error_flag, response_message, entity_name, entity_classification):
    my_response = dict()
    data = dict()

    my_response['error_flag'] = error_flag
    my_response['response_message'] = response_message
    data['entity_name'] = entity_name
    data['entity_classification'] = entity_classification
    my_response['data'] = data

    return my_response

def Text_Preprocessing(text_blob):
    # remove multiple spaces and remove weird symbols and remove space and remove numbers
    text_blob = re.sub(r"[^a-zA-Z]", '', text_blob, 0, re.MULTILINE)
    return text_blob.lower()

def URL_Preprocessing(queriedString):
    # remove multiple spaces
    queriedString = re.sub(r"\s\s+", ' ', queriedString, 0, re.MULTILINE)
    # remove weird symbols
    queriedString = re.sub(r"[^ \w+\s?]", ' ', queriedString, 0, re.MULTILINE)    
    # replace space with +
    queriedString = re.sub(r"\s", '+', queriedString, 0, re.MULTILINE)
    return queriedString.lower()

Flask_db_copy = ''
def copy_from_db():
    global Flask_db_copy

    all_db_rec = database.find()

    if all_db_rec:
        Flask_db_copy = [{ "entity_name" : result['entity_name'], "entity_classification" : result['entity_classification'] } for result in all_db_rec]
        # return "Copied everything from database"
        return "ok"
    else:
        # return make_response_JSON(True, "Error fetching records from database", '', '')
        return "err"

copy_db_to_server_status = copy_from_db()

def find_record_in_database(queriedString, Google_Places_API_key, database):
    global Flask_db_copy
    try:            
        check = Text_Preprocessing(queriedString)

        for collection in Flask_db_copy:
            pp = collection['entity_name']
            pp = Text_Preprocessing(pp)
            
            if check in pp:
                return make_response_JSON(False, "Found in the database", collection['entity_name'], collection['entity_classification'])
        else:
            return Recognize(queriedString, Google_Places_API_key, database)
        
    except IndexError:
        return make_response_JSON(False, "Recognize returned no results", '', '')
    
    except Exception as e:
        return make_response_JSON(True, "Exception has occoured in Recognize : {}".format(e), '', '')

def Recognize(queriedString, Google_Places_API_key, database):
    PLACES_API_URL = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&fields=name,place_id&input={}&key={}'.format(queriedString, Google_Places_API_key)
    # print(PLACES_API_URL)
    try:
        PLACES_API_RESPONSE = requests.get(PLACES_API_URL)
        PLACES_API_DATA = PLACES_API_RESPONSE.json()
        entity_name = PLACES_API_DATA['candidates'][0]['name']
        place_id = PLACES_API_DATA['candidates'][0]['place_id']
        
        # DEBUG
        print("entity_name: ",entity_name, "place_id: ",place_id)

        if not (entity_name and place_id):
            return make_response_JSON(True, "Retry", '', '')

    except IndexError:
        return make_response_JSON(False, "Places API returned no results", '', '')

    except Exception as e:
        return make_response_JSON(True, "Exception has occoured in Places API call : {}".format(e), '', '')

    DETAILS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}&fields=type'.format(Google_Places_API_key, place_id)
    # print(DETAILS_API_URL)
    try:
        DETAILS_API_RESPONSE = requests.get(DETAILS_API_URL)
        DETAILS_API_DATA = DETAILS_API_RESPONSE.json()        
        entity_type_total = DETAILS_API_DATA['result']['types']
        # print(DETAILS_API_DATA)
        # insert code to classify entity based on its types
        entity_classification = entity_type_total
        # entity_classification = ""
        
        try:
            database.insert_one({ "_id": place_id, "entity_name" : entity_name, "entity_classification" : entity_classification })

            return make_response_JSON(False, "Database updated with 1 new record", entity_name, entity_classification)

        except pymongo.errors.DuplicateKeyError:
            # results = database.find({ "entity_name" : queriedString })
            # if results.count():
            # else:
                # return make_response_JSON(True, "Exception in pymongo call", '', '')
            return make_response_JSON(False, "Record already exists in the database", entity_name, entity_classification)

        except Exception as e:
            return make_response_JSON(True, "Pymongo Exception : {}".format(e), '', '')

    except IndexError:
        return make_response_JSON(False, "Details API returned no results", '', '')

    except Exception as e:        
        return make_response_JSON(True, "Exception has occoured in Details API call : {}".format(e), '', '')

app = Flask(__name__)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def index():
    if request.args.get("x") and request.args.get("x") != "1CE15CS145":
        temp_json = make_response_JSON(True, "Usage : localhost/?x=<SECRET_KEY>&q=<ENTITY>", '', '')
        return jsonify(temp_json)
    if request.args.get("q") and request.args.get("x") == '1CE15CS145':
        queriedString = request.args.get("q")
        queriedString = URL_Preprocessing(queriedString)

        if copy_db_to_server_status == "ok":
            API_response = find_record_in_database(queriedString, Google_Places_API_key, database)
            if API_response:
                return jsonify(API_response)
            else:
                temp_json = make_response_JSON(True, "API call has failed", '', '')
                return jsonify(temp_json)
                
        elif copy_db_to_server_status == "err":
            temp_json = make_response_JSON(True, "Cannot copy database to server", '', '')
            return jsonify(temp_json)
        
    else:
        temp_json = make_response_JSON(True, "Usage : localhost/?x=<SECRET_KEY>&q=<ENTITY>", '', '')
        return jsonify(temp_json)

'''
@app.route('/show/')
def showAll():
    if request.args.get("x"):
        x = request.args.get("x")
        if x != "1CE15CS145":
            return render_template('error.html', msg = "Unauthorized API call")
        else:
            try:            
                results = database.find()
                if results.count():                        
                    answer = [{ "entity_name" : result['entity_name'], "entity_classification" : result['entity_classification'] } for result in results]
                    return jsonify(answer)
                else:
                    return make_response_JSON(False, "Recognize returned no results", '', '')
            
            except IndexError:
                return make_response_JSON(False, "Recognize returned no results", '', '')
            
            except Exception as e:
                return make_response_JSON(True, "Exception has occoured in Recognize : {}".format(e), '', '')
    else:
        return render_template('index.html')
'''

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 80, debug = True, threaded = True)