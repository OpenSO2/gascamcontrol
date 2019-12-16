# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
import logging
import sys
from conf import options as settings
import os
import threading
import time

class OutputGrabber():
    """Class used to grab standard output or another stream."""
    escape_char = "\b"

    def __init__(self, stream=None, threaded=False):
        self.origstream = stream
        self.threaded = threaded
        if self.origstream is None:
            self.origstream = sys.stdout
        self.origstreamfd = self.origstream.fileno()
        self.capturedtext = ""
        # Create a pipe so the stream can be captured:
        self.pipe_out, self.pipe_in = os.pipe()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def start(self):
        """
        Start capturing the stream data.
        """
        self.capturedtext = ""
        # Save a copy of the stream:
        self.streamfd = os.dup(self.origstreamfd)
        # Replace the original stream with our write pipe:
        os.dup2(self.pipe_in, self.origstreamfd)
        if self.threaded:
            # Start thread that will read the stream:
            self.workerThread = threading.Thread(target=self.readOutput)
            self.workerThread.start()
            # Make sure that the thread is running and os.read() has executed:
            time.sleep(0.01)

    def stop(self):
        """Stop capturing stream data and save the text in `capturedtext`."""
        # Print the escape character to make the readOutput method stop:
        self.origstream.write(self.escape_char)
        # Flush the stream to make sure all our data goes in before
        # the escape character:
        self.origstream.flush()
        if self.threaded:
            # wait until the thread finishes so we are sure that
            # we have until the last character:
            self.workerThread.join()
        else:
            self.readOutput()
        # Close the pipe:
        os.close(self.pipe_in)
        os.close(self.pipe_out)
        # Restore the original stream:
        os.dup2(self.streamfd, self.origstreamfd)
        # Close the duplicate stream:
        os.close(self.streamfd)

        self.logger = logging.getLogger("myLog")
        self.logger.warning(f"len cpttxt{len(self.capturedtext)}")
        self.logger.warning(self.capturedtext)

    def readOutput(self):
        """Read stream (one byte at a time) and save text to `capturedtext`."""
        self.logger = logging.getLogger("myLog")
        encoding = "iso-8859-1"
        self.logger.warning("read output")

        while True:
            char = os.read(self.pipe_out, 1)

            self.logger.warning("self.escape_char" + self.escape_char)
            if not char or self.escape_char in char.decode(encoding):
                break
            self.logger.warning("still something in there i guess " + char.decode(encoding))
            print(char)

            self.capturedtext += char.decode(encoding)
            # self.capturedtext += "capture test"
            # break


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
