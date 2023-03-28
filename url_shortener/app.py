import os
from flask import Flask,render_template,request,flash,redirect,url_for

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import pyshorteners
from urllib.parse import urlparse

from validators import url as validate_url


app=Flask(__name__)


#######################SQLALCHEMY CONFIGURATION#############################


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)  #passing application to sqlalchemy this creates object to sqlalchemy
Migrate(app, db)        #migrate flask object and sqlalchemy object


############################################################################
###############################creating tabkle/model#########################


class Url_shortner(db.Model):
    __tablename__='URL' #defining table name as grocery

    #definning columns of table
    id=db.Column(db.Integer, primary_key = True)
    url=db.Column(db.Text,unique=True)
    short_url=db.Column(db.Text,unique=True)

    #creating a constructor
    def __init__(self, url, short_url):
        self.url=url
        self.short_url=short_url

    
    def __repr__(self):
        return "url name is {} and short url is {}".format(self.url,self.short_url) 
    


@app.route('/')
def index():
    return render_template('Home.html')


@app.route('/add',methods=['GET','POST'])
def add_input():
    url=''
    short_url=''
    if request.method=='POST':
        url=request.form.get('url_L')

        # check if input is a valid url
        if not validate_url(url):
            return "Invalid Url!Go back to our User Input page anbd enter a valid url"
        
        else:
    #check whether url already exist in databse
            found_url =Url_shortner.query.filter_by(url=url).first()
            if found_url:
                return render_template('input.html',short=found_url.short_url)

            else:
                short_url = pyshorteners.Shortener().tinyurl.short(url)


        # appending input values to database created
                new_url = Url_shortner(url, short_url)
                db.session.add(new_url)
                db.session.commit()
    return render_template('input.html',short=short_url)
        
    


@app.route('/searchitem',methods=['GET','POST'])
def find():
    if request.method=='POST':
        url = request.form.get('item')

        if not validate_url(url):
            return "Invalid Url!Go back and enter the correct url"
        else:
            item = Url_shortner.query.filter_by(url=url).first()
            if item:
                return render_template('search.html', item=item.short_url)
            else:

                return "Url not found!Use our User input page to shorten you url"
        
    return render_template('search.html')

@app.route('/display',methods=['Get','POST'])
def display_items():
    items=Url_shortner.query.all()
    

    if request.method=='POST':
        db.session.query(Url_shortner).delete()
        db.session.commit()
        return redirect(url_for('display_items'))

    return render_template('displays.html',items=items)


















if __name__=='__main__':
    app.run(debug=True)