#!/usr/bin/env python3
"""EPUB Generator for Vumbua: Momentum is Life.

Builds:
1. vumbua-momentum-is-life-illustrated.epub (with portrait-oriented Harmony map in frontmatter)
2. vumbua-momentum-is-life-text-only.epub (clean, media-free for Eleven Reader TTS)

Follows IDPF EPUB3 standards with strict OEBPS manifest, NCX, NAV, responsive SVG map wrapper,
and chapter-by-chapter typography.
"""

import os
import re
import html
import uuid
import zipfile
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DATA_DIR = os.path.join(ROOT_DIR, "sessions", "data", "clean")
MAP_PATH = os.path.join(ROOT_DIR, "campaign", "Harmony-Map-portrait.jpeg")
OUTPUT_DIR = os.path.join(ROOT_DIR, "novel")

SESSION_FILES = [
    "s0-clean-story.md",
    "s1-clean-story.md",
    "s2-clean-story.md",
    "s2.5-clean-story.md",
    "s3-clean-story.md",
    "s4-clean-story.md",
    "s4.5-clean-story.md",
    "s5-clean-story.md",
    "s6-clean-story.md",
    "s7-clean-story.md",
    "s7.5-clean-story.md",
    "s8-clean-story.md",
    "s9-clean-story.md",
    "s10-clean-story.md",
    "s11-clean-story.md",
    "s12-clean-story.md",
]


def clean_markdown_to_html(md_text):
    """Converts novel markdown into clean, valid XHTML."""
    # Strip HTML comments (like <!-- RAW_RANGE ... --> and <!-- LEDGER ... -->)
    text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)

    # Strip YAML frontmatter
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)

    lines = text.split("\n")
    html_out = []
    in_p = False

    for line in lines:
        stripped = line.strip()

        # Horizontal rules
        if stripped in ("---", "***", "___"):
            if in_p:
                html_out.append("</p>")
                in_p = False
            html_out.append("<hr class=\"ornament\"/>")
            continue

        # Headers
        header_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if header_match:
            if in_p:
                html_out.append("</p>")
                in_p = False
            level = len(header_match.group(1))
            heading_text = header_match.group(2)
            # Escape HTML
            heading_text = html.escape(heading_text)
            # Support bold / italic in headers
            heading_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", heading_text)
            heading_text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", heading_text)
            html_out.append(f"<h{level}>{heading_text}</h{level}>")
            continue

        # Blank line = paragraph break
        if not stripped:
            if in_p:
                html_out.append("</p>")
                in_p = False
            continue

        # Regular text line
        escaped_line = html.escape(stripped)
        # Bold and italics
        escaped_line = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", escaped_line)
        escaped_line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", escaped_line)
        escaped_line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", escaped_line)
        escaped_line = re.sub(r"_(.*?)_", r"<em>\1</em>", escaped_line)

        if not in_p:
            html_out.append("<p>")
            in_p = True
            html_out.append(escaped_line)
        else:
            html_out.append(" " + escaped_line)

    if in_p:
        html_out.append("</p>")

    return "\n".join(html_out)


def split_session_into_chapters(md_text, session_id):
    """Splits a session story file into individual chapter blocks based on ## headings."""
    # Strip comments and YAML frontmatter first
    text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)

    # Split by level 2 headers (##) or level 1 headers (#)
    sections = re.split(r"(?=(?:^|\n)##\s+)", text)
    chapters = []

    for idx, sec in enumerate(sections):
        sec = sec.strip()
        if not sec:
            continue

        # Find heading
        m = re.match(r"^##\s+(.*?)(?:\n|$)", sec)
        if m:
            title = m.group(1).strip()
        else:
            # Check for level 1 heading
            m1 = re.match(r"^#\s+(.*?)(?:\n|$)", sec)
            if m1:
                title = m1.group(1).strip()
            else:
                title = f"{session_id.upper()} Part {idx+1}"

        html_body = clean_markdown_to_html(sec)
        chapters.append({
            "title": title,
            "html": html_body
        })

    return chapters


def build_epub(output_path, include_map=True):
    """Assembles a valid EPUB3 archive."""
    book_id = "urn:uuid:vumbua-momentum-is-life-book1-2026"
    title = "Momentum is Life: Vumbua Academy for Explorers"
    author = "The Vumbua Table"
    date_str = datetime.now().strftime("%Y-%m-%d")

    chapters = []
    chapter_id = 1

    for sf in SESSION_FILES:
        sid = sf.split("-")[0]
        fpath = os.path.join(CLEAN_DATA_DIR, sf)
        if not os.path.exists(fpath):
            print(f"Warning: file {fpath} not found!")
            continue

        with open(fpath, "r", encoding="utf-8") as handle:
            content = handle.read()

        sub_chapters = split_session_into_chapters(content, sid)
        for sc in sub_chapters:
            chapters.append({
                "id": f"chap_{chapter_id:03d}",
                "filename": f"chap_{chapter_id:03d}.xhtml",
                "title": sc["title"],
                "html": sc["html"]
            })
            chapter_id += 1

    print(f"[{'ILLUSTRATED' if include_map else 'TEXT-ONLY'}] Total parsed chapters: {len(chapters)}")

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. mimetype (MUST be first file, uncompressed)
        zf.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # 2. META-INF/container.xml
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        zf.writestr("META-INF/container.xml", container_xml)

        # 3. OEBPS/style.css
        style_css = """@charset "UTF-8";
body {
  font-family: serif;
  font-size: 1.05em;
  line-height: 1.5;
  margin: 5% 5% 5% 5%;
  text-align: justify;
}
h1 {
  font-size: 1.8em;
  text-align: center;
  margin-top: 15%;
  margin-bottom: 5%;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  page-break-before: always;
}
h2 {
  font-size: 1.4em;
  text-align: center;
  margin-top: 10%;
  margin-bottom: 6%;
  letter-spacing: 0.05em;
  page-break-before: always;
}
h3 {
  font-size: 1.15em;
  text-align: center;
  margin-top: 6%;
  margin-bottom: 4%;
}
p {
  margin-top: 0;
  margin-bottom: 0.3em;
  text-indent: 1.5em;
}
p:first-of-type, h1 + p, h2 + p, h3 + p, hr + p {
  text-indent: 0;
}
hr.ornament {
  border: 0;
  height: 1px;
  background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.4), rgba(0,0,0,0));
  margin: 2em 0;
  text-align: center;
}
.map-body {
  margin: 0 !important;
  padding: 0 !important;
  text-align: center;
  page-break-before: always;
  page-break-after: always;
  background-color: #000;
}
.map-container {
  width: 100vw;
  height: 100vh;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}
.map-container svg {
  max-width: 100%;
  max-height: 100%;
  display: block;
}
.title-page {
  text-align: center;
  page-break-before: always;
  page-break-after: always;
  margin-top: 20%;
}
.title-page h1 {
  font-size: 2.2em;
  margin-bottom: 0.2em;
}
.title-page h2 {
  font-size: 1.3em;
  font-weight: normal;
  font-style: italic;
  margin-top: 0;
  margin-bottom: 2em;
}
.title-page p.author {
  font-size: 1.1em;
  margin-top: 2em;
}
.title-page p.campaign {
  font-size: 0.9em;
  color: #555;
  margin-top: 3em;
}
"""
        zf.writestr("OEBPS/style.css", style_css)

        # 4. Optional Map Asset & Page
        manifest_items = []
        spine_refs = []

        manifest_items.append('<item id="style" href="style.css" media-type="text/css"/>')
        manifest_items.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
        manifest_items.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
        manifest_items.append('<item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>')
        manifest_items.append('<item id="author_note" href="author_note.xhtml" media-type="application/xhtml+xml"/>')

        spine_refs.append('<itemref idref="titlepage"/>')

        if include_map and os.path.exists(MAP_PATH):
            with open(MAP_PATH, "rb") as mf:
                zf.writestr("OEBPS/images/harmony_map_portrait.jpeg", mf.read())

            manifest_items.append('<item id="map_img" href="images/harmony_map_portrait.jpeg" media-type="image/jpeg"/>')
            manifest_items.append('<item id="map_page" href="map.xhtml" media-type="application/xhtml+xml"/>')
            spine_refs.append('<itemref idref="map_page"/>')

            # Map Page XHTML with responsive SVG container (1536x2752 viewBox)
            map_xhtml = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>Map of Harmony and the Unexplored Lands</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
  <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0"/>
</head>
<body class="map-body">
  <div class="map-container">
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="100%" height="100%" viewBox="0 0 1536 2752" preserveAspectRatio="xMidYMid meet">
      <image width="1536" height="2752" xlink:href="images/harmony_map_portrait.jpeg"/>
    </svg>
  </div>
</body>
</html>"""
            zf.writestr("OEBPS/map.xhtml", map_xhtml)

        # 5. Title Page
        title_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <div class="title-page">
    <h1>Momentum is Life</h1>
    <h2>Vumbua Academy for Explorers (Book 1)</h2>
    <p class="author">{html.escape(author)}</p>
    <p class="campaign">A Vumbua Campaign Novelization</p>
  </div>
</body>
</html>"""
        zf.writestr("OEBPS/titlepage.xhtml", title_xhtml)

        # 5b. Author's Note Page
        spine_refs.append('<itemref idref="author_note"/>')
        author_note_xhtml = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>A Note from the Author</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <h2>A NOTE FROM THE AUTHOR</h2>
  <p>Stories begin in strange, unexpected ways. This one began around a tabletop, where five friends and a Game Master decided this world was worth archiving. We worked together to take our session transcripts and mold them into this format, staying as faithful to the table as possible. We are not authors, but we are pretty proud of our work and story.</p>
  <p>To that end, we wanted to offer this book free or as low cost as possible to see if there was interest in our world. If you are reading or listening to this - you are among the first 100 to do so and we are very grateful!</p>
  <p>Dear person 101, we look forward to greeting you and cleaning up our book with the feedback of the ones who came before. In the meantime, we hope you give us some grace and take the extra step to suspend your disbelief as we bring you into our world.</p>
  <p>When we first envisioned <em>Vumbua</em>, we set out to build an epic fantasy where the frontier wasn't just empty land on an archivist's yellowing map, but a living, breathing mystery demanding curiosity, empathy, and raw courage. At the heart of that mystery are five unforgettable cadets - each were played by one of us in the campaign:</p>
  <p><strong>Britt</strong>, the fierce, tree-hugging Mizizi ranger with weeping willow dreadlocks, whose stubborn loyalty holds her kin together when the world starts coming apart.</p>
  <p><strong>Aggie</strong>, her gentle, brilliant cousin with an alabaster-and-scarlet mushroom shell, who seeks to understand the world's ancient songs before they fade forever.</p>
  <p><strong>Ignatius</strong>, the exiled ash-blood whose fiery hair crowns a deep hunger for purpose, struggling to balance his fiery heritage with the discipline of an explorer.</p>
  <p><strong>Loami</strong>, the grease-smudged union mechanic whose heavy wrench and unyielding moral compass remind us that every grand voyage is built on the sweat and solidarity of the engine room.</p>
  <p>And <strong>Iggy</strong>, the soil-kin sprout in an oversized woolen coat, whose innocent wonder and pocketfuls of mud remind us why the world is worth saving in the first place.</p>
  <p>What you hold here is their chronicle—novelized directly from our living campaign transcripts, preserving every line of dialogue, every frantic gamble, and every heartbeat of their journey through the Basalt Run.</p>
  <p>To the players, the storytellers, and everyone who ever looked past the edge of the map and wondered what lay beyond: thank you. Remember...</p>
  <p><em>Momentum is life.</em></p>
  <p class="author" style="text-align: right; margin-top: 2em; font-style: italic;">— The Vumbua Table</p>
</body>
</html>"""
        zf.writestr("OEBPS/author_note.xhtml", author_note_xhtml)

        # 6. Chapter Pages
        for chap in chapters:
            manifest_items.append(f'<item id="{chap["id"]}" href="{chap["filename"]}" media-type="application/xhtml+xml"/>')
            spine_refs.append(f'<itemref idref="{chap["id"]}"/>')

            chap_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{html.escape(chap["title"])}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{chap["html"]}
</body>
</html>"""
            zf.writestr(f"OEBPS/{chap['filename']}", chap_xhtml)

        # 7. Navigation Document (nav.xhtml - EPUB3)
        nav_items_html = []
        if include_map and os.path.exists(MAP_PATH):
            nav_items_html.append('      <li><a href="map.xhtml">Map: Harmony &amp; The Unexplored Lands</a></li>')
        nav_items_html.append('      <li><a href="author_note.xhtml">A Note from the Author</a></li>')
        for chap in chapters:
            nav_items_html.append(f'      <li><a href="{chap["filename"]}">{html.escape(chap["title"])}</a></li>')

        nav_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>Table of Contents</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="titlepage.xhtml">Title Page</a></li>
{chr(10).join(nav_items_html)}
    </ol>
  </nav>
</body>
</html>"""
        zf.writestr("OEBPS/nav.xhtml", nav_xhtml)

        # 8. NCX (EPUB2 backward compatibility for older Kindle/Kobo)
        ncx_points = []
        play_order = 1
        ncx_points.append(f"""    <navPoint id="navPoint-{play_order}" playOrder="{play_order}">
      <navLabel><text>Title Page</text></navLabel>
      <content src="titlepage.xhtml"/>
    </navPoint>""")
        play_order += 1

        if include_map and os.path.exists(MAP_PATH):
            ncx_points.append(f"""    <navPoint id="navPoint-{play_order}" playOrder="{play_order}">
      <navLabel><text>Map: Harmony &amp; The Unexplored Lands</text></navLabel>
      <content src="map.xhtml"/>
    </navPoint>""")
            play_order += 1

        ncx_points.append(f"""    <navPoint id="navPoint-{play_order}" playOrder="{play_order}">
      <navLabel><text>A Note from the Author</text></navLabel>
      <content src="author_note.xhtml"/>
    </navPoint>""")
        play_order += 1

        for chap in chapters:
            ncx_points.append(f"""    <navPoint id="navPoint-{play_order}" playOrder="{play_order}">
      <navLabel><text>{html.escape(chap["title"])}</text></navLabel>
      <content src="{chap["filename"]}"/>
    </navPoint>""")
            play_order += 1

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
{chr(10).join(ncx_points)}
  </navMap>
</ncx>"""
        zf.writestr("OEBPS/toc.ncx", toc_ncx)

        from datetime import timezone
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">{book_id}</dc:identifier>
    <dc:title>{html.escape(title)}</dc:title>
    <dc:creator>{html.escape(author)}</dc:creator>
    <dc:language>en</dc:language>
    <dc:date>{date_str}</dc:date>
    <dc:description>In a world driven by momentum, discovery is everything. For generations, the maps of Harmony had stood still—until two breakthrough expeditions made contact with the isolated Ash-Blood volcanic isles and the ancient Mizizi root-forest. To train a new vanguard of exploranauts, the Vumbua Academy of Explorers drops anchor at the frontier, opening an unprecedented intake for over one hundred thousand hopeful candidates. Entering alone for their own private reasons, five unlikely candidates find fate and circumstance repeatedly throwing them together—realizing that passing the exams is only the beginning... and momentum is life.</dc:description>
    <dc:subject>Fantasy</dc:subject>
    <dc:subject>Science Fantasy</dc:subject>
    <dc:subject>Adventure</dc:subject>
    <dc:subject>Daggerheart</dc:subject>
    <meta property="dcterms:modified">{utc_now}</meta>
  </metadata>
  <manifest>
{chr(10).join(['    ' + item for item in manifest_items])}
  </manifest>
  <spine toc="ncx">
{chr(10).join(['    ' + ref for ref in spine_refs])}
  </spine>
</package>"""
        zf.writestr("OEBPS/content.opf", content_opf)

    print(f"[SUCCESS] Wrote EPUB to: {output_path} ({os.path.getsize(output_path) / (1024*1024):.2f} MB)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Illustrated EPUB (with portrait-oriented Harmony map)
    illustrated_path = os.path.join(OUTPUT_DIR, "vumbua-momentum-is-life-illustrated.epub")
    build_epub(illustrated_path, include_map=True)

    # 2. Text-only EPUB for Eleven Reader TTS
    text_only_path = os.path.join(OUTPUT_DIR, "vumbua-momentum-is-life-text-only.epub")
    build_epub(text_only_path, include_map=False)


if __name__ == "__main__":
    main()
