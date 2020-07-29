from urllib.parse import parse_qs
from html import escape
from utils.constants import Constants
from utils.utils import Utils


class Body:
    def __init__(self):
        self.const = Constants()
        self.utils = Utils()

    def extract_params(self, env):
        """Extracting body paremeters
        """
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(env[self.const.CONTENT_LENGTH])
        except (ValueError):
            request_body_size = 0
        if request_body_size == 0:
            return None
        request_body = env[self.const.WSGI_INPUT].read(request_body_size)
        # JSON type
        if env[self.const.CONTENT_TYPE] == self.const.JSON_REQUEST:
            return self.utils.json_to_py(request_body)
        return parse_qs(request_body)

    def extract_binary(self, env):
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(env[self.const.CONTENT_LENGTH])
        except (ValueError):
            request_body_size = 0
        if request_body_size == 0:
            return None
        request_body = env[self.const.WSGI_INPUT].read(request_body_size)
        return request_body
