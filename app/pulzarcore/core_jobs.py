from pulzarutils.utils import Utils
from pulzarutils.utils import Constants
from pulzarutils.file_utils import FileUtils
from pulzarutils.constants import ReqType
from pulzarutils.stream import Config
from pulzarcore.core_rdb import RDB
from pulzarcore.core_request import CoreRequest
from pulzarutils.node_utils import NodeUtils


class CoreJobs:
    """Base class for job implementation
    """

    def __init__(self, parameters, notification=False):
        """Constructor

            To test locally, set the attribute local_exec = True

            arguments:
             - parameters (dict)
             - notification (bool)

        """
        # Allows to execute the job locally
        self.local_exec = False
        self._pulzar_utils = Utils()
        self._pulzar_const = Constants()
        self._pulzar_database = RDB(
            self._pulzar_const.DB_NODE_JOBS) if local_exec is False else None
        self.pulzar_parameters = parameters
        self._notification_enabled = notification
        self._job_id = parameters['job_id']
        self._start_time = self._pulzar_utils.get_current_datetime()
        self._log = []
        self._failed_job = False
        self._pulzar_job_output = []
        self._pulzar_data_file_path = None
        self._pulzar_config = parameters['_pulzar_config']

        # log
        self._pulzar_register_parameters()
        self._pulzar_get_data()

    def pulzar_set_output(self, output_str):
        """Write output

        Parameters
            - output_str: String
        """
        self._pulzar_job_output.append(output_str)

    def _pulzar_store_file(self, file_name):
        """Store some results
            Using varidb system
        """
        file_utils = FileUtils(self._pulzar_const)
        server_config = Config(self._pulzar_const.CONF_PATH)
        node_utils = NodeUtils(self._pulzar_const)
        node = node_utils.discover_volume()
        # Master url
        server_host = server_config.get_config('server', 'host')
        server_port = server_config.get_config('server', 'port')
        base_dir = '/jobs'
        if self._pulzar_config['scheduled']:
            base_dir += '/sheduled/' + str(self._job_id)
        else:
            base_dir += '/regular/' + str(self._job_id)
        file_utils.set_path(base_dir)
        full_key = base_dir + '/' + \
            self._pulzar_utils.get_base_name_from_file(file_name)
        # File creation
        base64_str = self._pulzar_utils.encode_base_64(
            full_key, True)
        # Trying to create the key-value
        key_to_binary = self._pulzar_utils.encode_str_to_byte(base64_str)
        file_utils.set_key(key_to_binary, base64_str)
        file_utils.read_binary_local_file(file_name)
        request_object = CoreRequest(
            server_host, server_port, self._pulzar_const.ADD_RECORD)
        request_object.set_type(ReqType.POST)
        request_object.set_path(self._pulzar_const.ADD_RECORD)
        # We have to send the key, volume and port.
        request_object.set_payload({
            'key': file_utils.get_key(),
            'volume': node,
            'temporal': 90
        })
        if not request_object.make_request():
            # If an error ocurr in the server, we need to delete the file.
            file_utils.remove_file()
            return False
        self.pulzar_add_log('FILE: ' + file_utils.get_decoded_key())
        return True

    def _pulzar_get_data(self):
        """Check file/config and assign it
        """
        if 'pulzar_data' in self.pulzar_parameters:
            file_path = self.pulzar_parameters['pulzar_data']
            abs_path = '/var/lib/pulzar/data/' + self._pulzar_utils.encode_base_64(
                file_path, to_str=True)
            if self._pulzar_utils.file_exists(abs_path):
                self._pulzar_data_file_path = abs_path
        print(self._pulzar_data_file_path)

    def pulzar_get_filepath(self):
        """Return filepath
        """
        return self._pulzar_data_file_path

    def _pulzar_register_parameters(self):
        if self.pulzar_parameters:
            self.pulzar_add_log(
                self._pulzar_utils.py_to_json(self.pulzar_parameters)
            )

    def _pulzar_run_job(executor):
        """Decorator to handle job execution
        """

        def wrapper(self):
            print('Pulzar core executing')
            try:
                executor(self)
            except Exception as err:
                self._mark_as_failed()
                self.pulzar_add_log('PULZAR_ERROR::' + str(err))
            self._pulzar_notification()
            return self.is_the_job_ok()
        return wrapper

    def is_the_job_ok(self):
        """Should be at the end
        """
        return not self._failed_job

    def _mark_as_failed(self):
        self._failed_job = True

    def pulzar_add_log(self, message, bulk=False):
        """With bulk=True, a list of string is allowed
        """
        if bulk and isinstance(message, list):
            self._log += message
        self._log.append(message)

    def _pulzar_notification(self):
        """Notify to master
        """
        if self.local_exec:
            return
        job_table = 'job'
        if self._pulzar_config['scheduled']:
            job_table = 'schedule_job'
        end_time = self._pulzar_utils.get_current_datetime()
        delta = end_time - self._start_time
        # Saving logs
        final_log = '\n'.join(self._log)
        final_output = '\n'.join(self._pulzar_job_output)
        sql = 'UPDATE {} SET log = ?, duration = ?, output = ? WHERE job_id = {}'.format(
            job_table, self._job_id)
        self._pulzar_database.execute_sql_insert(
            sql, (final_log, delta.total_seconds(), final_output))

        # Notifications
        if self._notification_enabled:
            print('Sending notification...')
