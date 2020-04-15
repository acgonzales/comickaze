import logging

import coloredlogs
import requests

from .objects import Suggestion


class Comickaze:
    BASE_URL = "https://readcomicsonline.ru"

    def __init__(self, log_level="INFO"):
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level=log_level, logger=self.logger)

        self.session = requests.session()

    def search_comics(self, query):
        res = self.session.get("{0}/search".format(self.BASE_URL), params={
            "query": query
        })

        suggestions = res.json()["suggestions"]

        return [Suggestion(self, suggestion["value"], suggestion["data"]) for suggestion in suggestions]
