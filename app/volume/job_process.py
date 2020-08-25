import importlib
from pulzarutils.utils import Utils
from pulzarutils.constants import ReqType
from pulzarutils.messenger import Messenger
from pulzarcore.core_request import CoreRequest
from pulzarcore.core_db import DB
from pulzarcore.core_job_node import Job
from pulzarcore.core_body import Body


class JobProcess:
    """Main class to handle jobs
    """

    def __init__(self, constants):
        self.const = constants
        self.utils = Utils()
        self.db_backup = DB(self.const.DB_BACKUP)
        self.messenger = Messenger()

    def process_request(self, url_path, env):
        """Receiving the order to launch a job
        """
        try:
            # Extracting data
            body = Body()
            params = body.extract_params(env)
            print('params for job', params)

            # Scheduling job
            job_id = params['job_id']
            job_file_name = params['job_name']
            job_file_path = params['job_path']
            job_parameters = params['parameters']
            job_scheduled = params['scheduled']

            # check if the job exists
            path_to_search = 'jobs' + job_file_path + '/' + job_file_name + '.py'
            print('path: ', path_to_search)
            good = False
            if self.utils.file_exists(path_to_search):
                print('Job exists, scheduling ', job_file_name)
                job_object = Job(job_id, path_to_search,
                                 job_parameters, job_scheduled)
                good = job_object.schedule_job(self.const)

            # Response
            if good:
                self.messenger.code_type = self.const.JOB_OK
                self.messenger.set_message = 'ok'
            else:
                self.messenger.code_type = self.const.JOB_ERROR
                self.messenger.set_message = 'internal error'
                self.messenger.mark_as_failed()

        except Exception as err:
            print('Error JobProcess', err)
            self.messenger.code_type = self.const.PULZAR_ERROR
            self.messenger.set_message = str(err)
            self.messenger.mark_as_failed()

        return self.messenger
