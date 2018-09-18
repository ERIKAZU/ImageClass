# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template, make_response, send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

import subprocess
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Maomao have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

headers = {'Content-Type': 'text/html'}


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Please Upload Image only'), FileRequired(u'The file was empty!')])
    submit = SubmitField(u'Upload')


@app.route('/')
def hello_world():
    return make_response(render_template('index.html'), 200, headers)
    # return 'You can find: \n Project [Exploration on Death and Time] at /Lifetime \n ' \
    #        'Project [Mental Health] at /MentalHealth'


@app.route('/Time')
def death_and_time():

    return make_response(render_template('death_and_time.html'), 200, headers)


@app.route('/MentalHealth')
def mental_health():
    return make_response(render_template('mental_health.html'), 200, headers)


@app.route('/HarryPotter')
def harry_potter():
    return make_response(render_template('harry_potter.html'), 200, headers)


@app.route('/ImgClass', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data, name='temp.jpg')
        file_url = photos.url(filename)

        proc = subprocess.Popen(
            "python tensor_image_classifier.py --model_dir=./tensor_model --image_file=./"+filename,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        ret = proc.communicate()[0]
        proc.wait()
        with open("predictions.txt") as predict_file:
            predictions = json.load(predict_file)
            predict_item = predictions["0"]["item"]
            predict_score = int(float(predictions["0"]["score"]) * 100)
            results = "Min thinks this is [" + predict_item + "] with about " + str(predict_score) + "% confidence. "

        # if os.path.exists("./temp.jpg"):
        #     os.remove("./temp.jpg")
    else:
        file_url = None
        results = None
    return render_template('upload.html', form=form, file_url=file_url, results=results)


@app.route('/img/<path:filepath>')
def img_data(filepath):
    return send_from_directory('static/img', filepath)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4999, debug=False)
