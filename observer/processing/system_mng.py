from .video_processing import VideoProcessing
from .faces_manager import FacesManager
from .options import Options
from .alert_system import AlertSystem
from .log_stash import LogStash

class Borg():
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state

class SystemMng(Borg):
    _first_initialization = True
    def __init__(self, **kwargs):
        Borg.__init__(self)
        if SystemMng._first_initialization:
            print("Initializing SystemMng")
            SystemMng._first_initialization = False
            self.face_mgn = kwargs["face_mgn"]
            self.options = kwargs["options"]
            self.video_proc = kwargs["video_proc"]
            self.alert_sys = kwargs["alert_sys"]
            self.log_sys = kwargs["log_sys"]

    def add_face(self, face_id, face_embedding):
        self.face_mgn.add_face(face_id, face_embedding)

    def delete_face(self, name):
        self.face_mgn.remove_face(name)

    def generate_embedding(self, image_path):
        return self.face_mgn.generate_embedding(image_path)

    def video_cameras_stop(self):
        self.video_proc.toggle_stop()

    def get_camera_frame(self, camera_id):
        return self.video_proc.get_camera_cur_frame(camera_id)

    def get_options(self):
        return self.options.get_options()
    
    def get_option(self, op):
        return self.options.get_option(op)

    def restart_cameras(self):
        self.video_proc.restart_cameras()