class Constants:
    def __init__(self):
        # General
        self.DEBUG = True
        self.VERSION = '0.1'
        self.PASS = 'admin'
        self.PASSPORT = 'passport'

        # Database
        self.DB_PATH = 'storage/master.db'

        # Env
        self.REQUEST_METHOD = 'REQUEST_METHOD'
        self.SERVER_NAME = 'SERVER_NAME'
        self.SERVER_PORT = 'SERVER_PORT'
        self.PATH_INFO = 'PATH_INFO'
        self.QUERY_STRING = 'QUERY_STRING'
        self.HTTP_USER_AGENT = 'HTTP_USER_AGENT'
        self.SERVER_PROTOCOL = 'SERVER_PROTOCOL'

        # REST admin paths
        self.SKYNET = '/skynet'
        self.REGISTER = self.SKYNET + '/register'

        # Type of requests
        self.REGULAR = 'regular'
        self.ADMIN = 'admin'
        self.SKYNET = 'skynet'

        