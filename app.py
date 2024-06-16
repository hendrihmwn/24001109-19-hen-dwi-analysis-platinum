import pandas as pd
import clean_helper as c
import prediction_helper as pr
import sqlite3
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

# import tensorflow as t

DB_FILE = 'db/sentiment_analysis.db'

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

@swag_from("docs/sentiment_text_nnmlp.yml", methods=['POST'])
@app.route('/sentiment-text-nnmlp', methods=['POST'])
def sentiment_text_nnmlp():
    # required validation
    if 'text' not in request.form:
        return res('text is required', 400)
    
    text = request.form['text']

    # predict
    hasil = pr.prediction_by_mlp(text)
    # save db
    data = [(text, hasil, "mlp_classifier")]
    insert_into_texts(data)
    
    return res({
        "input_text": text,
        "sentiment": hasil,
        "model_type": "mlp_classifier"
    })

@swag_from("docs/sentiment_file_nnmlp.yml", methods=['POST'])
@app.route('/sentiment-file-nnmlp', methods=['POST'])
def sentiment_file_nnmlp():
    # required validation
    if 'file' not in request.files:
        return res('file is required', 400)
    
    file = request.files.getlist('file')[0]
    df = pd.read_csv(file)
    texts = df.text.to_list()

    res_arr = []
    data_insert = []
    for text in texts:
        # predict
        hasil = pr.prediction_by_mlp(text)
        # append array insert
        data_insert.append((text, hasil, "mlp_classifier"))

        res_arr.append({
        "input_text": text,
        "sentiment": hasil,
        "model_type": "mlp_classifier"
    })
    
    # save db
    insert_into_texts(data_insert)
    return res(res_arr)

@swag_from("docs/sentiment_text_lstm.yml", methods=['POST'])
@app.route('/sentiment-text-lstm', methods=['POST'])
def sentiment_text_lstm():
    # required validation
    if 'text' not in request.form:
        return res('text is required', 400)
    
    text = request.form['text']

    # predict
    hasil = pr.prediction_by_lstm(text)
    # save db
    data = [(text, hasil, "lstm")]
    insert_into_texts(data)
    
    return res({
        "input_text": text,
        "sentiment": hasil,
        "model_type": "lstm"
    })

@swag_from("docs/sentiment_file_lstm.yml", methods=['POST'])
@app.route('/sentiment-file-lstm', methods=['POST'])
def sentiment_file_lstm():
    # required validation
    if 'file' not in request.files:
        return res('file is required', 400)
    
    file = request.files.getlist('file')[0]
    df = pd.read_csv(file)
    texts = df.text.to_list()

    res_arr = []
    data_insert = []
    for text in texts:
        # predict
        hasil = pr.prediction_by_lstm(text)
        # append array insert
        data_insert.append((text, hasil, "lstm"))

        res_arr.append({
        "input_text": text,
        "sentiment": hasil,
        "model_type": "lstm"
    })
    
    # save db
    insert_into_texts(data_insert)
    return res(res_arr)


def res(data, code = 200):
    return jsonify({
        "status_code": code,
        "data": data
    }), code

def insert_into_texts(data):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.cursor().executemany("INSERT INTO texts (input_text, sentiment, model_type) VALUES (?, ?, ?)", data)
        conn.commit()
        print ("success insert to texts")
    except sqlite3.Error as e:
        conn.rollback()
        print ("failed insert to texts", str(e))
    conn.cursor().close()
    conn.close()

if __name__ == '__main__':
    app.run()