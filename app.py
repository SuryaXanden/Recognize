import requests, re
from flask import Flask, jsonify, request, render_template

def make_a_call(q):
    
    q = re.sub(r"\s\s+", ' ', q, 0, re.MULTILINE)
    q = re.sub(r"[^ \w+\s?]", ' ', q, 0, re.MULTILINE)
    q = re.sub(r"\s", '+', q, 0, re.MULTILINE)

    key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

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
            
    except:
        print("error in Places API call")
        return

    # DETAILS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}&fields=address_component,scope,type'.format(key,place_id)
    DETAILS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}&fields=type'.format(key,place_id)

    try:
        
        DETAILS_API_RESPONSE = requests.get(DETAILS_API_URL)

        DETAILS_API_DATA = DETAILS_API_RESPONSE.json()
        
        est_type = DETAILS_API_DATA['result']['types']

        return {"entity name" : entity_name,"entity type" : est_type}

    except:
        
        print("error in Details API call")
        
        return

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    if request.args.get("q"): 
        q = request.args.get("q")
        API_response = make_a_call(q)
        if API_response:
            return jsonify(API_response)
        else:
            return render_template('error.html', msg = "API call has failed" )
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80,debug=True,threaded=True)