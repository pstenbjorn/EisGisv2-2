import psycopg2
from config import db_config
import models

class dbConn():
    
    def getcon(self, connname=None):
        if connname == None:
            connname = 'default'
        
        conn = psycopg2.connect(**db_config.DATABASES[connname])
        
        return conn
    
    def login(self, username, password, remember):
        i = 0
        un = ''
        cn = self.getcon(None)
        query = "select user_name from eis_admin where userid = '{0}' and user_pass = '{1}'".format(username, password)
        with cn.cursor() as cur:
            cur.execute(query)
            for r in cur:
                un = r[0]
                i+=1
        
        cn.close()
        l = [True if i>0 else False, True, False, un]
        thisuser = models.User(*l)
                
        return thisuser
        
    
    def get_data(self, query, instance=None, headers=True):
        
        rs = []
        cn = self.getcon(instance)
        with cn.cursor() as cur:
            cur.execute(query)
            if headers: 
                cols = [c[0] for c in cur.description]
                rs.append(tuple(cols))                
            for r in cur:
                rs.append(r)                        
        
        cn.close()
        return rs