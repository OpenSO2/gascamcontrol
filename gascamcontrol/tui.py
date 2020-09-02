"""Text User Interface (tui) for so2cam."""
# https://docs.python.org/3.6/library/textwrap.html
import logging
import curses
from .processingqueue import Queue
from .devicemanager import Devicemanager
from .diskmanager import Diskmanager
from .conf import Conf


class CursesHandler(logging.Handler):
    """Redirect logging output to curses window."""

    def __init__(self, screen):
        logging.Handler.__init__(self)
        self.screen = screen

    def emit(self, record):
        """Render record to screen."""
        msg = self.format(record)
        colorpair = curses.color_pair(int(record.levelno > 20))
        self.screen.addstr(f"\n{msg}", colorpair)
        self.screen.refresh()


class Tui:
    """Implement Text User Interface using curses."""

    _loglevel = logging.DEBUG

    def __init__(self):
        self.maxx = None
        self.maxy = None
        self.padding = None
        self.stdscr = None
        self.logger = logging.getLogger(__name__)
        self.logging = self.logger
        self._status_win = None
        self.queue = Queue()
        self.devicemanager = Devicemanager()
        self.diskmanager = Diskmanager()
        self.curses_handler = None
        self.conf = Conf()

    def startup(self):
        """Initiate curses."""
        curses.wrapper(self.setupscreen)

    def setupscreen(self, stdscr):
        """Initiate and layout screen, start windows."""
        self.stdscr = stdscr
        self.maxy, self.maxx = stdscr.getmaxyx()
        stdscr.nodelay(1)

        title = "SO2 Camera"
        stdscr.addstr(0, (self.maxx - len(title)) // 2, title)

        padding = 2
        self.padding = padding

        log_win = self.log_win()
        self.ctrl_win()
        self.status_win()
        self.info_win()

        self.connect_logger_to_window(log_win)

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)

        stdscr.refresh()

    @property
    def loglevel(self):
        """Get current log level."""
        return self._loglevel

    @loglevel.setter
    def loglevel(self, value):
        """Set log level in log and on screen."""
        self._loglevel = value
        self.logger.setLevel(value)
        self.status_win()

    def update(self):
        """Update screen."""
        self.handle_input()
        self.status_win()

    def handle_input(self):
        """Parse and act on command input."""
        inputchar = self.stdscr.getch()
        if inputchar == ord('1'):
            self.loglevel = logging.DEBUG
        if inputchar == ord('2'):
            self.loglevel = logging.INFO
        if inputchar == ord('3'):
            self.loglevel = logging.WARN
        if inputchar == ord('y'):
            self.devicemanager.start()
        if inputchar == ord('n'):
            self.devicemanager.stop()
        if inputchar == ord('q'):
            pass
        #     conf.options["stop"] = True

    def log_win(self):
        """Window showing current log output."""
        height = self.maxy // 2 - 4
        offset_x = self.padding
        offset_y = self.maxy - height - 4
        width = self.maxx - self.padding
        win_wrapper = curses.newwin(height, width, offset_y, offset_x)
        title = "Log"
        win_wrapper.box()
        win_wrapper.addstr(0, (self.maxx - len(title)) // 2, title)
        win_wrapper.refresh()

        win = curses.newwin(height - self.padding*2,
                            width - self.padding*2,
                            offset_y + self.padding,
                            offset_x + self.padding)
        win.scrollok(True)
        win.idlok(True)
        win.leaveok(True)
        win.refresh()
        return win

    def connect_logger_to_window(self, win):
        """Route logger output to logger window."""
        self.curses_handler = CursesHandler(win)
        formatter_display = logging.Formatter(
            '%(asctime)-8s | %(name)s | %(levelname)-7s | %(message)-s',
            '%H:%M:%S')
        self.curses_handler.setFormatter(formatter_display)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.curses_handler)

    def ctrl_win(self):
        """Control window listing available commands."""
        height = 4
        width = self.maxx - self.padding
        offset_y = self.maxy - height
        offset_x = self.padding
        win = curses.newwin(height, width, offset_y, offset_x)
        title = "Control"
        win.box()
        win.addstr(0, (width - len(title)) // 2, title)
        win.addstr(1, 1, "y = start   1 = logging:debug   2 = logging:info")
        win.addstr(2, 1, "n = stop    3 = logging:error                   ")

        win.refresh()

    def info_win(self):
        """Window showing general information."""
        height = self.maxy // 2 - self.padding
        width = self.maxx // 2 - self.padding
        offset_x = offset_y = self.padding
        win = curses.newwin(height, width, offset_y, offset_x)
        title = "Info"
        win.box()
        win.addstr(0, (offset_y + width - len(title)) // 2, title)

        win.addstr(1, 1, "Gas Cam Control Software")

        win.addstr(3, 1, "A control program for run multi-view cameras and ")
        win.addstr(4, 1, "pre-process UV camera data.")
        win.addstr(5, 1, "")
        win.addstr(6, 1, f"Version: {self.conf.get_version()}")
        win.addstr(7, 1, "Licence: MIT")
        win.addstr(8, 1, "Source: git.io/Jv3hl")
        win.addstr(9, 1, "Info: johann.jacobson@uni-hamburg.de")
        win.refresh()

    def status_win(self):
        """Status window showing system status information."""
        if not self._status_win:
            height = self.maxy // 2 - self.padding
            width = self.maxx // 2 - self.padding
            offset_y = self.padding
            offset_x = self.padding + self.maxx // 2

            self._status_win = curses.newwin(height, width, offset_y, offset_x)
            title = "Status"
            self._status_win.box()
            position = (offset_y + width - len(title)) // 2
            self._status_win.addstr(0, position, title)
        status = "running"
        self._status_win.addstr(1, 1, f"Aquisition: {status}")
        self._status_win.addstr(
            2, 1, f"Loglevel: {logging.getLevelName(self.loglevel)}")
        self._status_win.addstr(3, 1, f"Queue Fill level: {len(self.queue)}")
        self._status_win.addstr(
            4, 1, f"Image sets created: {self.devicemanager.noofimages}")
        self._status_win.addstr(
            5, 1, f"Images saved: {self.diskmanager.noofimages}")
        # self._status_win.addstr(
        #     6, 1, f"Last image set created: {len(self.queue)}")
        self._status_win.refresh()
        self.stdscr.refresh()

    def restore(self):
        """Reset terminal to original state.

        Exceptions from outside will not trigger curses.wrapper cleanup, so
        this is needed to reset manually.
        """
        self.logging.info("reset terminal...")
        logging.getLogger().removeHandler(self.curses_handler)
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
