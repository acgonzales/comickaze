class Chapter:
    def __init__(self, title, link, comic, date=None):
        """Chapter of a {Comic}

        Arguments:
            title {str} -- Title
            link {str} -- Link
            comic {Comic} -- Comic that contains this {Chapter}

        Keyword Arguments:
            date {datetime|str} -- Date published (default: {None})
        """
        self.title = title
        self.link = link
        self.comic = comic
        self.date = date

    def __str__(self):
        return self.title
