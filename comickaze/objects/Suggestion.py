class Suggestion:
    def __init__(self, comickaze, title, slug):
        """Suggestion object from {Comickaze.search_comics()}

        Arguments:
            comickaze {Comickaze} -- Comickaze instance
            title {str} -- Title
            slug {str} -- Slug
        """

        self.comickaze = comickaze
        self.title = title
        self.slug = slug
        self.link = f"{comickaze.BASE_URL}/comic/{slug}"

    def get_comic(self):
        return self.comickaze.get_comic(self.link)

    def __str__(self):
        return self.title
