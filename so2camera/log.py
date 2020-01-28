"""Logging setup, config python logging."""
import logging
import sys
import configargparse
import conf


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    parser.add("--debug", default=False, const=True, action="store_const",
               help="Set default log level to debug")
    parser.add("--logfile", default="so2-camera.log", help="Logfile")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class StreamToLogger():
    """Redirect print to a logger instance."""

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        """Write buffer to logger."""
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self, buf=""):
        """Alias for write."""
        self.write(buf)


class Log():
    """Configure and init logging."""

    def __init__(self, loggername):
        self.loggername = loggername
        self.logger = logging.getLogger(self.loggername)
        self.options = conf.Conf().options
        self.route_to_file()
        self.route_print()

    def route_print(self):
        """Route print statement to logger by overwriting stdout and stderr."""
        # stdout_logger = logging.getLogger(self.loggername)
        # sys.stdout = StreamToLogger(stdout_logger, logging.INFO)

        # stderr_logger = logging.getLogger(self.loggername)
        # sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)

        sys.stdout = StreamToLogger(self.logger, logging.INFO)
        sys.stderr = StreamToLogger(self.logger, logging.ERROR)

    def route_to_file(self):
        """Route logs to logfile (even debug messages)."""
        logfile = self.options.logfile
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        filehandle = logging.FileHandler(logfile)
        loglevel = logging.DEBUG if self.options.debug else logging.INFO
        filehandle.setLevel(loglevel)
        filehandle.setFormatter(formatter)
        self.logger.addHandler(filehandle)
