from bs4 import BeautifulSoup


def soupify(markup) -> BeautifulSoup:
    return BeautifulSoup(markup, "html.parser")
