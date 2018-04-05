import picamera
import time
import smbus
import datetime
from random import randint
import queue
import threading
import uptime

def milli_time():
    return int(round(time.time() * 1000))

class VideoEncoder(picamera.PiCookedVideoEncoder):
    def start(self, output, motion_output=None):
        self.parent.frame_number = 0
        self.start_time = int(time.time())
        super(VideoEncoder, self).start(output, motion_output)

    def _callback_write(self, buf, key=0):

        if (buf.flags & picamera.mmal.MMAL_BUFFER_HEADER_FLAG_CONFIG):
            return super(VideoEncoder, self)._callback_write(buf)

        if (buf.flags & picamera.mmal.MMAL_BUFFER_HEADER_FLAG_FRAME_END):
            self.parent.frame_number += 1
            self.parent.queue.put({
                "frame": self.parent.frame_number,
                "pts_time": buf.pts,
            })

        return super(VideoEncoder, self)._callback_write(buf)

class MyCamera(picamera.PiCamera):
    def __init__(self, queue):
        super(MyCamera, self).__init__(clock_mode='raw')
        self.frame_number = 0
        self.queue = queue

    def _get_video_encoder(
            self, camera_port, output_port, format, resize, **options):
        return VideoEncoder(
                self, camera_port, output_port, format, resize, **options)

g_cam = None

def start_recording_data(
    queue,
    output,
    recording_time=60,
    resolution=(640, 480),
    framerate=30,
    start_preview=False,
    i2c_worker=None,
    video_worker=None
):
    global g_cam
    with MyCamera(queue) as camera:
        camera.resolution = resolution
        camera.framerate = framerate
        if start_preview:
            camera.start_preview()
        time.sleep(2)

        print("GO")
        g_cam = camera
        i2c_worker.start()
        video_worker.start()

        camera.start_recording(output)
        camera.wait_recording(recording_time)
        camera.stop_recording()

def i2c_read_worker(value_file):
    global g_cam
    with open(value_file, 'w') as wfile:
        wfile.write("ts,controls\n")
        while True:
            car_controls = request_data()
            wfile.write("{},{}\n".format(g_cam.timestamp, car_controls))
            wfile.flush()
            time.sleep(0.1)

def video_worker(queue, value_file):
    with open(value_file, 'w') as wfile:
        wfile.write("ts,frame\n")
        while True:
            frame_data = queue.get()

            frame_number = int(frame_data["frame"])
            pts_time = int(frame_data["pts_time"])

            print(frame_data)
            wfile.write("{},{}\n".format(
                pts_time,
                frame_number,
            ))
            wfile.flush()

            queue.task_done()


bus = smbus.SMBus(1)
address = 0x04
def request_data():
    return int(bus.read_byte(address))

q = queue.Queue()

i2c_file="captures_ms/readings.csv"
frame_file="captures_ms/frames.csv"
h264_file="captures_ms/car.h264"

i2c_worker = threading.Thread(target=i2c_read_worker, args=(i2c_file,))
i2c_worker.setDaemon(True)

video_worker = threading.Thread(target=video_worker, args=(q, frame_file))
video_worker.setDaemon(True)

start_recording_data(
    queue=q,
    output=h264_file,
    recording_time=320,
    framerate=15,
    start_preview=True,
    i2c_worker=i2c_worker,
    video_worker=video_worker
)

i2c_worker.join()
video_worker.join()
