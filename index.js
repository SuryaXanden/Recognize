const fetch = require('node-fetch');
const express = require('express');
const key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ";


function getPlaceDetails(q,res) {
    let PLACES_API_URL = `https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&fields=name,place_id&input=${q}&key=${key}`;
    let request_to_places = () => fetch(PLACES_API_URL)
    .then(resp => resp.json())
    .then(API => {
        return { 
            "entity_name": API['candidates'][0]['name'],
            "place_id" : API['candidates'][0]['place_id']                
        } 
    });
    
    let request_details = request_to_places().then(place_search => {
        let DETAILS_API_URL = `https://maps.googleapis.com/maps/api/place/details/json?key=${key}&placeid=${place_search['place_id']}&fields=type`;
        return fetch(DETAILS_API_URL)
        .then(response => response.json())
        .then(json => {
            return {
                "entity_name": place_search['entity_name'],
                "place_id" : place_search['place_id'],
                "place_details": json['result']['types']
            }
        });
    });
    request_details.then(output => res.send(JSON.stringify(output)));
    // request_details.then(output => console.log(JSON.stringify(output)))
}


const app = express();
const port = 80;

app.get('/', (req, res) => {
    let q = req.query.q;
    if(q)
    {
        q = q.replace(/\s\s+/img, ' ');
        q = q.replace(/[^ \w+\s?]/img, ' ');
        q = q.replace(/\s/img, '+');
        getPlaceDetails(q,res);
    }
    else
    {
        res.send('<title>Recognize</title><span>Usage <a href="http://localhost/?q=kfc resturant ind">http://localhost/?q=kfc resturant ind</a></span>')
    }
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))