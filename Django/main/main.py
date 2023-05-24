from flask import Flask, jsonify, abort
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import UniqueConstraint
import requests
from producer import publish
import sched
import time
import sys

from humiolib.HumioClient import HumioIngestClient
import json
import re
import time
import subprocess

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
## --
import json_log_formatter
import logging
from logging.handlers import RotatingFileHandler
## --
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@db/main'
CORS(app)

db = SQLAlchemy(app)
## --
formatter = json_log_formatter.JSONFormatter()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
## --







@dataclass
class Product(db.Model):
    id: int
    title: str
    image: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))

@dataclass
class User(db.Model):
    id: int
    emailID: str
    passwrd: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    emailID = db.Column(db.String(200))
    passwrd = db.Column(db.String(200))


@dataclass
class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')

@app.route('/api/products')
def index():
    logger.info('Product list requested')
    return jsonify(Product.query.all())

@app.route('/api/products/<int:id>/<int:iid>/like', methods=['POST'])
def like(id,iid):
    s = 'http://172.17.0.1:8000/api/user/' + str(iid)
    req = requests.get(s)
    json = req.json()

    try:
        productUser = ProductUser(user_id=json['id'], product_id=id)
        db.session.add(productUser)
        logger.info('Product liked', extra={'product_id': id, 'user_id': json['id']})
        db.session.commit()

        
        publish('product_liked', id)
    except:
        abort(400, 'You already liked this product')
    
    return jsonify({
        'message': 'success' 
    })


scheduler = sched.scheduler(time.time, time.sleep)

def send_logs():
    try:
        #uid =  db.session.query(User).filter_by(id=1).first()
        #mail = uid.emailID
        client = HumioIngestClient(base_url= "https://cloud.community.humio.com",ingest_token="2c8e1aa3-bb43-4569-8438-b97fc40412ab")
        split_words = ['DEBUG','ERROR','WARNING','INFO']
        #print(split_words)
        pattern = "|".join(map(re.escape,split_words))
        #print(pattern)


        messages =[]
        f = open("./test.log","r")
        prev = ""
        for i in f.readlines():
            if re.search(pattern,i):
                #print(prev)
                messages.append(prev)
                prev = i
            else:
                prev += i
        # to pop the first empty string appended to it
        messages.pop(0)

        #print(messages)
        client.ingest_messages(messages)
        print("Ingestion done")

        

        log_objects = []

        with open('test.log') as f:
            for line in f:
                match = re.search(r'\{.*\}', line)
                if match:
                    try:
                        log_data = json.loads(match.group(0))
                        log_objects.append(log_data)
                    except json.JSONDecodeError:
                        pass

        with open('error.json', 'w') as f:
            json.dump(log_objects, f, indent=4)

        with open('error.json') as f:
            log_data = json.load(f)

        error_messages = []

        for log_entry in log_data:
            if log_entry['level'] == 'ERROR':
                error_messages.append(log_entry['message'])
        
        sender = 'prajjushashu@gmail.com'
        recipient = 'emil.bluemax@gmail.com'

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = 'Erro Report'

        body = ''
        for i in error_messages:
            body=body+"\n"+i
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, 'lparhvkcykchtfzg')
            text = msg.as_string()
            server.sendmail(sender, recipient, text)
            print('Email sent successfully')

        # with open('test.log', 'w') as f:
        #     f.truncate(0)

        #print("Hello console !!",mail)
    except Exception as e:
        logging.error(f'Failed to send logs to Humio: {str(e)}')
    scheduler.enter(10, 1, send_logs)

scheduler.enter(0, 1, send_logs)
scheduler.run()



'''@app.route('/api/products/<int:id>/like', methods=['POST'])
def like(id):
    req = requests.get('http://172.17.0.1:8000/api/user')
    json = req.json()

    try:
        productUser = ProductUser(user_id=json['id'], product_id=id)
        db.session.add(productUser)
        db.session.commit()

        publish('product_liked', id)
    except:
        abort(400, 'You already liked this product')
    
    return jsonify({
        'message': 'success' 
    })'''

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')