import unicodedata
import string
from os import path
import shutil
import pathlib

import requests
from bs4 import BeautifulSoup


def create_session():
    return requests.session()


def soupify(markup) -> BeautifulSoup:
    return BeautifulSoup(markup, "html.parser")


def create_folders(directory):
    directory = path.normpath(directory)

    p = pathlib.Path(directory)
    p.mkdir(parents=True, exist_ok=True)


def delete_folders(directory):
    if path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)


def clean_filename(filename):
    # https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8
    whitelist = "-_.() %s%s" % (string.ascii_letters, string.digits) + "',#"
    char_limit = 255
    replace = ''

    # replace spaces
    for r in replace:
        filename = filename.replace(r, '_')

    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize(
        'NFKD', filename).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename) > char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]
