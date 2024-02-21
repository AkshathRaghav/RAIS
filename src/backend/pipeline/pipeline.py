import backend.evaluator.paper.paper as Paper
import backend.evaluator.repository as Repo
from backend.tools.logger import LoggerSetup

import os

class Pipeline:
    def __init__(self, config):
        logging_setup = LoggerSetup('Pipeline')
        self.logger = logging_setup.get_logger()
        self.logger.info('<------------------------------------>')
        self.logger.info('Initializing Pipeline...')        

        self.paper = self.make_paper(config['paper'])
        self.codebase = self.make_codebase(config['repository'])

        self.logger.info('Pipeline initialized with configuration.')

    
    def make_paper(self, paper_url):
        return Paper(paper_url)
        
    def make_codebase(self, repository_details):
        if repository_details['type'] == 'github':
            return Github(**repository_details['details'])
        elif repository_details['type'] == 'huggingface':
            return HuggingFace(**repository_details['details'])
        else:
            raise ValueError("Unsupported repository source!")
  
    def run(self):
        self.paper()
        self.logger.info('Paper extraction completed.')
        self.codebase() 
        self.logger.info('Codebase tree created.')
        self.logger.info('Pipeline run completed.')
        self.logger.info('<------------------------------------>')
