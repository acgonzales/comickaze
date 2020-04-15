from bs4 import BeautifulSoup


def soupify(markup):
    return BeautifulSoup(markup, "html.parser")
