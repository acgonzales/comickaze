import coloredlogs
import logging


class Comickaze:
    def __init__(self, log_level="INFO"):
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level=log_level, logger=self.logger)
