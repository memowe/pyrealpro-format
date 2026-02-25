from dataclasses import dataclass
import argparse
from collections.abc import Iterable
from pathlib import Path
import urllib.request
import re
from parsel import Selector

type URL = str
type PlaylistName = str
type IRealProData = str


@dataclass
class Args:
    url: URL
    output: Path


def parse_args() -> Args:

    parser = argparse.ArgumentParser(description="Download iReal Pro playlists.")
    parser.add_argument(
        "--url", required=True, help="URL of the iReal Pro playlists page."
    )
    parser.add_argument(
        "--output", required=True, help="Directory to save the downloaded playlists."
    )

    args = parser.parse_args()
    return Args(url=args.url, output=Path(args.output))


def retrieve_playlists(url: URL) -> Iterable[tuple[PlaylistName, IRealProData]]:

    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request) as response:
        html = response.read().decode()

    for link in Selector(text=html).css("h3 a"):
        text = link.css("::text").get()
        irealb = link.attrib.get("href")
        if text and irealb:
            yield (text, irealb)


def write_playlist_to_file(
    directory: Path, name: PlaylistName, content: IRealProData
) -> None:

    safe_name = re.sub(r"[^\w -]", "_", name).strip()
    filename = directory / f"{safe_name}.irealb"
    filename.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    print(f"Downloading playlists from: {args.url}")

    for name, content in retrieve_playlists(args.url):
        write_playlist_to_file(args.output, name, content)
        print(f"Saved playlist: {name}")


if __name__ == "__main__":
    main()
