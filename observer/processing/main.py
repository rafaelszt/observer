"""
    Detect and identify a face in a stream of video
"""
import logging
import sys
import time
import os

import cv2
from flask import Flask

from .video_processing import VideoProcessing
from .faces_manager import FacesManager
from .options import Options
from .system_mng import SystemMng
from .alert_system import AlertSystem
from .log_stash import LogStash

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)

started = False

def system_init():
    if started:
        return SystemMng()
        
    op = Options()
    logs = LogStash()

    args = {
        "email_user": os.getenv('OBS_EMAIL_USER'),
        "email_passwd": os.getenv('OBS_EMAIL_PASSWD'),
        "email_from": os.getenv('OBS_EMAIL_FROM'),
        "email_to": os.getenv('OBS_EMAIL_TO')
    }
    alerts = AlertSystem(logs, **args)
    faces_manager = FacesManager()

    vd_proc = VideoProcessing(alerts, op, faces_manager)
    vd_proc.run()

    kwargs = {
        "face_mgn": faces_manager,
        "options": op,
        "video_proc": vd_proc,
        "alert_sys": alerts,
        "log_sys": logs
    }

    sys_mgn = SystemMng(**kwargs)

    return sys_mgn
