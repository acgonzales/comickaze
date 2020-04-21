import click
from click import echo, types
from colorama import Fore, Back, Style, init as colorama_init
from PyInquirer import prompt

from comickaze import Comickaze
from comickaze.objects import Comic, Suggestion, Chapter
from comickaze.Converter import CBZ, PDF, IMG


@click.group()
def cli():
    """Comickaze CLI"""
    colorama_init()


@cli.command()
@click.argument("query", type=types.STRING)
@click.option("-o", "--output-format", type=types.Choice([CBZ, PDF, IMG]), default=CBZ, help="The file format of the downloaded comics.")
@click.option("-d", "--download-dir", type=types.Path(exists=False, resolve_path=True, file_okay=False, dir_okay=True), prompt=True, help="Download directory.")
@click.option("--delete-original", is_flag=True, default=True, help="Set to false if you want to keep the images before it was converted.")
@click.option("-t", "--threads", type=types.INT, default=4, help="Number of threads to use while download a chapter.")
@click.option("--daemon", type=types.BOOL, default=True, help="Sets the daemon value of the threads.")
@click.option("-ll", "--log-level", type=types.Choice(["DEBUG", "VERBOSE", "ERROR"]), default="ERROR", help="Sets the logger's log level.")
def download(query, output_format, download_dir, delete_original, threads, daemon, log_level):
    """Download Comics"""

    ck = Comickaze(log_level=log_level)

    suggestions = ck.search_comics(query)

    def display_comic(comic: Comic) -> Comic:
        lines = [
            [("Title", comic.title)],
            [("Other Names", comic.other_names)],
            [("Link", comic.link)],
            [("Number of Chapters", len(comic.chapters))],
            [("Tags", ", ".join(comic.tags))],
            [("Categories", ", ".join(comic.categories))],
            [("Status", comic.status), ("Year", comic.year)],
            [("Type", comic.comic_type), ("Authors", ", ".join(
                comic.authors) if comic.authors else None)],
            [("Views", comic.views), ("Ratings", comic.rating)],
            [("Summary", comic.summary)]
        ]

        for line in lines:
            to_display = ""

            for label, val in line:
                label = f"{Fore.YELLOW}{label}{Style.RESET_ALL}"

                if label == "Summary":
                    to_display += f"{label}: \n"
                else:
                    to_display += f"{label}: {val}\t".expandtabs(50)

            echo(to_display)

    suggestion_question = [
        {
            "type": "list",
            "name": "suggested",
            "message": f"Got {len(suggestions)} result(s). Select the comics you want to download.",
            "choices": [{
                "name": suggestion.title,
                "value": index
            } for index, suggestion in enumerate(suggestions)],
            "filter": lambda index: suggestions[index]
        }
    ]

    suggestion = prompt(suggestion_question)["suggested"]

    comic = suggestion.get_comic()
    comic.chapters.reverse()

    echo()
    display_comic(comic)
    echo()

    chapter_questions = [
        {
            "type": "confirm",
            "name": "comic_confirm",
            "message": "Is this the comic you wanted to download?"
        },
        {
            "type": "checkbox",
            "name": "chapters",
            "message": "Select the chapters you want to download.",
            "when": lambda answers: answers["comic_confirm"],
            "choices": [{
                "name": chapter.title,
                "value": index
            } for index, chapter in enumerate(comic.chapters)],
            "filter": lambda indices: [chapter for index, chapter in enumerate(comic.chapters) if index in indices]
        }
    ]

    answers = prompt(chapter_questions)

    if answers["comic_confirm"]:
        chapters = answers["chapters"]

        downloader = ck.create_downloader(
            chapters, number_of_threads=threads, output_format=output_format, daemon=daemon)
        downloader.start(download_dir)


if __name__ == "__main__":
    cli()
