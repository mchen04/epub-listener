import json
from dataclasses import asdict
from pathlib import Path
from zipfile import ZipFile

import pytest
from ebooklib import epub

from epub_listener.infrastructure.parsers.ebooklib_parser import EbookLibParser

PARSER_CASES = json.loads(
    (Path(__file__).parent / "fixtures" / "epub-parser.json").read_text(encoding="utf-8")
)


def write_raw_epub(path: Path, documents: list[str]) -> None:
    """Keep malformed source markup intact until the real parser reads it."""
    book = epub.EpubBook()
    book.set_identifier("parser-characterization")
    book.set_title("Synthetic Parser Characterization")
    book.set_language("en")
    items = []
    for index in range(len(documents)):
        item = epub.EpubHtml(title="Placeholder", file_name=f"c{index}.xhtml", lang="en")
        item.content = "<h1>Placeholder</h1>"
        book.add_item(item)
        items.append(item)
    book.spine = items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(path, book)
    with ZipFile(path) as archive:
        entries = [(entry, archive.read(entry.filename)) for entry in archive.infolist()]
    replacements = {
        f"EPUB/c{index}.xhtml": text.encode("utf-8") for index, text in enumerate(documents)
    }
    with ZipFile(path, "w") as archive:
        for entry, content in entries:
            archive.writestr(entry, replacements.get(entry.filename, content))


@pytest.mark.parametrize("case", PARSER_CASES, ids=lambda case: case["name"])
def test_parser_preserves_characterized_html(case: dict, tmp_path: Path) -> None:
    path = tmp_path / "characterization.epub"
    write_raw_epub(path, case["documents"])
    actual = [asdict(chapter) for chapter in EbookLibParser().parse(path)]
    assert actual == case["chapters"]


def test_parser_does_not_treat_large_navigation_document_as_chapter(tmp_path: Path) -> None:
    path = tmp_path / "large-navigation.epub"
    book = epub.EpubBook()
    book.set_identifier("large-navigation")
    book.set_title("Large Navigation")
    book.set_language("en")

    chapter = epub.EpubHtml(title="Chapter 1", file_name="chapter.xhtml", lang="en")
    chapter.content = "<h1>Chapter 1</h1><p>" + "This is actual chapter prose. " * 10 + "</p>"
    book.add_item(chapter)
    book.toc = tuple(
        epub.Link("chapter.xhtml", f"An intentionally verbose chapter link {number}", str(number))
        for number in range(50)
    )
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", chapter]
    epub.write_epub(path, book)

    chapters = EbookLibParser().parse(path)

    assert len(chapters) == 1
    assert chapters[0].title == "Chapter 1"
    assert "intentionally verbose chapter link" not in chapters[0].text
