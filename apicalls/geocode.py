import requests
import json
from datastore import dbaccess


census_api_string = """https://geocoding.geo.census.gov/geocoder/locations/address?street={0}&city={1}&state={2}&zip={3}&benchmark=9&format=json"""


def GeoFromDb(file_id):
    
    db = dbaccess.dbConn()
    sq = """SELECT sa.street_address_id, full_address, city, state, zipcode, latitude, longitude, 
            precinct_portion_id, 
            create_user
            FROM upload_data.street_address sa
            left outer join public.census_geocoded_address aa
            on aa.street_address_id = sa.street_address_id
            where 
            aa.census_geocode_id is null and
            processed_date is null and file_id='{0}';""".format(file_id)

    rec = db.get_data(sq, headers=False)
    for r in rec:
        cdic = {'address':r[1],'city':r[2],'state':r[3],'zip':r[4]}
        cg = CensusGeocode(**cdic)
        cg.getgeo()
        llat = 'not found'
        llong = 'not found'
        if len(cg.lat) > 0:
            llat = cg.lat[0]
        if len(cg.long) > 0:
            llong = cg.long[0]        
        
        q = """INSERT INTO public.census_geocoded_address(street_address_id, lat, long)
            select {0},'{1}','{2}'
            """.format(r[0], llat, llong)
        db.run_query(q)
    

class CensusGeocode(object):
    def __init__(self, **kwargs):
        self.address = kwargs['address'].replace(' ', '+')
        self.city = kwargs['city'].replace(' ', '+')
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
        
        
        
