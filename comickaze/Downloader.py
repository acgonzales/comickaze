from typing import List

from os import path
import threading
import time
import logging

import coloredlogs
from progress.bar import FillingCirclesBar

from . import Comickaze
from .util import create_session, clean_filename, create_folders
from .objects import Chapter, Comic


class Downloader:
    def __init__(self, comickaze: Comickaze, chapters: List[Chapter]):
        self.comickaze = comickaze
        self.chapters = chapters
        self.comic = chapters[0].comic

        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level="VERBOSE", logger=self.logger)

    def start(self, download_dir):
        self.logger.info(
            f"Attempting to download {self.comic.title}, {len(self.chapters)} chapter(s).")

        download_dir = path.normpath(download_dir)
        comic_dir = path.join(
            download_dir, clean_filename(self.comic.title))

        self.logger.debug(f"Trying to create folders: {comic_dir}")
        create_folders(comic_dir)

        total_pages = 0
        for chapter in self.chapters:
            total_pages += len(chapter.get_pages())

        number_of_chapters = len(self.chapters)

        with FillingCirclesBar(f"Downloading {self.comic.title}", max=total_pages) as bar:
            start_time = time.time()

            session = create_session()

            for i, chapter in enumerate(self.chapters):
                bar.suffix = f"Chapter {i + 1} of {number_of_chapters}. ETA: %(eta)ds"

                pages = chapter.get_pages()

                chapter_dir = path.join(
                    comic_dir, clean_filename(chapter.title))
                self.logger.debug(f"Trying to create folders: {chapter_dir}")
                create_folders(chapter_dir)

                for page in pages:
                    self._download(page, chapter_dir, session=session)
                    bar.next()

            end_time = time.time()
            self.logger.info(
                f"Download complete! Time elapsed: {end_time - start_time}")

    def _download_pages(self, pages: List[str], download_dir: str, session=create_session(), **kwargs):
        for page in pages:
            self._download(page, download_dir, session=session)

            if "bar" in kwargs:
                kwargs["bar"].next()

    def _download(self, page: str, download_dir: str, session=create_session()):
        filename = clean_filename(page[page.rfind("/") + 1:])
        page_path = path.join(download_dir, filename)

        r = session.get(page, stream=True)

        with open(page_path, "wb") as f:
            for chunk in r:
                f.write(chunk)


class MultiThreadedDownloader(Downloader):
    def __init__(self, comickaze: Comickaze, chapters: List[Chapter], number_of_threads: int = 4, daemon=True):
        super().__init__(comickaze, chapters)

        self.number_of_threads = number_of_threads
        self.daemon = daemon

    def start(self, download_dir):
        download_dir = path.normpath(download_dir)
        comic_dir = path.join(
            download_dir, clean_filename(self.comic.title))

        total_pages = 0
        for chapter in self.chapters:
            total_pages += len(chapter.get_pages())

        number_of_chapters = len(self.chapters)

        with FillingCirclesBar(f"Downloading {self.comic.title}", max=total_pages) as bar:
            start_time = time.time()

            for i, chapter in enumerate(self.chapters):
                pages = chapter.pages

                bar.suffix = f"Chapter {i + 1} of {number_of_chapters}. ETA: %(eta)ds"

                chapter_dir = path.join(
                    comic_dir, clean_filename(chapter.title))
                self.logger.debug(f"Trying to create folders: {chapter_dir}")
                create_folders(chapter_dir)

                threads = []
                mid = int(len(pages) / self.number_of_threads) + 1
                for i in range(self.number_of_threads):
                    start = i * mid
                    end = start + mid

                    if end > len(pages) and (i == self.number_of_threads - 1 and len(pages[end:]) != 0):
                        end = len(pages)

                    chapters_to_download = pages[start:end]
                    t = threading.Thread(target=self._download_pages,
                                         args=(chapters_to_download, chapter_dir), kwargs={"bar": bar}, daemon=self.daemon)
                    threads.append(t)
                    t.start()

                for thread in threads:
                    thread.join()

            end_time = time.time()
            self.logger.info(
                f"Download complete! Time elapsed: {end_time - start_time}")
