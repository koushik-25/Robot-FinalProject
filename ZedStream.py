from flask import Flask, Response
import cv2
import pyzed.sl as sl

app = Flask(__name__)

def generate_frames():
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.camera_fps = 30
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Failed to open the camera")
        return

    runtime_params = sl.RuntimeParameters()
    zed.enable_streaming()

    while True:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            frame = sl.Mat()
            zed.retrieve_image(frame, sl.VIEW.LEFT)
            image = frame.get_data()
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            print("Failed to grab frame")
            break

    zed.disable_streaming()
    zed.close()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
