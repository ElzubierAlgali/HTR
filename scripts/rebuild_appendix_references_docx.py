#!/usr/bin/env python3
"""Build Appendix and References DOCX with stdlib only (ZIP + OOXML)."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def _run(text: str, *, bold: bool = False, italic: bool = False, mono: bool = False, size: int = 22) -> str:
    fonts = (
        '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/>'
        if mono
        else '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
    )
    props = [fonts, f'<w:sz w:val="{size}"/>', f'<w:szCs w:val="{size}"/>']
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    return (
        "<w:r>"
        f"<w:rPr>{''.join(props)}</w:rPr>"
        f'<w:t xml:space="preserve">{escape(text)}</w:t>'
        "</w:r>"
    )


def _para(runs_xml: str, *, style: str | None = None, hanging: bool = False, justify: bool = True) -> str:
    ppr = ["<w:pPr>"]
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if hanging:
        ppr.append(
            '<w:ind w:left="720" w:hanging="720"/>'
        )
    if justify and style not in {"Title", "Heading1"}:
        ppr.append('<w:jc w:val="both"/>')
    elif style in {"Title"}:
        ppr.append('<w:jc w:val="center"/>')
    ppr.append("</w:pPr>")
    return f"<w:p>{''.join(ppr)}{runs_xml}</w:p>"


def _heading(text: str, level: int) -> str:
    style = "Title" if level == 0 else "Heading1"
    size = 32 if level == 0 else 26
    # Re-size inline runs from _inline_md
    runs = _inline_md(text)
    # bump sizes in runs by rewriting sz vals for heading
    runs = runs.replace('w:val="22"', f'w:val="{size}"').replace('w:val="19"', f'w:val="{size}"')
    # ensure bold on all runs
    runs = runs.replace("<w:rPr>", "<w:rPr><w:b/>")
    return _para(runs, style=style, justify=False)


def _plain(text: str) -> str:
    return _para(_run(text))


def _code_block(text: str) -> str:
    lines = text.rstrip("\n").split("\n")
    parts = []
    for line in lines:
        parts.append(_para(_run(line if line else " ", mono=True, size=19), justify=False))
    return "".join(parts)


def _inline_md(text: str) -> str:
    """Render a subset of markdown: **bold**, `code`, *italic*."""
    pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)")
    runs = []
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            runs.append(_run(text[pos : m.start()]))
        token = m.group(0)
        if token.startswith("**"):
            runs.append(_run(token[2:-2], bold=True))
        elif token.startswith("`"):
            runs.append(_run(token[1:-1], mono=True, size=19))
        else:
            runs.append(_run(token[1:-1], italic=True))
        pos = m.end()
    if pos < len(text):
        runs.append(_run(text[pos:]))
    if not runs:
        runs.append(_run(""))
    return "".join(runs)


def markdown_to_body(md: str, *, hanging_refs: bool = False) -> str:
    body = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith("# "):
            body.append(_heading(line[2:].strip(), 0))
            i += 1
            continue
        if line.startswith("## "):
            body.append(_heading(line[3:].strip(), 1))
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            block = []
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # closing fence
            body.append(_code_block("\n".join(block)))
            continue
        # gather paragraph
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith("```"):
            para_lines.append(lines[i].rstrip())
            i += 1
        text = " ".join(para_lines)
        body.append(
            _para(
                _inline_md(text),
                hanging=hanging_refs and not text.startswith("Harvard"),
            )
        )
    return "".join(body)


def write_docx(path: Path, body_xml: str) -> None:
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml">
  <w:body>
    {body_xml}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", RELS)
        zf.writestr("word/document.xml", document)


def main() -> None:
    appendix_md = (DOCS / "APPENDIX_CODE.md").read_text(encoding="utf-8")
    refs_md = (DOCS / "REFERENCES.md").read_text(encoding="utf-8")

    appendix_body = markdown_to_body(appendix_md)
    refs_body = markdown_to_body(refs_md, hanging_refs=True)

    out_a = DOCS / "APPENDIX.docx"
    out_r = DOCS / "REFERENCES.docx"
    out_c = DOCS / "APPENDIX_AND_REFERENCES.docx"

    write_docx(out_a, appendix_body)
    write_docx(out_r, refs_body)
    # page break between appendix and references
    page_break = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    write_docx(out_c, appendix_body + page_break + refs_body)

    print(f"Wrote {out_a}")
    print(f"Wrote {out_r}")
    print(f"Wrote {out_c}")


if __name__ == "__main__":
    main()
