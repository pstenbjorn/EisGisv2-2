import requests
import json

census_api_string = """https://geocoding.geo.census.gov/geocoder/locations/address?street={0}&city={1}&state={2}&zip={3}&benchmark=9&format=json"""


class CensusGeocode(object):
    def __init__(self, **kwargs):
        self.address = kwargs['address'].replace(' ', '+')
        self.city = kwargs['city']
        self.state = kwargs['state']
        self.zip = kwargs['zip']
        self.lat = list()
        self.long = list()
        
    def getgeo(self):
        url = census_api_string.format(self.address, self.city, self.state, self.zip)
        res = requests.get(url)
        j_res = json.loads(res.text)
        lats = list()
        longs = list()
        try:    
            matches = j_res['result']['addressMatches']
            if len(matches) > 0:
                for match in matches:
                    lats.append(match['coordinates']['y'])
                    longs.append(match['coordinates']['x'])
        except:
            lats.append('geocoding error')
            longs.append('geocoding error')
        
        self.lat = lats
        self.long = longs    
        
        
        
