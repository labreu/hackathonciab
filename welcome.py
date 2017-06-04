# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify, url_for, render_template, request
import json
import datetime
import random
import base64
from watson_developer_cloud import VisualRecognitionV3
from watson_developer_cloud import TextToSpeechV1

app = Flask(__name__)
visual_recognition = VisualRecognitionV3('2016-05-20', api_key='24e15fd4b578b3355c6abcb1d9ab37203a54c5ec')


def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'=' * (4 - missing_padding)
    return base64.b64decode(data)


@app.route('/imgs')
def imgs():
    names = os.listdir('static/imgs/')
    r = []
    for i, x in enumerate(names):
        uri = url_for('static', filename='imgs/' + str(x))
        v = '<a href="{}">{} - {}</a>'.format(uri, str(i), x)
        r.append(v)
    return '<br>'.join(r)


@app.route('/')
def index():
    return render_template('index.html', endpoint=endpoint)


@app.route('/lastfile')
def last_file():
    return app.send_static_file("jsonfile.json")


@app.route('/lastphoto')
def last_photo():
    return app.send_static_file('imgs/img.jpg')


@app.route('/analysephoto')
def analyse():
    try:
        with open('static/imgs/img.jpg', 'rb') as image_file:
            results = visual_recognition.classify(images_file=image_file)
            return json.dumps(results, indent=2)
    except Exception as e:
        return repr(e)


@app.route('/analysephoto2')
def analyse2():
    try:
        test_url = 'https://backendpy.mybluemix.net/lastphoto'
        url_result = visual_recognition.classify(images_url=test_url)
        return json.dumps(url_result, indent=2)
    except Exception as e:
        return repr(e)


@app.route('/detectfaces')
def detect():
    try:
        with open('static/imgs/img.jpg', 'rb') as image_file:
            results = visual_recognition.detect_faces(images_file=image_file)
            return json.dumps(results, indent=2)
    except Exception as e:
        return repr(e)


@app.route('/detecttext')
def detectt():
    try:
        with open('static/imgs/img.jpg', 'rb') as image_file:
            results = visual_recognition.recognize_text(images_file=image_file)
            return json.dumps(results, indent=2)
    except Exception as e:
        return repr(e)


@app.route('/putphoto', methods=['POST'])
def putphoto():
    jsonfile = request.form.to_dict(flat=True)
    jsonimg = request.form.get("img", "nd")
    d = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
    i1 = base64.b64decode(jsonimg.split(',')[1])
    with open("static/imgs/imagem-{}.jpg".format(d), "wb") as f:
        f.write(i1)

    # Simulacao de previsao
    t_espera = str(10 + random.randint(-5, 5))
    jsonfile['img'] = ''
    jsonfile['datetime'] = d
    jsonfile['agencia'] = 'XXX'
    jsonfile['t_espera'] = t_espera

    with open("static/imgs/metadados-{}.txt".format(d), "a") as f:
        f.write(json.dumps(jsonfile))

    return t_espera


def process_image(n):
    try:
        response = ''

        imgs = os.listdir('static/imgs/')
        img = 'static/imgs/' + imgs[n]

        with open(img, 'rb') as image_file:
            try:
                results = visual_recognition.classify(images_file=image_file)
                response += json.dumps(results, indent=2)
                response += ', '
            except Exception as e:
                print(e)
        with open(img, 'rb') as image_file:
            try:
                results = visual_recognition.detect_faces(images_file=image_file)
                response += json.dumps(results, indent=2)
                response += ', '
            except Exception as e:
                print(e)
        with open(img, 'rb') as image_file:
            try:
                results = visual_recognition.recognize_text(images_file=image_file)
                t = results.get("images", [{"text": 'Texto nao encontrado'}])[0].get("text", "Texto nao encontrado")
                if len(t) != 0:
                    content = text_to_speech.synthesize(t, accept='audio/wav', voice='pt-BR_IsabelaVoice')
                    with open('static/output.wav', 'wb') as audio_file:
                        audio_file.write(content)
                response += '\n'
                response += json.dumps(results, indent=2)

            except Exception as e:
                print(e)

        return response
    except Exception as e:
        return repr(e)


@app.route('/api/analyse/<int:n>')
def analysis(n):
    return process_image(n)


@app.route("/lastaudio")
def audio_():
    return app.send_static_file('output.wav')

text_to_speech = TextToSpeechV1(
    username='4b735ba1-4b78-40a5-bac6-15300cd91826',
    password='6sRcVhm1QAaT',
    x_watson_learning_opt_out=True)


debug_ = False
endpoint = ''
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    if debug_:
        endpoint = 'http://127.0.0.1:5000'
        app.run(debug=True)  # host='0.0.0.0', port=int(port)

    else:
        endpoint = 'https://backendpy.mybluemix.net'
        app.run(host='0.0.0.0', port=int(port))  # host='0.0.0.0', port=int(port)

