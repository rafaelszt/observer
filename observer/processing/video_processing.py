import cv2
from threading import Thread
import logging
import numpy as np
from time import sleep

from .options import Options
from .faces_manager import FacesManager
from .face import Recognition

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class VideoProcessing():      
    def __init__(self, alert_system, options, faces_manager):
        self.alert_system = alert_system
        self.faces_manager = faces_manager
        self.options = options
        self.stream_ips = self.options.get_cameras()
        print(self.stream_ips)
        self.cameras_threads = []
        self.camera_cur_frame = {}
        self.stop = False

    def run(self):
        for id, stream in self.stream_ips.items():
            logger.info("Started new processing on camera id %s", id)
            p = Thread(target=self.check_video, args=(stream, id,))
            p.start()
            self.cameras_threads.append(p)

    def add_overlays(self, frame, faces):
        if faces is not None:
            for face in faces:
                face_bb = face.bounding_box.astype(int)
                cv2.rectangle(frame,
                            (face_bb[0], face_bb[1]), (face_bb[2], face_bb[3]),
                            (0, 255, 0), 2)

                if not face.name:
                    face.name = "Unknown"

                cv2.putText(frame, face.name, (face_bb[0], face_bb[3]),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                            thickness=2, lineType=2)

    def check_video(self, feed, stream_id):
        stream = cv2.VideoCapture(feed)
        face_recognition = Recognition()
        self.camera_cur_frame[stream_id] = np.zeros((400, 400, 3), np.uint8)
        frame_number = 1
        frame_counter = 0
        error_count = 0
        error_limit = 10

        while not self.stop:
            ret, frame = stream.read()

            if not ret:
                if error_count > error_limit:
                    logger.error("Error count of %s exceeded. Closing stream.", error_limit)
                    break

                error_count += 1
                logger.error("Could not read stream. Trying again.")
                stream = cv2.VideoCapture(feed)
                continue

            if frame_counter % frame_number == 0:
                faces_saved = self.faces_manager.get_faces()
                faces = face_recognition.identify(frame, faces_saved)

                # Verify if we got an Unknown person and send an alert
                for face_found in faces:
                    if not face_found.name:
                        self.alert_system.send_alert(stream_id, frame)
                    
                    else:
                        face_found.name = self.faces_manager.get_name(face_found.name)
                        
                self.add_overlays(frame, faces)
                self.camera_cur_frame[stream_id] = frame
            frame_counter += 1

        logger.info("Stopping camera #{}".format(stream_id))

    def get_camera_cur_frame(self, id):
        img = self.camera_cur_frame.get(id, np.zeros((360, 640, 3), np.uint8))
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def toggle_stop(self):
        self.stop = not self.stop

    def restart_cameras(self):
        self.toggle_stop()
        sleep(60)
        self.stream_ips = self.options.get_cameras()
        self.toggle_stop()
        self.run()

