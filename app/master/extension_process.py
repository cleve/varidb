import importlib
import random
from pulzarutils.utils import Utils
from pulzarcore.core_body import Body
from pulzarcore.core_db import DB
from pulzarutils.messenger import Messenger


class ExtensionProcess:
    """Process extension calls
    """

    def __init__(self, constants, logger):
        self.TAG = self.__class__.__name__
        self.const = constants
        self.logger = logger
        self.utils = Utils()
        # DB of values already loaded
        self.db_values = DB(self.const.DB_PATH)
        self.messenger = Messenger()

    def read_in_chunks(self, file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k.
        """
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def read_binary_file(self, env, url_path):
        """Read binary file into env and rename it as 
        
        Parameters
        ----------
        url_path : str
            Path section of the url

        Returns
        -------
        str:
            File name or None
        """
        try:
            request_body_size = int(env[self.const.CONTENT_LENGTH])
        except (ValueError):
            request_body_size = 0
        if request_body_size > 0:
            temp_file = self.utils.get_tmp_file()
            # Read binary file sent.
            f = env[self.const.WSGI_INPUT]
            for piece in self.read_in_chunks(f):
                temp_file.write(piece)

            # Creating directories if does not exist.
            temp_file.close()  # Close the file to be copied.
            return temp_file.name
        return None

    def process_request(self, url_path, query_string, env=None):
        # Extract and save body if its present
        file_path = None
        if env is not None:
            file_path = self.read_binary_file(env, url_path)
        # Extract query parameters if is the case
        query_params = self.utils.extract_query_params(
            'http://fakeurl.com?' + query_string)
        # Get request type, checking for key value.
        regex_result = self.utils.get_search_regex(
            url_path, self.const.RE_EXTENSION)
        if regex_result:
            try:
                call_path_list = regex_result.groups()[0][1:].split('/')
                file_name = call_path_list[0]
                args = call_path_list[1:]
                modules = self.utils.read_file_name_from_dir(
                    'extensions/', 'py')
                if file_name + '.py' in modules:
                    # Import module and method execute.
                    import_fly = importlib.import_module(
                        'extensions.' + file_name)
                    extension_class = getattr(
                        import_fly, file_name.capitalize())
                    extension_object = extension_class(
                        args, query_params, file_path)
                    j_byte = extension_object.execute()
                    # Clear tmp is exists
                    extension_object.clean_tmp()
                    self.messenger.code_type = self.const.EXTENSION_RESPONSE
                    self.messenger.set_response(j_byte)
                else:
                    self.messenger.code_type = self.const.USER_ERROR
                    self.messenger.mark_as_failed()
                    self.messenger.set_message = 'Wrong query, extension not found'

            except Exception as err:
                self.logger.exception('{}:{}'.format(self.TAG, err))
                self.messenger.code_type = self.const.PULZAR_ERROR
                self.messenger.mark_as_failed()
                self.messenger.set_message = str(err)

        else:
            self.messenger.code_type = self.const.USER_ERROR
            self.messenger.mark_as_failed()
            self.messenger.set_message = 'Wrong query'

        return self.messenger
