from datetime import datetime
import logging
import os

import sqlite3
from flask import g

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class LogStash():
    def __init__(self):
        db_path = "./instance/observer.sqlite" 
        self.db = sqlite3.connect(
            db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES
        )

    def create_log(self, camera_id, file_name):
        c = self.db.cursor()
        c.execute('INSERT INTO log (date, camera, image_path) VALUES(?, ?, ?)', (datetime.now(), camera_id, file_name))
        self.db.commit()
