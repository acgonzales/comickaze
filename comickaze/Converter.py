import os
from os import path
from zipfile import ZipFile, ZIP_DEFLATED

import img2pdf

from .util import create_folders, delete_folders, clean_filename

PDF = "pdf"
CBZ = "cbz"
IMG = "jpg"


def get_clean_output_path(output):
    filename = clean_filename(path.basename(output))
    return path.join(path.dirname(output), filename)


def get_images(dir):
    return [path.join(dir, img) for img in os.listdir(dir) if img.endswith(".jpg") or img.endswith(".png")]


def to_CBZ(comic_dir, delete=True, **kwargs):
    output_dir = path.dirname(comic_dir)
    filename = path.basename(comic_dir) + ".cbz"

    if filename in kwargs:
        filename = clean_filename(kwargs["filename"])

        if not filename.endswith(f".{CBZ}"):
            filename += f".{CBZ}"

    if "output_dir" in kwargs:
        if path.isdir(kwargs["output_dir"]):
            output_dir = kwargs["output_dir"]

    create_folders(output_dir)

    output = path.join(output_dir, filename)

    with ZipFile(output, "w", ZIP_DEFLATED) as handle:
        rel_root = path.abspath(path.join(comic_dir, os.pardir))

        for root, _, files in os.walk(comic_dir):
            handle.write(root, path.relpath(root, rel_root))

            for file in files:
                _filename = path.join(root, file)

                if path.isfile(_filename):
                    arc_name = path.join(path.relpath(root, rel_root), file)
                    handle.write(_filename, arc_name)

    if delete:
        delete_folders(comic_dir)


def to_PDF(comic_dir, delete=True, **kwargs):
    output_dir = comic_dir

    if "output_dir" in kwargs:
        if path.isdir(kwargs["output_dir"]):
            output_dir = kwargs["output_dir"]

    create_folders(output_dir)
    for chapter_dir in os.listdir(comic_dir):
        chapter_dir = path.join(comic_dir, chapter_dir)

        if path.isdir(chapter_dir):
            filename = path.basename(chapter_dir) + ".pdf"

            with open(path.join(output_dir, filename), "wb") as f:
                f.write(img2pdf.convert(get_images(chapter_dir)))

            if delete:
                delete_folders(chapter_dir)
