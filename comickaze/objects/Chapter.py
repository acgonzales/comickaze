from .Comic import Comic
from comickaze import Comickaze


class Chapter:
    def __init__(self, comickaze: Comickaze, title: str, link: str, comic: Comic, date=None):
        """Chapter of a {Comic}

        Arguments:
            comickaze {Comickaze} -- Comickaze instance
            title {str} -- Title
            link {str} -- Link
            comic {Comic} -- Comic that contains this {Chapter}

        Keyword Arguments:
            date {datetime|str} -- Date published (default: {None})
        """

        self.comickaze = comickaze
        self.title = title
        self.link = link
        self.comic = comic
        self.date = date
        self.pages = []

    def get_links(self):
        return self.comickaze.get_chapter_links(self)

    def __str__(self):
        return self.title
