import logging
import os


class LoggerSetup:
    def __init__(self, name, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.level = level
        self.setup_logger()

    def setup_logger(self):
        # Set the logger level
        self.logger.setLevel(self.level)

        # Check if the logger already has a console handler to avoid duplicate messages
        if not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
            # Create a console handler and set its level
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.level)

            # Create a formatter and set it for the console handler
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(formatter)

            # Add the console handler to the logger
            self.logger.addHandler(console_handler)

        # Prevent the logger from logging to the root logger's handlers
        self.logger.propagate = False

    def get_logger(self):
        return self.logger
