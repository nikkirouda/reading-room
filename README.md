# The Reading Room

A reader for public-domain classics from Project Gutenberg. One page, no accounts, no tracking.
Built for the household 2026-11-07/08; served from GitHub Pages; installable to the phone's home screen.

- **The shelf** (`shelf.json` + `books/`): texts from gutenberg.org, unaltered (licence boilerplate kept;
  the reader hides it on screen). Ids, titles and authors come from the gutendex.com catalogue — never guessed.
- **Offline**: `sw.js` keeps the page itself and every book you open on the device; "Keep the whole shelf
  offline" fetches all of them (about 62 MB). Shell requests are network-first, so updates arrive without a cache bump.
- **Your place** in each book is saved on the device as you scroll (chapter + paragraph). Places can be
  exported to a file and imported on another device (footer).
- **Catalogue search** asks gutendex.com (allows cross-site reads). Gutenberg's own servers do not, so a book
  not on the shelf is either fetched as a file and opened with "Open a Gutenberg .txt", or added to the shelf.
- **Privacy**: `noindex,nofollow` on the page; commits use the GitHub no-reply address.

## Adding a book

    python3 tools/fetch_shelf.py --add <gutenberg id>    # verifies against the catalogue, downloads the text, updates shelf.json
    git add -A && git commit -m "Shelf: <title>" && git push

## Fonts

Literata (reading) and IBM Plex Sans (interface), self-hosted in `fonts/` (Open Font License), so the page
works offline and loads nothing from third parties except the catalogue search.
