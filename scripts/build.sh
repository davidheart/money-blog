#!/usr/bin/env bash
# 웹사이트와 책을 로컬에서 렌더한다. 배포하지 않는다.
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/assemble_book.py

echo "웹사이트를 렌더합니다."
quarto render

if [[ "${1:-}" == "--pdf" ]]; then
  echo "책 HTML, EPUB, PDF를 렌더합니다."
  quarto render book
else
  echo "책 HTML과 EPUB를 렌더합니다. PDF는 scripts/build.sh --pdf"
  quarto render book --to html
  quarto render book --to epub --no-clean
fi

echo "끝났습니다. 웹사이트: _site/index.html  책: book/_book/index.html"
