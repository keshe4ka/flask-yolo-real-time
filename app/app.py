from flask import Flask, render_template, Response, jsonify

from app.auth import auth
from app.camera import Camera

app = Flask(__name__)
camera = Camera()


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
    person_count, laptop_count = camera.get_count()

    return jsonify({
        'person_count': person_count,
        'laptop_count': laptop_count
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
