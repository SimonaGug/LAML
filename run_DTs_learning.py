import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

import os
import sys
import config
from contextlib import contextmanager

#import logging
#logging.getLogger('rpy2').setLevel(logging.WARNING)

class Utility:
    @staticmethod
    @contextmanager
    def suppress_stdout_stderr():
        """A context manager that redirects stdout and stderr to devnull."""
        with open(os.devnull, 'w') as fnull:
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = fnull, fnull
            try:
                yield
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

class C50:
    rules_path : str
    folder_path : str

    def __init__(self, rules_path):
        self.rules_path = rules_path

    def run_c50(self, rules_path):
        pandas2ri.activate()
        with open(f'DTs-learning.R', 'r') as file:
            r_script = file.read()

        with Utility.suppress_stdout_stderr():
            robjects.r(r_script)
        #robjects.r(r_script)
            process_data = robjects.globalenv['process_data']
            return process_data(rules_path)



if __name__ == '__main__':
    problem_num = config.PROBLEM
    domain_num = config.DOMAIN
    domain_name = config.DOMAIN_DIC[domain_num].lower()

    rules_path =  config.DATA_FRAMES_PATH + f'\\{domain_name}'

    rules_path =  config.DATA_FRAMES_PATH + f'\\{domain_name}'
    
    C50_object = C50(rules_path)
    result = C50_object.run_c50(rules_path)