#!/usr/bin/env python3
"""Agnostic EPUB Generator for Tabletop Campaign Novelizations.

Builds:
1. [output_prefix]-illustrated.epub (with frontmatter map/artwork if configured)
2. [output_prefix]-text-only.epub (clean, media-free for TTS e-readers)

Follows IDPF EPUB3 standards with strict OEBPS manifest, NCX, NAV, and chapter typography.
Loads metadata dynamically from novel/book_config.json.
"""

import os
import re
import html
import json
import uuid
import zipfile
import glob
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "novel", "book_config.json")
CLEAN_DATA_DIR = os.path.join(ROOT_DIR, "sessions", "data", "clean")
OUTPUT_DIR = os.path.join(ROOT_DIR, "novel")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "title": "Untitled Campaign Novel",
        "subtitle": "Book 1",
        "series": "Tabletop Chronicles",
        "author": "The Table",
        "campaign": "Tabletop Campaign Novelization",
        "description": "A novelized fantasy adventure adapted directly from tabletop roleplaying campaign transcripts.",
        "subjects": ["Fantasy", "Adventure", "Tabletop RPG"],
        "author_note": {
            "title": "A NOTE FROM THE AUTHORS",
            "paragraphs": [
                "Stories begin in strange, unexpected ways. This one began around a tabletop, where friends and a Game Master decided this world was worth archiving."
            ],
            "signoff": "— The Table"
        },
        "cover_image": None,
        "map_image": None,
        "output_prefix": "campaign-novel"
    }


def find_session_story_files():
    """Finds all clean story markdown files in natural session order."""
    pattern = os.path.join(CLEAN_DATA_DIR, "s*-clean-story.md")
    files = glob.glob(pattern)
    
    def sort_key(filepath):
        basename = os.path.basename(filepath)
        m = re.search(r"s([0-9]+(?:\.[0-9]+)?)", basename)
        return float(m.group(1)) if m else 999.0

    return sorted(files, key=sort_key)


def clean_markdown_to_html(md_text):
    """Converts novel markdown into clean, valid XHTML."""
    text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)

    lines = text.split("\n")
    html_out = []
    in_p = False

    for line in lines:
        stripped = line.strip()

        if stripped in ("---", "***", "___"):
            if in_p:
                html_out.append("</p>")
                in_p = False
            html_out.append('<hr class="ornament"/>')
            continue

        header_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if header_match:
            if in_p:
                html_out.append("</p>")
                in_p = False
            level = len(header_match.group(1))
            heading_text = html.escape(header_match.group(2))
            heading_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", heading_text)
            heading_text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", heading_text)
            html_out.append(f"<h{level}>{heading_text}</h{level}>")
            continue

        if not stripped:
            if in_p:
                html_out.append("</p>")
                in_p = False
            continue

        escaped_line = html.escape(stripped)
        escaped_line = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", escaped_line)
        escaped_line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", escaped_line)
        escaped_line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", escaped_line)
        escaped_line = re.sub(r"_(.*?)_", r"<em>\1</em>", escaped_line)

        if not in_p:
            html_out.append("<p>")
            in_p = True
            html_out.append(escaped_line)
        else:
            html_out.append(f" {escaped_line}")

    if in_p:
        html_out.append("</p>")

    return "\n".join(html_out)


def parse_chapters_from_story(md_text, session_prefix="s"):
    """Splits session story markdown into individual chapters by ## or # headings."""
    text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)

    lines = text.split("\n")
    chapters = []
    current_title = None
    current_lines = []
    chap_idx = 1

    for line in lines:
        stripped = line.strip()
        header_match = re.match(r"^(#{1,2})\s+(.*)$", stripped)
        if header_match:
            h_text = header_match.group(2).strip()
            if current_title and current_lines:
                ch_content = "\n".join(current_lines).strip()
                if ch_content:
                    chapters.append({
                        "id": f"{session_prefix}_chap_{chap_idx:03d}",
                        "title": current_title,
                        "filename": f"{session_prefix}_chap_{chap_idx:03d}.xhtml",
                        "html": clean_markdown_to_html(f"## {current_title}\n\n{ch_content}")
                    })
                    chap_idx += 1
            current_title = h_text
            current_lines = []
        else:
            current_lines.append(line)

    if current_title and current_lines:
        ch_content = "\n".join(current_lines).strip()
        if ch_content:
            chapters.append({
                "id": f"{session_prefix}_chap_{chap_idx:03d}",
                "title": current_title,
                "filename": f"{session_prefix}_chap_{chap_idx:03d}.xhtml",
                "html": clean_markdown_to_html(f"## {current_title}\n\n{ch_content}")
            })

    return chapters


def build_epub(output_path, include_media=True):
    config = load_config()
    title = config.get("title", "Untitled Campaign Novel")
    subtitle = config.get("subtitle", "")
    author = config.get("author", "The Table")
    description = config.get("description", "")
    author_note_cfg = config.get("author_note", {})

    story_files = find_session_story_files()
    all_chapters = []

    for sf in story_files:
        s_id = os.path.basename(sf).split("-")[0]
        with open(sf, "r", encoding="utf-8") as f:
            content = f.read()
        chaps = parse_chapters_from_story(content, session_prefix=s_id)
        all_chapters.extend(chaps)

    print(f"[{'ILLUSTRATED' if include_media else 'TEXT-ONLY'}] Total parsed chapters: {len(all_chapters)}")

    book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_DNS, title.lower())}"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        zf.writestr("META-INF/container.xml", container_xml)

        style_css = """
@namespace "http://www.w3.org/1999/xhtml";
body {
  font-family: serif;
  line-height: 1.5;
  margin: 5%;
  text-align: justify;
}
h1, h2, h3 { font-family: sans-serif; text-align: center; }
h1 { font-size: 1.8em; margin-top: 15%; margin-bottom: 5%; text-transform: uppercase; page-break-before: always; }
h2 { font-size: 1.4em; margin-top: 10%; margin-bottom: 6%; page-break-before: always; }
p { margin-top: 0; margin-bottom: 0.3em; text-indent: 1.5em; }
p:first-of-type, h1 + p, h2 + p, hr + p { text-indent: 0; }
hr.ornament { border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.4), rgba(0,0,0,0)); margin: 2em 0; }
.title-page { text-align: center; page-break-before: always; margin-top: 20%; }
"""
        zf.writestr("OEBPS/style.css", style_css)

        manifest_items = [
            '<item id="style" href="style.css" media-type="text/css"/>',
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
            '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
            '<item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>',
            '<item id="author_note" href="author_note.xhtml" media-type="application/xhtml+xml"/>'
        ]
        spine_refs = ['<itemref idref="titlepage"/>', '<itemref idref="author_note"/>']

        # Title Page
        title_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <div class="title-page">
    <h1>{html.escape(title)}</h1>
    <h2>{html.escape(subtitle)}</h2>
    <p class="author">{html.escape(author)}</p>
  </div>
</body>
</html>"""
        zf.writestr("OEBPS/titlepage.xhtml", title_xhtml)

        # Author Note
        author_paragraphs = author_note_cfg.get("paragraphs", [])
        p_html = "".join([f"<p>{html.escape(p)}</p>\n" for p in author_paragraphs])
        author_note_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{html.escape(author_note_cfg.get("title", "A Note from the Authors"))}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <h2>{html.escape(author_note_cfg.get("title", "A NOTE FROM THE AUTHORS"))}</h2>
  {p_html}
  <p style="text-align: right; margin-top: 2em; font-style: italic;">{html.escape(author_note_cfg.get("signoff", "— The Table"))}</p>
</body>
</html>"""
        zf.writestr("OEBPS/author_note.xhtml", author_note_xhtml)

        # Chapter pages
        for chap in all_chapters:
            manifest_items.append(f'<item id="{chap["id"]}" href="{chap["filename"]}" media-type="application/xhtml+xml"/>')
            spine_refs.append(f'<itemref idref="{chap["id"]}"/>')
            chap_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{html.escape(chap["title"])}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
{chap["html"]}
</body>
</html>"""
            zf.writestr(f"OEBPS/{chap['filename']}", chap_xhtml)

        # nav.xhtml
        nav_items_html = ['      <li><a href="author_note.xhtml">A Note from the Authors</a></li>']
        for chap in all_chapters:
            nav_items_html.append(f'      <li><a href="{chap["filename"]}">{html.escape(chap["title"])}</a></li>')

        nav_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Table of Contents</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="titlepage.xhtml">Title Page</a></li>
{'\n'.join(nav_items_html)}
    </ol>
  </nav>
</body>
</html>"""
        zf.writestr("OEBPS/nav.xhtml", nav_xhtml)

        # toc.ncx
        ncx_points = [
            '    <navPoint id="navPoint-1" playOrder="1"><navLabel><text>Title Page</text></navLabel><content src="titlepage.xhtml"/></navPoint>',
            '    <navPoint id="navPoint-2" playOrder="2"><navLabel><text>A Note from the Authors</text></navLabel><content src="author_note.xhtml"/></navPoint>'
        ]
        po = 3
        for chap in all_chapters:
            ncx_points.append(f'    <navPoint id="navPoint-{po}" playOrder="{po}"><navLabel><text>{html.escape(chap["title"])}</text></navLabel><content src="{chap["filename"]}"/></navPoint>')
            po += 1

        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{book_id}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{html.escape(title)}</text></docTitle>
  <navMap>
{'\n'.join(ncx_points)}
  </navMap>
</ncx>"""
        zf.writestr("OEBPS/toc.ncx", toc_ncx)

        # content.opf
        content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">{book_id}</dc:identifier>
    <dc:title>{html.escape(title)}</dc:title>
    <dc:creator>{html.escape(author)}</dc:creator>
    <dc:language>en</dc:language>
    <dc:date>{date_str}</dc:date>
    <dc:description>{html.escape(description)}</dc:description>
    <meta property="dcterms:modified">{utc_now}</meta>
  </metadata>
  <manifest>
{'\n'.join(['    ' + item for item in manifest_items])}
  </manifest>
  <spine toc="ncx">
{'\n'.join(['    ' + ref for ref in spine_refs])}
  </spine>
</package>"""
        zf.writestr("OEBPS/content.opf", content_opf)

    print(f"[SUCCESS] Wrote EPUB to: {output_path} ({os.path.getsize(output_path) / (1024*1024):.2f} MB)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    config = load_config()
    prefix = config.get("output_prefix", "campaign-novel")
    illustrated_path = os.path.join(OUTPUT_DIR, f"{prefix}-illustrated.epub")
    build_epub(illustrated_path, include_media=True)
    text_only_path = os.path.join(OUTPUT_DIR, f"{prefix}-text-only.epub")
    build_epub(text_only_path, include_media=False)


if __name__ == "__main__":
    main()
