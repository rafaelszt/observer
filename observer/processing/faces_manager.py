import logging
import os
import shutil
import cv2
from random import choice
import sqlite3

import numpy as np

from .classifier import train_classifier
from .face import Recognition

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class FacesManager():
    def __init__(self):
        db_path = "./instance/observer.sqlite" 
        self.db = sqlite3.connect(
            db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        faces = self.db.execute(
                'SELECT id, embedding'
                ' FROM face'
            ).fetchall()
        
        self.faces = {}
        for _id, embedding in faces:
            self.faces[_id] = np.frombuffer(embedding, dtype=np.float32)
    
    def generate_embedding(self, image_path):
        recognition = Recognition()
        image = cv2.imread(image_path)
        face_embedding = recognition.add_identity(image)

        if face_embedding is not None:
            return face_embedding.tobytes()

    def add_face(self, face_id, embedding):
        self.faces[face_id] = np.frombuffer(embedding, dtype=np.float32)
            
    def remove_face(self, face_id):
        self.faces.pop(face_id, None)

    def get_faces(self):
        return self.faces

    def get_name(self, _id):
        faces = self.db.execute(
                'SELECT id, name'
                ' FROM face'
                ' WHERE id = (?)', (_id,)
            ).fetchone()

        if faces:
            return faces[1]
        
        return None