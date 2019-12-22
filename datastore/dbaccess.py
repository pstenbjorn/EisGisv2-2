import psycopg2
from config import db_config
import models
import csv

class dbConn():
    
    def getcon(self, connname=None):
        if connname == None:
            connname = 'default'
        
        conn = psycopg2.connect(**db_config.DATABASES[connname])
        
        return conn
    
    def bulkinsert(self, lobj, ins_statement):
        cn = self.getcon(None)
        cur = cn.cursor()
        records_list_template = ','.join(['%s'] * len(lobj))
        ins_query = ins_statement + " VALUES {}".format(records_list_template)
        cur.execute(ins_query, lobj)
        cn.commit()
        cn.close()
        
    
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
    
    def insert_record(self, table_name, fields, values):
        
        cn = self.getcon(None)
        cur = cn.cursor()
        sql = "insert into {0} ({1}) SELECT {2}".format(table_name, fields, values)
        cur.execute(sql)
        cn.commit()
        cn.close()
     
    def run_query(self, query):
        cn = self.getcon(None)
        cur = cn.cursor()
        cur.execute(query)
        cn.commit()
        cn.close()
        
    def import_file(self, file_id, filepath, username):
                
        cn = self.getcon(None)
        sq = "select file_name, file_type from upload_data.uploaded_file where file_id ={0}".format(file_id)
        cur = cn.cursor()
        cur.execute(sq)
        filename = ""
        tablename = ""
        for r in cur:
            filename = filepath + r[0]
            tablename = r[1]
                       
        
        l = list()
        with open(filename, newline='') as csvfile:
            filereader = csv.reader(csvfile,delimiter=',')
            for row in filereader:
                l.append(row)
        
        tcur = cn.cursor()
        if not self.does_file_exist(file_id, tablename):
            
            if tablename == 'address':
                
                sql = """INSERT INTO upload_data.street_address(
                    full_address, house_number, house_number_suffix, 
                    street_predirection, street_name, street_type, address_postdirection, 
                    city, state, zipcode, latitude, longitude, precinct_portion_id
                    , file_id, create_user) 
                    SELECT '{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}','{14}'"""
                
                for rr in l:
                    if rr[0]!= 'full_address':
                        tcur.execute(sql.format(rr[0],rr[1],rr[2],rr[3],rr[4],rr[5],rr[6],rr[7],rr[8],rr[9],rr[10],rr[11],rr[12],file_id,username))
                    
            
            if tablename == 'district':
                
                
                sql = """INSERT INTO upload_data.district(
                    district_id, district_type_id, district_name, 
                    state, create_user, file_id)
                    select '{0}', 
                    (select district_type_id from upload_data.district_type where 
                        district_type_name = '{1}' and state = '{3}'),
                    '{2}', '{3}','{4}','{5}'"""
                
                for rr in l:
                    if rr[0] != 'district_id':
                        tcur.execute(sql.format(rr[0],rr[1],rr[2],rr[3], username,file_id))
    
            if tablename == 'precinctdistrict':
                sql = """INSERT INTO upload_data.district_precinct(
                        district_id, precinct_portion_id, state, create_user, file_id)
                        select '{0}','{1}','{2}','{3}','{4}'"""
                
                for rr in l:
                    if rr[0] != 'district_id':
                        tcur.execute(sql.format(rr[0],rr[1],rr[2],username,file_id))
        
        cn.commit()
        cn.close()
    
    def does_file_exist(self,file_id, tablename):
        pgtable = ''
        if tablename == 'address':
            pgtable = 'upload_data.street_address'
        if tablename == 'district':
            pgtable = 'upload_data.district'
        if tablename == 'precinctdistrict':
            pgtable = 'upload_data.district_precinct'
            
        q = "select count(*) from {0} where file_id ='{1}'".format(pgtable, file_id)
        dd = self.get_data(q, headers=False)
        recs = 0
        for i in dd:
            recs = i[0]
        
        if recs > 0:
            return True
        else:
            return False
        
            
    
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