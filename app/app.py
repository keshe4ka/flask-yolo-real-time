from flask import Flask, render_template, Response

from app.camera import Camera
from app.auth import auth

app = Flask(__name__)


# use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera


@app.route('/video_feed')
def video_feed():
    camera = Camera()
    return Response(camera.gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
