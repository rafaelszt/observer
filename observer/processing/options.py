import json
import logging
import sqlite3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Options():
    def __init__(self):
        self.con = sqlite3.connect(
            "./instance/observer.sqlite",
            check_same_thread=False)
        self.con.row_factory = dict_factory
        cur = self.con.cursor()

        self.options = cur.execute(
                'SELECT *'
                ' FROM option'
            ).fetchone()

    def get_options(self):
        return self.options

    def get_option(self, op):
        return self.options.get(op)

    def get_cameras(self):
        cur = self.con.cursor()

        self.options = cur.execute(
                'SELECT *'
                ' FROM option'
            ).fetchone()

        cameras = {}
        cameras['0'] = self.options.get("video_url_0")
        cameras['1'] = self.options.get("video_url_1")
        cameras['2'] = self.options.get("video_url_2")
        cameras['3'] = self.options.get("video_url_3")

        return cameras


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d