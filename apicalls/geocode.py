import requests


class CensusGeocode(object):
    def __init__(self, **kwargs):
        self.address = kwargs['addresss']
        self.city = kwargs['city']
        self.state = kwargs['state']
        self.zip = kwargs['zip']
        self.lat
        self.long
        
"""https://geocoding.geo.census.gov/geocoder/locations/address?street=4869+Bonnie+Brae+Rd&city=Richmond&state=VA&zip=23234&benchmark=9&format=json
"""        