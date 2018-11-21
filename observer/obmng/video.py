from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Response
)
from flask_security import login_required

from observer.processing.system_mng import SystemMng

bp = Blueprint('videos', __name__)

def gen(system_mng, camera_id):
    while True:
        frame = system_mng.get_camera_frame(camera_id)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
@bp.route('/video_feed_1')
def video_feed_1():
    system_mng = SystemMng()
    return Response(gen(system_mng, '0'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/video_feed_2')
def video_feed_2():
    system_mng = SystemMng()
    return Response(gen(system_mng, '1'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/video_feed_3')
def video_feed_3():
    system_mng = SystemMng()
    return Response(gen(system_mng, '2'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/video_feed_4')
def video_feed_4():
    system_mng = SystemMng()
    return Response(gen(system_mng, '3'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

