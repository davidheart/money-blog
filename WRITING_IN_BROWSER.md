# 브라우저에서 글 쓰기

컴퓨터에 Quarto나 Python을 설치하지 않아도 됩니다. 글은 브라우저에서 고쳐 커밋하고, 배너와 책 목차는 GitHub Actions가 만듭니다. 풀 리퀘스트에서는 렌더만 합니다. `main`에 들어가면, Pages 소스를 GitHub Actions로 켜 둔 뒤 블로그가 https://davidheart.github.io/money-blog/ 에 올라갑니다. 이 문서를 따른다고 저장소 공개나 Pages 설정이 바뀌지는 않습니다.

새 글의 틀은 `posts/_template/`입니다. `index.qmd`의 각 항목 위에 한글 설명이 있습니다. 이 폴더는 블로그 목록과 책에 들어가지 않습니다.

## github.dev 에서 쓰기

1. 로그인된 상태로 [https://github.dev/davidheart/money-blog](https://github.dev/davidheart/money-blog) 를 엽니다. GitHub 저장소 페이지에서 `.` 키를 눌러도 같은 편집기가 열립니다.
2. 왼쪽 파일 목록에서 `posts/_template`을 엽니다.
3. `posts` 폴더를 오른쪽 클릭하고 **New Folder…** 를 누릅니다. 이름은 `2026-11-05-slug`처럼 짓습니다. 앞은 오늘 날짜 `YYYY-MM-DD`이고, 뒤는 소문자·숫자·한글·하이픈만 씁니다.
4. 그 폴더 안에서 **New File…** 로 `index.qmd`를 만듭니다. `posts/_template/index.qmd`를 열어 전체를 복사해 붙여 넣습니다. `body.md`와 `_banner.md`도 같은 방식으로 복사합니다. `_banner.md`는 고치지 않습니다. 없어도 되며, 그러면 CI가 `status`와 `tags`로 만듭니다.
5. `index.qmd`에서 값을 고칩니다.
   - `title`: 글 제목. 책의 장 제목이 됩니다.
   - `date`: `YYYY-MM-DD`. 폴더 이름의 날짜와 같아야 합니다.
   - `part`: `parts.yml`에 있는 부 제목과 글자까지 같아야 합니다.
   - `chapter`: 그 부 안의 순서. `1장` 또는 `1장 제목`.
   - `status`: `draft`(초고), `review`(검토 중), `final`(확정) 가운데 하나.
   - `tags`: 목록. 자리표시자가 아니면 `예시`를 넣지 않습니다.
   - `categories`에는 `part`와 같은 글을 남기고, `description`은 목록에 보일 한 줄을 적습니다.
6. `body.md`에 본문을 씁니다. 템플릿 안내 문장은 지웁니다. 미리보기는 `body.md`를 연 뒤 오른쪽 위의 미리보기 아이콘을 누르거나, `Ctrl+Shift+V`(맥은 `Cmd+Shift+V`)를 누릅니다. 명령 팔레트에서 **Markdown: Open Preview** 를 골라도 됩니다.
7. 사실로 읽을 문장에는 출처와 날짜를 답니다. 자세한 규칙은 `STYLE.md`입니다.
   - 문헌으로 남길 자료는 `references.bib`에 항목을 만들고 본문에 `문장이다.[@문헌키]` 를 적습니다. 항목에는 저자, 제목, 그리고 `year` 또는 `date`가 있어야 합니다. 웹 자료이면 `url`과 `urldate`를 함께 둡니다.
   - 문헌 목록에 넣지 않는 출처는 각주입니다.

```markdown
문장이다.[^자료]

[^자료]: 기관 또는 저자, 자료 이름, 2026-11-04.
```

8. 왼쪽 **Source Control** 아이콘을 열고, 바꾼 파일을 모두 체크한 뒤 메시지를 적고 **Commit & Push** 를 누릅니다. 책 목차 파일(`book/chapters/`, `book/_quarto.yml`, `book/back-index.qmd`)은 고치지 않습니다.
9. 커밋이 올라가면 Actions의 `render`가 `python3 scripts/assemble_book.py`를 실행하고 웹사이트와 책 HTML·EPUB을 만듭니다. 명령은 직접 실행하지 않아도 됩니다. 풀 리퀘스트에서는 여기서 끝입니다. `main`에 푸시되고 Pages 소스가 GitHub Actions이면 블로그가 https://davidheart.github.io/money-blog/ 에 올라갑니다.

## github.com 에서 파일 추가하기

github.dev가 열리지 않을 때 씁니다.

1. [https://github.com/davidheart/money-blog](https://github.com/davidheart/money-blog) 를 엽니다.
2. **Add file** → **Create new file** 을 누릅니다.
3. 이름 칸에 `posts/2026-11-05-slug/index.qmd` 를 적습니다. `/` 가 폴더를 만듭니다.
4. `posts/_template/index.qmd`의 내용을 붙여 넣고 값을 고칩니다. **Commit changes** 로 저장합니다.
5. 다시 **Add file** → **Create new file** 로 `posts/2026-11-05-slug/body.md` 를 만듭니다. 편집 화면의 **Preview** 탭에서 문장을 봅니다. 안내 문장은 지우고 본문을 적습니다. 인용과 각주는 위의 7번, 그리고 `STYLE.md`와 같습니다.
6. `_banner.md`는 만들지 않아도 됩니다. CI가 만듭니다. 만들려면 템플릿의 `_banner.md`를 그대로 커밋하고, 내용은 고치지 않습니다.
7. 커밋하면 같은 `render` 워크플로가 조립과 렌더를 확인합니다. `main`에 들어간 뒤 Pages가 켜져 있으면 블로그가 갱신됩니다. 풀 리퀘스트에서는 사이트를 올리지 않습니다.
