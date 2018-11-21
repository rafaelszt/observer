import requests
import logging
import datetime
from threading import Thread
import uuid

import cv2
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import glob

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class AlertSystem():
    def __init__(self, log_system, **kwargs):
        self.email_user = kwargs.get("email_user")
        self.email_passwd = kwargs.get("email_passwd")
        self.email_from = kwargs.get("email_from")
        self.email_to = kwargs.get("email_to")

        self.log_system = log_system

        self.camera_id = ""
        self.timestamp = ""

        self.last_alert = None
        self.total_alerts = 0

    def __send_email(self):
        logger.info("Sending email to %s", self.email_to)

        text = "Unidentified face detected at {}, on camera ID {}".format(self.timestamp, self.camera_id)
        subject = '[Observer] Alert Triggered'

        msg = MIMEMultipart()
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Date'] = self.timestamp
        msg['Subject'] = subject
        msg.attach(MIMEText(text))

        # set attachments
        files = glob.glob("/tmp/observer_*")
        logger.info("Number of images attached to email: %s", len(files))
        for f in files:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                msg.attach(part)

        # The actual mail send
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        try:
            server.login(self.email_user, self.email_passwd)
        except smtplib.SMTPAuthenticationError:
            logger.error("Bad Username or Password when trying to authenticate to email server.")
        except:
            logger.error("Unknow error on login.")
        else:
            server.sendmail(self.email_from, self.email_to, msg.as_string())
        finally:
            server.quit()

    def alert(self, image):
        self.__send_email()
        file_name = self.save_image_to_disk(image)
        self.log_system.create_log(self.camera_id, file_name)

    def save_image_to_disk(self, image):
        file_name = 'image_alerts/' + str(uuid.uuid4()) + '.jpg'
        cv2.imwrite('observer/obmng/static/' + file_name, image)
        return file_name

    def send_alert(self, camera_id, image):
        self.camera_id = camera_id
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        limit = 3

        if not self.last_alert:
            self.last_alert = datetime.datetime.now()

        time_diff = (datetime.datetime.now() - self.last_alert).seconds

        if time_diff > limit:
            if self.total_alerts > limit:
                Thread(target=self.alert, args=(image, )).start()
                print("Sending alerts")

            print("Zeroing")
            self.total_alerts = 0
            self.last_alert = None

        else:
            print("Not enough time")
            self.total_alerts += 1


