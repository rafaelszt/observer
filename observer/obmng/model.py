import os
import os.path as op
import datetime

from flask_admin import form
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy.event import listens_for
from sqlalchemy import create_engine
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                       String, ForeignKey, Unicode, LargeBinary

from observer.obmng.database import Base

class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))
    

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('user', lazy='dynamic'))


class Face(Base):
    __tablename__ = 'face'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(64))
    path = Column(Unicode(128))
    embedding = Column(LargeBinary)

    def __unicode__(self):
        return self.name

@listens_for(Face, 'after_delete')
def del_face(mapper, connection, target):
    file_path = op.join(op.dirname(__file__), './static/faces')

    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass
        try:
            os.remove(op.join(file_path,
                              form.thumbgen_filename(target.path)))
        except OSError:
            pass


class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    camera = Column(Integer)
    image_path = Column(Unicode(128))

    def __unicode__(self):
        return self.name


class Option(Base):
    __tablename__ = 'option'
    id = Column(Integer, primary_key=True)
    alert_email = Column(String(512))
    callback_url = Column(String(512))
    video_url_0 = Column(String(2048))
    video_url_1 = Column(String(2048))
    video_url_2 = Column(String(2048))
    video_url_3 = Column(String(2048))