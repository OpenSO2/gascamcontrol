# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
import logging
from conf import options as settings


class Log():
    def __init__(self, loggername):
        self.loggername = loggername
        self.logger = logging.getLogger(loggername)
        self.error = self.logger.error
        self.warning = self.logger.warning
        self.info = self.logger.info
        self.route_to_file()

    def route_to_file(self):
        """Route logs to logfile (even debug messages)."""
        logfile = settings["logfile"]
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        filehandle = logging.FileHandler(logfile)
        filehandle.setLevel(logging.DEBUG)
        filehandle.setFormatter(formatter)
        self.logger.addHandler(filehandle)
