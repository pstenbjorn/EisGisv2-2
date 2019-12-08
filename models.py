from datastore import dbaccess as db
from utils import ps_util as u
from flask_login import UserMixin
import json


class User():
    def __init__(self, *args):
        self.is_authenticated = args[0]
        self.is_active = args[1]
        self.is_anonymous = args[2]
        self.userid = args[3]
    
    def get_id(self):
        return self.userid

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
class districts():
    def __init__(self, **kwargs):
        self.districtid = kwargs['districtid']
        self.district_name = kwargs['district_name']
        self.url = kwargs['url']
        self.shape_file = kwargs['shape_file']
        self.ocdid = kwargs['ocdid']
        
        
def get_districts(limit):
    d = db.dbConn()   
    s = "select * from districts.district"
    if len(limit) > 0:
        s += " where districtid in ("
        for l in limit:
            s+= str(l) + ','            
        
        s = s[:-1]
        s += ")"
    r = d.get_data(s)
    dc = u.list_to_dict(r)
    w = []
    for i in dc:
        ww = districts(**i)
        w.append(ww)
            
    return w
        
        
        
        