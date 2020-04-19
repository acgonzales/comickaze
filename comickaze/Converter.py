import os
from os import path
from zipfile import ZipFile, ZIP_DEFLATED

import img2pdf

from .util import create_folders, clean_filename


def get_clean_output_path(output):
    filename = clean_filename(path.basename(output))
    return path.join(path.dirname(output), filename)


def get_images(dir):
    return [path.join(path, img) for img in os.listdir(path) if img.endswith(".jpg") or img.endswith(".png")]


def to_CBZ(comic_dir, output):
    output = get_clean_output_path(output)

    with ZipFile(output, "w", ZIP_DEFLATED) as handle:
        rel_root = path.abspath(comic_dir, os.pardir)

        for root, _, files in os.walk(path):
            handle.write(root, path.relpath(root, rel_root))

            for file in files:
                _filename = path.join(root, file)

                if path.isfile(_filename):
                    arc_name = path.join(path.relpath(root, rel_root), file)
                    handle.write(_filename, arc_name)


def to_PDF(comic_dir, output):
    output = get_clean_output_path(output)

    with open(output, "wb") as f:
        f.write(img2pdf.convert(get_images(comic_dir)))
