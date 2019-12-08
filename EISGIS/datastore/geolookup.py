
district_type_table = [{'US' : {'congress': 'tl_2017_us_cd115', 'counties': 'tl_2018_us_county'}}, 
                       {'AZ': {'lower_house': 'tl_2018_04_sldl', 'upper_house': 'tl_2018_04_sldu'}}]

def get_district(state, type, lat, long):
    
    t = district_type_table[state][type]
    plsql = """select t.namelsad
    from {0} t 
    where ST_CONTAINS(ST_SetSRID(geom, 2263), ST_GeometryFromText('POINT({1} {2})', 2263))""".format(t, long, lat)
    