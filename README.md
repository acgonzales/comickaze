# Comickaze

A package to search and download comics on [ReadComicsOnline.ru](https://readcomicsonline.ru/).

## Installation

```bash
pip install Comickaze
```

## Usage

### As a Package

```python
from comickaze import Comickaze, Converter

# You dont need this, for testing purposes only
import random

download_dir = "download_dir"

c = Comickaze(log_level="VERBOSE")

# Searching
search_results = c.search_comics("Deadpool") # Returns a list of Suggestion object
random_suggestion = random.choice(search_results)

# Getting Comic info, returns Comic object
# Getting comic info from Suggestion object
comic = random_suggestion.get_comic()

# Getting comic info from URL
comic = c.get_comic("https://readcomicsonline.ru/comic/batman-the-adventures-continue-2020")

# Downloading Comic Chapters
# Output format choices: CBZ, PDF, IMG
download_dir = "download_dir"
output_format = Converter.CBZ

normal_downloader = c.create_downloader(comic.chapters, number_of_threads=1, output_format=output_format)
multithreaded_downloader = c.create_downloader(comic.chapters, number_of_threads=8, output_format=output_format)

# normal_downloader.start(download_dir)
multithreaded_downloader.start(download_dir)
```

## TODO:

- [x] CLI
- [ ] More CLI features
- [ ] More sources.
