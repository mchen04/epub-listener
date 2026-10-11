"""EPUB parser using EbookLib."""

import logging
import warnings
from pathlib import Path
from xml.etree import ElementTree

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub

from epub_listener.application.ports import ChapterParser
from epub_listener.domain.exceptions import ParseError
from epub_listener.domain.models import Chapter

logger = logging.getLogger(__name__)

# EbookLib is noisy about future versions; suppress once at module load.
warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib.epub")
warnings.filterwarnings("ignore", category=FutureWarning, module="ebooklib.epub")


_TEXT_TAGS = frozenset(
    {
        "body",
        "p",
        "div",
        "span",
        "section",
        "article",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "title",
        "em",
        "strong",
        "b",
        "i",
        "u",
        "s",
        "a",
        "blockquote",
        "ul",
        "ol",
        "li",
        "dl",
        "dt",
        "dd",
        "sub",
        "sup",
        "small",
        "br",
        "hr",
        "img",
    }
)
_VOID_TAGS = frozenset({"br", "hr", "img"})


def _extract_body(body: bytes) -> tuple[str, str]:
    """Read ordinary serialized markup without building a second HTML tree."""
    # EbookLib serializes the body as UTF-8 XML. Keep BeautifulSoup's encoding
    # detection and HTML-specific string rules for anything outside this subset.
    if body.isascii() and b"<!" not in body and b"<?" not in body:
        try:
            root = ElementTree.fromstring(  # noqa: S314 - DTDs and declarations excluded above
                b"<root>" + body + b"</root>"
            )
        except ElementTree.ParseError:
            pass
        else:
            elements = list(root.iter())[1:]
            if all(
                element.tag in _TEXT_TAGS
                and not (element.tag in _VOID_TAGS and (element.text or len(element)))
                for element in elements
            ):
                xml_heading = next(
                    (element for element in elements if element.tag in {"h1", "h2", "title"}),
                    None,
                )
                title = (
                    "".join(text.strip() for text in xml_heading.itertext())
                    if xml_heading is not None
                    else "Unknown Chapter"
                )
                return title, "\n".join(root.itertext())

    soup = BeautifulSoup(body, "html.parser")
    heading = soup.find(["h1", "h2", "title"])
    title = heading.get_text(strip=True) if heading else "Unknown Chapter"
    return title, soup.get_text(separator="\n")


class EbookLibParser(ChapterParser):
    """Parse EbookLib documents with restricted XML extraction and HTML fallback."""

    MIN_CHAPTER_LENGTH = 100  # characters; filters frontmatter / debris

    def parse(self, epub_path: Path) -> list[Chapter]:
        """Extract chapters from the given EPUB file."""
        if not epub_path.exists():
            raise ParseError(f"EPUB file not found: {epub_path}")

        try:
            book = epub.read_epub(str(epub_path))
        except Exception as exc:
            raise ParseError(f"Failed to read EPUB file: {exc}") from exc

        raw_chapters: list[Chapter] = []
        seen_titles: set[str] = set()
        doc_index = 0

        for item in book.get_items():
            if item.get_type() != ebooklib.ITEM_DOCUMENT:
                continue
            # EbookLib reports the EPUB 3 navigation document as ordinary
            # XHTML.  Large tables of contents can exceed the length filter
            # and otherwise become a fake final audiobook chapter.
            if isinstance(item, epub.EpubNav):
                continue

            title, text = _extract_body(item.get_body_content())

            if title in seen_titles:
                title = f"{title} ({doc_index})"
            seen_titles.add(title)

            cleaned_lines = [line.strip() for line in text.split("\n") if line.strip()]
            cleaned_text = "\n\n".join(cleaned_lines)

            if len(cleaned_text) >= self.MIN_CHAPTER_LENGTH:
                chapter_id = f"{doc_index:04d}"
                raw_chapters.append(Chapter(id=chapter_id, title=title, text=cleaned_text))
                doc_index += 1

        # Secondary dedup: drop chapters with identical text
        unique: list[Chapter] = []
        seen_texts: set[str] = set()
        for ch in raw_chapters:
            if ch.text not in seen_texts:
                seen_texts.add(ch.text)
                unique.append(ch)

        logger.info("Parsed %d unique chapters from %s", len(unique), epub_path)
        return unique
