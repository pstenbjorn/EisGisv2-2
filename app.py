from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_login import LoginManager, current_user, login_user, login_manager
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os
import json
import models
from configs import Config
from forms import LoginForm
from datastore import dbaccess
from flask_login.utils import login_required


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
    
    return render_template('index.html', title=d["title"], pagename=d['pagename'])
    
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
            session["user"] = ld.toJSON()
            next_page = url_for('index')            
            
            return redirect(next_page)
        else:
            flash('Login failed, please try again')
    
    return render_template('login.html', title='Sign In', pagename='Login to EIS GIS', form=form)
    

@app.route('/api/<ver>/<path>')
@app.route('/api/<ver>/<path>/<id>')
def api(ver=None,path=None,id=None):
    d = None
    if path == None:
        d = {'meta': {},
             'data': {'id': 222, 'name':'Paul'}}
    
    
    j = json.dumps(d)
    
    
    
    return j

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']    
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect('/upload')
    else:
        return render_template('upload.html', title='Upload Files', pagename='File upload')

    