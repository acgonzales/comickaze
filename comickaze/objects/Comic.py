class Comic:
    def __init__(self, title, link, image=None, comic_type=None, status=None, other_names=None,
                 authors=None, year=None, categories=None, tags=None, views=None, rating=None,
                 summary=None, chapters=None):
        """Comic Object

        Arguments:
            title {str} -- Title
            link {str} -- Link

        Keyword Arguments:
            image {str} -- Url of the cover image (default: {None})
            comic_type {str} -- Comic type (default: {None})
            status {str} -- Comic status (default: {None})
            other_names {str} -- [description] (default: {None})
            authors {list} -- List of authors (default: {None})
            year {str} -- Year of release (default: {None})
            categories {list} -- List of categories (default: {None})
            tags {list} -- List of tags (default: {None})
            views {int|str} -- Views (default: {None})
            rating {float|str} -- Ratings on the scale of 1-5 (default: {None})
            summary {str} -- Summary of the comic (default: {None})
            chapters {list[Chapter]} -- List of chapters of the comic (default: {None})
        """

        self.title = title
        self.link = link
        self.summary = summary
        self.chapters = chapters
        self.image = image
        self.comic_type = comic_type
        self.status = status
        self.other_names = other_names
        self.authors = authors
        self.year = year
        self.categories = categories
        self.tags = tags
        self.views = views
        self.rating = rating

    def __str__(self):
        return self.title
