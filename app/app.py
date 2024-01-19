from random import random, randint

from flask import Flask, render_template, Response, jsonify

from app.auth import auth
from app.camera import Camera

app = Flask(__name__)
camera = Camera()


# use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera


@app.route('/video_feed')
def video_feed():
    return Response(camera.gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')


@app.route('/objects-count')
def objects_count():
    # Здесь вам нужно реализовать логику получения данных из вашего API
    # Замените следующие две строки на вашу реализацию
    person_count, laptop_count = camera.get_count()

    # Возвращаем данные в формате JSON
    return jsonify({
        'person_count': person_count,
        'laptop_count': laptop_count
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
