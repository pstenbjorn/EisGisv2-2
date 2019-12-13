from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_login import LoginManager, current_user, login_user, login_manager
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os
import json
import models
from configs import Config
from forms import LoginForm, GeoCodeAddress
from datastore import dbaccess
from flask_login.utils import login_required
from apicalls import geocode as pgeo
import datetime

app = Flask(__name__)

app.config.from_object(Config)
dstorepath = 'datastore//'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

login = LoginManager(app)

login.login_view = 'login'

@login.user_loader
def load_user(id):
    return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
#@login_required
def index():
    d = {'title':'EIS Geoenabled Elections', 'pagename':'EIS Geoenabled Elections'}
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if 'userid' not in session['user']:
        return redirect(url_for('login'))
    
    user = session['user']['userid']
    return render_template('index.html', title=d["title"], pagename=d['pagename'], username=user)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        db = dbaccess.dbConn()
        ld = db.login(form.username.data, form.password.data, form.remember_me.data)
        if ld.is_authenticated == True:
            login_user(ld, remember=form.remember_me.data)            
            session["user"] = json.loads(ld.toJSON())
            next_page = url_for('index')            
            
            return redirect(next_page)
        else:
            flash('Login failed, please try again')
    
    return render_template('login.html', title='Sign In', pagename='Login to EIS GIS', form=form)
  
@app.route('/geocode', methods=['GET', 'POST'])
def geocode():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    form = GeoCodeAddress()
    if form.validate_on_submit():
        ad = {'address': form.fulladdress.data, 'city':form.city.data, 'state': form.state.data, 'zip':form.zipCode.data}
        geo = pgeo.CensusGeocode(**ad)
        geo.getgeo()        
        mapped_address = ad        
        lat = geo.lat[0]
        long = geo.long[0]
        return render_template('geocode.html', title='Test Geocoding', pagename='Test Geocoder', form=form, ad = mapped_address, lat=lat, long=long)
                        
    else:
        return render_template('geocode.html', title='Test Geocoding', pagename='Test Geocoder', form=form, username=session["user"]["userid"])
      

@app.route('/api/<ver>/<path>')
@app.route('/api/<ver>/<path>/<id>')
def api(ver=None,path=None,id=None):
    d = None
    if path == None:
        d = {'meta': {},
             'data': {'id': 222, 'name':'Paul'}}
    
    
    j = json.dumps(d)
    
    
    
    return j

@app.route('/delete/<tablename>/<idcolumn>/<rowid>')
def delete(tablename, idcolumn, rowid):
    db = dbaccess.dbConn() 
    q = "delete from {0} where {1} = {2}::int".format(tablename,idcolumn,rowid);
    db.run_query(q)
    
    return redirect('/upload')
    #return q

@app.route('/process')
def process():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = username=session["user"]["userid"]
    
    db = dbaccess.dbConn()
    q = """select distinct file_type from 
        upload_data.uploaded_file 
        where processed_date is null and create_user = '{0}'""".format(username)
    r = db.get_data(q, headers=False)
    
    
    

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['file']
        filetype = request.form.get('filetype')
        db = dbaccess.dbConn()            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = str(datetime.datetime.now()).replace(' ', '').replace('-','').replace(':','').replace('.','') + '_' + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            fields = 'file_name,file_type,create_user'
            values = "'{0}','{1}','{2}'".format(filename, filetype,session["user"]["userid"])
            db.insert_record('upload_data.uploaded_file', fields,values)
            return redirect('/upload')
    else:
        db=dbaccess.dbConn()
        q = """select '/' ||file_id::varchar as file_id, 
            file_name, file_type, create_date::varchar from upload_data.uploaded_file
            where 
            create_user = '{0}' and processed_date is null;
            """.format(session["user"]["userid"])
        d = db.get_data(q)
        cp = check_process()
                        
        return render_template('upload.html', title='Upload Files', pagename='File upload', data=d, can_process=cp, username=session["user"]["userid"])

def check_process():
    username = username=session["user"]["userid"]
    db = dbaccess.dbConn()
    q = """select distinct file_type from 
        upload_data.uploaded_file 
        where processed_date is null and create_user = '{0}'""".format(username)
    r = db.get_data(q, headers=False)   
    valid = ["address","district","precinctdistrict"]
    for rr in r:
        if rr[0] in valid:
            valid.remove(rr[0])
            
    if len(valid) > 0:
        return 0
    else:
        return 1