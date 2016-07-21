"""
Routes and views for the flask application.
"""

import datetime
from flask import render_template,request,session
from FlaskWebProject1 import app
from pymongo import MongoClient
from bson import ObjectId
import base64
import time,os

app.secret_key = 'Your Key'

def checkcredentials(uname,encrpted):
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    db = client.myazuredb
    id = db.login.find_one({'username': uname, 'password': encrpted})
    return id

def checkusercredentials(uname):
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    db = client.myazuredb
    id = db.login.find_one({'username': uname})
    return id

def insertnewuser(uname, encrpted, psize, nsize, lsize):
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    db = client.myazuredb
    db.login.insert({'username': uname, 'password': encrpted, 'psize': psize, 'nsize': nsize, 'lsize': lsize})
    return

@app.route('/takeuserinput',methods=['POST', 'GET'])
def takeuserinput():
    progsttime = time.time()
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    if request.method == 'POST':
        if request.form['submit'] == 'User Input':
            uname = request.form['uname']
            min = request.form['input1']
            number = request.form['input2']
            myrec = []
            pictime = []
            dbsttime = time.time()
            db = client.myazuredb
            pasttime = datetime.datetime.now() - datetime.timedelta(minutes=int(min))
            #rec = db.posts.find()
            print pasttime
            d,t = str(pasttime).split()
            t = t[:-3]
            print t
            rtime = d + 'T' + t + 'Z'
            print rtime
            '''
            recs = db.posts.find()
            for rec in recs:
                print rec['datetime']
                if (str(rec['datetime']) >= str(pasttime)):
                    myrec.append(rec)
            '''
            rec = db.posts.find( { "$and": [{'username':session['username']}, {'datetime': {"$gt": pasttime}}]})
            dbendtime = time.time() - dbsttime
            return render_template('showdata.html', datas=rec, pictime=pictime, dbtime=dbendtime, username=session['username'])

@app.route('/update',methods=['POST', 'GET'])
def update():
    progsttime = time.time()
    progendtime = time.time()
    dbsttime = time.time()
    dbendtime = time.time()
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    if request.method == 'POST':
        if request.form['submit'] == 'Update':
            field = request.form['field']
            data = request.form['data']
            id = request.form['id']
            db = client.myazuredb
            if (field == 'priority'):
                if (int(data) < 0 or int(data) > 10):
                    message = 'Priority range must be between 0 to 10'
                    rec = db.posts.find({'username': session['username']})
                    return render_template('showdata.html', datas=rec, username=session['username'],progtime=progendtime,dbtime=dbendtime,message=message)
            db.posts.update({'_id':ObjectId(id)},{"$set": {field:data}})
            rec = db.posts.find({'username': session['username']})
            return render_template('showdata.html', datas=rec, username=session['username'],progtime=progendtime,dbtime=dbendtime)

@app.route('/upload',methods=['POST', 'GET'])
def upload():
    progsttime = time.time()
    progendtime = time.time()
    dbsttime = time.time()
    dbendtime = time.time()
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    if request.method == 'POST':
        if request.form['submit'] == 'Upload':
            db = client.myazuredb
            userinfo = db.login.find_one({'username': session['username']},{'psize': 1, 'nsize':1, 'lsize':1})
            lsize = userinfo['lsize']
            count = db.posts.find({'username':session['username']}).count()

            if(lsize == ''):
                lsize = 999
            else:
                lsize = int(lsize)
            
            
            if (count >= lsize):
                message = 'No of files Limit exceeded'
                return render_template('login.html', username=session['username'], message=message)
            
            ufile = request.files['fileToUpload']
            subject = request.form['subject']
            priority = request.form['priority']
            
            #filesize = os.stat(ufile.filename).st_size
            blob = ufile.read()
            filesize = len(blob)
            
            
            if ufile.filename.endswith(".txt"):
                if (filesize <= int(userinfo['nsize'])):
                    type="text"
                    content = blob
                else:
                    message = 'Note is too large to upload'
                    return render_template('login.html', username=session['username'], message=message)
            else:
                if (filesize <= int(userinfo['psize'])):
                    type="image"
                    content = base64.b64encode(blob)
                else:
                    message = 'Image is too large to upload'
                    return render_template('login.html', username=session['username'], message=message)
            
            post = {"content": content, "type": type, "subject": subject, "priority": priority, "datetime": datetime.datetime.now(), "username": session['username']}
            dbsttime = time.time()
            post_id = db.posts.insert_one(post).inserted_id
            
    dbendtime = time.time() - dbsttime
    progendtime = time.time() - progsttime
    return render_template('login.html',username=session['username'],progtime=progendtime,dbtime=dbendtime)

@app.route('/showdata',methods=['POST', 'GET'])
def showdata():
    progsttime = time.time()
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    if request.method == 'POST':
        if request.form['submit'] == 'Show':
            field = request.form['field']
            order = request.form['order']
            dbsttime = time.time()
            db = client.myazuredb
            if (order == 'ascending'):
                rec = db.posts.find({'username': session['username']}).sort([(field, 1)])
            else:
                rec = db.posts.find({'username': session['username']}).sort([(field, -1)])
            dbendtime = time.time() - dbsttime
            progendtime = time.time() - progsttime
            return render_template('showdata.html', datas=rec, username=session['username'],progtime=progendtime,dbtime=dbendtime)

@app.route('/delete/<id>')
def delete(id):
    print id
    client = MongoClient('mongodb://Username:yourpassword@mlab.com:portnumber/userdb')
    db = client.myazuredb
    db.posts.delete_one({'_id':ObjectId(id)})
    rec = db.posts.find({'username': session['username']})

    return render_template('showdata.html', datas=rec,username=session['username'])

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if request.form['submit'] == 'Login':

            session['username'] = request.form['username']
            pwd = request.form['password']
            encrped = base64.b64encode(pwd)
            id = checkcredentials(session['username'],encrped)
            #print id
            if (id == None):
                result = 'Invalid username and password. Please try again.'
                return render_template('index.html', result=result)

            return render_template('login.html', username=session['username'])

@app.route('/logout',methods=['POST', 'GET'])
def logout():
    session["__invalidate__"] = True
    return render_template('index.html')

@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
    if request.method == 'POST':
        if request.form['submit'] == 'Sign up':

            newusername = request.form['username']
            pwd = request.form['password']

            #dbconnect()
            encrped = base64.b64encode(pwd)
            
            id = checkusercredentials(newusername)
            #print id
            if (id != None):
                result = 'User Name already exists. Please try again.'
                return render_template('index.html', result=result)
            
            session['username'] = newusername
            psize = request.form['psize']
            nsize = request.form['nsize']
            lsize = request.form['lsize']
            insertnewuser(newusername, encrped, psize, nsize, lsize)
            return render_template('login.html', username=session['username'])

    return render_template('index.html')

@app.route('/')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.datetime.now().year,
    )


