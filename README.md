# 디지털화폐 초고

윤성관이 나중에 한 권의 책으로 엮기 위해 쓰는 비공개 초고입니다. 본문은 `posts/`에 한 번만 둡니다. 블로그는 그 글을 날짜순으로 보여주고, 책은 부·장 순서로 다시 엮습니다.

조판은 [Quarto](https://quarto.org) 1.11입니다. 웹사이트, HTML 책, EPUB, PDF를 같은 원고에서 만들 수 있습니다. 이 저장소는 Quarto 1.11.9에서 렌더를 확인했습니다.

공개 배포는 하지 않습니다. GitHub Pages, `quarto publish`, 배포용 워크플로는 켜 두지 않았습니다. 저장소 공개 설정도 바꾸지 않습니다.

글의 권리는 저자에게 있습니다. 원고에 오픈소스 라이선스를 붙이지 않았습니다. `styles/chicago-notes-bibliography.csl`만 Citation Style Language 저장소의 스타일(CC BY-SA 3.0)입니다.

## 디렉터리

| 경로 | 역할 |
| --- | --- |
| `posts/` | 글. 블로그의 원천이자 책 본문 |
| `book/` | 책 프로젝트. 서문, 감사의 글, 용어집, 참고문헌, 색인 |
| `parts.yml` | 잠정 부 이름 |
| `references.bib` | 참고문헌 데이터 |
| `styles/chicago-notes-bibliography.csl` | 각주형 인용 스타일 |
| `STYLE.md` | 인용, 상태, 문체 |
| `scripts/assemble_book.py` | 글의 `part`와 `chapter`로 책 목차를 다시 씀 |
| `.github/workflows/render.yml` | 렌더 확인만. 배포 없음 |

빌드 결과인 `_site/`와 `book/_book/`은 git에 넣지 않습니다.

## 글을 쓰는 방법

1. `posts/YYYY-MM-DD-슬러그/` 디렉터리를 만듭니다. 슬러그는 소문자, 숫자, 한글, 하이픈만 씁니다.
2. `index.qmd`에 프론트매터를 적고, 본문 자리에 아래 한 줄을 둡니다.
3. 본문은 `body.md`에만 적습니다. 프론트매터를 넣지 않습니다.
4. `python3 scripts/assemble_book.py`를 실행합니다.
5. 바뀐 `book/_quarto.yml`, `book/chapters/`, `book/back-index.qmd`를 글과 함께 커밋합니다.

`index.qmd`의 모양입니다.

```yaml
---
title: "돈이란 무엇인가"
date: 2026-11-03
part: "1부 돈의 본질"
chapter: "1장 돈이란 무엇인가"
status: draft
tags:
  - 예시
  - 돈
categories:
  - "1부 돈의 본질"
description: "예시입니다. 돈의 정의를 나중에 적을 자리입니다."
---

{{< include _banner.md >}}

{{< include body.md >}}
```

`_banner.md`는 조립 스크립트가 `status`와 `tags`로 만듭니다. 상태 문장을 본문에 다시 적지 않습니다.

`part`는 `parts.yml`의 `title`과 글자까지 같아야 합니다. `chapter`는 그 부 안에서의 순서이며 `1장` 또는 `1장 제목`으로 적습니다. `categories`에는 그 `part` 값을 넣습니다. 블로그 목록의 분류로 씁니다.

인용, 각주, 색인 표제어, 예시 글의 한계는 `STYLE.md`에 있습니다.

## 상태

`status`는 다음 셋 중 하나입니다.

| 값 | 표시 | 블로그 | 책 |
| --- | --- | --- | --- |
| `draft` | 초고 | 넣음 | 넣음 |
| `review` | 검토 중 | 넣음 | 넣음 |
| `final` | 확정 | 넣음 | 넣음 |

페이지 맨 위의 배너는 프론트매터의 `status`와 `tags`로 만든 `_banner.md`입니다. `tags`에 `예시`가 있으면 자리표시자라고 함께 표시합니다. 지금 들어 있는 두 글은 모두 예시입니다. 사실, 통계, 인용문으로 읽지 않습니다. 상태를 바꾼 뒤에는 조립 스크립트를 다시 실행합니다.

확정되지 않은 글도 일단 책에 넣습니다. 빈 부에는 `book/placeholders/`의 자리표시자 장이 들어갑니다. 그 부에 글이 생기면 자리표시자는 목차에서 빠집니다.

## 잠정 부

저자가 바꿀 수 있습니다. 지금은 `parts.yml`이 다음 네 부입니다.

1. 1부 돈의 본질
2. 2부 지급결제와 금융시장인프라
3. 3부 토큰화와 디지털화폐(CBDC·스테이블코인·예금토큰)
4. 4부 중앙은행의 다음 10년

부를 고친 뒤에는 글의 `part` 값을 맞추고 `python3 scripts/assemble_book.py`를 다시 실행합니다.

책 제목은 일단 「디지털화폐 초고」, 부제는 「돈, 지급결제, 토큰화, 그리고 중앙은행」입니다. 제목은 `book/_quarto.template.yml`과 웹사이트 `_quarto.yml`에 있습니다. 템플릿을 고친 뒤에도 조립 스크립트를 다시 실행합니다. `book/_quarto.yml`은 직접 고치지 않습니다.

## 로컬에서 블로그 빌드

필요합니다.

- [Quarto](https://quarto.org/docs/get-started/) 1.11.x
- Python 3와 PyYAML (`python3-yaml` 또는 `pip install pyyaml`)

```bash
quarto render
```

결과는 `_site/index.html`입니다. 브라우저에서 그 파일을 엽니다.

## 로컬에서 책 빌드

```bash
python3 scripts/assemble_book.py
quarto render book --to html
quarto render book --to epub --no-clean
```

결과는 `book/_book/index.html`과 `book/_book/digital-currency-draft.epub`입니다. EPUB만 다시 만들 때는 `--no-clean`을 붙입니다. 이 옵션이 없으면 Quarto가 출력 폴더를 비워 HTML이 지워집니다.

HTML 책의 옆 목차에는 부가 나뉩니다. EPUB 목차는 장을 한 줄로 펼치므로, 각 장 위에 부 이름을 다시 적습니다. 서문, 감사의 글, 용어집, 참고문헌, 색인은 장 번호에 같이 들어갑니다.

웹사이트와 HTML·EPUB 책을 한 번에 만들려면 다음을 실행합니다.

```bash
scripts/build.sh
```

`python3 scripts/assemble_book.py --check`는 생성된 책 파일이 글과 어긋나면 실패합니다. GitHub Actions도 이 검사를 한 뒤 HTML과 EPUB만 렌더합니다.

### PDF

PDF는 LuaLaTeX와 한국어 글꼴이 있을 때 만듭니다. 글꼴 이름은 Noto Serif CJK KR, Noto Sans CJK KR, Noto Sans Mono CJK KR입니다. Debian 또는 Ubuntu에서는 `fonts-noto-cjk` 패키지에 들어 있습니다. Quarto의 TinyTeX를 쓸 수 있습니다.

```bash
quarto install tinytex
scripts/build.sh --pdf
```

`scripts/build.sh --pdf`는 `_quarto.yml`에 적힌 HTML, EPUB, PDF를 모두 렌더합니다. PDF만 다시 만들려면 `quarto render book --to pdf`를 실행합니다.

## 나중에 GitHub Pages로 공개할 때

지금은 하지 않습니다. 이 작업은 Pages를 켜지 않고, 저장소 공개 범위도 바꾸지 않습니다.

공개를 따로 결정할 때만 다음을 검토하면 됩니다.

1. 초고 배너, HTML의 `noindex`, 예시 글을 걷어낼지 정합니다.
2. 저장소를 공개할지 정합니다. 비공개 저장소의 GitHub Pages는 사용하는 GitHub 플랜에 따라 제한됩니다.
3. 배포 대상은 웹사이트 결과물 `_site`입니다. 책의 PDF와 EPUB은 웹사이트와 별도로 다룹니다.
4. 예시 명령은 `quarto publish gh-pages`입니다. 이 명령을 실행하면 공개 배포가 됩니다.

`.github/workflows/render.yml`에는 배포 단계가 없습니다. 렌더가 되는지만 확인합니다.

## 저작과 견해

저자는 윤성관(David), 한국은행 디지털화폐실 실장입니다. 소속은 저자를 식별하기 위한 것입니다. 이 초고는 한국은행의 공식 견해가 아닙니다.
