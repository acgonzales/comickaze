from typing import List

from functools import partial
from os import path, listdir
import threading
import time
import logging

import coloredlogs
from progress.bar import FillingCirclesBar

from . import Comickaze
from .Converter import CBZ, PDF, IMG
from .Converter import to_CBZ, to_PDF
from .util import create_session, clean_filename, create_folders, delete_folders
from .objects import Chapter, Comic


class Downloader:
    def __init__(self, chapters: List[Chapter], output_format: str = CBZ, number_of_threads=4, **kwargs):
        """Creates a Downloader object

        Arguments:
            chapters {List[Chapter]} -- Chapters to be downloaded

        Keyword Arguments:
            number_of_threads {int} -- Number of threads to use when downloading (default: {4})
            output_format {str} -- Coversion format (default: {"cbz"})
        """

        self.chapters = chapters
        self.comic = chapters[0].comic

        output_format = output_format.lower()
        if output_format not in [CBZ, PDF, IMG]:
            self.output_format = CBZ

        self.output_format = output_format
        self.number_of_threads = number_of_threads
        self.daemon = True

        if "daemon" in kwargs:
            try:
                self.daemon = kwargs["daemon"]
            except:
                pass

        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level="VERBOSE", logger=self.logger)

    def start(self, download_dir: str):
        """Starts the download process.

        Arguments:
            download_dir {str} -- Download directory
        """

        self.logger.info(
            f"Attempting to download {self.comic.title}, {len(self.chapters)} chapter(s).")

        download_dir = path.normpath(download_dir)
        comic_dir = path.join(
            download_dir, clean_filename(self.comic.title))

        self.comic_dir = comic_dir

        self.logger.debug(f"Trying to create folders: {comic_dir}")
        create_folders(comic_dir)

        total_pages = 0
        for chapter in self.chapters:
            total_pages += len(chapter.get_pages())

        with FillingCirclesBar(f"Downloading {self.comic.title}", max=total_pages) as bar:
            start_time = time.time()

            if self.number_of_threads > 1:
                self.logger.debug("Starting multithreaded download...")
                self._multi_threaded_download(download_dir, bar=bar)
            else:
                self.logger.debug("Starting singlethreaded download...")
                self._single_threaded_download(download_dir, bar=bar)

            end_time = time.time()

            print()
            self.logger.info(
                f"Download complete! Time elapsed: {end_time - start_time}")

            self._convert()
            self.logger.info(f"Operation done!")

    def _single_threaded_download(self, download_dir: str, **kwargs):
        session = create_session()

        for i, chapter in enumerate(self.chapters):
            if "bar" in kwargs:
                kwargs["bar"].suffix = f"Chapter {i + 1} of {len(self.chapters)}. Estimated time left: %(eta)ds"

            pages = chapter.pages

            chapter_dir = path.join(
                self.comic_dir, clean_filename(chapter.title))

            self.logger.debug(f"Trying to create folders: {chapter_dir}")
            create_folders(chapter_dir)

            for page in pages:
                self._download(page, chapter_dir, session=session)

                if "bar" in kwargs:
                    kwargs["bar"].next()

    def _multi_threaded_download(self, download_dir: str, **kwargs):
        for i, chapter in enumerate(self.chapters):
            pages = chapter.pages

            if "bar" in kwargs:
                kwargs["bar"].suffix = f"Chapter {i + 1} of {len(self.chapters)}. Estimated time left: %(eta)ds"

            chapter_dir = path.join(
                self.comic_dir, clean_filename(chapter.title))
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

                if "bar" in kwargs:
                    t = threading.Thread(target=self._download_pages,
                                         args=(chapters_to_download, chapter_dir), kwargs={"bar": kwargs["bar"]}, daemon=self.daemon)
                else:
                    t = threading.Thread(target=self._download_pages,
                                         args=(chapters_to_download, chapter_dir), daemon=self.daemon)

                threads.append(t)
                t.start()

            for thread in threads:
                thread.join()

    def _convert(self, **kwargs):
        self.logger.info(f"Converting into {self.output_format} format.")

        if self.output_format == CBZ:
            to_CBZ(self.comic_dir, self.comic.title)
        elif self.output_format == PDF:
            to_PDF(self.comic_dir)

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
