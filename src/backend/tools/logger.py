import logging
import os

class LoggerSetup:
    def __init__(self, name, log_directory=os.environ['LOGS'], log_file='app.log', level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.log_directory = log_directory
        self.log_file = log_file
        self.level = level
        self.setup_logger()

    def setup_logger(self):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
        log_file_path = os.path.join(self.log_directory, self.log_file)

        logging.basicConfig(
            filename=log_file_path,
            level=self.level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # Adding console handler to see logs in console as well
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.propagate = False

    def get_logger(self):
        return self.logger
