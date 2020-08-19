import tempfile
import random
from pulzarcore.core_jobs import CoreJobs


class Example(CoreJobs):
    """Example of job programation

    Here we were generating a file and using the internal
    system to store it
    """

    def __init__(self, params):
        super().__init__(params)

    def process_data(self):
        if self.pulzar_get_filepath() is not None:
            print('Opening ', self.pulzar_get_filepath())
            line_number = 1
            with open(self.pulzar_get_filepath(), 'rb') as f:
                for line in f:
                    print('(' + str(line_number) + ')', line.decode())
                    line_number += 1

    @CoreJobs._pulzar_run_job
    def run_my_code(self):
        print('Parameters', self.parameters)
        total_lines = self.parameters['arg1']

        # Generating temporary file
        temporary_file = tempfile.NamedTemporaryFile(delete=False)
        print('opening file')
        with open(temporary_file.name, 'w') as f:
            line = 0
            while line < total_lines:
                f.write(str(random.randint(0, 1000)))
                line += 1
        print('saving file', temporary_file.name)
        self._pulzar_store_file(temporary_file.name)


def execute(arguments):
    """Point of entrance
    """
    example = Example(arguments)
    example.run_my_code()
    return example.is_the_job_ok()