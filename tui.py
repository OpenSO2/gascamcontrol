"""Text User Interface (tui) for so2cam."""
import logging
import curses
import conf


class CursesHandler(logging.Handler):
    """Redirect logging output to curses window."""

    def __init__(self, screen):
        logging.Handler.__init__(self)
        self.screen = screen

    def emit(self, record):
        """Render record to screen."""
        msg = self.format(record)
        self.screen.addstr("\n{}".format(msg))
        self.screen.refresh()


class Tui():
    """Implement Text User Interface using curses."""

    _loglevel = logging.DEBUG

    def __init__(self):
        self.maxx = None
        self.maxy = None
        self.padding = None
        self.stdscr = None
        self.logger = logging.getLogger('myLog')
        self._status_win = None

    def __enter__(self):
        stdscr = curses.initscr()
        self.stdscr = stdscr
        curses.noecho()
        curses.cbreak()
        curses.setsyx(-1, -1)

        maxy, maxx = stdscr.getmaxyx()
        self.maxy = maxy
        self.maxx = maxx

        stdscr.keypad(True)
        stdscr.nodelay(1)
        # stdscr.box()
        title = "SO2 Camera"
        stdscr.addstr(0, (maxx - len(title)) // 2, title)
        stdscr.refresh()

        padding = 2
        self.padding = padding

        log_win = self.log_win()
        self.ctrl_win()
        self.status_win()
        self.info_win()

        self.connect_logger_to_window(log_win)
        return self

    @property
    def loglevel(self):
        return self._loglevel

    @loglevel.setter
    def loglevel(self, value):
        self._loglevel = value
        self.logger.setLevel(value)
        self.status_win()

    def update(self):
        self.handle_input()

    def handle_input(self):
        inputchar = self.stdscr.getch()
        if inputchar == ord('1'):
            self.loglevel = logging.DEBUG
        if inputchar == ord('2'):
            self.loglevel = logging.INFO
        if inputchar == ord('3'):
            self.loglevel = logging.WARN
        if inputchar == ord('q'):
            self.stdscr.addstr("Some text here")
            conf.options["stop"] = True

    def log_win(self):
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

    def connect_logger_to_window(self, win, loggername='myLog'):
        handler = CursesHandler(win)
        formatter_display = logging.Formatter(
            '%(asctime)-8s | %(levelname)-7s | %(message)-s', '%H:%M:%S')
        handler.setFormatter(formatter_display)
        logger = logging.getLogger(loggername)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def ctrl_win(self):
        height = 4
        width = self.maxx - self.padding
        offset_y = self.maxy - height
        offset_x = self.padding
        win = curses.newwin(height, width, offset_y, offset_x)
        title = "Control"
        win.box()
        win.addstr(0, (width - len(title)) // 2, title)
        win.addstr(1, 1, "y = start")
        win.addstr(2, 1, "q = stop")
        win.refresh()

    def info_win(self):
        height = self.maxy // 2 - self.padding
        width = self.maxx // 2 - self.padding
        offset_x = offset_y = self.padding
        win = curses.newwin(height, width, offset_y, offset_x)
        title = "Info"
        win.box()
        win.addstr(0, (offset_y + width - len(title)) // 2, title)
        win.refresh()

    def status_win(self):
        height = self.maxy // 2 - self.padding
        width = (self.maxx) // 2 - self.padding
        offset_y = self.padding
        offset_x = self.padding + self.maxx // 2
        win = curses.newwin(height, width, offset_y, offset_x)
        title = "Status"
        status = "running"
        win.box()
        win.addstr(0, (offset_y + width - len(title)) // 2, title)
        win.addstr(1, 1, f"Aquisition: {status}")
        win.addstr(2, 1, f"Loglevel: {logging.getLevelName(self.loglevel)}")
        win.refresh()

    def __exit__(self, *args):
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
