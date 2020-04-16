from typing import List
import logging

import coloredlogs
import requests

from .Downloader import Downloader
from .objects import Suggestion, Comic, Chapter
from .util import soupify, create_session


class Comickaze:
    BASE_URL = "https://readcomicsonline.ru"

    def __init__(self, log_level: str = "ERROR"):
        """Comickaze instance

        Keyword Arguments:
            log_level {str} -- Log level (default: {"ERROR"})
        """
        self.log_level = log_level
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level=log_level, logger=self.logger)

        self.session = create_session()

    def search_comics(self, query: str) -> list:
        """Searches comics

        Arguments:
            query {str} -- Query

        Returns:
            list[Suggestion] -- Search results in a form of {Suggestion}
        """

        self.logger.info(f"Searching for {query}...")
        res = self.session.get("{0}/search".format(self.BASE_URL), params={
            "query": query
        })

        suggestions = res.json()["suggestions"]
        self.logger.info(f"Search done. Found {len(suggestions)} suggestions.")

        return [Suggestion(self, suggestion["value"], suggestion["data"]) for suggestion in suggestions]

    def get_comic(self, link: str) -> Comic:
        """Gets information about the comic in the given link

        Arguments:
            link {str} -- Link of the comic

        Returns:
            Comic -- Comic object
        """

        try:
            self.logger.info(f"Trying to access {link}")
            res = self.session.get(link)
        except:
            self.logger.error(
                f"Something went wrong accessing the page: {link}.")
            raise

        try:
            self.logger.info(f"Trying to parse the page...")
            soup = soupify(res.text)

            col = soup.find("div", attrs={"class": "col-sm-12"})

            list_container = col.find("div", attrs={"class": "list-container"})

            title = list_container.find(
                "h2", attrs={"class": "listmanga-header"}).text.strip()
            self.logger.debug(f"Found title: {title}")

            comic = Comic(title, link)

            image = list_container.find("img", attrs={"img-responsive"})["src"]
            comic.image = "https://www." + image[2:]
            self.logger.debug(f"Found image: {comic.image}")

            info_box = col.find("dl", attrs={"class": "dl-horizontal"})

            d_tags = info_box.find_all("dt")
            d_data = info_box.find_all("dd")

            for i, tag in enumerate(d_tags):
                tag = tag.text.lower()
                data_text = d_data[i].text.strip()
                val = data_text

                if tag == "type":
                    comic.comic_type = data_text
                elif tag == "status":
                    comic.status = data_text
                elif tag == "other names":
                    comic.other_names = data_text
                elif tag == "author(s)":
                    _authors = d_data[i].find_all("a")
                    comic.authors = [a.text.strip() for a in _authors]
                    val = comic.authors
                elif tag == "date of release":
                    comic.year = data_text
                elif tag == "categories":
                    _categories = d_data[i].find_all("a")
                    comic.categories = [c.text.strip() for c in _categories]
                    val = comic.categories
                elif tag == "tags":
                    _tags = d_data[i].find_all("a")
                    comic.tags = [t.text.strip() for t in _tags]
                    val = comic.tags
                elif tag == "views":
                    try:
                        views = int(data_text)
                    except ValueError:
                        views = data_text

                    comic.views = views
                    val = views
                elif tag == "rating":
                    rating_div = d_data[i].find(
                        "div", attrs={"id": "item-rating"})
                    score = rating_div["data-score"]

                    try:
                        rating = float(score)
                    except ValueError:
                        rating = score

                    comic.rating = rating
                    val = rating

                self.logger.debug(f"Found {tag}: {val}")

            comic.summary = col.find("div", attrs={"class": "manga well"}).find(
                "p").text.strip()
            self.logger.debug(f"Found summary: {comic.summary}")

            li_chapters = col.find("ul", attrs={"class": "chapters"}).find_all(
                "li", attrs={"class": "volume-0"})
            comic.chapters = []
            for chapter in li_chapters:
                _anch = chapter.find(
                    "h5", attrs={"class": "chapter-title-rtl"}).find("a")

                chapter_title = _anch.text.strip()
                chapter_link = _anch["href"]

                try:
                    date = chapter.find(
                        "div", attrs={"class": "date-chapter-title-rtl"}).text.strip()
                except:
                    date = None

                comic.chapters.append(
                    Chapter(self, chapter_title, chapter_link, comic, date=date))

            self.logger.info(
                f"Found {title} with {len(comic.chapters)} chapter(s).")

            return comic
        except:
            self.logger.error(
                f"Something went wrong parsing the page.")
            raise

    def get_chapter_pages(self, chapter: Chapter):
        link = chapter.link
        chapter_slug = link[link.rfind("/") + 1:]

        image_link_format = f"https://readcomicsonline.ru/uploads/manga/{chapter.comic.slug}/chapters/{chapter_slug}/"

        try:
            res = self.session.get(link)
        except:
            self.logger.error(
                f"Something went wrong accessing the page: {link}.")
            raise

        try:
            soup = soupify(res.text)

            pages_select = soup.find("select", attrs={"id": "page-list"})

            for option in pages_select.find_all("option"):
                val = int(option["value"])
                s_val = str(val)

                if val < 10:
                    s_val = "0" + s_val

                chapter.pages.append(image_link_format + f"{s_val}.jpg")

            return chapter.pages
        except:
            self.logger.error(
                f"Something went wrong parsing the page.")
            raise

    def create_chapter_downloader(self, chapter: Chapter, number_of_threads=2):
        return Downloader(self, [chapter], number_of_threads=number_of_threads)

    def create_multi_chapter_downloader(self, chapters: List[Chapter], number_of_threads=2):
        return Downloader(self, chapters, number_of_threads=number_of_threads)
