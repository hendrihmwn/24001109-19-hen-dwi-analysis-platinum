import pandas as pd
import clean_helper as c
import sqlite3
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

DB_FILE = 'db/text_clean.db'

app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': 'API Documentation for Sentiment Analysis',
    'version': '1.0.0',
    'description': 'Dokumentasi API untuk Sentiment Analysis',
    }
    # host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

@app.route('/', methods=['GET'])
def hello_world():
    return 'API for Sentiment Analysis'

@swag_from("docs/sentiment_text.yml", methods=['POST'])
@app.route('/sentiment-text', methods=['POST'])
def sentiment_text():
    # required validation
    if 'text' not in request.form:
        return res('text is required', 400)
    
    text = request.form['text']
    
    return res({
        "text": text,
        "sentiment": "negatif"
        })

@swag_from("docs/sentiment_file.yml", methods=['POST'])
@app.route('/sentiment-file', methods=['POST'])
def sentiment_file():
    # required validation
    if 'file' not in request.files:
        return res('file is required', 400)
    
    file = request.files.getlist('file')[0]
    df = pd.read_csv(file)
    texts = df.text.to_list()
    # read kamus for replacing word
    kamus = c.kamus_alay()

    res_arr = []
    for text in texts:
        res.append({
        "text": text,
        "sentiment": "negatif"
    })
        
    return res(res_arr)

def res(data, code = 200):
    return jsonify({
        "status_code": code,
        "data": data
    }), code

def insert_into_texts(data):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.cursor().executemany("INSERT INTO texts (text_clean, text_raw) VALUES (?, ?)", data)
        conn.commit()
        print ("success insert to texts")
    except sqlite3.Error as e:
        conn.rollback()
        print ("failed insert to texts", str(e))
    conn.cursor().close()
    conn.close()

if __name__ == '__main__':
    app.run()