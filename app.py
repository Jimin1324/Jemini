import os
from flask import Flask, render_template, jsonify, request
import google.generativeai as genai
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# Edit the url blow to connect to your MongoDB Database
url = "mongodb+srv://YOUR_MONGODB_ID:YOUR_MONGODB_PASSWORD@YOUR_MONGODB_DATABASE.YOUR_MONGODB_CLUSTER.mongodb.net/"



client = MongoClient(url, server_api=ServerApi('1'))
db = client.dbusers

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")     
except Exception as e:
    print(e)

genai.configure(api_key="YOUR_GEMINI_KEY")  # Add here your Gemini Api Key
model = genai.GenerativeModel(model_name="gemini-1.5-flash") 
myarray = []

def delandput(dbuser):
    myarray.clear() 
    for row in dbuser:
        if 'name' in row:
            myarray.insert(0, row['name'])
        elif 'text' in row: 
            myarray.insert(0, row['text'])


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/history', methods=['GET'])
def getHistory():
    dbuser = db.users.find()
    delandput(dbuser)
    return jsonify({'result': 'success', 'history': myarray})

@app.route('/api/asking', methods=['POST'])
def getQuestion():
    askingReceive = request.form['asking']
    
    response = model.generate_content(askingReceive)
    doc = {'text': response.text}  
    db.users.insert_one(doc)
    
    return jsonify({'result': 'success', 'msg': askingReceive})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)