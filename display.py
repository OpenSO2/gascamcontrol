import comm
import logging


class Display():
    def __init__(self):
        self.comm = None

    def run(self):
        self.comm = comm
        logger = logging.getLogger('myLog')
        logger.info("run display")

        self.comm.a["app"].router.add_static('/app', 'webapp', show_index=True)
