#!/usr/bin/env python3
"""Keep the Reading Room shelf stocked.

  fetch_shelf.py            download any text listed in shelf.json that is missing from books/
  fetch_shelf.py --add ID   look ID up on gutendex.com, download its UTF-8 text, add it to shelf.json

Texts come from gutenberg.org unaltered. Word counts are measured between the
*** START / *** END markers. Nothing is written to shelf.json without a catalogue hit.
"""
import json, re, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SHELF = HERE / "shelf.json"
BOOKS = HERE / "books"
UA = {"User-Agent": "reading-room-shelf/1.0"}


def get(url, timeout=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def word_count(text):
    m = re.search(r"\*\*\* ?START OF.*?\n", text)
    n = re.search(r"\*\*\* ?END OF", text)
    body = text[m.end():n.start()] if m and n else text
    return len(body.split())


def download(book_id):
    BOOKS.mkdir(exist_ok=True)
    dest = BOOKS / f"pg{book_id}.txt"
    if dest.exists() and dest.stat().st_size > 20000:
        return dest
    data = get(f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt")
    text = data.decode("utf-8", "replace")
    if "Project Gutenberg" not in text[:2000]:
        raise SystemExit(f"{book_id}: that is not a Gutenberg text file")
    dest.write_text(text, encoding="utf-8")
    return dest


def main(argv):
    shelf = json.loads(SHELF.read_text(encoding="utf-8"))
    if len(argv) >= 2 and argv[0] == "--add":
        book_id = int(argv[1])
        if any(b["id"] == book_id for b in shelf["books"]):
            print(f"{book_id} is already on the shelf"); return
        cat = json.loads(get(f"https://gutendex.com/books/?ids={book_id}"))
        if not cat["results"]:
            raise SystemExit(f"{book_id}: not in the gutendex catalogue")
        b = cat["results"][0]
        dest = download(book_id)
        entry = {
            "id": book_id,
            "title": re.sub(r"\s*:\s*\$b\s*", ": ", b["title"]),
            "author": "; ".join(a["name"] for a in b["authors"]),
            "words": word_count(dest.read_text(encoding="utf-8")),
            "file": f"books/pg{book_id}.txt",
            "downloads": b["download_count"],
        }
        shelf["books"].append(entry)
        shelf["books"].sort(key=lambda x: x["id"])
        SHELF.write_text(json.dumps(shelf, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("added", entry["title"], "—", entry["author"], f"({entry['words']} words)")
        return
    missing = [b for b in shelf["books"] if not (HERE / b["file"]).exists()]
    for b in missing:
        download(b["id"]); print("fetched", b["title"])
    print(f"{len(shelf['books'])} on the shelf, {len(missing)} fetched")


if __name__ == "__main__":
    main(sys.argv[1:])
