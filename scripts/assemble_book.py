#!/usr/bin/env python3
"""posts/ 의 프론트매터로 책 목차와 장 파일을 다시 쓴다.

생성물:
  posts/*/_banner.md
  book/placeholders/_banner.md
  book/_quarto.yml
  book/chapters/*.qmd
  book/back-index.qmd

본문은 posts/<slug>/body.md 에만 둔다. 이 스크립트는 그 파일을 고치지 않는다.
"""

from __future__ import annotations

import datetime as dt
import difflib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML이 필요합니다. python3-yaml 을 설치하거나 pip install pyyaml 을 실행하세요.", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
CHAPTERS = BOOK / "chapters"
POSTS = ROOT / "posts"
PARTS_FILE = ROOT / "parts.yml"
TEMPLATE = BOOK / "_quarto.template.yml"

STATUSES = {"draft", "review", "final"}
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
CHAPTER_RE = re.compile(r"^(\d+)장(?:\s+\S.*)?$")
SLUG_RE = re.compile(r"^[a-z0-9가-힣]+(?:-[a-z0-9가-힣]+)*$")
INCLUDE_RE = re.compile(r"\{\{<\s*include\s+body\.md\s*>\}\}")
BANNER_RE = re.compile(r"\{\{<\s*include\s+_banner\.md\s*>\}\}")
IDX_RE = re.compile(r"\[([^\]\n]+)\]\{\.idx\}")
PLACEHOLDER_CITE = "example-placeholder"


class AssembleError(Exception):
    pass


def yaml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def read_text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        raise AssembleError(f"{rel(path)}: UTF-8 BOM을 지워 주세요.")
    return data.decode("utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def split_front_matter(path: Path) -> tuple[dict, str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise AssembleError(f"{rel(path)}: 파일 맨 위가 YAML 프론트매터(---)가 아닙니다.")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssembleError(f"{rel(path)}: 프론트매터를 닫는 --- 가 없습니다.")
    raw = text[4:end]
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise AssembleError(f"{rel(path)}: YAML을 읽지 못했습니다. {exc}") from exc
    if not isinstance(meta, dict):
        raise AssembleError(f"{rel(path)}: 프론트매터가 사전이 아닙니다.")
    body = text[end + 5 :]
    return meta, body


def as_string(value, path: Path, key: str) -> str:
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise AssembleError(f"{rel(path)}: `{key}` 값이 비어 있지 않은 문자열이어야 합니다.")


def as_string_list(value, path: Path, key: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise AssembleError(f"{rel(path)}: `{key}` 는 비어 있지 않은 목록이어야 합니다.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise AssembleError(f"{rel(path)}: `{key}` 항목은 문자열이어야 합니다.")
        items.append(item.strip())
    return items


def load_parts() -> list[dict]:
    if not PARTS_FILE.exists():
        raise AssembleError("parts.yml 이 없습니다.")
    data = yaml.safe_load(read_text(PARTS_FILE))
    parts = data.get("parts") if isinstance(data, dict) else None
    if not isinstance(parts, list) or not parts:
        raise AssembleError("parts.yml 의 parts 목록이 비어 있습니다.")
    seen: set[int] = set()
    titles: set[str] = set()
    normalized = []
    for part in parts:
        if not isinstance(part, dict):
            raise AssembleError("parts.yml: 각 부는 사전이어야 합니다.")
        number = part.get("number")
        title = part.get("title")
        empty = part.get("empty")
        if not isinstance(number, int) or number < 1:
            raise AssembleError(f"parts.yml: 부 번호가 잘못되었습니다. {number!r}")
        if not isinstance(title, str) or not title.strip():
            raise AssembleError(f"parts.yml: {number}부의 제목이 없습니다.")
        if not isinstance(empty, str) or not empty.strip():
            raise AssembleError(f"parts.yml: {number}부의 empty 경로가 없습니다.")
        title = title.strip()
        empty = empty.strip()
        if number in seen:
            raise AssembleError(f"parts.yml: 부 번호 {number}이 겹칩니다.")
        if title in titles:
            raise AssembleError(f"parts.yml: 부 제목이 겹칩니다. {title}")
        empty_path = BOOK / empty
        if not empty_path.is_file():
            raise AssembleError(f"parts.yml: 자리표시자 파일이 없습니다. book/{empty}")
        seen.add(number)
        titles.add(title)
        normalized.append({"number": number, "title": title, "empty": empty})
    normalized.sort(key=lambda item: item["number"])
    return normalized


def iter_posts() -> list[dict]:
    if not POSTS.is_dir():
        raise AssembleError("posts/ 디렉터리가 없습니다.")
    posts = []
    for index in sorted(POSTS.glob("*/index.qmd")):
        if index.parent.name.startswith((".", "_")):
            continue
        meta, body = split_front_matter(index)
        posts.append(validate_post(index, meta, body))
    if not posts:
        raise AssembleError("posts/*/index.qmd 글이 없습니다.")
    return posts


def validate_post(index: Path, meta: dict, qmd_body: str) -> dict:
    required = ["title", "date", "part", "chapter", "status", "tags", "description", "categories"]
    missing = [key for key in required if key not in meta]
    if missing:
        raise AssembleError(f"{rel(index)}: 프론트매터가 없습니다. {', '.join(missing)}")

    title = as_string(meta["title"], index, "title")
    date = as_string(meta["date"], index, "date")
    part = as_string(meta["part"], index, "part")
    chapter = as_string(meta["chapter"], index, "chapter")
    status = as_string(meta["status"], index, "status")
    description = as_string(meta["description"], index, "description")
    tags = as_string_list(meta["tags"], index, "tags")
    categories = as_string_list(meta["categories"], index, "categories")

    match = DATE_RE.match(date)
    if not match:
        raise AssembleError(f"{rel(index)}: date 는 YYYY-MM-DD 입니다. 받은 값: {date}")
    try:
        dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError as exc:
        raise AssembleError(f"{rel(index)}: 없는 날짜입니다. {date}") from exc

    dirname = index.parent.name
    if not dirname.startswith(date + "-"):
        raise AssembleError(
            f"{rel(index)}: 디렉터리 이름은 `{date}-슬러그` 로 시작해야 합니다. 지금은 `{dirname}` 입니다."
        )
    slug = dirname[len(date) + 1 :]
    if not SLUG_RE.match(slug):
        raise AssembleError(
            f"{rel(index)}: 슬러그는 소문자, 숫자, 한글, 하이픈만 씁니다. 지금은 `{slug}` 입니다."
        )

    chapter_match = CHAPTER_RE.match(chapter)
    if not chapter_match:
        raise AssembleError(
            f"{rel(index)}: chapter 는 `1장` 또는 `1장 제목` 형식이어야 합니다. 받은 값: {chapter}"
        )
    chapter_number = int(chapter_match.group(1))
    if chapter_number < 1:
        raise AssembleError(f"{rel(index)}: 장 번호는 1 이상이어야 합니다.")

    if status not in STATUSES:
        raise AssembleError(
            f"{rel(index)}: status 는 draft, review, final 가운데 하나여야 합니다. 받은 값: {status}"
        )
    if part not in categories:
        raise AssembleError(f"{rel(index)}: categories 에 part 값 `{part}` 이 없습니다.")
    if not INCLUDE_RE.search(qmd_body) or not BANNER_RE.search(qmd_body):
        raise AssembleError(
            f"{rel(index)}: `{{{{< include _banner.md >}}}}` 와 `{{{{< include body.md >}}}}` 가 둘 다 있어야 합니다. 본문을 index.qmd에 직접 적지 않습니다."
        )

    body_path = index.parent / "body.md"
    if not body_path.is_file():
        raise AssembleError(f"{rel(body_path)}: 본문 파일이 없습니다.")
    body = read_text(body_path)
    if body.startswith("---"):
        raise AssembleError(f"{rel(body_path)}: body.md 에는 프론트매터를 두지 않습니다.")
    if not body.strip():
        raise AssembleError(f"{rel(body_path)}: 본문이 비어 있습니다.")
    if PLACEHOLDER_CITE in body and "예시" not in tags:
        raise AssembleError(
            f"{rel(body_path)}: `{PLACEHOLDER_CITE}` 는 예시 글에서만 씁니다. tags 에 `예시`가 없습니다."
        )

    return {
        "index": index,
        "body_path": body_path,
        "body": body,
        "title": title,
        "date": date,
        "part": part,
        "chapter": chapter,
        "chapter_number": chapter_number,
        "status": status,
        "tags": tags,
        "slug": slug,
        "dirname": dirname,
    }


def assign_parts(parts: list[dict], posts: list[dict]) -> dict[int, list[dict]]:
    by_title = {part["title"]: part for part in parts}
    grouped: dict[int, list[dict]] = {part["number"]: [] for part in parts}
    seen: dict[tuple[int, int], Path] = {}
    for post in posts:
        part = by_title.get(post["part"])
        if part is None:
            known = ", ".join(item["title"] for item in parts)
            raise AssembleError(
                f"{rel(post['index'])}: part `{post['part']}` 이 parts.yml 에 없습니다. 쓸 수 있는 값: {known}"
            )
        key = (part["number"], post["chapter_number"])
        if key in seen:
            raise AssembleError(
                f"같은 부에 장 번호가 겹칩니다. {post['part']} {post['chapter_number']}장: "
                f"{rel(seen[key])} 와 {rel(post['index'])}"
            )
        seen[key] = post["index"]
        post["part_number"] = part["number"]
        grouped[part["number"]].append(post)
    for items in grouped.values():
        items.sort(key=lambda item: (item["chapter_number"], item["date"], item["dirname"]))
    return grouped


def chapter_filename(post: dict) -> str:
    return f"{post['part_number']:02d}-{post['chapter_number']:02d}-{post['slug']}.qmd"


def banner_markdown(status: str, tags: list[str]) -> str:
    labels = {"draft": "초고", "review": "검토 중", "final": "확정"}
    kinds = {"draft": "warning", "review": "important", "final": "note"}
    label = labels.get(status, status)
    kind = kinds.get(status, "note")
    if "예시" in tags:
        title = f"예시 · {label}"
        text = "이 글은 구조 확인용 자리표시자입니다. 사실, 통계, 인용문을 담지 않습니다."
    else:
        title = label
        text = f"사실 주장은 출처와 날짜가 있는 인용만 적습니다. 상태: {status}."
    return "::: {.callout-" + kind + "}\n## " + title + "\n\n" + text + "\n:::\n"


def render_chapter(post: dict) -> str:
    tags = "\n".join(f"  - {yaml_str(tag)}" for tag in post["tags"])
    source = f"posts/{post['dirname']}/body.md"
    banner = f"../../posts/{post['dirname']}/_banner.md"
    body = f"../../posts/{post['dirname']}/body.md"
    where = f"{post['part']} · {post['chapter']}"
    return (
        "---\n"
        f"# 생성 파일. 원천: {source}\n"
        f"# scripts/assemble_book.py 가 다시 씁니다. 본문은 body.md 만 고치세요.\n"
        f"title: {yaml_str(post['title'])}\n"
        f"date: {yaml_str(post['date'])}\n"
        f"part: {yaml_str(post['part'])}\n"
        f"chapter: {yaml_str(post['chapter'])}\n"
        f"status: {yaml_str(post['status'])}\n"
        "tags:\n"
        f"{tags}\n"
        "---\n"
        "\n"
        "::: {.epub-part}\n"
        f"*{where}*\n"
        ":::\n"
        "\n"
        f"{{{{< include {banner} >}}}}\n"
        "\n"
        f"{{{{< include {body} >}}}}\n"
    )


def render_parts_block(parts: list[dict], grouped: dict[int, list[dict]]) -> str:
    lines: list[str] = []
    for part in parts:
        lines.append(f"    - part: {yaml_str(part['title'])}")
        lines.append("      chapters:")
        posts = grouped[part["number"]]
        if posts:
            for post in posts:
                lines.append(f"        - chapters/{chapter_filename(post)}")
        else:
            lines.append(f"        - {part['empty']}")
    return "\n".join(lines) + "\n"


def render_quarto_yml(parts_block: str) -> str:
    if not TEMPLATE.is_file():
        raise AssembleError("book/_quarto.template.yml 이 없습니다.")
    lines = read_text(TEMPLATE).splitlines(keepends=True)
    indexes = [i for i, line in enumerate(lines) if "@@PARTS@@" in line]
    if len(indexes) != 1:
        raise AssembleError("book/_quarto.template.yml 에 @@PARTS@@ 표시가 하나 있어야 합니다.")
    idx = indexes[0]
    return "".join(lines[:idx] + [parts_block] + lines[idx + 1 :])


def render_back_index(parts: list[dict], grouped: dict[int, list[dict]]) -> str:
    places: dict[str, list[str]] = {}
    for part in parts:
        for post in grouped[part["number"]]:
            where = f"{part['title']}, 「{post['title']}」"
            for term in IDX_RE.findall(post["body"]):
                term = term.strip()
                if not term:
                    continue
                bucket = places.setdefault(term, [])
                if where not in bucket:
                    bucket.append(where)
    lines = [
        "---",
        "title: \"색인\"",
        "# 생성 파일. scripts/assemble_book.py 가 본문의 [표제어]{.idx} 를 모아 다시 씁니다.",
        "---",
        "",
        "이 색인은 본문에 `[표제어]{.idx}`로 적은 말을 가나다순으로 모은 것이다. HTML, EPUB, PDF가 같은 목록을 쓴다. 쪽수가 달린 자동 색인은 기본 빌드에 넣지 않았다. 한국어 조판에서 자동 쪽수 색인이 아직 안정되지 않았기 때문이다.",
        "",
    ]
    if not places:
        lines.append("아직 표제어가 없다.")
        lines.append("")
    else:
        for term in sorted(places):
            where = "; ".join(places[term])
            lines.append(f"- {term} — {where}")
        lines.append("")
    return "\n".join(lines)


def expected_files(parts: list[dict], posts: list[dict]) -> dict[Path, str]:
    grouped = assign_parts(parts, posts)
    files: dict[Path, str] = {}
    for post in posts:
        files[post["index"].parent / "_banner.md"] = banner_markdown(post["status"], post["tags"])
        files[CHAPTERS / chapter_filename(post)] = render_chapter(post)
    files[BOOK / "placeholders" / "_banner.md"] = banner_markdown("draft", ["예시"])
    files[BOOK / "_quarto.yml"] = render_quarto_yml(render_parts_block(parts, grouped))
    files[BOOK / "back-index.qmd"] = render_back_index(parts, grouped)
    return files


def stale_outputs(expected: dict[Path, str]) -> list[Path]:
    stale: list[Path] = []
    if CHAPTERS.exists():
        keep = {path for path in expected if path.parent == CHAPTERS}
        stale.extend(path for path in CHAPTERS.glob("*.qmd") if path not in keep)
    if POSTS.exists():
        stale.extend(path for path in POSTS.glob("*/_banner.md") if path not in expected)
    return sorted(stale)


def show_diff(path: Path, new: str) -> None:
    old = read_text(path) if path.exists() else ""
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=rel(path) + " (저장소)",
        tofile=rel(path) + " (조립 결과)",
        n=2,
    )
    sys.stderr.writelines(diff)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    try:
        files = expected_files(load_parts(), iter_posts())
    except AssembleError as exc:
        print(f"조립 실패: {exc}", file=sys.stderr)
        return 1

    stale = stale_outputs(files)
    mismatched = []
    for path, content in files.items():
        current = read_text(path) if path.exists() else None
        if current != content:
            mismatched.append(path)

    if check:
        if mismatched or stale:
            print("책 조립 결과가 저장소와 다릅니다. python3 scripts/assemble_book.py 를 실행하고 커밋하세요.", file=sys.stderr)
            for path in mismatched:
                print(f"- 다름: {rel(path)}", file=sys.stderr)
                show_diff(path, files[path])
            for path in stale:
                print(f"- 지울 파일: {rel(path)}", file=sys.stderr)
            return 1
        print("조립 결과가 저장소와 같습니다.")
        return 0

    CHAPTERS.mkdir(parents=True, exist_ok=True)
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"씀: {rel(path)}")
    for path in stale:
        path.unlink()
        print(f"지움: {rel(path)}")
    print(f"책을 조립했습니다. 장 {sum(1 for path in files if path.parent == CHAPTERS)}개.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
