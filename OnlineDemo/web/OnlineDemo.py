from flask import Flask, request, render_template, make_response, send_from_directory

app = Flask(__name__)

headers = {'Content-Type': 'text/html'}

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

@app.route('/img/<path:filepath>')
def img_data(filepath):
    return send_from_directory('static/img', filepath)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4999, debug=False)
