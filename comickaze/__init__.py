import coloredlogs
import logging

from comickaze import Comickaze

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)
