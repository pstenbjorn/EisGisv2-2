import requests
import json
from datastore import dbaccess
import asyncio


arcgis_clientid = "XtOL7IWHA13SPXZI"
arcgis_client_secret = "05968d4dece94858a4e2b1e6b3b70f84"
arcgis_auth = "https://www.arcgis.com/sharing/oauth2/token?client_id={0}&grant_type=client_credentials&client_secret={1}&f=pjson"
arcgis_geo = "http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?singleLine={0}&forStorage=true&token={1}&f=pjson"
census_api_string = """https://geocoding.geo.census.gov/geocoder/locations/address?street={0}&city={1}&state={2}&zip={3}&benchmark=9&format=json"""


async def AssyncGeo(recs):
    glist = list()
    for r in recs:
        cdic = {'address':r[1],'city':r[2],'state':r[3],'zip':r[4]}
        ag = ArcGisGeoCode(**cdic)
        ag.GetGeo()
        llat = 'not found'
        llong = 'not found'
        if len(ag.lat) > 0:
            llat = ag.lat[0]
        if len(ag.long) > 0:
            llong = ag.long[0]
            
        tp = (r[0], llat, llong)
        glist.append(tp)
    
    return glist
    

async def GeoFromDb(file_id):
    
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
    if len(rec) > 0:
        res = await AssyncGeo(rec)
        db.bulkinsert(res, "INSERT INTO public.census_geocoded_address(street_address_id, lat, long)")
 
def processAddresses(username): 
    db = dbaccess.dbConn()
    sq = """select s.street_address_id, ga.lat, ga.long, d.district_name, d.district_type_name, 
        d.district_id, d.district_type_id,
        d.geo_table 
        from upload_data.street_address s
        inner join 
        (select dp.precinct_portion_id, dp.district_id, dd.district_name, dt.district_type_id, dt.district_type_name, dt.geo_table from
        upload_data.district_precinct dp 
        inner join upload_data.district dd on dd.district_id = dp.district_id
        inner join upload_data.district_type dt on dt.district_type_id = dd.district_type_id
          where dp.processed_date is null and dd.processed_date is null
        ) d on
         d.precinct_portion_id = s.precinct_portion_id
        inner join public.census_geocoded_address ga on ga.street_address_id = s.street_address_id
        where s.processed_date is null and s.create_user = '{0}'""".format(username)
    
    rec = db.get_data(sq, headers=False)
    for aa in rec:
        ad = {'lat':aa[1], 'long':aa[2],'geotable':aa[7], 'dist_name':aa[3], 'dist_type':aa[4]}
        ageo = GeoValidate(**ad)
        ageo.getMapped()
        sqlins = """INSERT INTO public.audited_addresses(
            street_address_id, district_id, district_type_id, 
            mapped_district_name, geocoding_source, dist_from_edge, matches, create_user)
            VALUES ({0},'{1}', {2},
             '{3}', '{4}', {5}, {6}, '{7}');""".format(aa[0],aa[5],aa[6], ageo.mapped_dist,'ArcGis',ageo.km_from_edge, ageo.matched, username)
        db.run_query(sqlins)
        
    #update data_upload tables
    usql = "update upload_data.{0} set processed_date = now() where processed_date is null and create_user = '{1}'"
    db.run_query(usql.format('district', username))
    db.run_query(usql.format('district_precinct', username))
    db.run_query(usql.format('street_address', username))
   
   
class GeoValidate(object):
    def __init__(self,**kwargs):
        self.lat = kwargs['lat']
        self.long = kwargs['long']
        self.table = kwargs['geotable']
        self.dist_name = kwargs['dist_name']
        self.dist_type = kwargs['dist_type']
        self.mapped_dist =''
        self.km_from_edge = 0
        self.matched = False
        
    def getMapped(self):
        db = dbaccess.dbConn()
        psql = """select t.namelsad,
        st_distance(ST_Transform(ST_GeometryFromText('POINT({1} {2})', 4326)::geometry, 3857)
                             ,ST_Transform(ST_Boundary(ST_SetSRID(geom, 4326))::geometry, 3857)) as dist
        from public.{0} t 
        where ST_CONTAINS(ST_SetSRID(geom, 4326), 
            ST_GeometryFromText('POINT({1} {2})', 4326))""".format(self.table, self.long, self.lat)
        rec = db.get_data(psql, headers=False)
        for r in rec:
            self.mapped_dist = r[0]
            self.km_from_edge = float(r[1])/1000
    
        try:
            if ' ' + str(int(self.dist_name)) in self.mapped_dist:
                self.matched = True
        except:
            if ' ' + str(self.dist_name) in self.mapped_dist:
                self.matched = True
    
    
class ArcGisGeoCode(object):
    def __init__(self,**kwargs):
        self.address = kwargs['address']
        self.city = kwargs['city']
        self.state = kwargs['state']
        self.zip = kwargs['zip']
        self.lat = list()
        self.long = list()
        
    def GetToken(self):
        url = arcgis_auth.format(arcgis_clientid, arcgis_client_secret)
        result = requests.get(url)
        json_result = json.loads(result.text)
        token = json_result['access_token']
        return token
    
    def GetGeo(self):
        address = "{0}, {1}, {2}, {3}".format(self.address,self.city,self.state,self.zip)
        url = arcgis_geo.format(address,self.GetToken())
        result = requests.get(url)
        json_result = json.loads(result.text)
        candidates = json_result['candidates']
        lats = list()
        longs = list()
        for c in candidates:
            lats.append(c['location']['y'])
            longs.append(c['location']['x'])
        self.lat = lats
        self.long = longs
       
        
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
        
        
        
