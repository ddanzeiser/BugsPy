# Standard
import requests
import logging
import sys

# BugsPy
from modules import config, exceptions

logger = logging.getLogger("Client")

class Client:
    def __init__(self):
        self.session = requests.Session()
        self.cfg = config.credentials
        self.session.headers.update({
            "User-Agent": self.cfg['user_agent'],
            "Host": "api.bugs.co.kr",
        })

    def auth(self):
        data = {
            "device_id": self.cfg['device_id'],
            "passwd": self.cfg['password'],
            "userid": self.cfg['username']
        }
        r = self.make_call("secure", "mbugs/3/login?", data=data)
        if r['ret_code'] == 300:
            raise exceptions.AuthenticationError("Invalid Credentials")
        else:
            logger.info("Login Successful")
        self.nickname = r['result']['extra_data']['nickname']
        self.connection_info = r['result']['coninfo']
        return self.connection_info

    def get_con_info(self):
        return self.connection_info

    def make_call(self, sub, epoint, data=None, json=None, params=None):
        r = self.session.post("https://{}.bugs.co.kr/{}api_key={}".format(sub, epoint, self.cfg['api_key']), json=json, data=data, params=params)
        return r.json()

    def get_meta(self, type, id):
        if type == "album":
            json=[{"id":"album_info","args":{"albumId":id}}, {"id":"artist_role_info","args":{"contentsId":id,"type":"ALBUM"}}]
        elif type == "artist":
            json=[{"id":"artist_info","args":{"artistId":id}}, {"id":"artist_album","args":{"artistId":id, "albumType":"main","tracksYn":"Y","page":1,"size":500}}]
        else:
            print("Invalid type provided")
            sys.exit()
        r = self.make_call("api", "3/home/invokeMap?", json=json)
        if r['ret_code'] != 0:
            raise Exception("Failed to get album metadata.")
        return r