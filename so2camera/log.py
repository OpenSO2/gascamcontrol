# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
import logging
import sys
import os
from contextlib import contextmanager
import ctypes
import io
import tempfile
from conf import options as settings


@contextmanager
def stdout_redirector():
    libc = ctypes.CDLL(None)
    c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
    c_stderr = ctypes.c_void_p.in_dll(libc, 'stderr')

    streamout = io.BytesIO()
    streamerr = io.BytesIO()
    # The original fd stdout points to. Usually 1 on POSIX systems.
    original_stdout_fd = sys.stdout.fileno()
    original_stderr_fd = sys.stderr.fileno()

    def _redirect_stdout(to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        libc.fflush(c_stdout)
        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys.stdout.close()
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stdout_fd)
        # Create a new sys.stdout that points to the redirected fd
        sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, 'wb'))

    def _redirect_stderr(to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        libc.fflush(c_stderr)
        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys.stderr.close()
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stderr_fd)
        # Create a new sys.stdout that points to the redirected fd
        sys.stderr = io.TextIOWrapper(os.fdopen(original_stderr_fd, 'wb'))

    # Save a copy of the original stdout fd in saved_stdout_fd
    saved_stdout_fd = os.dup(original_stdout_fd)
    saved_stderr_fd = os.dup(original_stderr_fd)
    try:
        # Create a temporary file and redirect stdout to it
        tfile = tempfile.TemporaryFile(mode='w+b')
        _redirect_stdout(tfile.fileno())
        tfileerr = tempfile.TemporaryFile(mode='w+b')
        _redirect_stderr(tfileerr.fileno())
        # Yield to caller, then redirect stdout back to the saved fd
        yield
        _redirect_stdout(saved_stdout_fd)
        _redirect_stderr(saved_stderr_fd)
        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)

        tfileerr.flush()
        tfileerr.seek(0, io.SEEK_SET)

        streamout.write(tfile.read())
        streamerr.write(tfileerr.read())
    finally:
        tfile.close()
        tfileerr.close()
        os.close(saved_stdout_fd)
        os.close(saved_stderr_fd)

        logger = logging.getLogger('myLog')
        logger.info(streamout.getvalue().decode('utf-8').rstrip())
        logger.error(streamerr.getvalue().decode('utf-8').rstrip())


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
