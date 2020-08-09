import requests
from pulzarutils.constants import ReqType
from pulzarutils.utils import Utils


class CoreRequest:
    def __init__(self, host, port, url_path):
        self.utils = Utils()
        self.host = host
        self.port = port
        self.path = url_path
        self.request_type = ReqType.GET
        self.payload = None
        self.response = None

    def set_type(self, type_request=ReqType.GET):
        self.request_type = type_request

    def set_path(self, path_string):
        self.path = path_string

    def set_payload(self, payload):
        self.payload = payload

    def make_request(self, json_request=False):
        try:
            # Check
            req = None
            complete_url = 'http://' + self.host + ':' + self.port + self.path
            if self.request_type is None or self.path is None and self.utils.validate_url(complete_url):
                return False
            url_port = complete_url
            if self.request_type == ReqType.GET:
                req = requests.get(
                    url_port,
                    timeout=10
                )
            if self.request_type == ReqType.POST:
                if json_request:
                    req = requests.post(
                        url_port,
                        json=self.payload,
                        timeout=10
                    )
                else:
                    req = requests.post(
                        url_port,
                        data=self.payload,
                        timeout=10
                    )

            if req.status_code == 200:
                self.response = req.text
                return True
            return False
        except Exception as err:
            print(err)
            return False