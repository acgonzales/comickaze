from typing import List

from os import path
import threading
import time
import logging

import coloredlogs
from progress.bar import ChargingBar

from . import Comickaze
from .util import create_session, clean_filename, create_folders
from .objects import Chapter, Comic


class Downloader:
    def __init__(self, comickaze: Comickaze, chapters: List[Chapter], number_of_threads: int = 2, is_descending=True):
        self.comickaze = comickaze
        self.chapters = chapters

        if is_descending:
            self.chapters.reverse()

        self.comic = chapters[0].comic
        self.number_of_threads = number_of_threads

        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level="ERROR", logger=self.logger)

    def start(self, download_dir):
        self.logger.info(
            f"Attempting to download {self.comic.title}, {len(self.chapters)} chapter(s).")

        download_dir = path.normpath(download_dir)
        comic_dir = path.join(
            download_dir, clean_filename(self.comic.title))

        self.logger.debug(f"Trying to create folders: {comic_dir}")
        create_folders(comic_dir)

        with ChargingBar(f"Downloading {self.comic.title}", max=len(self.chapters), suffix=f"Chapter 1 of {len(self.chapters)}") as bar:
            start_time = time.time()

            for i, chapter in enumerate(self.chapters):
                bar.suffix = f"Chapter {i + 1} of {len(self.chapters)}. ETA: %(eta)ds"

                pages = chapter.get_pages()

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
                    t = threading.Thread(target=self._download,
                                         args=(i, chapters_to_download, chapter_dir), daemon=True)
                    threads.append(t)
                    t.start()

                for i, thread in enumerate(threads):
                    thread.join()

                bar.next()

            end_time = time.time()
            self.logger.info(
                f"Download complete! Time elapsed: {start_time - end_time}")

    def _download(self, name: str, pages: List[str], download_dir: str):
        thread_session = create_session()

        for page in pages:
            filename = clean_filename(page[page.rfind("/") + 1:])
            page_path = path.join(download_dir, filename)

            r = thread_session.get(page)

            # if r.status_code == 200:
            with open(page_path, "wb") as f:
                # for chunk in r.iter_content():
                f.write(r.content)
