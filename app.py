#make an API call
import requests

q = raw_input("Enter the search term: ")

key = "AIzaSyDLTDdea9gVmUj8rhsKf_y0p1WcV01o5AQ"

API_URL = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&fields=name,place_id&input={}&key={}'.format(q,key)

API_RESPONSE = requests.get(API_URL)
API_DATA = API_RESPONSE.json()

# print(API_DATA)


