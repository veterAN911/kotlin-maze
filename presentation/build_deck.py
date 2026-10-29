#!/usr/bin/env python3
"""Генерирует автономную HTML-презентацию по проекту Maze.

Запуск:  python3 presentation/build_deck.py
Результат: presentation/index.html
Код для IDE-вставок читается из реальных файлов проекта, поэтому презентацию
можно пересобрать после изменений в коде.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

# ---------------------------------------------------------------------------
# исходники и подсветка
# ---------------------------------------------------------------------------

KEYWORDS = {
    "as", "break", "class", "companion", "const", "continue", "data", "do",
    "else", "enum", "false", "for", "fun", "if", "in", "interface", "is",
    "lateinit", "null", "object", "open", "override", "package", "private",
    "protected", "public", "return", "sealed", "super", "this", "throw", "true",
    "try", "catch", "finally", "val", "var", "when", "while", "by", "import",
    "internal", "require", "until", "downTo", "step",
}

JS_KEYWORDS = {
    "async", "await", "break", "case", "catch", "class", "const", "continue",
    "debugger", "default", "delete", "do", "else", "export", "extends", "false",
    "finally", "for", "function", "if", "import", "in", "instanceof", "let",
    "new", "null", "of", "return", "static", "super", "switch", "this", "throw",
    "true", "try", "typeof", "undefined", "var", "void", "while", "yield",
}


def read_lines(rel: str) -> list[str]:
    return (ROOT / rel).read_text(encoding="utf-8").splitlines()


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def highlight_line(line: str, lang: str = "kotlin") -> str:
    """Небольшой подсветчик Kotlin/JavaScript: комментарии, строки, ключевые слова, числа."""
    keywords = JS_KEYWORDS if lang in ("js", "html") else KEYWORDS
    out: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        if line.startswith("//", i):
            out.append(f'<span class="c">{esc(line[i:])}</span>')
            break
        ch = line[i]
        if ch in ('"', "'", "`"):
            j = i + 1
            while j < n:
                if line[j] == "\\":
                    j += 2
                    continue
                if line[j] == ch:
                    j += 1
                    break
                j += 1
            out.append(f'<span class="s">{esc(line[i:j])}</span>')
            i = j
            continue
        m = re.match(r"@[A-Za-z_][A-Za-z0-9_]*", line[i:])
        if m:
            out.append(f'<span class="a">{esc(m.group(0))}</span>')
            i += len(m.group(0))
            continue
        m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", line[i:])
        if m:
            word = m.group(0)
            if word in keywords:
                out.append(f'<span class="k">{esc(word)}</span>')
            elif word[:1].isupper():
                out.append(f'<span class="t">{esc(word)}</span>')
            else:
                out.append(esc(word))
            i += len(word)
            continue
        m = re.match(r"\d+(?:\.\d+)?", line[i:])
        if m:
            out.append(f'<span class="n">{esc(m.group(0))}</span>')
            i += len(m.group(0))
            continue
        out.append(esc(ch))
        i += 1
    return "".join(out)


def in_ranges(line_no: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a <= line_no <= b for a, b in ranges)


def code_html(
    rel: str,
    ranges: list[tuple[int, int]],
    highlights: list[tuple[int, int]] | None = None,
    strong: list[tuple[int, int]] | None = None,
    font_size: float | None = None,
) -> tuple[str, float]:
    highlights = highlights or []
    strong = strong or []
    lines = read_lines(rel)
    total = sum(b - a + 1 for a, b in ranges)
    max_len = max(
        (len(lines[i - 1]) for a, b in ranges for i in range(a, b + 1)),
        default=1,
    )
    lang = "js" if rel.endswith((".html", ".js")) else "kotlin"
    # Ограничиваем и по вертикали, и по горизонтали: иначе длинные строки
    # обрезаются справа в статичной картинке.
    fs_v = 560.0 / max(total * 1.5, 1)
    fs_w = 695.0 / max(max_len * 0.60, 1)
    fs = min(14.5, fs_v, fs_w)
    if font_size:
        fs = min(font_size, fs_w)
    fs = max(fs, 8.2)
    rows: list[str] = []
    first = True
    for a, b in ranges:
        if not first:
            rows.append('<div class="ln gap"><span class="no">⋯</span><span class="tx"></span></div>')
        first = False
        for line_no in range(a, b + 1):
            text = lines[line_no - 1]
            cls = "ln"
            if in_ranges(line_no, highlights):
                cls += " hl"
            if in_ranges(line_no, strong):
                cls += " strong"
            rows.append(
                f'<div class="{cls}" id="L{line_no}">'
                f'<span class="no">{line_no}</span>'
                f'<span class="tx">{highlight_line(text, lang)}</span></div>'
            )
    return "".join(rows), fs


# ---------------------------------------------------------------------------
# дерево проекта
# ---------------------------------------------------------------------------

PROJECT: dict = {
    "app": {
        "src/main/kotlin": {
            "domain": {
                "algorithm": {
                    "EllerMazeGenerator.kt": None,
                    "MazeSolver.kt": None,
                    "CaveGenerator.kt": None,
                    "QLearningAgent.kt": None,
                },
                "model": {
                    "Maze.kt": None,
                    "Cave.kt": None,
                },
                "service": {
                    "GameInterface.kt": None,
                    "GameService.kt": None,
                },
            },
            "database": {
                "repository": {
                    "MazeFileRepository.kt": None,
                    "CaveFileRepository.kt": None,
                },
                "mapper": {"MazeMapper.kt": None},
                "model": {"MazeFileModel.kt": None},
            },
            "ui": {
                "MazeScreen.kt": None,
                "CaveScreen.kt": None,
                "AgentScreen.kt": None,
                "MazeCanvas.kt": None,
                "Common.kt": None,
                "mapper": {"MazeUiMapper.kt": None},
            },
            "di": {"AppContainer.kt": None},
            "web": {"WebServer.kt": None},
            "App.kt": None,
            "Launcher.kt": None,
        },
        "src/test/kotlin": {
            "QLearningAgentTest.kt": None,
            "GameServiceTest.kt": None,
            "EllerTest.kt": None,
            "SolverTest.kt": None,
            "CaveGeneratorTest.kt": None,
            "CaveFileRepositoryTest.kt": None,
            "MazeFileRepositoryTest.kt": None,
            "MazeMapperTest.kt": None,
            "MazeModelTest.kt": None,
            "MazeUiMapperTest.kt": None,
            "WebServerTest.kt": None,
        },
        "src/main/resources": {
            "web/index.html": None,
            "playing_field.txt": None,
            "PlayingField.json": None,
        },
        "build.gradle.kts": None,
    },
    "Makefile": None,
    "gradle/libs.versions.toml": None,
    "buildSrc/src/main/kotlin/kotlin-jvm.gradle.kts": None,
}


def flatten_tree(node: dict, prefix: str = "") -> list[tuple[str, str, bool]]:
    rows: list[tuple[str, str, bool]] = []
    for name, child in node.items():
        path = f"{prefix}/{name}" if prefix else name
        if isinstance(child, dict):
            rows.append((path, name, True))
            rows.extend(flatten_tree(child, path))
        else:
            rows.append((path, name, False))
    return rows


FLAT_TREE = flatten_tree(PROJECT)


def layer_class(path: str) -> str:
    if "/domain/algorithm/" in path:
        return "lay-algo"
    if "/domain/model/" in path:
        return "lay-model"
    if "/src/test/" in path:
        return "lay-test"
    if "/database/" in path:
        return "lay-data"
    if "/ui/" in path or path.endswith("MazeCanvas.kt"):
        return "lay-ui"
    if "/web/" in path:
        return "lay-web"
    return ""


def count_files(node: dict) -> int:
    total = 0
    for child in node.values():
        if isinstance(child, dict):
            total += count_files(child)
        else:
            total += 1
    return total


def tree_rows(
    node: dict,
    prefix: str,
    active: str,
    *,
    expand_all: bool = False,
    collapse: set[str] | None = None,
    depth: int = 0,
    out: list[str] | None = None,
) -> list[str]:
    collapse = collapse or set()
    if out is None:
        out = []
    for name, child in node.items():
        path = f"{prefix}/{name}" if prefix else name
        is_dir = isinstance(child, dict)
        on_path = active == path or active.startswith(path + "/")
        if is_dir:
            expanded = (expand_all and path not in collapse) or on_path
            icon = "▾" if expanded else "▸"
            count = "" if expanded else f'<span class="cnt">{count_files(child)}</span>'
            cls = "tree-row dir"
            if on_path:
                cls += " in-path"
            out.append(
                f'<div class="{cls}" style="padding-left:{10 + depth * 13}px">'
                f'<span class="tw">{icon}</span><span class="fi folder"></span>'
                f'<span class="nm">{esc(name)}</span>{count}</div>'
            )
            if expanded:
                tree_rows(
                    child,
                    path,
                    active,
                    expand_all=expand_all,
                    collapse=collapse,
                    depth=depth + 1,
                    out=out,
                )
        else:
            cls = "tree-row file"
            if active == path:
                cls += " active"
            elif active.startswith(path.rsplit("/", 1)[0] + "/"):
                cls += " sibling"
            cls += " " + layer_class(path)
            out.append(
                f'<div class="{cls}" style="padding-left:{10 + depth * 13}px">'
                f'<span class="tw"></span><span class="fi kt"></span>'
                f'<span class="nm">{esc(name)}</span>'
                f'{("<span class=\"dot\"></span>" if active == path else "")}</div>'
            )
    return out


def tree_html(active: str, *, expand_all: bool = False) -> str:
    rows = tree_rows(PROJECT, "", active, expand_all=expand_all)
    return '<div class="tree-scroll"><div class="tree">' + "".join(rows) + "</div></div>"


def project_tree_html(active: str = "app/src/main/kotlin/domain/algorithm/QLearningAgent.kt") -> str:
    collapse = {"app/src/test/kotlin", "app/src/main/resources"}
    rows = tree_rows(PROJECT, "", active, expand_all=True, collapse=collapse)
    return '<div class="project-tree">' + "".join(rows) + "</div>"


# ---------------------------------------------------------------------------
# IDE-панель
# ---------------------------------------------------------------------------

def ide_panel(
    rel: str,
    ranges: list[tuple[int, int]],
    *,
    highlights: list[tuple[int, int]] | None = None,
    strong: list[tuple[int, int]] | None = None,
    active: str | None = None,
    tabs: list[str] | None = None,
    fs: float | None = None,
) -> str:
    active = active or rel
    rows, font_size = code_html(rel, ranges, highlights, strong, fs)
    filename = Path(rel).name
    total_lines = len(read_lines(rel))
    parts = rel.split("/")
    if "app" in parts:
        idx = parts.index("app")
        rel_tail = parts[idx:]
    else:
        rel_tail = parts
    crumbs = " › ".join(rel_tail[:-1])
    line_from = ranges[0][0]
    line_to = ranges[-1][1]
    lang_label = "JavaScript" if rel.endswith((".html", ".js")) else "Kotlin"
    tab_html = f'<div class="tab active">{esc(filename)}<span class="tab-dot"></span></div>'
    for t in (tabs or [])[:2]:
        tab_html += f'<div class="tab ghost">{esc(t)}</div>'
    tab_html += '<div class="tab-plus">+</div>'
    return f'''
<div class="ide" style="--fs:{font_size:.2f}px">
  <div class="ide-top">
    <div class="dots"><i></i><i></i><i></i></div>
    <div class="ide-title">Maze — IntelliJ IDEA</div>
    <div class="ide-actions"><span>⌘K</span><span>⌘⇧F</span></div>
  </div>
  <div class="ide-main">
    <aside class="ide-side">
      <div class="ide-side-head"><span>Project</span><span class="side-badge">src</span></div>
      {tree_html(active)}
    </aside>
    <section class="ide-editor">
      <div class="tabs">{tab_html}</div>
      <div class="crumbs"><span>{esc(crumbs)}</span><span class="crumb-sep">›</span><span class="crumb-file">{esc(filename)}</span><span class="crumb-lines">:{line_from}–{line_to}</span></div>
      <div class="editor"><div class="code">{rows}</div></div>
      <div class="status"><span>UTF-8</span><span>{lang_label}</span><span>LF</span><span>{total_lines} lines</span><span>Ln {line_from}, Col 1</span></div>
    </section>
  </div>
</div>
'''


# ---------------------------------------------------------------------------
# мелкие компоненты
# ---------------------------------------------------------------------------

def note(title: str, items: list[str], tone: str = "") -> str:
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="note {tone}"><h3>{title}</h3><ul>{lis}</ul></div>'


def notes(*blocks: str) -> str:
    return '<aside class="notes">' + "".join(blocks) + "</aside>"


def tag(text: str, tone: str = "cyan") -> str:
    return f'<span class="tag {tone}">{text}</span>'


def code_inline(text: str) -> str:
    return f"<code>{esc(text)}</code>"


def slide(
    title: str,
    kicker: str,
    sub: str,
    body: str,
    *,
    foot: str = "",
    cls: str = "",
) -> dict:
    return {
        "title": title,
        "kicker": kicker,
        "sub": sub,
        "body": body,
        "foot": foot,
        "cls": cls,
    }


# ---------------------------------------------------------------------------
# SVG-схемы
# ---------------------------------------------------------------------------

ARCH_SVG = r'''
<svg class="diagram" viewBox="0 0 1400 545" role="img" aria-label="Архитектура проекта">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#22d3ee"/>
    </marker>
    <marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#a78bfa"/>
    </marker>
  </defs>
  <g class="d-box ui">
    <rect x="70" y="16" width="390" height="106" rx="16"/>
    <text x="265" y="52" class="d-title">Compose Desktop</text>
    <text x="265" y="76" class="d-sub">MazeScreen · CaveScreen · AgentScreen</text>
    <text x="265" y="98" class="d-sub">Canvas 500×500 · стены 2 px</text>
  </g>
  <g class="d-box web">
    <rect x="940" y="16" width="390" height="106" rx="16"/>
    <text x="1135" y="52" class="d-title">Vue 3 SPA</text>
    <text x="1135" y="76" class="d-sub">index.html + vue.global.prod.js</text>
    <text x="1135" y="98" class="d-sub">canvas 500×500 · без алгоритмов в JS</text>
  </g>
  <g class="d-box service">
    <rect x="455" y="184" width="490" height="104" rx="16"/>
    <text x="700" y="220" class="d-title">GameInterface / GameService</text>
    <text x="700" y="244" class="d-sub">фасад: генерация · файлы · решение · агент</text>
    <text x="700" y="266" class="d-sub">экраны не знают, как устроены алгоритмы</text>
  </g>
  <g class="d-box algo">
    <rect x="55" y="356" width="620" height="112" rx="16"/>
    <text x="365" y="390" class="d-title">Алгоритмы</text>
    <text x="365" y="414" class="d-sub">EllerMazeGenerator · MazeSolver</text>
    <text x="365" y="436" class="d-sub">CaveGenerator · QLearningAgent</text>
    <text x="365" y="456" class="d-sub">только доменные модели, без UI и файлов</text>
  </g>
  <g class="d-box data">
    <rect x="725" y="356" width="620" height="112" rx="16"/>
    <text x="1035" y="390" class="d-title">Репозитории и мапперы</text>
    <text x="1035" y="414" class="d-sub">MazeFileRepository · CaveFileRepository</text>
    <text x="1035" y="436" class="d-sub">MazeMapper: MazeFileModel → Maze</text>
    <text x="1035" y="456" class="d-sub">валидация формата и границ</text>
  </g>
  <g class="d-box models">
    <rect x="455" y="500" width="490" height="36" rx="12"/>
    <text x="700" y="524" class="d-title small">Domain models: Maze · Cave · Position</text>
  </g>
  <path class="d-line" d="M265 122 L265 152 L700 152 L700 184"/>
  <path class="d-line" d="M1135 122 L1135 152 L700 152 L700 184"/>
  <path class="d-line" d="M560 288 L365 288 L365 356"/>
  <path class="d-line" d="M840 288 L1035 288 L1035 356"/>
  <path class="d-line" d="M365 468 L365 486 L700 486 L700 500"/>
  <path class="d-line" d="M1035 468 L1035 486 L700 486 L700 500"/>
  <g class="d-label"><rect x="575" y="142" width="250" height="22" rx="11"/><text x="700" y="157">вызовы через интерфейс</text></g>
  <g class="d-label violet"><rect x="756" y="164" width="238" height="22" rx="11"/><text x="875" y="179">общий Kotlin-модуль</text></g>
  <g class="d-label"><rect x="382" y="302" width="206" height="22" rx="11"/><text x="485" y="317">чистые функции</text></g>
  <g class="d-label"><rect x="860" y="302" width="244" height="22" rx="11"/><text x="982" y="317">файлы и валидация</text></g>
</svg>
'''

FLOW_SVG = r'''
<svg class="diagram flow" viewBox="0 0 1400 250" role="img" aria-label="Поток данных">
  <defs>
    <marker id="farr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#22d3ee"/>
    </marker>
  </defs>
  <g class="f-box"><rect x="30" y="48" width="190" height="92" rx="14"/><text x="125" y="80" class="f-title">Файл .txt</text><text x="125" y="104" class="f-sub">формат ТЗ</text><text x="125" y="124" class="f-sub">rows cols + матрицы</text></g>
  <g class="f-box"><rect x="252" y="48" width="190" height="92" rx="14"/><text x="347" y="80" class="f-title">parse()</text><text x="347" y="104" class="f-sub">размер 1..50</text><text x="347" y="124" class="f-sub">0/1, число строк</text></g>
  <g class="f-box"><rect x="474" y="48" width="190" height="92" rx="14"/><text x="569" y="80" class="f-title">MazeMapper</text><text x="569" y="104" class="f-sub">MazeFileModel</text><text x="569" y="124" class="f-sub">→ домен</text></g>
  <g class="f-box"><rect x="696" y="48" width="190" height="92" rx="14"/><text x="791" y="80" class="f-title">Maze</text><text x="791" y="104" class="f-sub">стены + canGo</text><text x="791" y="124" class="f-sub">0-based</text></g>
  <g class="f-box"><rect x="918" y="48" width="190" height="92" rx="14"/><text x="1013" y="80" class="f-title">Алгоритм</text><text x="1013" y="104" class="f-sub">Eller · BFS</text><text x="1013" y="124" class="f-sub">CA · Q-learning</text></g>
  <g class="f-box"><rect x="1140" y="48" width="230" height="92" rx="14"/><text x="1255" y="80" class="f-title">Canvas 500×500</text><text x="1255" y="104" class="f-sub">стены 2 px</text><text x="1255" y="124" class="f-sub">маршрут через центры</text></g>
  <path class="f-line" d="M220 94 L252 94"/><path class="f-line" d="M442 94 L474 94"/><path class="f-line" d="M664 94 L696 94"/><path class="f-line" d="M886 94 L918 94"/><path class="f-line" d="M1108 94 L1140 94"/>
  <g class="f-cap"><text x="125" y="190">сырой текст</text><text x="347" y="190">проверки</text><text x="569" y="190">изоляция формата</text><text x="791" y="190">единая модель</text><text x="1013" y="190">чистая логика</text><text x="1255" y="190">только отрисовка</text></g>
  <text x="700" y="228" class="f-bottom">Ошибка на любом шаге превращается в понятное сообщение пользователю, а не в падение приложения</text>
</svg>
'''

Q_LOOP_SVG = r'''
<svg class="diagram qloop" viewBox="0 0 560 360" role="img" aria-label="Цикл обучения агента">
  <defs>
    <marker id="qarr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#22d3ee"/>
    </marker>
  </defs>
  <g class="q-box"><rect x="20" y="70" width="200" height="120" rx="16"/><text x="120" y="108" class="q-title">Среда</text><text x="120" y="132" class="q-sub">лабиринт</text><text x="120" y="154" class="q-sub">стены · финиш</text></g>
  <g class="q-box accent"><rect x="340" y="70" width="200" height="120" rx="16"/><text x="440" y="108" class="q-title">Агент</text><text x="440" y="132" class="q-sub">Q-таблица</text><text x="440" y="154" class="q-sub">ε-greedy</text></g>
  <path class="q-line" d="M220 105 L340 105"/><text x="280" y="95" class="q-label">действие a</text>
  <path class="q-line violet" d="M340 165 L220 165"/><text x="280" y="157" class="q-label violet">s′, r</text>
  <text x="280" y="222" class="q-note">s′ — новое состояние · r — награда</text>
  <path class="q-loop" d="M440 190 C440 270 120 300 120 190" marker-end="url(#qarr)"/>
  <text x="280" y="280" class="q-label">эпизод: random start → шаги → финиш</text>
  <g class="q-formula"><rect x="70" y="300" width="420" height="42" rx="10"/><text x="280" y="327" class="q-formula-text">Q(s,a) ← Q(s,a) + α · (r + γ · max Q(s′) − Q(s,a))</text></g>
</svg>
'''

TITLE_ART = r"""
<svg viewBox="0 0 470 590" role="img" aria-label="Декоративный лабиринт и Q-таблица">
  <defs>
    <linearGradient id="tg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#22d3ee" stop-opacity=".20"/>
      <stop offset="1" stop-color="#a78bfa" stop-opacity=".10"/>
    </linearGradient>
    <filter id="tglow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect x="8" y="8" width="454" height="574" rx="28" fill="url(#tg)" stroke="rgba(148,163,184,.22)"/>
  <text x="38" y="52" fill="#67e8f9" font-family="SF Mono,Menlo,monospace" font-size="11" letter-spacing="3">Q-LEARNING · AGENT</text>
  <text x="38" y="80" fill="#8fa0b8" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="12">таблица: 4 числа на клетку</text>
  <g stroke="#22324a" stroke-width="2" opacity=".85">
    <path d="M50 128 H402 M50 192 H402 M50 256 H402 M50 320 H402 M50 384 H402 M50 448 H402"/>
    <path d="M50 128 V448 M114 128 V448 M178 128 V448 M242 128 V448 M306 128 V448 M370 128 V448 M402 128 V448"/>
  </g>
  <g stroke="#31435f" stroke-width="7" stroke-linecap="round" opacity=".9">
    <path d="M50 192 H114 M178 192 H242 M306 192 H402"/>
    <path d="M50 256 H178 M242 256 H306 M370 256 H402"/>
    <path d="M50 320 H114 M178 320 H242 M306 320 H370"/>
    <path d="M50 384 H114 M178 384 H306 M370 384 H402"/>
    <path d="M114 128 V192 M178 192 V320 M242 320 V448 M306 256 V384 M370 128 V192 M370 384 V448"/>
  </g>
  <path d="M82 160 H146 V224 H210 V288 H274 V352 H338 V416 H370" fill="none" stroke="#e53935" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" filter="url(#tglow)"/>
  <circle cx="82" cy="160" r="9" fill="#2e7d32" stroke="#07101d" stroke-width="3"/>
  <circle cx="370" cy="416" r="9" fill="#1565c0" stroke="#07101d" stroke-width="3"/>
  <g font-family="SF Mono,Menlo,monospace" font-size="10.5">
    <text x="38" y="500" fill="#7f8ba0">s = (2, 3) · a = →</text>
    <text x="238" y="500" fill="#7f8ba0">Q = 12.4</text>
    <rect x="36" y="518" width="398" height="42" rx="9" fill="rgba(7,11,20,.72)" stroke="rgba(34,211,238,.28)"/>
    <text x="52" y="545" fill="#a7f3ff">Q(s,a) ← Q + α·(r + γ·max Q′ − Q)</text>
  </g>
  <text x="38" y="566" fill="#4f6280" font-family="SF Mono,Menlo,monospace" font-size="9" letter-spacing="1.6">500 × 500 · 2 PX · 81 TEST</text>
</svg>
"""

ROUTE_SVG = r'''
<svg class="mini-route" viewBox="0 0 300 300" role="img" aria-label="Маршрут в лабиринте">
  <rect x="8" y="8" width="284" height="284" rx="10" fill="#0b1220" stroke="#2b3a55" stroke-width="2"/>
  <g stroke="#2e2e2e" stroke-width="6" stroke-linecap="round">
    <path d="M8 8 H292 M8 8 V292 M292 8 V292 M8 292 H292"/>
    <path d="M8 79 H292 M8 150 H292 M8 221 H292"/>
    <path d="M79 8 V79 M150 8 V79 M221 8 V79"/>
    <path d="M8 79 V150 M79 79 V150 M150 79 V221 M221 79 V150 M292 79 V150"/>
    <path d="M8 150 V221 M79 150 V221 M150 221 V292 M221 150 V292 M292 150 V221"/>
    <path d="M8 221 V292 M79 221 V292 M221 221 V292 M292 221 V292"/>
  </g>
  <path d="M43 43 H114 V114 H185 V185 H256" fill="none" stroke="#e53935" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="43" cy="43" r="11" fill="#2e7d32" stroke="#0b1220" stroke-width="3"/>
  <circle cx="256" cy="185" r="11" fill="#1565c0" stroke="#0b1220" stroke-width="3"/>
</svg>
'''


# ---------------------------------------------------------------------------
# слайды
# ---------------------------------------------------------------------------

SLIDES: list[dict] = []


def add(*args, **kwargs) -> None:
    SLIDES.append(slide(*args, **kwargs))


# 1. title ---------------------------------------------------------------
add(
    "",
    "",
    "",
    f'''
<div class="title-wrap">
  <div class="title-maze">{TITLE_ART}</div>
  <div class="title-kicker">MAZE · ЗАЩИТА ПРОЕКТА</div>
  <h1 class="title-big">Maze<span class="title-dot">.</span></h1>
  <p class="title-lead">Лабиринты, пещеры, BFS и Q-learning: как устроен проект, где лежит каждая часть и что говорить на защите.</p>
  <div class="hero-chips">
    {tag("Kotlin 1.9.22", "cyan")}
    {tag("Compose Desktop", "violet")}
    {tag("Ktor 2.3.13", "amber")}
    {tag("Vue 3", "green")}
    {tag("Q-learning", "red")}
    {tag("81 тест", "cyan")}
  </div>
  <div class="hero-grid">
    <div class="hero-stat"><div class="hero-num">6</div><div class="hero-cap">частей ТЗ</div></div>
    <div class="hero-stat"><div class="hero-num">4</div><div class="hero-cap">алгоритма</div></div>
    <div class="hero-stat"><div class="hero-num">81</div><div class="hero-cap">тест</div></div>
    <div class="hero-stat"><div class="hero-num">100%</div><div class="hero-cap">покрытие алгоритмов</div></div>
  </div>
  <div class="title-foot">Открывайте в браузере: стрелки ← →, пробел, <b>T</b> — оглавление, <b>F</b> — полный экран.</div>
</div>
''',
    cls="title-slide",
)

# 2. map -----------------------------------------------------------------
add(
    "Карта ТЗ: что защищаем",
    "ОБЗОР",
    "Шесть частей проекта: от модели лабиринта до веб-интерфейса. Всё, что отмечено «готово», лежит в src/maze/app/src.",
    f'''
<div class="grid-3 six">
  <div class="part-card"><div class="pnum">PART 1</div><h3>Лабиринт</h3><p>Файл, модель, загрузка, отрисовка 500×500, стены 2 px.</p><div class="part-key">1..50 · 0/1 · 2 px</div><div class="files">Maze.kt · MazeFileRepository.kt · MazeCanvas.kt</div><span class="status ok">готово</span></div>
  <div class="part-card"><div class="pnum">PART 2</div><h3>Генерация</h3><p>Идеальный лабиринт алгоритмом Эллера, без петель и изолированных зон.</p><div class="part-key">sets · merge · openings</div><div class="files">EllerMazeGenerator.kt</div><span class="status ok">готово</span></div>
  <div class="part-card"><div class="pnum">PART 3</div><h3>Решение</h3><p>BFS, кратчайший маршрут, линия 2 px через центры клеток.</p><div class="part-key">queue · previous · buildPath</div><div class="files">MazeSolver.kt · MazeCanvas.kt</div><span class="status ok">готово</span></div>
  <div class="part-card"><div class="pnum">PART 4</div><h3>Пещеры</h3><p>Клеточный автомат, шаг/авто, загрузка и сохранение.</p><div class="part-key">8 соседей · birth/death 0..7</div><div class="files">Cave.kt · CaveGenerator.kt · CaveScreen.kt</div><span class="status ok">готово</span></div>
  <div class="part-card"><div class="pnum">PART 5</div><h3>Q-learning</h3><p>Агент учится проходить лабиринт из любой точки до фиксированного финиша.</p><div class="part-key">Q(s,a) · ε-greedy · эпизоды</div><div class="files">QLearningAgent.kt · AgentScreen.kt</div><span class="status ok">готово</span></div>
  <div class="part-card"><div class="pnum">PART 6</div><h3>Web</h3><p>Vue-страница + Ktor API; генерация, файлы и решение на том же Kotlin-ядре.</p><div class="part-key">GET/POST · JSON вручную</div><div class="files">WebServer.kt · web/index.html</div><span class="status ok">готово</span></div>
</div>
<div class="banner">Ключевая идея: UI и веб — только тонкие оболочки. Вся логика в доменном слое, алгоритмы ничего не знают про Compose, Ktor и файлы.</div>
<div class="demo-strip">
  <div class="demo-pill"><b>1</b>Эллер 50×50</div>
  <div class="demo-pill"><b>2</b>BFS-маршрут</div>
  <div class="demo-pill"><b>3</b>Пещера: шаг/авто</div>
  <div class="demo-pill"><b>4</b>Агент 10×10</div>
  <div class="demo-pill"><b>5</b>Web: /api/solve</div>
</div>
''',
)

# 3. stack ---------------------------------------------------------------
add(
    "Стек и как он подключён",
    "ИНФРАСТРУКТУРА",
    "Gradle-сборка, Compose Desktop, Ktor, Vue 3 и тестовый контур. В зависимостях нет RL-библиотек, JSON-библиотек и DI-фреймворков.",
    f'''
<div class="grid-4 stack-grid">
  <div class="stack-card"><div class="stack-ico">K</div><h3>Kotlin + JVM 21</h3><div class="ver">1.9.22 / toolchain 21</div><p>Язык всего проекта. Версия Java задана в buildSrc convention-плагине.</p><div class="stack-how">toolchain(21) · buildSrc convention</div><div class="files">buildSrc/.../kotlin-jvm.gradle.kts</div></div>
  <div class="stack-card"><div class="stack-ico c">▣</div><h3>Compose Desktop</h3><div class="ver">1.6.0</div><p>Окно, вкладки, Canvas 500×500, кнопки и поля ввода.</p><div class="stack-how">compose.desktop.currentOs</div><div class="files">app/build.gradle.kts · ui/</div></div>
  <div class="stack-card"><div class="stack-ico a">⇄</div><h3>Ktor + Netty</h3><div class="ver">2.3.13</div><p>Встроенный HTTP-сервер: страница, API, JSON руками.</p><div class="stack-how">ktorServerCore + ktorServerNetty</div><div class="files">web/WebServer.kt · Launcher.kt</div></div>
  <div class="stack-card"><div class="stack-ico g">V</div><h3>Vue 3</h3><div class="ver">global prod</div><p>SPA без CDN: vue.global.prod.js лежит в ресурсах.</p><div class="stack-how">GET /vue.global.prod.js · без npm</div><div class="files">resources/web/</div></div>
  <div class="stack-card"><div class="stack-ico y">✓</div><h3>kotlin.test + JUnit 5</h3><div class="ver">BOM 5.10.2</div><p>81 тест, JUnit Platform, отчёт о покрытии JaCoCo.</p><div class="stack-how">kotlin("test") + JaCoCo от buildSrc</div><div class="files">app/src/test/kotlin</div></div>
  <div class="stack-card"><div class="stack-ico v">⚙</div><h3>Gradle 9.3.0</h3><div class="ver">wrapper + buildSrc</div><p>Мультипроект, convention-плагин, caching, toolchain.</p><div class="stack-how">gradlew + libs.versions.toml</div><div class="files">gradlew · settings.gradle.kts</div></div>
  <div class="stack-card"><div class="stack-ico c">≡</div><h3>ktlint + Dokka</h3><div class="ver">14.2.0 / 1.9.20</div><p>Стиль Kotlin и HTML-документация из KDoc (make ktlint, make dvi).</p><div class="stack-how">ktlint 14.2.0 · Dokka 1.9.20</div><div class="files">.editorconfig · build.gradle.kts</div></div>
  <div class="stack-card"><div class="stack-ico r">M</div><h3>Makefile</h3><div class="ver">GNU targets</div><p>all, install, uninstall, clean, dvi, dist, tests + run/ktlint.</p><div class="stack-how">make run/test/build/dvi/dist</div><div class="files">Makefile</div></div>
</div>
<div class="run-strip">
  <div><span class="run-label">Запуск</span><code>make run</code> или <code>./gradlew run</code> → окно + <code>http://localhost:9090</code></div>
  <div><span class="run-label">Проверка</span><code>make tests</code> · <code>./gradlew ktlintCheck</code> · <code>./gradlew jacocoTestReport</code></div>
  <div><span class="run-label">Сборка</span><code>make build</code> · <code>make install</code> · <code>make dist</code></div>
</div>
<div class="dep-flow">
  <div class="dep-node"><b>buildSrc</b><span>toolchain 21 · JUnit · JaCoCo</span></div>
  <div class="dep-arrow">→</div>
  <div class="dep-node"><b>app</b><span>Compose + Ktor + resources</span></div>
  <div class="dep-arrow">→</div>
  <div class="dep-node"><b>GameService</b><span>фасад над алгоритмами</span></div>
  <div class="dep-arrow">→</div>
  <div class="dep-node"><b>domain</b><span>Maze · Cave · Q-table</span></div>
  <div class="dep-arrow">→</div>
  <div class="dep-node"><b>UI / Web</b><span>две тонкие оболочки</span></div>
</div>
''',
)

# 4. project tree ---------------------------------------------------------
add(
    "Дерево проекта: где что искать",
    "НАВИГАЦИЯ",
    "Слева — реальная структура src/maze. Справа — что лежит в каждом слое и куда идти за ответом.",
    f'''
<div class="two-col tree-slide">
  <div class="project-tree-card">
    <div class="pt-head"><span class="pt-dot"></span><span>src/maze</span><span class="pt-badge">Kotlin</span></div>
    {project_tree_html()}
  </div>
  <aside class="notes">
    {note("Домен и алгоритмы", [
        f"{code_inline('domain/algorithm')} — 4 алгоритма: Эллер, BFS, пещера, Q-learning.",
        f"{code_inline('domain/model')} — Maze, Cave, Position: только данные и правила.",
        f"{code_inline('domain/service')} — GameInterface/GameService: фасад для UI.",
    ], "tone-cyan")}
    {note("Данные и UI", [
        f"{code_inline('database')} — парсинг/сохранение файлов и MazeMapper.",
        f"{code_inline('ui')} — три вкладки, Canvas и маппер координат.",
        f"{code_inline('web')} — Ktor-роуты; страница лежит в resources/web.",
    ], "tone-violet")}
    {note("Тесты", [
        f"{code_inline('app/src/test/kotlin')} — 11 классов, 81 тест.",
        "Алгоритмы покрыты на 100% по строкам и ветвям; UI проверяется вручную.",
    ], "tone-amber")}
    {note("Цвета в дереве", [
        '<span class="legend-dot" style="background:#6ee7b7"></span>algorithm — Эллер, BFS, пещера, агент',
        '<span class="legend-dot" style="background:#c4b5fd"></span>model — Maze, Cave, Position',
        '<span class="legend-dot" style="background:#93c5fd"></span>database — repository, mapper',
        '<span class="legend-dot" style="background:#fcd34d"></span>ui — экраны, Canvas, маппер',
    ], "tone-violet")}
    <div class="tree-links">
      <b>Куда смотреть на защите</b>
      <a href="#" onclick="show(18);return false">QLearningAgent.kt <span>слайд 19</span></a>
      <a href="#" onclick="show(10);return false">EllerMazeGenerator.kt <span>слайд 11</span></a>
      <a href="#" onclick="show(12);return false">MazeSolver.kt <span>слайд 13</span></a>
      <a href="#" onclick="show(24);return false">WebServer.kt <span>слайд 25</span></a>
    </div>
  </aside>
</div>
''',
)

# 5. architecture --------------------------------------------------------
add(
    "Архитектура: слои и изоляция",
    "КАК СВЯЗАНО",
    "Одна и та же доменная логика используется и в desktop, и в web. UI знает только интерфейс GameInterface.",
    f'''
<div class="arch-wrap">
  {ARCH_SVG}
  <div class="arch-note"><b>Сборка зависимостей:</b> AppContainer вручную создаёт репозитории, GameService и экраны; web получает тот же сервис. DI-библиотек и глобального состояния нет.</div>
  <div class="arch-legend">
    <div class="arch-card"><b>UI не знает алгоритмов</b><span>Экраны вызывают GameService, а не EllerMazeGenerator или QLearningAgent напрямую.</span></div>
    <div class="arch-card"><b>Web использует то же ядро</b><span>Ktor принимает текст лабиринта, вызывает GameService и отдаёт JSON.</span></div>
    <div class="arch-card"><b>Данные изолированы</b><span>MazeFileModel ≠ Maze; UiPoint/UiLine ≠ Position. Между ними — мапперы.</span></div>
  </div>
</div>
''',
)

# 6. data flow -----------------------------------------------------------
add(
    "Поток данных: от файла до экрана",
    "СКВОЗНОЙ ПУТЬ",
    "Один и тот же маршрут проходят лабиринт, пещера и веб-запрос: разбор → валидация → домен → алгоритм → отрисовка.",
    f'''
<div class="flow-wrap">
  <div class="flow-io">
    <div class="io-card"><b>ВХОД</b><span>.txt по ТЗ · HTTP body · поля UI</span></div>
    <div class="io-arrow">→</div>
    <div class="io-card out"><b>ВЫХОД</b><span>Maze/Cave · path · JSON · Canvas</span></div>
  </div>
  {FLOW_SVG}
  <div class="arch-legend">
    <div class="arch-card"><b>Валидация на входе</b><span>Размер 1..50, число строк/столбцов, только 0/1, сплошная внешняя граница.</span></div>
    <div class="arch-card"><b>Домен ничего не знает о файлах</b><span>Maze — это матрицы стен и canGo; формат живёт только в repository/mapper.</span></div>
    <div class="arch-card"><b>Отрисовка только по модели</b><span>Canvas не парсит текст: он получает Maze/Cave/Position и рисует.</span></div>
  </div>
  <div class="flow-examples">
    <div class="ex-card"><b>Размер вне диапазона</b><code>rows = 51</code><span>«Размеры лабиринта должны быть от 1 до 50»</span></div>
    <div class="ex-card"><b>Значение не 0/1</b><code>2</code><span>«Ожидалось 0 или 1» — файл не попадёт в домен.</span></div>
    <div class="ex-card"><b>Координата вне поля</b><code>startRow = 99</code><span>HTTP 400 + JSON с сообщением, без stack trace.</span></div>
  </div>
  <div class="flow-bottom">Один <b>parse → Maze</b> используют экран, тесты и HTTP: три входа — один домен.</div>
</div>
''',
)

# 7. part 1 model --------------------------------------------------------
add(
    "Part 1: модель лабиринта",
    "PART 1 · MAZE",
    "Maze — это размеры, две матрицы стен и два правила: canGo и openNeighbors. Матрицы хранят правую и нижнюю стенку клетки.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/model/Maze.kt",
      [(12, 39)],
      highlights=[(19, 32), (34, 39)],
      strong=[(26, 29)],
      tabs=["Cave.kt", "Position.kt"],
  )}
  {notes(
      note("Как читать матрицы", [
          f"{code_inline('verticalWalls[r][c] == 1')} — стена справа от клетки (r,c).",
          f"{code_inline('horizontalWalls[r][c]')} — стена снизу.",
          "Последний столбец и последняя строка — внешняя граница; верхнюю и левую границу дорисовывает UI.",
      ], "tone-cyan"),
      note("canGo: единственная точка проверки перехода", [
          f"{code_inline('dr/dc')} определяют направление; для каждого — своя матрица и проверка границы.",
          "Если переход не соседний или упирается в стену — false.",
          f"{code_inline('openNeighbors')} использует canGo; на нём стоят BFS и тесты.",
      ], "tone-violet"),
      note("Как это связано дальше", [
          "BFS и агент вызывают canGo, поэтому не знают о файлах и UI.",
          "MazeUiMapper переводит Position в UiPoint и линии для Canvas.",
          "MazeModelTest: 7 проверок границ и открытых соседей.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="Файл: domain/model/Maze.kt · строки 12–39",
)

# 8. part 1 load ---------------------------------------------------------
add(
    "Part 1: загрузка, парсинг, валидация",
    "PART 1 · ФАЙЛЫ",
    "Пользователь выбирает файл; repository читает текст и проверяет формат до того, как он попадёт в домен.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/database/repository/MazeFileRepository.kt",
      [(16, 35)],
      highlights=[(17, 26), (30, 32)],
      strong=[(26, 26), (30, 30)],
      tabs=["MazeMapper.kt", "MazeRepository.kt"],
  )}
  {notes(
      note("Проверки в parse()", [
          "Первая строка — ровно два целых числа.",
          f"Размеры {code_inline('1..50')}; иначе — IllegalArgumentException.",
          f"Строк в файле ровно {code_inline('1 + rows * 2')}: две матрицы.",
          "В каждой строке ровно cols значений, каждое 0 или 1.",
          "Пустые строки фильтруются, поэтому файл без разделителя тоже читается.",
      ], "tone-cyan"),
      note("Проверки в MazeMapper.toDomain", [
          "Размеры и размеры матриц совпадают.",
          f"Правая граница: {code_inline('verticalWalls[r][cols-1] == 1')}.",
          f"Нижняя граница: {code_inline('horizontalWalls[rows-1][c] == 1')}.",
          "Дырявая внешняя граница ломает canGo — лучше отловить сразу.",
      ], "tone-violet"),
      note("Контракт формата", [
          "1 строка-размер + rows×2 строк матриц, cols чисел в каждой.",
          "Битый файл не доходит до Maze — исключение ловит UI или HTTP-слой.",
          "CaveFileRepository повторяет те же проверки для пещеры.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="MazeFileRepository.kt:16–35 · MazeMapper.kt:8–20",
)

# 9. part 1 render -------------------------------------------------------
add(
    "Part 1: отрисовка 500×500 и стены 2 px",
    "PART 1 · CANVAS",
    "MazeCanvas переводит клетки в пиксели: клетка = ширина/cols, стена = 2/500 ширины поля. Маршрут рисуется через центры.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/ui/MazeCanvas.kt",
      [(60, 86)],
      highlights=[(61, 67), (69, 76), (78, 86)],
      strong=[(78, 86)],
      tabs=["MazeUiMapper.kt", "MazeScreen.kt"],
  )}
  {notes(
      note("Геометрия", [
          f"{code_inline('cellW = size.width / cols')}, {code_inline('cellH = size.height / rows')} — лабиринт занимает всё поле.",
          f"{code_inline('wallWidth = size.width * 2 / 500')} — 2 пикселя при поле 500.",
          "Поле фиксировано: 500.dp; окно может быть больше, Canvas не растягивается.",
      ], "tone-cyan"),
      note("Что рисуется", [
          "MazeUiMapper.wallLines добавляет верхнюю и левую границу, затем все правые и нижние стены.",
          "Маршрут — красная линия, стены — тёмно-серые, поле — белое: цвет отличается.",
          f"{code_inline('pathPoints')} сдвигает на +0.5 клетки, поэтому линия идёт через центры.",
      ], "tone-violet"),
      note("Где это в UI", [
          f"{code_inline('MazeScreen')} — вкладка лабиринта; {code_inline('AgentScreen')} переиспользует тот же Canvas.",
          "Клик по полю пересчитывается из пикселей в (row, col).",
      ], "tone-amber"),
  )}
</div>
''',
    foot="MazeCanvas.kt:60–86 · MazeUiMapper.pathPoints",
)

# 10. part 2 idea --------------------------------------------------------
add(
    "Part 2: алгоритм Эллера — идея",
    "PART 2 · ГЕНЕРАЦИЯ",
    "Эллер строит идеальный лабиринт построчно: клетки объединяются в множества, а стены убираются только между разными множествами.",
    f'''
<div class="eller-wrap">
  <div class="steps">
    <div class="step"><div class="step-num">01</div><div><b>Множества</b><span>Каждая клетка начинает в своём множестве. Одинаковый номер = клетки уже соединены.</span></div></div>
    <div class="step"><div class="step-num">02</div><div><b>Правые стены</b><span>Идём по строке: если соседи из разных множеств, случайно убираем стену и сливаем множества. Между своими — нельзя, иначе появится петля.</span></div></div>
    <div class="step"><div class="step-num">03</div><div><b>Проходы вниз</b><span>Случайно открываем нижние стены, но проверяем: у каждого множества должен остаться хотя бы один проход вниз.</span></div></div>
    <div class="step"><div class="step-num">04</div><div><b>Новая строка</b><span>Клетки без прохода вниз получают новые номера множеств. В последней строке просто сливаем все множества вправо.</span></div></div>
  </div>
  <div class="eller-side">
    <div class="set-demo">
      <div class="set-row"><span class="set-cell s1">A</span><span class="set-cell s1">A</span><span class="set-cell s2">B</span><span class="set-cell s2">B</span><span class="set-cell s3">C</span><span class="set-cell s3">C</span></div>
      <div class="set-arrow">убираем стену между A и B → A A A B C C</div>
      <div class="set-row"><span class="set-cell s1">A</span><span class="set-cell s1">A</span><span class="set-cell s1">A</span><span class="set-cell s2">B</span><span class="set-cell s3">C</span><span class="set-cell s3">C</span></div>
    </div>
    <div class="principle"><b>Почему идеальный</b><span>Ровно N−1 проход, нет циклов (стены рвём только между разными множествами), все клетки достижимы (каждое множество получает выход вниз, последняя строка всё сливает).</span></div>
  </div>
  <div class="eller-facts">
    <div class="eller-fact"><b>N−1</b><span>проходов ровно</span></div>
    <div class="eller-fact"><b>1</b><span>связная компонента</span></div>
    <div class="eller-fact"><b>0</b><span>циклов</span></div>
    <div class="eller-fact"><b>O(N)</b><span>доп. память под sets</span></div>
  </div>
</div>
<div class="banner">Для 1×1 алгоритм тоже работает: цикл по строкам не выполняется, возвращается одна клетка.</div>
''',
)

# 11. part 2 code --------------------------------------------------------
add(
    "Part 2: код Эллера",
    "PART 2 · КОД",
    "Главный цикл: слияние множеств справа, гарантированные проходы вниз и новые номера для клеток, которые не продолжаются.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/algorithm/EllerMazeGenerator.kt",
      [(23, 53)],
      highlights=[(26, 31), (36, 47), (50, 52)],
      strong=[(27, 30)],
      tabs=["EllerTest.kt", "Maze.kt"],
  )}
  {notes(
      note("Правые стены", [
          f"Условие {code_inline('sets[c] != sets[c+1]')} — обязательное: иначе получится петля.",
          f"{code_inline('mergeSets')} перекрашивает все клетки множества from в to.",
      ], "tone-cyan"),
      note("Нижние проходы", [
          f"{code_inline('setsWithOpening')} запоминает, у кого уже есть выход вниз.",
          "Второй проход по строке принудительно открывает стену у множеств без выхода.",
          "Это страховка от отрезанных областей.",
      ], "tone-violet"),
      note("Новая строка и последняя", [
          "Клетки с закрытой нижней стеной получают новый set id.",
          "В последней строке (строки 55–64) убираем все правые стены между разными множествами — остаётся один связный лабиринт.",
      ], "tone-amber"),
  )}
</div>
''',
    foot="EllerMazeGenerator.kt:23–53 · последняя строка: 55–64",
)

# 12. part 2 tests -------------------------------------------------------
add(
    "Part 2: почему лабиринт идеальный + тесты",
    "PART 2 · ПРОВЕРКА",
    "Тест проверяет два свойства: проходов ровно N−1 и из左上 угла достижимы все клетки. Это и есть определение идеального лабиринта.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/test/kotlin/EllerTest.kt",
      [(39, 70)],
      highlights=[(39, 40), (42, 50), (53, 70)],
      strong=[(40, 40)],
      tabs=["SolverTest.kt", "Maze.kt"],
  )}
  {notes(
      note("Определение в коде", [
          f"{code_inline('openPassages == rows*cols - 1')} — дерево, а не граф с циклами.",
          f"{code_inline('allReachable')} — BFS из (0,0) должен посетить все клетки.",
          "Оба условия вместе = идеальный лабиринт.",
      ], "tone-cyan"),
      note("Что ещё проверяется", [
          "Все размеры от 1×1 до 10×10.",
          "Размеры 0 и 51 отклоняются.",
          "Покрытие EllerMazeGenerator — 100% строк и ветвей.",
      ], "tone-violet"),
      note("Почему этого достаточно", [
          "N−1 проход + связность исключают и петли, и изолированные участки.",
          "Для 50×50 те же свойства выполняются по построению; граничный размер проверяется отдельно в других тестах.",
      ], "tone-amber"),
  )}
</div>
''',
    foot="EllerTest.kt:13–21, 39–70 · покрытие 100%",
)

# 13. part 3 BFS ---------------------------------------------------------
add(
    "Part 3: BFS-решатель",
    "PART 3 · BFS",
    "Очередь + visited + previous. BFS гарантирует кратчайший путь по числу клеток; путь собирается назад от финиша.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/algorithm/MazeSolver.kt",
      [(13, 34), (44, 55)],
      highlights=[(17, 22), (24, 33), (44, 55)],
      strong=[(26, 31)],
      tabs=["SolverTest.kt", "Maze.kt"],
  )}
  {notes(
      note("Почему BFS", [
          "Все переходы стоят одинаково — один шаг. BFS первым доходит до финиша по кратчайшему числу клеток.",
          f"{code_inline('visited')} не даёт повторно положить клетку в очередь.",
      ], "tone-cyan"),
      note("Восстановление пути", [
          f"{code_inline('previous[r][c]')} хранит, откуда пришли.",
          "Идём от финиша назад, пока не упрёмся в null (у старта предка нет), затем разворачиваем.",
      ], "tone-violet"),
      note("Границы", [
          "Старт или финиш вне поля — emptyList.",
          "Старт = финиш — список из одной клетки.",
          "Нет пути — emptyList, UI показывает «Путь не найден».",
      ], "tone-amber"),
  )}
</div>
''',
    foot="MazeSolver.kt:13–55 · тесты: SolverTest.kt",
)

# 14. part 3 render ------------------------------------------------------
add(
    "Part 3: маршрут на экране",
    "PART 3 · ОТРИСОВКА",
    "Маршрут — красная линия толщиной 2 px через центры клеток. Цвет отличается от стен и поля, как требует ТЗ.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/ui/MazeCanvas.kt",
      [(69, 86)],
      highlights=[(78, 86)],
      strong=[(79, 85)],
      tabs=["MazeUiMapper.kt", "SolverTest.kt"],
  )}
  {notes(
      note("Точки маршрута", [
          f"{code_inline('MazeUiMapper.pathPoints')}: (col + 0.5, row + 0.5) — ровно центр клетки.",
          "Линия рисуется между соседними точками; толщина та же, что у стен, — 2 px.",
          "Цвета: стены #2E2E2E, поле белое, маршрут #E53935.",
      ], "tone-cyan"),
      note("Что проверяют тесты", [
          "Известный 2×2: конкретный путь.",
          "Из середины выбирается короткий из двух маршрутов.",
          "Все размеры 1..10, старт/финиш, выход за границы, отсутствие пути.",
      ], "tone-violet"),
      ROUTE_SVG,
  )}
</div>
''',
    foot="MazeCanvas.kt:69–86 · SolverTest.kt",
)

# 15. part 4 cave model --------------------------------------------------
add(
    "Part 4: пещера — модель и соседи",
    "PART 4 · CAVE",
    "Пещера — матрица 0/1. Живая клетка — стена, мёртвая — свободно. Клетки за границей считаются живыми: это ключ к поведению автомата.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/model/Cave.kt",
      [(10, 33)],
      highlights=[(19, 33)],
      strong=[(29, 29)],
      tabs=["CaveGenerator.kt", "CaveScreen.kt"],
  )}
  {notes(
      note("Кто есть кто", [
          f"{code_inline('1')} — живая клетка (стена), {code_inline('0')} — мёртвая (свободно).",
          f"{code_inline('aliveNeighbours')} считает 8 соседей, центр пропускается.",
          f"За границей {code_inline('count += 1')} — по ТЗ внешние клетки живые.",
      ], "tone-cyan"),
      note("Следствия для краёв", [
          "У угла 5 живых соседей, у края 3, в центре 0 — поэтому края «затягивает» стенами.",
          "Если заменить 1 на 0, форма пещер станет другой; это осознанное требование ТЗ.",
      ], "tone-violet"),
      note("Почему это важно", [
          "CaveGenerator.step считает по этой функции; тесты проверяют углы, края и центр.",
      ], "tone-amber"),
  )}
</div>
''',
    foot="Cave.kt:10–33 · клетки за границей = живые",
)

# 16. part 4 step/UI -----------------------------------------------------
add(
    "Part 4: шаг автомата, UI и файлы",
    "PART 4 · UI",
    "step() считает новое поле в отдельный массив. UI даёт «Шаг» и «Авто» с задержкой N мс; файл пещеры читается и сохраняется без второй матрицы.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/algorithm/CaveGenerator.kt",
      [(29, 50)],
      highlights=[(34, 35), (37, 48)],
      strong=[(41, 46)],
      tabs=["CaveScreen.kt", "CaveFileRepository.kt"],
  )}
  {notes(
      note("Правила step", [
          f"Живая: если {code_inline('alive < deathLimit')} — умирает, иначе живёт.",
          f"Мёртвая: если {code_inline('alive > birthLimit')} — рождается. Именно строгое > для рождения.",
          "Пределы 0..7 проверяются через require.",
      ], "tone-cyan"),
      note("Двойная буферизация", [
          f"Результат пишется в {code_inline('next')}, а не в исходную пещеру.",
          "Иначе вторая половина поля считалась бы уже по изменённым данным.",
      ], "tone-violet"),
      note("UI и файлы", [
          f"{code_inline('CaveScreen')}: «Шаг» и «Авто»; {code_inline('LaunchedEffect(running, delayMs)')} делает delay(N) и step().",
          "Загрузка/сохранение: первая строка rows cols, дальше rows строк по cols чисел 0/1.",
          "15 тестов CaveGeneratorTest, покрытие 100%.",
      ], "tone-amber"),
  )}
</div>
''',
    foot="CaveGenerator.kt:29–50 · CaveScreen.kt:48–69, 86–99",
)

# 17. part 5 concepts ----------------------------------------------------
add(
    "Part 5: что такое агент и что значит «обучить»",
    "PART 5 · ПОНЯТИЯ",
    "Агент — это не нейросеть и не внешняя библиотека. Это объект с Q-таблицей: для каждой клетки четыре числа. Обучение — заполнить таблицу опытом.",
    f'''
<div class="concept-wrap">
  <div class="concept-left">
    <div class="concept-grid">
      <div class="concept-card"><div class="c-ico">S</div><h3>Состояние</h3><p>Клетка лабиринта, например (2,3). Всего rows × cols состояний.</p><div class="cc-ex">s = Position(2, 3)</div><div class="cc-ref">domain/model/Maze.kt</div></div>
      <div class="concept-card"><div class="c-ico">A</div><h3>Действие</h3><p>0 — вверх, 1 — вниз, 2 — влево, 3 — вправо. В стену нельзя.</p><div class="cc-ex">a = 3 → canGo(s, вправо)</div><div class="cc-ref">Maze.openNeighbors()</div></div>
      <div class="concept-card"><div class="c-ico">R</div><h3>Награда</h3><p>−1 за шаг, 0 за финиш. Максимум Q = минимум шагов.</p><div class="cc-ex">r = −1 · на финише r = 0</div><div class="cc-ref">trainEpisode(): FINISH_REWARD</div></div>
      <div class="concept-card"><div class="c-ico">π</div><h3>Политика</h3><p>argmax Q в текущей клетке; при равенстве — случайный выбор.</p><div class="cc-ex">a* = argmax Q(s, ·)</div><div class="cc-ref">bestAction()</div></div>
    </div>
    <div class="banner small-banner">Агент хранит <b>Q-таблицу</b> и фиксированные <b>maze + end</b>. Он не хранит маршрут — маршрут извлекается жадным проходом по Q.</div>
  </div>
  <div class="concept-right">
    {Q_LOOP_SVG}
  </div>
  <div class="concept-bottom">
    <div class="cb-k">ЧТО ЗНАЧИТ «ОБУЧЕНИЕ»</div>
    <div class="cb-t">Это не запоминание одного маршрута, а оценка действий. После каждого эпизода Q-значения сдвигаются к фактической награде; поэтому агент умеет выходить из любой стартовой клетки, а не только из той, которую видел.</div>
  </div>
</div>
''',
)

# 18. part 5 mechanics ---------------------------------------------------
add(
    "Part 5: Q-learning — формула и цикл",
    "PART 5 · МЕХАНИКА",
    "Q(s,a) — ожидаемая награда, если из состояния s пойти в a и дальше действовать оптимально. После каждого шага таблица подтягивается к цели Беллмана.",
    f'''
<div class="ql-wrap">
  <div class="ql-top">
    <div class="formula-card">
      <div class="formula-label">ОБНОВЛЕНИЕ</div>
      <div class="formula">Q(s,a) ← Q(s,a) + α · [ r + γ · max<sub>a′</sub> Q(s′,a′) − Q(s,a) ]</div>
      <div class="formula-note">На финише max Q(s′) = 0: эпизод закончился, будущего нет.</div>
    </div>
    <div class="qtable-card">
      <div class="qt-title">Q-таблица · клетка → 4 действия</div>
      <div class="qtable">
        <div class="qt-head">s</div><div class="qt-head">↑</div><div class="qt-head">↓</div><div class="qt-head">←</div><div class="qt-head">→</div>
        <div class="qt-cell">(2,3)</div><div class="qt-best">12.4</div><div>8.1</div><div>9.7</div><div>10.2</div>
        <div class="qt-cell">(2,4)</div><div class="qt-best">14.8</div><div>11.2</div><div>13.0</div><div>9.4</div>
        <div class="qt-cell">(3,3)</div><div>7.2</div><div class="qt-best">10.5</div><div>6.8</div><div>8.9</div>
      </div>
      <div class="qt-note">Зелёное — max Q. Политика агента: идти в это действие.</div>
    </div>
  </div>
  <div class="param-grid">
    <div class="param"><div class="p-k">α</div><div class="p-v">0.1</div><div class="p-l">скорость обучения</div></div>
    <div class="param"><div class="p-k">γ</div><div class="p-v">0.9</div><div class="p-l">учёт будущего</div></div>
    <div class="param"><div class="p-k">ε</div><div class="p-v">0.5 → 0.05</div><div class="p-l">исследование → использование</div></div>
    <div class="param"><div class="p-k">E</div><div class="p-v">max(50k, N·150)</div><div class="p-l">эпизоды; 50×50 → 375k</div></div>
  </div>
  <div class="episode-strip">
    <div class="ep"><b>1</b> random start</div><div class="ep-arr">→</div>
    <div class="ep"><b>2</b> ε-greedy выбор</div><div class="ep-arr">→</div>
    <div class="ep"><b>3</b> шаг + награда</div><div class="ep-arr">→</div>
    <div class="ep"><b>4</b> обновление Q</div><div class="ep-arr">→</div>
    <div class="ep"><b>5</b> до финиша / maxSteps</div>
  </div>
  <div class="example-card">
    <b>Один шаг обучения</b>
    <span>s=(2,3), a=вправо, r=−1, max Q(s′)=12.4, Q(s,a)=8.1</span>
    <code>8.1 + 0.1·(−1 + 0.9·12.4 − 8.1) = 8.306</code>
  </div>
  <div class="why-grid">
    <div class="why"><b>Почему −1 за шаг</b><span>Длинный путь суммарно хуже короткого — агент сам выбирает меньше шагов.</span></div>
    <div class="why"><b>Почему γ = 0.9</b><span>Будущая награда чуть менее важна, но видна на десятки шагов вперёд.</span></div>
    <div class="why"><b>Почему ε падает</b><span>Сначала исследовать все клетки, затем использовать найденный маршрут.</span></div>
  </div>
</div>
''',
)

# 19. part 5 training code ----------------------------------------------
add(
    "Part 5: код обучения агента",
    "PART 5 · TRAIN",
    "Один эпизод: случайный старт, шаги ε-greedy, награда, обновление Q. Ограничение maxSteps = клетки × 4 не даёт эпизоду зависнуть.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/algorithm/QLearningAgent.kt",
      [(38, 61)],
      highlights=[(43, 45), (46, 59)],
      strong=[(52, 56)],
      tabs=["QLearningAgentTest.kt", "GameService.kt"],
  )}
  {notes(
      note("Разбор строк", [
          f"{code_inline('randomStart()')} — любая клетка, кроме финиша: так агент учится из любой точки.",
          f"{code_inline('chooseAction(current, epsilon)')} — ε-greedy.",
          f"{code_inline('move')} проверяет стену; если нельзя — остаёмся на месте и получаем −1.",
      ], "tone-cyan"),
      note("Обновление", [
          f"{code_inline('reward = if (next == end) 0 else -1')}.",
          f"{code_inline('bestNext = if (next == end) 0 else q[next].max()')} — терминальное состояние.",
          f"Строка 56: {code_inline('q[s][a] = old + α·(r + γ·bestNext − old)')}.",
      ], "tone-violet"),
      note("Параметры и защита", [
          "Эпизоды: max(50 000, клетки × 150).",
          "Для 1×1 maze trainEpisode сразу выходит, иначе randomStart зациклится.",
          f"{code_inline('train(0)')} и отрицательные значения отклоняются.",
      ], "tone-amber"),
      note("Почему maxSteps", [
          "Защита от зацикливания: без лимита неверная политика кружит вечно.",
          "Лимит = клетки × 4 — с запасом больше любого простого пути.",
          "По достижении лимита эпизод обрывается, Q обновляется по последнему шагу.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="QLearningAgent.kt:38–61 · α=0.1, γ=0.9",
)

# 20. part 5 path code ---------------------------------------------------
add(
    "Part 5: как из Q-таблицы получается маршрут",
    "PART 5 · PATH",
    "После обучения маршрут не ищется заново: агент просто идёт жадно по максимальному Q. visited защищает от циклов, стена — от невалидного шага.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/algorithm/QLearningAgent.kt",
      [(63, 95)],
      highlights=[(63, 81), (90, 95)],
      strong=[(70, 75)],
      tabs=["QLearningAgentTest.kt", "AgentScreen.kt"],
  )}
  {notes(
      note("pathToEnd", [
          "Старт = финиш → [start].",
          "На каждом шаге bestAction(current); если move вернул ту же клетку (стена) или клетка уже посещена — emptyList.",
          "Проверка visited гарантирует завершение: клеток конечное число.",
      ], "tone-cyan"),
      note("bestAction", [
          f"{code_inline('values.max()')} — лучшее Q; среди равных выбирается случайное.",
          "Случайность убирает постоянное предпочтение первого действия.",
      ], "tone-violet"),
      note("Когда пути нет", [
          "Недостижимый финиш или обучение не сошлось — emptyList; UI пишет «Агент не знает выхода».",
          "Тесты покрывают недостижимый финиш, тупик, необученного агента и старт = финиш.",
      ], "tone-amber"),
      note("Граница ответственности", [
          "pathToEnd ожидает start внутри поля; UI проверяет это до вызова.",
          "Для API стоит добавить require(start in field), но ТЗ этого не требует.",
          "Тот же путь рисует MazeCanvas — отрисовка не знает, кто его построил.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="QLearningAgent.kt:63–95 · жадная политика + visited",
)

# 21. part 5 UI ----------------------------------------------------------
add(
    "Part 5: взаимодействие с обученным агентом",
    "PART 5 · UI",
    "Сценарий: загрузить файл → задать финиш → обучить в фоне → задать старт → показать маршрут. Новый лабиринт сбрасывает старого агента.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/ui/AgentScreen.kt",
      [(134, 150), (160, 172)],
      highlights=[(141, 149), (160, 171)],
      strong=[(147, 149)],
      tabs=["MazeCanvas.kt", "GameService.kt"],
  )}
  {notes(
      note("Обучение", [
          f"Финиш берётся из полей; проверка {code_inline('inMaze')}.",
          f"Обучение уходит в {code_inline('Dispatchers.Default')} — окно не замирает.",
          f"Пока идёт обучение, кнопки генерации/загрузки отключены.",
      ], "tone-cyan"),
      note("Показ маршрута", [
          f"Старт задаётся полями или кликом; {code_inline('game.agentPath(trained, from)')}.",
          "Пустой результат → понятная ошибка «Агент не знает выхода из этой клетки».",
          "Маршрут рисуется тем же MazeCanvas, что и решение BFS.",
      ], "tone-violet"),
      note("Сброс", [
          f"{code_inline('showMaze')} ставит {code_inline('agent = null')}: агент обучен на другом лабиринте и не должен использоваться.",
          "При загрузке нового файла сбрасываются path, start и ошибки.",
      ], "tone-amber"),
      note("Почему в фоне", [
          "scope.launch + withContext(Default): UI-поток остаётся отзывчивым.",
          "Пока training=true, кнопки обучения и маршрута заблокированы.",
          "Это Compose-состояние: при уходе с экрана корутина отменяется вместе с ним.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="AgentScreen.kt:134–172 · обучение в фоне",
)

# 22. part 5 isolation ---------------------------------------------------
add(
    "Part 5: изоляция данных и фиксация среды",
    "PART 5 · ИЗОЛЯЦИЯ",
    "Агент хранит собственные maze и end. GameService — единственная точка входа; UI не может подменить лабиринт у уже обученного агента.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/domain/service/GameService.kt",
      [(63, 77)],
      highlights=[(65, 72), (74, 77)],
      strong=[(69, 71)],
      tabs=["AgentScreen.kt", "GameInterface.kt"],
  )}
  {notes(
      note("Что зафиксировано", [
          f"{code_inline('QLearningAgent(maze, end)')} — оба параметра val конструктора.",
          "Q-таблица private; снаружи доступны только train() и pathToEnd().",
          "Новый maze/end = новый агент и новое обучение, старый не меняется.",
      ], "tone-cyan"),
      note("Фасад", [
          f"{code_inline('trainAgent')} создаёт и обучает агента; {code_inline('agentPath')} только делегирует.",
          "UI зависит от GameInterface, а не от QLearningAgent напрямую.",
      ], "tone-violet"),
      note("Фон и сброс", [
          f"Обучение в {code_inline('Dispatchers.Default')}; UI не блокируется.",
          f"{code_inline('AgentScreen.showMaze')} обнуляет agent при новом лабиринте.",
          "Глобального состояния нет: AppContainer создаёт один GameService, но агент живёт в состоянии экрана.",
      ], "tone-amber"),
      note("Что это гарантирует", [
          "Нельзя обучить на одном лабиринте и построить путь на другом: maze/end — поля агента.",
          "trainAgent всегда создаёт нового агента; повторный маршрут обучение не запускает.",
          "GameInterface позволяет заменить реализацию, не меняя экраны.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="GameService.kt:63–77 · QLearningAgent.kt:13–18",
)

# 23. part 5 tests -------------------------------------------------------
add(
    "Part 5: тесты и покрытие агента",
    "PART 5 · ТЕСТЫ",
    "13 тестов QLearningAgent + 3 интеграционных GameService. Покрытие модуля — 100% строк и ветвей; проверены все старты 10×10 и 20×20.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/test/kotlin/QLearningAgentTest.kt",
      [(15, 29), (32, 46)],
      highlights=[(20, 28), (38, 45)],
      strong=[(26, 27)],
      tabs=["GameServiceTest.kt", "QLearningAgent.kt"],
  )}
  {notes(
      note("Что покрыто", [
          "Все клетки 10×10 и 20×20: путь непустой, начинается в start, заканчивается в end.",
          "Маршрут не проходит через стены и не повторяет клетки.",
          "Старт = финиш, 1×1, недостижимый финиш, лабиринт без проходов, необученный агент.",
          "Детерминизм по seed, счётчик эпизодов, отказ при episodes ≤ 0.",
      ], "tone-cyan"),
      note("Интеграция с BFS", [
          f"{code_inline('GameServiceTest')} сравнивает маршрут агента с {code_inline('solveMaze')} на идеальных лабиринтах.",
          "В идеальном лабиринте путь единственный, поэтому совпадение — строгая проверка кратчайшести.",
      ], "tone-violet"),
      note("Замер", [
          "JaCoCo: QLearningAgent — 100% instruction/branch/line/method (54/54 строки, 50/50 ветвей).",
          "20×20: все 400 стартов нашли выход. 10×10 на трёх лабиринтах: маршрут из каждой клетки совпал с BFS.",
      ], "tone-amber"),
      note("Почему 20×20, а не 50×50", [
          "50×50 — 375 000 эпизодов: такой unit-тест сильно замедлил бы CI.",
          "Свойства политики не зависят от размера; 50×50 проверяется запуском.",
          "400 стартов 20×20 и 3×100 стартов 10×10 дают достаточную выборку.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="QLearningAgentTest.kt:15–46 · GameServiceTest.kt:26–46",
)

# 24. part 6 architecture ------------------------------------------------
add(
    "Part 6: веб-интерфейс",
    "PART 6 · WEB",
    "Ktor отдаёт страницу и API; Vue рисует Canvas и ходит в API. Все алгоритмы остаются на Kotlin-сервере, в JS их нет.",
    f'''
<div class="web-wrap">
  <div class="web-left">
    <div class="mini-label">Поток данных</div>
    <div class="web-box"><div class="wb-k">Browser</div><div class="wb-t">Vue 3 SPA</div><div class="wb-s">index.html · canvas 500×500 · file input</div></div>
    <div class="web-arrow">⇅ HTTP/JSON</div>
    <div class="web-box accent"><div class="wb-k">Ktor + Netty</div><div class="wb-t">WebServer.kt</div><div class="wb-s">/, /vue.global.prod.js, /api/maze, /api/solve</div></div>
    <div class="web-arrow">↓ вызов сервиса</div>
    <div class="web-box"><div class="wb-k">Same core</div><div class="wb-t">GameService</div><div class="wb-s">Eller · MazeSolver · repositories · mapper</div></div>
    <div class="web-js"><b>Чего в JS нет</b><span>Генерации, BFS и Q-learning: страница только зовёт API и рисует ответ.</span></div>
  </div>
  <div class="web-right">
    <div class="mini-label">Карта API</div>
    <div class="route-table">
      <div class="rt-row rt-head"><span>Метод</span><span>Путь</span><span>Что делает</span></div>
      <div class="rt-row"><span class="m get">GET</span><span>/</span><span>HTML-страница</span></div>
      <div class="rt-row"><span class="m get">GET</span><span>/vue.global.prod.js</span><span>Vue локально, без CDN</span></div>
      <div class="rt-row"><span class="m get">GET</span><span>/api/maze?rows&cols</span><span>Генерация; размеры clamp 1..50</span></div>
      <div class="rt-row"><span class="m post">POST</span><span>/api/maze</span><span>Разбор текста, ответ: maze + text</span></div>
      <div class="rt-row"><span class="m post">POST</span><span>/api/solve?...</span><span>BFS; 400 при ошибках</span></div>
    </div>
    <div class="mini-label" style="margin-top:2px">Один запрос «решить»</div>
    <div class="web-seq"><b>1</b> fetch POST /api/solve · body: maze text + start/end<br><b>2</b> сервер: parse → validate → BFS → JSON path<br><b>3</b> 200: path[] · 400: {{ error }} → показ ошибки</div>
    <div class="web-note">JSON собирается вручную, без библиотеки. Координаты в API — с нуля; браузер переводит 1-based → 0-based.</div>
    <div class="mini-label" style="margin-top:2px">Проверка из терминала</div>
    <div class="web-curl"><b>curl</b> -X POST 'http://localhost:9090/api/solve?startRow=0&amp;startCol=0&amp;endRow=49&amp;endCol=49' --data-binary @maze.txt</div>
  </div>
  <div class="web-caveat"><b>Объём Part 6:</b> по ТЗ веб обязан покрывать Part 1–3 — здесь загрузка, генерация Eller и BFS. Q-learning-агент доступен в desktop-приложении.</div>
</div>
''',
)

# 25. part 6 Ktor code ---------------------------------------------------
add(
    "Part 6: Ktor API — код",
    "PART 6 · SERVER",
    "Роуты тонкие: разобрали вход, вызвали GameService, отдали JSON. Ошибки парсинга/координат — 400 и сообщение.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/kotlin/web/WebServer.kt",
      [(37, 73)],
      highlights=[(40, 73), (50, 59), (62, 70)],
      strong=[(50, 59)],
      tabs=["WebServerTest.kt", "GameService.kt"],
  )}
  {notes(
      note("Почему так", [
          "Страница только рисует; генерация и BFS — на сервере.",
          "Размеры из query coercе в 1..50, чтобы нельзя было попросить гигантский лабиринт.",
          "Ответ содержит и объект maze, и text в формате ТЗ — страница может скачать файл как есть.",
      ], "tone-cyan"),
      note("Обработка ошибок", [
          f"{code_inline('parseMaze')} в try/catch → 400 с текстом.",
          "Для solve дополнительно проверяются целые координаты и попадание в поле.",
          "Все ответы — JSON; текст экранируется вручную.",
      ], "tone-violet"),
      note("Тесты", [
          "WebServerTest: 11 тестов через Ktor test host.",
          "Генерация, загрузка, решение, старт = финиш, выход за границы, битые координаты, битый файл.",
      ], "tone-amber"),
      note("Почему JSON руками", [
          "Нет kotlinx.serialization: меньше зависимостей и видно всё экранирование.",
          "textToJson экранирует кавычки, слэши и переводы строк.",
          'Ошибка всегда одного вида: 400 + {"error": "..."}',
      ], "tone-cyan"),
  )}
</div>
''',
    foot="WebServer.kt:37–73 · /api/solve: 73–99",
)

# 26. part 6 Vue code ----------------------------------------------------
add(
    "Part 6: Vue SPA — код",
    "PART 6 · CLIENT",
    "Клиент валидирует ввод, переводит координаты в 0-based, отправляет текст лабиринта и рисует ответ. Никакой логики лабиринта в JS.",
    f'''
<div class="two-col">
  {ide_panel(
      "app/src/main/resources/web/index.html",
      [(195, 227)],
      highlights=[(202, 219)],
      strong=[(214, 219)],
      tabs=["WebServer.kt", "WebServerTest.kt"],
  )}
  {notes(
      note("Что делает Vue", [
          f"{code_inline('send()')} — fetch + разбор JSON + ошибка.",
          f"{code_inline('generate/load')} — GET/POST и {code_inline('showMaze')}.",
          f"{code_inline('toggleSolution')} — проверка целых, 1-based → 0-based, POST /api/solve.",
      ], "tone-cyan"),
      note("Отрисовка", [
          f"{code_inline('draw()')}: canvas 500×500, WALL=2, стены #2E2E2E, маршрут #E53935.",
          "Точки старта/финиша рисуются даже без маршрута.",
          "Клик по canvas пересчитывает координаты с учётом масштаба.",
      ], "tone-violet"),
      note("Файлы", [
          "Загрузка: file input → text → POST /api/maze.",
          "Сохранение: Blob из text, download maze.txt.",
          "Vue лежит локально: интернет для работы не нужен.",
      ], "tone-amber"),
      note("Как открыть", [
          "Launcher выбирает свободный порт начиная с 9090 и открывает браузер.",
          "Ktor отдаёт index.html и vue.global.prod.js из resources.",
          "На защите: генерация → скачать файл → загрузить обратно → маршрут.",
      ], "tone-cyan"),
  )}
</div>
''',
    foot="resources/web/index.html:195–227 · draw(): 241–296",
)

# 27. validation ---------------------------------------------------------
add(
    "Валидация: где что проверяется",
    "КАЧЕСТВО",
    "Валидация распределена по слоям: файл, домен, UI, HTTP. Наружу всегда выходит понятное сообщение, а не stack trace.",
    f'''
<div class="val-wrap">
<div class="table-card">
  <div class="val-table">
    <div class="vt-row vt-head"><span>Слой</span><span>Где</span><span>Что проверяется</span><span>Результат</span></div>
    <div class="vt-row"><span>Файл лабиринта</span><span class="mono">MazeFileRepository</span><span>размер 1..50, ровно 1+2·rows строк, cols значений, только 0/1</span><span class="bad">IllegalArgumentException → UI error</span></div>
    <div class="vt-row"><span>Границы лабиринта</span><span class="mono">MazeMapper</span><span>правая и нижняя граница сплошные (1)</span><span class="bad">IllegalArgumentException</span></div>
    <div class="vt-row"><span>Файл пещеры</span><span class="mono">CaveFileRepository</span><span>размер 1..50, ровно 1+rows строк, cols значений, 0/1</span><span class="bad">IllegalArgumentException → UI error</span></div>
    <div class="vt-row"><span>Домен</span><span class="mono">Eller / CaveGenerator / QLearningAgent</span><span>размеры, chance 0..100, birth/death 0..7, episodes &gt; 0</span><span class="bad">require → исключение</span></div>
    <div class="vt-row"><span>Desktop UI</span><span class="mono">MazeScreen / CaveScreen / AgentScreen</span><span>целые числа, диапазоны, координаты внутри поля</span><span class="good">текст ошибки, приложение живо</span></div>
    <div class="vt-row"><span>Web server</span><span class="mono">WebServer</span><span>координаты — int, попадание в maze, тело парсится</span><span class="bad">400 + JSON error</span></div>
    <div class="vt-row"><span>Web client</span><span class="mono">index.html</span><span>целые, 1..50, координаты ≥ 1</span><span class="good">сообщение в .error</span></div>
  </div>
</div>
<div class="error-examples">
  <div class="err-card"><div class="err-k">ФАЙЛ → UI</div><div class="err-m">Число строк в файле не соответствует размеру лабиринта</div></div>
  <div class="err-card"><div class="err-k">UI → ПОЛЬЗОВАТЕЛЬ</div><div class="err-m">Старт вне лабиринта: строка 1..50, столбец 1..50</div></div>
  <div class="err-card"><div class="err-k">HTTP → 400</div><div class="err-m">{{"error":"Координаты точек должны быть целыми числами"}}</div></div>
</div>
<div class="banner">Отдельно: <b>agentPath</b> сам не проверяет выход за границы — это делает UI. Для API-устойчивости можно добавить проверку в pathToEnd (не требование ТЗ).</div>
</div>
''',
)

# 28. tests quality ------------------------------------------------------
add(
    "Тесты и качество",
    "ПРОВЕРКА",
    "81 тест в 11 классах, все проходят. Алгоритмы покрыты на 100%; UI проверяется вручную, потому что это Compose-экран.",
    f'''
<div class="quality-wrap">
  <div class="quality-left">
    <div class="cov-head">Покрытие по JaCoCo · строки / ветви</div>
    <div class="cov-list">
    <div class="cov-row"><span>EllerMazeGenerator</span><div class="bar"><i style="width:100%"></i></div><b>100%</b></div>
    <div class="cov-row"><span>MazeSolver</span><div class="bar"><i style="width:100%"></i></div><b>100%</b></div>
    <div class="cov-row"><span>CaveGenerator</span><div class="bar"><i style="width:100%"></i></div><b>100%</b></div>
    <div class="cov-row"><span>QLearningAgent</span><div class="bar"><i style="width:100%"></i></div><b>100%</b></div>
    <div class="cov-row"><span>Maze</span><div class="bar"><i style="width:100%"></i></div><b>100% lines</b></div>
    <div class="cov-row"><span>WebServer</span><div class="bar"><i style="width:100%"></i></div><b>100% lines</b></div>
    <div class="cov-row"><span>MazeFileRepository</span><div class="bar"><i style="width:100%"></i></div><b>100% lines</b></div>
    <div class="cov-row"><span>MazeUiMapper</span><div class="bar"><i style="width:100%"></i></div><b>100% lines</b></div>
    <div class="cov-row"><span>MazeMapper</span><div class="bar"><i style="width:94%"></i></div><b>94% lines</b></div>
    </div>
    <div class="cov-note">UI-слой (Compose) не входит в unit-покрытие: это декларативные экраны, их проверяем запуском приложения.</div>
  </div>
  <div class="quality-right">
    <div class="test-classes">
      <div><b>QLearningAgentTest</b><span>13</span></div>
      <div><b>CaveGeneratorTest</b><span>15</span></div>
      <div><b>WebServerTest</b><span>11</span></div>
      <div><b>MazeFileRepositoryTest</b><span>8</span></div>
      <div><b>CaveFileRepositoryTest</b><span>7</span></div>
      <div><b>MazeModelTest</b><span>7</span></div>
      <div><b>MazeUiMapperTest</b><span>6</span></div>
      <div><b>SolverTest</b><span>6</span></div>
      <div><b>GameServiceTest</b><span>3</span></div>
      <div><b>MazeMapperTest</b><span>3</span></div>
      <div><b>EllerTest</b><span>2</span></div>
    </div>
    <div class="checks">
      <div><span class="ok-dot"></span><code>./gradlew test</code> — 81/81</div>
      <div><span class="ok-dot"></span><code>./gradlew ktlintCheck</code> — чисто</div>
      <div><span class="ok-dot"></span><code>./gradlew jacocoTestReport</code> — отчёт</div>
      <div><span class="ok-dot"></span><code>make build</code> — сборка + тесты</div>
    </div>
  </div>
  <div class="quality-foot">
    <div class="qf-card"><b>450 / 450</b><span>инструкций QLearningAgent по JaCoCo</span></div>
    <div class="qf-card"><b>54 / 54 · 50 / 50</b><span>строк и ветвей QLearningAgent</span></div>
    <div class="qf-card"><b>400 / 400</b><span>стартов 20×20 дошли до финиша в тесте</span></div>
  </div>
</div>
''',
)

# 29. cheat sheet --------------------------------------------------------
add(
    "Быстрая карта: что где искать",
    "ШПАРГАЛКА",
    "Если на защите спросят «где это?» — откройте эту таблицу. Пути указаны от src/maze.",
    f'''
<div class="table-card cheat-card">
  <div class="cheat-table">
    <div class="ct-row ct-head"><span>Что ищем</span><span>Файл</span><span>Ключевое</span></div>
    <div class="ct-row"><span>Q-learning: обучение</span><span class="mono">domain/algorithm/QLearningAgent.kt</span><span>train / trainEpisode / Q-таблица</span></div>
    <div class="ct-row"><span>Маршрут агента</span><span class="mono">domain/algorithm/QLearningAgent.kt</span><span>pathToEnd / bestAction / move</span></div>
    <div class="ct-row"><span>Экран агента</span><span class="mono">ui/AgentScreen.kt</span><span>финиш → обучение → старт → маршрут</span></div>
    <div class="ct-row"><span>Фасад</span><span class="mono">domain/service/GameService.kt</span><span>trainAgent / agentPath / solveMaze</span></div>
    <div class="ct-row"><span>Генерация Эллера</span><span class="mono">domain/algorithm/EllerMazeGenerator.kt</span><span>sets / mergeSets / openings</span></div>
    <div class="ct-row"><span>BFS</span><span class="mono">domain/algorithm/MazeSolver.kt</span><span>queue / previous / buildPath</span></div>
    <div class="ct-row"><span>Пещера</span><span class="mono">domain/algorithm/CaveGenerator.kt</span><span>random / step</span></div>
    <div class="ct-row"><span>Файлы</span><span class="mono">database/repository/*</span><span>parse / save / toText</span></div>
    <div class="ct-row"><span>Отрисовка</span><span class="mono">ui/MazeCanvas.kt</span><span>500×500 / 2 px / path</span></div>
    <div class="ct-row"><span>Веб-API</span><span class="mono">web/WebServer.kt</span><span>GET/POST /api/maze, /api/solve</span></div>
    <div class="ct-row"><span>Веб-страница</span><span class="mono">resources/web/index.html</span><span>Vue 3 + canvas</span></div>
    <div class="ct-row"><span>DI / сборка</span><span class="mono">di/AppContainer.kt · build.gradle.kts</span><span>composition root / зависимости</span></div>
    <div class="ct-row"><span>Тесты</span><span class="mono">app/src/test/kotlin</span><span>11 классов, 81 тест</span></div>
  </div>
</div>
''',
)

# 30. Q&A ----------------------------------------------------------------
qa = [
    ("Почему Q-learning, а не BFS?", "ТЗ требует RL. Агент учится по наградам; BFS — только эталон в тестах и отдельный решатель Part 3."),
    ("Как гарантируется кратчайший путь?", "Шаг −1, финиш 0 → максимизация Q = минимизация шагов. На 10×10 маршрут сверен с BFS; на 20×20 все 400 стартов нашли выход."),
    ("Почему старт случайный?", "Чтобы покрыть все состояния: требование «из любой начальной точки». В тестах проверены все клетки."),
    ("Что если финиш недостижим?", "Обучение не падает; pathToEnd возвращает пустой список, UI пишет ошибку. Есть отдельный тест."),
    ("Почему таблица, а не нейросеть?", "Дискретное пространство до 50×50, 4 действия. Таблица проще, детерминированнее и не требует RL-библиотек."),
    ("Как фиксируется лабиринт и финиш?", "Оба — val в конструкторе QLearningAgent. Новый лабиринт в UI сбрасывает агента; переобучение создаёт нового."),
    ("Где валидация?", "Файл — repository/mapper; UI — экраны; HTTP — WebServer (400); домен — require. См. отдельный слайд."),
    ("Как связаны desktop и web?", "Оба идут через GameInterface/GameService. Веб не дублирует алгоритмы: JS только рисует и вызывает API."),
    ("Почему Эллер даёт идеальный лабиринт?", "N−1 проход, стены рвём только между разными множествами (нет петель), у каждого множества есть выход вниз (нет изоляции)."),
    ("Как считаются клетки за границей пещеры?", "Они живые: aliveNeighbours добавляет 1 за каждую клетку вне поля. Отсюда 5 соседей у угла и 3 у края."),
]
qa_cards = "".join(
    f'<div class="qa-card"><div class="qa-q">{i + 1}. {q}</div><div class="qa-a">{a}</div></div>'
    for i, (q, a) in enumerate(qa)
)
add(
    "Вопросы, которые могут задать",
    "Q&A",
    "Короткие ответы, которые стоит держать в голове. Если нужен код — вернитесь к слайду с этим файлом.",
    f'<div class="qa-grid">{qa_cards}</div>',
)

# 31. final --------------------------------------------------------------
add(
    "Что запомнить",
    "ИТОГ",
    "Одна страница, которая остаётся в голове после защиты.",
    f'''
<div class="final-grid">
  <div class="final-card"><div class="f-num">6</div><div class="f-t">частей ТЗ</div><div class="f-s">лабиринт · генерация · решение · пещеры · агент · web</div></div>
  <div class="final-card"><div class="f-num">4</div><div class="f-t">алгоритма</div><div class="f-s">Эллер · BFS · клеточный автомат · Q-learning</div></div>
  <div class="final-card"><div class="f-num">81</div><div class="f-t">тест</div><div class="f-s">11 классов · все проходят · ktlint чисто</div></div>
  <div class="final-card"><div class="f-num">100%</div><div class="f-t">покрытие алгоритмов</div><div class="f-s">Eller · BFS · Cave · QLearningAgent</div></div>
</div>
<div class="final-formula">
  <div class="ff-left">
    <div class="ff-k">Формула, которую спросят</div>
    <div class="ff-eq">Q(s,a) ← Q(s,a) + α · [ r + γ · max Q(s′) − Q(s,a) ]</div>
    <div class="ff-sub">α = 0.1 · γ = 0.9 · ε: 0.5 → 0.05 · 375 000 эпизодов для 50×50</div>
  </div>
  <div class="ff-right">
    <div class="ff-k">Что сказать одной фразой</div>
    <div class="ff-line">«Агент — это Q-таблица на 4 числа на клетку. Он учится эпизодами из случайных стартов, получает −1 за шаг и 0 за финиш, а маршрут потом строится жадно по максимальному Q.»</div>
  </div>
</div>
<div class="final-demo">
  <div class="fd-card"><b>Что показать</b><span><code>make run</code> → вкладки «Лабиринт», «Пещера», «Агент»; затем Web.</span></div>
  <div class="fd-card"><b>Что сказать</b><span>6 частей, 4 алгоритма, 81 тест. Агент обучается сам — без RL-библиотек.</span></div>
  <div class="fd-card"><b>Куда открыть</b><span><code>QLearningAgent.kt</code> → <code>AgentScreen.kt</code> → <code>WebServer.kt</code>.</span></div>
</div>
<div class="final-bottom">
  <div class="final-links">
    <span>Открыть код:</span> <code>src/maze/app/src/main/kotlin</code>
    <span>·</span> <span>Тесты:</span> <code>src/maze/app/src/test/kotlin</code>
    <span>·</span> <span>Запуск:</span> <code>make run</code>
  </div>
  <div class="thanks">
    <div class="th-title">Спасибо за внимание</div>
    <div class="th-sub">Готов показать код, тесты и обучение агента.<br>Вопросы — по любому слайду.</div>
  </div>
</div>
''',
    cls="final-slide",
)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = r"""
:root{
  --bg:#070b14;
  --bg2:#0b1220;
  --panel:#101a2e;
  --panel2:#131f37;
  --line:rgba(148,163,184,.18);
  --text:#e8eef8;
  --muted:#94a3b8;
  --cyan:#22d3ee;
  --violet:#a78bfa;
  --amber:#fbbf24;
  --green:#34d399;
  --red:#fb7185;
  --blue:#60a5fa;
  --mono:"SF Mono",Menlo,Monaco,Consolas,"Liberation Mono",monospace;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:#05080f;color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,Arial,sans-serif;overflow:hidden}
body{display:flex;align-items:center;justify-content:center}
#deckbar{position:fixed;top:0;left:0;right:0;height:44px;z-index:40;display:flex;align-items:center;gap:14px;padding:0 20px;background:rgba(8,13,24,.82);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);font-size:12px;color:var(--muted)}
#deckbar .brand{font-weight:800;letter-spacing:.16em;color:#fff;font-size:12px}
#deckbar .pill{display:inline-flex;align-items:center;gap:6px;padding:3px 9px;border:1px solid var(--line);border-radius:999px;background:rgba(148,163,184,.06);color:#cbd5e1}
#deckbar .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green)}
#deckbar .spacer{flex:1}
#deckbar button{appearance:none;border:1px solid var(--line);background:rgba(148,163,184,.08);color:#dbe5f3;font:inherit;font-size:11px;padding:5px 10px;border-radius:8px;cursor:pointer}
#deckbar button:hover{background:rgba(148,163,184,.16)}
#viewport{position:absolute;inset:44px 0 0 0;display:flex;align-items:center;justify-content:center}
.deck{width:1600px;height:900px;position:relative;transform-origin:center center;flex:0 0 auto}
.slide{position:absolute;inset:0;display:none;flex-direction:column;overflow:hidden;background:
  radial-gradient(1100px 620px at 92% -8%, rgba(34,211,238,.10), transparent 62%),
  radial-gradient(900px 540px at -6% 108%, rgba(167,139,250,.10), transparent 60%),
  linear-gradient(180deg,#0a1120 0%,#070c16 100%);
}
.slide::before{content:"";position:absolute;inset:0;pointer-events:none;background-image:
  linear-gradient(rgba(148,163,184,.035) 1px, transparent 1px),
  linear-gradient(90deg, rgba(148,163,184,.035) 1px, transparent 1px);
  background-size:42px 42px;mask-image:radial-gradient(circle at 50% 40%, #000 0%, transparent 78%)}
.slide.active{display:flex;animation:fade .28s ease}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.slide-inner{position:relative;z-index:1;display:flex;flex-direction:column;height:100%;padding:46px 64px 28px}
.slide-head{flex:0 0 auto;margin-bottom:16px}
.kicker{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--cyan);font-weight:800}
h1{font-size:42px;line-height:1.06;letter-spacing:-.025em;margin:10px 0 6px;max-width:1360px}
.sub{font-size:15.5px;line-height:1.45;color:var(--muted);max-width:1300px;margin:0}
.content{flex:1;min-height:0;display:flex;flex-direction:column;gap:14px}
.slide-foot{flex:0 0 22px;display:flex;align-items:flex-end;justify-content:space-between;gap:20px;color:#5f6d82;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.pageno{font-family:var(--mono);color:#93a4bd;letter-spacing:.04em}
.two-col{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1.66fr) minmax(380px,.74fr);gap:22px;width:100%}
.one-col{width:100%;min-height:0}
.tag{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:999px;font-size:10.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;border:1px solid transparent}
.tag.cyan{background:rgba(34,211,238,.10);color:#67e8f9;border-color:rgba(34,211,238,.25)}
.tag.violet{background:rgba(167,139,250,.10);color:#c4b5fd;border-color:rgba(167,139,250,.25)}
.tag.amber{background:rgba(251,191,36,.10);color:#fcd34d;border-color:rgba(251,191,36,.25)}
.tag.green{background:rgba(52,211,153,.10);color:#6ee7b7;border-color:rgba(52,211,153,.25)}
.tag.red{background:rgba(251,113,133,.10);color:#fda4af;border-color:rgba(251,113,133,.25)}
code{font-family:var(--mono);font-size:.92em;color:#d9e6f7;background:rgba(148,163,184,.10);padding:1px 5px;border-radius:5px}
b{color:#fff}

/* title */
.title-slide .slide-inner{justify-content:center;padding:64px 84px}
.title-kicker{font-size:12px;letter-spacing:.28em;color:var(--cyan);font-weight:900}
.title-big{font-size:104px;line-height:.9;letter-spacing:-.06em;margin:16px 0 18px;max-width:none}
.title-dot{color:var(--cyan)}
.title-lead{font-size:21px;line-height:1.42;color:#b6c4d8;max-width:850px;margin:0}
.hero-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:24px}
.hero-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:34px;max-width:900px}
.hero-stat{border:1px solid var(--line);background:linear-gradient(180deg,rgba(19,31,55,.8),rgba(13,21,38,.75));border-radius:16px;padding:18px 20px}
.hero-num{font-size:36px;font-weight:900;letter-spacing:-.04em;color:#fff;font-family:var(--mono)}
.hero-cap{color:var(--muted);font-size:12px;margin-top:2px}
.title-foot{margin-top:34px;color:#7c8ba1;font-size:12px}

/* map cards */
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.six{width:100%;flex:1;grid-template-rows:auto auto;align-content:center}
.part-card{position:relative;border:1px solid var(--line);border-radius:16px;padding:17px 18px 16px;background:linear-gradient(180deg,rgba(19,31,55,.82),rgba(13,21,38,.72));min-height:180px;display:flex;flex-direction:column;justify-content:center}
.pnum{font-family:var(--mono);font-size:10px;letter-spacing:.18em;color:var(--cyan);font-weight:800}
.part-card h3{margin:6px 0 6px;font-size:20px}
.part-card p{margin:0;color:#aebbd0;font-size:12.6px;line-height:1.42}
.part-key{margin-top:11px;padding-top:8px;border-top:1px dashed rgba(148,163,184,.16);font-family:var(--mono);font-size:9.6px;color:#8fa0b8}
.part-card .files{margin-top:16px;padding-top:0;font-family:var(--mono);font-size:9.8px;line-height:1.5;color:#7dd3fc;word-break:break-word}
.status{position:absolute;right:12px;top:13px;font-size:9px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:3px 7px;border-radius:999px}
.status.ok{color:#6ee7b7;background:rgba(52,211,153,.10);border:1px solid rgba(52,211,153,.25)}
.banner{margin-top:14px;border:1px solid rgba(34,211,238,.22);background:linear-gradient(90deg,rgba(34,211,238,.08),rgba(167,139,250,.06));border-radius:12px;padding:11px 15px;color:#b9c9dd;font-size:12.5px;line-height:1.45}
.small-banner{margin-top:12px}

/* stack */
.stack-grid{grid-template-columns:repeat(4,1fr);align-items:stretch;flex:1;grid-template-rows:auto auto;align-content:center}
.stack-card{border:1px solid var(--line);border-radius:14px;background:linear-gradient(180deg,rgba(19,31,55,.76),rgba(13,21,38,.70));padding:18px 16px 36px;min-height:150px;position:relative;display:flex;flex-direction:column;justify-content:flex-start}
.stack-ico{width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-weight:900;font-size:13px;background:rgba(34,211,238,.12);color:#67e8f9;border:1px solid rgba(34,211,238,.22)}
.stack-ico.c{background:rgba(96,165,250,.12);color:#93c5fd;border-color:rgba(96,165,250,.22)}
.stack-ico.a{background:rgba(251,191,36,.12);color:#fcd34d;border-color:rgba(251,191,36,.22)}
.stack-ico.g{background:rgba(52,211,153,.12);color:#6ee7b7;border-color:rgba(52,211,153,.22)}
.stack-ico.y{background:rgba(167,139,250,.12);color:#c4b5fd;border-color:rgba(167,139,250,.22)}
.stack-ico.v{background:rgba(251,113,133,.12);color:#fda4af;border-color:rgba(251,113,133,.22)}
.stack-ico.r{background:rgba(148,163,184,.12);color:#cbd5e1;border-color:rgba(148,163,184,.22)}
.stack-card h3{font-size:14px;margin:9px 0 2px}
.stack-card .ver{font-family:var(--mono);font-size:10px;color:var(--cyan);letter-spacing:.02em}
.stack-card p{font-size:12.1px;line-height:1.42;color:#aab8cc;margin:7px 0 0}
.stack-how{margin-top:9px;font-family:var(--mono);font-size:9.5px;line-height:1.4;color:#7dd3fc;word-break:break-word}
.stack-card .files{position:absolute;left:14px;right:14px;bottom:10px;font-family:var(--mono);font-size:9.2px;color:#7787a0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.run-strip{margin-top:12px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.run-strip>div{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.6);padding:8px 10px;font-size:10.5px;color:#aab8cc}
.run-label{display:block;font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);font-weight:800;margin-bottom:3px}
.run-strip code{font-size:10px}

/* project tree */
.tree-slide{grid-template-columns:minmax(0,1.12fr) minmax(400px,.88fr)}
.project-tree-card{border:1px solid rgba(148,163,184,.22);border-radius:14px;background:#181a1f;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.35);min-height:0}
.pt-head{height:32px;display:flex;align-items:center;gap:8px;padding:0 12px;background:#2b2d30;border-bottom:1px solid #111;font-family:var(--mono);font-size:10.5px;color:#c7cbd3}
.pt-dot{width:8px;height:8px;border-radius:50%;background:#22d3ee;box-shadow:0 0 8px #22d3ee}
.pt-badge{margin-left:auto;font-size:9px;color:#9aa4b2;border:1px solid #3a3d42;border-radius:4px;padding:1px 5px}
.project-tree{padding:6px 0;font-family:var(--mono);font-size:9.9px;line-height:1.2;overflow:hidden}
.project-tree .tree-row{height:15.6px}
.project-tree .tree-row .nm{font-size:9.7px}
.project-tree .tree-row.active{background:#2e436e}
.project-tree .tree-row.lay-algo .nm{color:#6ee7b7}
.project-tree .tree-row.lay-model .nm{color:#c4b5fd}
.project-tree .tree-row.lay-data .nm{color:#93c5fd}
.project-tree .tree-row.lay-ui .nm{color:#fcd34d}
.project-tree .tree-row.lay-web .nm{color:#f0abfc}
.project-tree .tree-row.lay-test .nm{color:#fda4af}

/* IDE */
.ide{height:100%;min-height:0;display:flex;flex-direction:column;border-radius:14px;overflow:hidden;border:1px solid rgba(148,163,184,.24);background:#1e1f22;box-shadow:0 22px 60px rgba(0,0,0,.45);font-family:var(--mono);position:relative}
.ide::after{content:"IDE-вид · активный файл подсвечен в дереве";position:absolute;top:38px;right:12px;font-size:8.5px;letter-spacing:.06em;color:#6b7280;background:rgba(30,31,34,.86);border:1px solid #2f3238;border-radius:999px;padding:2px 7px;pointer-events:none}
.ide-top{height:29px;flex:0 0 29px;display:flex;align-items:center;gap:10px;padding:0 11px;background:#2b2d30;border-bottom:1px solid #111;color:#8f939b;font-size:10px}
.dots{display:flex;gap:5px}
.dots i{width:8px;height:8px;border-radius:50%;display:block}
.dots i:nth-child(1){background:#ff5f57}.dots i:nth-child(2){background:#febc2e}.dots i:nth-child(3){background:#28c840}
.ide-title{font-size:10px;color:#b9bdc5}
.ide-actions{margin-left:auto;display:flex;gap:12px;color:#7c8089;font-size:9px}
.ide-main{flex:1;min-height:0;display:grid;grid-template-columns:236px minmax(0,1fr)}
.ide-side{min-height:0;background:#181a1f;border-right:1px solid #111;overflow:hidden;padding:6px 0;font-size:10.8px}
.ide-side-head{height:24px;display:flex;align-items:center;justify-content:space-between;padding:0 11px;color:#7c8089;font-size:9px;letter-spacing:.12em;text-transform:uppercase}
.side-badge{font-size:8px;color:#6f7a8b;border:1px solid #34373d;border-radius:4px;padding:0 4px}
.tree-scroll{height:calc(100% - 24px);overflow:hidden}
.tree{display:flex;flex-direction:column}
.tree-row{height:18px;display:flex;align-items:center;gap:5px;color:#c7cbd3;white-space:nowrap;padding-right:8px;font-size:10.4px}
.tree-row.in-path{color:#e5e7eb}
.tree-row.sibling{color:#8e96a3}
.tree-row.active{background:#2e436e;color:#fff;box-shadow:inset 3px 0 0 var(--cyan)}
.tree-row .tw{width:9px;flex:0 0 9px;color:#6b7280;font-size:8px}
.tree-row .fi{width:8px;height:8px;border-radius:2px;flex:0 0 8px}
.tree-row .fi.folder{background:#5b6b86;border-radius:2px;box-shadow:0 0 0 1px rgba(255,255,255,.06) inset}
.tree-row .fi.kt{background:#7f8ea8;transform:rotate(45deg);border-radius:1px;width:6px;height:6px}
.tree-row.active .fi.kt{background:#67e8f9}
.tree-row .nm{overflow:hidden;text-overflow:ellipsis}
.tree-row .cnt{margin-left:auto;color:#5f6672;font-size:8.5px}
.tree-row .dot{width:5px;height:5px;border-radius:50%;background:var(--cyan);margin-left:auto;box-shadow:0 0 7px var(--cyan)}
.tree-row.lay-algo .nm{color:#8ee7b4}.tree-row.lay-model .nm{color:#c4b5fd}.tree-row.lay-data .nm{color:#93c5fd}.tree-row.lay-ui .nm{color:#fcd34d}.tree-row.lay-web .nm{color:#f0abfc}.tree-row.lay-test .nm{color:#fda4af}
.ide-editor{min-width:0;min-height:0;display:flex;flex-direction:column;background:#1e1f22}
.tabs{height:31px;flex:0 0 31px;display:flex;align-items:flex-end;padding:0 8px;background:#1e1f22;border-bottom:1px solid #111;overflow:hidden}
.tab{height:26px;display:flex;align-items:center;gap:7px;padding:0 12px;background:#2b2d30;color:#c7cbd3;font-size:10.4px;border-radius:6px 6px 0 0;margin-right:2px;white-space:nowrap}
.tab.active{background:#1e1f22;color:#fff;box-shadow:inset 0 -2px 0 var(--cyan)}
.tab.ghost{background:#24262a;color:#7c8089}
.tab-dot{width:5px;height:5px;border-radius:50%;background:var(--cyan)}
.tab-plus{width:24px;height:26px;display:flex;align-items:center;justify-content:center;color:#6f737b;font-size:14px}
.crumbs{height:23px;flex:0 0 23px;display:flex;align-items:center;gap:7px;padding:0 11px;border-bottom:1px solid #111;color:#7c8089;font-size:9.4px;white-space:nowrap;overflow:hidden}
.crumb-file{color:#c7cbd3}
.crumb-sep{color:#4f5a6b}
.crumb-lines{color:#5f6672}
.editor{flex:1;min-height:0;overflow:auto;overflow-anchor:none;scroll-behavior:auto;padding:8px 0;background:#1e1f22;scrollbar-width:thin;scrollbar-color:#3b3f46 #1e1f22}
.code{font-size:var(--fs,12px);line-height:1.5;color:#bcbec4;min-width:max-content}
.ln{display:flex;min-height:1.5em;padding-right:12px}
.ln .no{width:42px;flex:0 0 42px;text-align:right;padding-right:11px;color:#60646c;user-select:none}
.ln .tx{white-space:pre;padding-left:2px}
.ln.hl{background:rgba(34,211,238,.09);box-shadow:inset 3px 0 0 rgba(34,211,238,.72)}
.ln.strong{background:rgba(251,191,36,.12);box-shadow:inset 3px 0 0 var(--amber)}
.ln.gap{opacity:.5}
.k{color:#cf8e6d}.s{color:#6aab73}.c{color:#7a7e85;font-style:italic}.n{color:#2aacb8}.a{color:#b3ae60}.t{color:#56a8f5}
.status{height:21px;flex:0 0 21px;display:flex;align-items:center;gap:14px;padding:0 11px;background:#2b2d30;border-top:1px solid #111;color:#7c8089;font-size:8.5px;white-space:nowrap}

/* notes */
.notes{min-height:0;display:flex;flex-direction:column;gap:12px;overflow:hidden}
.notes .note{flex:1;display:flex;flex-direction:column;justify-content:center}
.note{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,rgba(19,31,55,.76),rgba(13,21,38,.72));padding:14px 16px}
.note.tone-cyan{border-color:rgba(34,211,238,.24)}
.note.tone-violet{border-color:rgba(167,139,250,.24)}
.note.tone-amber{border-color:rgba(251,191,36,.24)}
.note h3{margin:0 0 7px;font-size:13.2px;color:#fff;letter-spacing:.01em}
.note ul{margin:0;padding-left:16px;display:flex;flex-direction:column;gap:6px}
.note li{font-size:12.1px;line-height:1.44;color:#b6c2d4}
.note li code{font-size:10.8px}
.note p{margin:0;font-size:11.5px;line-height:1.4;color:#b6c2d4}

/* diagrams */
.diagram{width:100%;height:auto;display:block}
.d-box rect{fill:rgba(16,26,46,.86);stroke:#2a3a55;stroke-width:1.4}
.d-box.ui rect{stroke:rgba(34,211,238,.45)}
.d-box.web rect{stroke:rgba(167,139,250,.45)}
.d-box.service rect{stroke:rgba(251,191,36,.45)}
.d-box.algo rect{stroke:rgba(52,211,153,.45)}
.d-box.data rect{stroke:rgba(96,165,250,.45)}
.d-box.models rect{fill:rgba(148,163,184,.08);stroke:rgba(148,163,184,.3)}
.d-title{fill:#e8eef8;font-size:19px;font-weight:800;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.d-title.small{font-size:15px}
.d-sub{fill:#94a3b8;font-size:12.5px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.d-line{fill:none;stroke:#22d3ee;stroke-width:1.8;marker-end:url(#arr);opacity:.8}
.d-label rect{fill:rgba(13,21,38,.94);stroke:rgba(34,211,238,.25)}
.d-label text{fill:#a7f3ff;font-size:10px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.d-label.violet rect{stroke:rgba(167,139,250,.3)}.d-label.violet text{fill:#c4b5fd}
.arch-wrap,.flow-wrap{width:100%;min-height:0;flex:1;display:flex;flex-direction:column;justify-content:space-between}
.arch-wrap .diagram{max-height:500px}
.arch-legend{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:8px}
.arch-card{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.62);padding:9px 11px}
.arch-card b{display:block;font-size:11.5px;margin-bottom:2px}
.arch-card span{display:block;font-size:10.5px;line-height:1.35;color:#9fb0c7}
.arch-note{border:1px solid rgba(34,211,238,.2);border-radius:10px;background:rgba(34,211,238,.045);padding:9px 13px;font-size:11px;line-height:1.4;color:#a9bacd}
.arch-note b{color:#67e8f9}
.flow .f-box rect{fill:rgba(16,26,46,.86);stroke:#2a3a55;stroke-width:1.3}
.f-title{fill:#e8eef8;font-size:15px;font-weight:800;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.f-sub{fill:#8fa0b8;font-size:10.4px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.f-line{fill:none;stroke:#22d3ee;stroke-width:1.6;marker-end:url(#farr);opacity:.8}
.f-cap text{fill:#6f8098;font-size:10px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.f-bottom{fill:#7f8ba0;font-size:10.5px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.flow-wrap .diagram{max-height:285px}
.flow-io{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:center;margin-bottom:6px}
.io-card{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.62);padding:7px 12px;display:flex;align-items:baseline;gap:9px}
.io-card b{font-size:8.8px;letter-spacing:.14em;color:var(--cyan);font-weight:900}
.io-card span{font-size:10.6px;color:#9fb0c7}
.io-arrow{color:#4f6280;font-size:14px}
.flow-bottom{margin-top:8px;border:1px solid var(--line);border-radius:10px;background:rgba(148,163,184,.05);padding:8px 12px;font-size:10.8px;color:#9fb0c7;text-align:center}

/* Eller */
.eller-wrap{display:grid;grid-template-columns:1.15fr .85fr;grid-template-rows:1fr auto;gap:18px;width:100%;min-height:0;flex:1;align-content:stretch}
.steps{display:flex;flex-direction:column;gap:9px;justify-content:space-between}
.step{display:flex;gap:12px;border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.66);padding:11px 13px;flex:1;align-items:center}
.step-num{font-family:var(--mono);font-size:20px;font-weight:900;color:var(--cyan);flex:0 0 30px}
.step b{display:block;font-size:15px;margin-bottom:4px}
.step span{display:block;font-size:12.3px;line-height:1.42;color:#aebbd0}
.eller-side{display:flex;flex-direction:column;gap:12px;justify-content:center}
.set-demo{border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.66);padding:14px}
.set-row{display:grid;grid-template-columns:repeat(6,1fr);gap:5px}
.set-cell{height:38px;display:flex;align-items:center;justify-content:center;border-radius:7px;font-family:var(--mono);font-weight:800;font-size:12px;color:#07101d}
.s1{background:#67e8f9}.s2{background:#c4b5fd}.s3{background:#fcd34d}
.set-arrow{font-size:10.5px;color:#8fa0b8;text-align:center;padding:8px 0}
.principle{border:1px solid rgba(251,191,36,.22);border-radius:12px;background:rgba(251,191,36,.06);padding:11px 13px}
.principle b{display:block;font-size:12px;margin-bottom:3px}
.principle span{font-size:11.2px;line-height:1.4;color:#bfc9d8}

/* mini route */
.mini-route{width:100%;max-height:210px;margin-top:2px}

/* concept */
.concept-wrap{display:grid;grid-template-columns:1.08fr .92fr;grid-template-rows:1fr auto;gap:14px 20px;width:100%;min-height:0;flex:1}
.concept-left{display:flex;flex-direction:column;gap:10px}
.concept-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;flex:1;grid-template-rows:1fr 1fr}
.concept-card{border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.66);padding:13px 14px;display:flex;flex-direction:column;justify-content:center}
.c-ico{width:24px;height:24px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-weight:900;font-size:11px;color:#67e8f9;background:rgba(34,211,238,.1);border:1px solid rgba(34,211,238,.22)}
.concept-card h3{font-size:13px;margin:7px 0 2px}
.concept-card p{font-size:11.2px;line-height:1.38;color:#aebbd0;margin:0}
.cc-ex{font-family:var(--mono);font-size:9.6px;color:#67e8f9;margin-top:9px}
.cc-ref{font-size:9.2px;color:#7183a0;margin-top:7px;padding-top:6px;border-top:1px dashed rgba(148,163,184,.18)}
.concept-right{min-height:0;display:flex;align-items:center;justify-content:center}
.concept-bottom{grid-column:1/-1;border:1px solid rgba(34,211,238,.22);border-radius:11px;background:linear-gradient(90deg,rgba(34,211,238,.07),rgba(167,139,250,.05));padding:9px 13px;display:flex;align-items:center;gap:14px}
.cb-k{font-size:8.8px;letter-spacing:.14em;color:var(--cyan);font-weight:900;white-space:nowrap}
.cb-t{font-size:10.8px;line-height:1.4;color:#b6c2d4}
.qloop{max-height:430px}
.q-box rect{fill:rgba(16,26,46,.9);stroke:#2a3a55;stroke-width:1.4}
.q-box.accent rect{stroke:rgba(34,211,238,.45)}
.q-title{fill:#e8eef8;font-size:18px;font-weight:800;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.q-sub{fill:#94a3b8;font-size:12px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.q-line{fill:none;stroke:#22d3ee;stroke-width:1.8;marker-end:url(#qarr)}
.q-line.violet{stroke:#a78bfa}
.q-label{fill:#a7f3ff;font-size:11px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.q-label.violet{fill:#c4b5fd}
.q-note{fill:#8fa8c0;font-size:10px;text-anchor:middle;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.q-loop{fill:none;stroke:#22d3ee;stroke-width:1.6;stroke-dasharray:4 4;marker-end:url(#qarr);opacity:.75}
.q-formula rect{fill:rgba(13,21,38,.94);stroke:rgba(34,211,238,.28)}
.q-formula-text{fill:#d9f7ff;font-size:12px;text-anchor:middle;font-family:"SF Mono",Menlo,monospace}

/* qlearning slide */
.ql-wrap{width:100%;display:flex;flex-direction:column;gap:12px;min-height:0;flex:1;justify-content:stretch;padding:2px 0}
.formula-card{border:1px solid rgba(34,211,238,.26);border-radius:14px;background:linear-gradient(90deg,rgba(34,211,238,.08),rgba(167,139,250,.05));padding:20px 20px;display:flex;flex-direction:column;justify-content:center}
.formula-label{font-size:9.5px;letter-spacing:.16em;color:var(--cyan);font-weight:900;text-transform:uppercase}
.formula{font-family:var(--mono);font-size:23px;letter-spacing:-.03em;color:#eafcff;margin:7px 0 4px;white-space:nowrap}
.formula-note{font-size:11px;color:#93a9c2}
.param-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;min-height:0;flex:.8}
.param{border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.66);padding:14px 14px;display:flex;flex-direction:column;justify-content:center}
.p-k{font-family:var(--mono);font-size:11px;color:var(--cyan);font-weight:800}
.p-v{font-family:var(--mono);font-size:19px;font-weight:900;color:#fff;margin:1px 0}
.p-l{font-size:10px;color:#93a4bd;line-height:1.3}
.episode-strip{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.6);padding:13px 15px;font-size:11.2px;color:#b6c2d4;flex:.42;min-height:0}
.ep b{color:#67e8f9;font-family:var(--mono);margin-right:4px}
.ep-arr{color:#4f6280}

/* web */
.web-wrap{display:grid;grid-template-columns:.9fr 1.1fr;grid-template-rows:1fr auto;align-content:stretch;gap:20px;width:100%;min-height:0;flex:1}
.web-left{display:flex;flex-direction:column;justify-content:space-between;gap:10px;padding:2px 0}
.web-box{border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.7);padding:13px 15px;min-height:100px;display:flex;flex-direction:column;justify-content:center}
.web-box.accent{border-color:rgba(34,211,238,.3)}
.wb-k{font-size:9.2px;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);font-weight:900}
.wb-t{font-size:17px;font-weight:800;color:#fff;margin:2px 0}
.wb-s{font-family:var(--mono);font-size:10.6px;color:#8fa0b8;line-height:1.4}
.web-arrow{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:#5f7591;font-size:10.5px;letter-spacing:.05em;flex:1;min-height:34px;max-height:60px}
.web-arrow::before,.web-arrow::after{content:"";width:1px;flex:1;background:linear-gradient(to bottom,rgba(95,117,145,.1),rgba(95,117,145,.6),rgba(95,117,145,.1))}
.web-right{display:flex;flex-direction:column;justify-content:space-between;gap:8px;min-height:0}
.web-curl{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.7);padding:8px 10px;font-family:var(--mono);font-size:9.8px;line-height:1.45;color:#8fa0b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.web-js{border:1px dashed rgba(148,163,184,.24);border-radius:10px;background:rgba(148,163,184,.04);padding:10px 12px}
.web-js b{display:block;font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#93a4bd;margin-bottom:3px}
.web-js span{font-size:10.8px;line-height:1.35;color:#7f8ba0}
.web-curl b{color:#67e8f9;font-weight:700}
.route-table{display:flex;flex-direction:column}
.rt-row{display:grid;grid-template-columns:50px 1.05fr 1.25fr;gap:8px;align-items:center}
.route-table{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:rgba(13,21,38,.6)}
.rt-row{padding:10px 11px;border-bottom:1px solid rgba(148,163,184,.1);font-size:11.4px;color:#b6c2d4}
.rt-row:last-child{border-bottom:0}
.rt-head{background:rgba(148,163,184,.07);color:#8fa0b8;font-size:9px;letter-spacing:.12em;text-transform:uppercase;font-weight:800}
.m{font-family:var(--mono);font-size:9px;font-weight:800;padding:2px 5px;border-radius:4px;text-align:center}
.m.get{background:rgba(52,211,153,.12);color:#6ee7b7}
.m.post{background:rgba(251,191,36,.12);color:#fcd34d}
.rt-row span:nth-child(2){font-family:var(--mono);font-size:10.2px;color:#d3e2f3}
.web-note{border:1px solid var(--line);border-radius:10px;background:rgba(148,163,184,.05);padding:9px 11px;font-size:10.8px;line-height:1.4;color:#9fb0c7}
.web-caveat{grid-column:1/-1;border:1px solid rgba(251,191,36,.22);border-radius:10px;background:rgba(251,191,36,.05);padding:8px 12px;font-size:10.5px;line-height:1.4;color:#cdb98a}
.web-caveat b{color:#fcd34d}

/* validation & cheat tables */
.table-card{width:100%;min-height:0;border:1px solid var(--line);border-radius:14px;background:rgba(13,21,38,.6);overflow:hidden}
.val-table,.cheat-table{width:100%;font-size:11.1px;height:100%;display:flex;flex-direction:column}
.val-wrap{display:flex;flex-direction:column;gap:10px;flex:1;min-height:0;width:100%}
.val-wrap .table-card,.cheat-card{flex:1;min-height:0}
.error-examples{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.err-card{border:1px solid rgba(251,113,133,.2);border-radius:10px;background:rgba(251,113,133,.05);padding:8px 11px}
.err-k{font-size:8.6px;letter-spacing:.14em;text-transform:uppercase;color:#fb7185;font-weight:900;margin-bottom:3px}
.err-m{font-family:var(--mono);font-size:9.8px;line-height:1.35;color:#e8c4cb}
.vt-row,.ct-row{display:grid;gap:10px;align-items:center;padding:10px 12px;border-bottom:1px solid rgba(148,163,184,.1);flex:1}
.vt-row{grid-template-columns:.9fr 1.15fr 2.2fr 1.25fr}
.ct-row{grid-template-columns:.9fr 1.3fr 1.3fr;padding-top:12px;padding-bottom:12px;flex:1}
.vt-row:last-child,.ct-row:last-child{border-bottom:0}
.vt-head,.ct-head{background:rgba(148,163,184,.07);color:#8fa0b8;font-size:8.8px;letter-spacing:.12em;text-transform:uppercase;font-weight:900}
.vt-row span,.ct-row span{color:#b6c2d4;line-height:1.3}
.mono{font-family:var(--mono);font-size:9.6px;color:#cfe2f5!important}
.bad{color:#fda4af!important}
.good{color:#6ee7b7!important}

/* quality */
.quality-wrap{display:grid;grid-template-columns:1.18fr .82fr;grid-template-rows:1fr auto;gap:18px;width:100%;min-height:0;flex:1}
.quality-left,.quality-right{display:flex;flex-direction:column;gap:10px;min-height:0;justify-content:space-between}
.cov-list{display:flex;flex-direction:column;gap:10px;flex:1;justify-content:center}
.cov-head{font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);font-weight:900}
.cov-row{display:grid;grid-template-columns:160px 1fr 70px;gap:10px;align-items:center;padding:0;flex:1;min-height:0}
.cov-row span{font-size:11.4px;color:#b6c2d4}
.cov-row b{font-family:var(--mono);font-size:10px;color:#6ee7b7;text-align:right}
.bar{height:8px;border-radius:999px;background:rgba(148,163,184,.12);overflow:hidden}
.bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#22d3ee,#34d399)}
.cov-note{font-size:10px;color:#7f8ba0;line-height:1.35;margin-top:2px}
.test-classes{border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.62);padding:6px 12px;display:flex;flex-direction:column;justify-content:space-between;flex:1}
.test-classes>div{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(148,163,184,.08);font-size:10.8px;color:#b6c2d4}
.test-classes>div:last-child{border-bottom:0}
.test-classes b{font-weight:600;color:#dbe6f4}
.test-classes span{font-family:var(--mono);color:#67e8f9}
.checks{display:flex;flex-direction:column;gap:5px;font-size:10.3px;color:#aebbd0}
.ok-dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:#34d399;margin-right:6px;box-shadow:0 0 6px #34d399}

/* Q&A */
.qa-grid{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(5,1fr);gap:9px;width:100%;min-height:0;flex:1}
.qa-card{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.64);padding:10px 12px;display:flex;flex-direction:column;justify-content:center}
.qa-q{font-size:12px;font-weight:800;color:#fff;line-height:1.3}
.qa-a{font-size:10.8px;line-height:1.38;color:#a9b7cb;margin-top:4px}

/* final */
.final-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;width:100%;flex:1.15;min-height:0}
.final-card{border:1px solid var(--line);border-radius:16px;background:linear-gradient(180deg,rgba(19,31,55,.82),rgba(13,21,38,.72));padding:18px 20px;display:flex;flex-direction:column;justify-content:center}
.f-num{font-family:var(--mono);font-size:46px;font-weight:900;letter-spacing:-.04em;color:#fff}
.f-t{font-size:12px;color:var(--cyan);font-weight:800;text-transform:uppercase;letter-spacing:.08em;margin-top:2px}
.f-s{font-size:11.2px;line-height:1.4;color:#93a4bd;margin-top:8px}
.final-formula{display:grid;grid-template-columns:1.1fr .9fr;gap:12px;margin-top:0;flex:1;min-height:0}
.ff-left,.ff-right{border:1px solid var(--line);border-radius:14px;background:rgba(13,21,38,.66);padding:13px 16px;display:flex;flex-direction:column;justify-content:center}
.ff-k{font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:var(--cyan);font-weight:900}
.ff-eq{font-family:var(--mono);font-size:18px;color:#eafcff;margin:6px 0 4px;white-space:nowrap}
.ff-sub{font-size:10.5px;color:#93a4bd}
.ff-line{font-size:13px;line-height:1.5;color:#c7d4e6;margin-top:7px}
.final-links{margin-top:14px;font-size:11px;color:#8fa0b8}
.final-slide .content{justify-content:stretch;gap:12px}
.final-bottom{display:flex;flex-direction:column;gap:2px;flex:0 0 auto}
.final-bottom .final-links{margin-top:0}
.final-slide .final-grid,.final-slide .final-formula,.final-slide .final-demo,.final-slide .final-links,.final-slide .thanks{margin-top:0}


/* --- доп. блоки для плотности слайдов --- */
.title-maze{position:absolute;right:34px;top:50px;width:470px;height:530px;opacity:.92;pointer-events:none;z-index:0}
.title-maze svg{width:100%;height:100%}
.title-wrap{position:relative;z-index:1}
.demo-strip{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.demo-pill{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.66);padding:8px 10px;font-size:10.5px;color:#b6c2d4}
.demo-pill b{display:flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:50%;background:rgba(34,211,238,.12);border:1px solid rgba(34,211,238,.25);color:#67e8f9;font-family:var(--mono);font-size:9px;flex:0 0 18px}
.dep-flow{display:flex;align-items:center;gap:7px;border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.55);padding:8px 10px}
.dep-node{flex:1;min-width:0;padding:5px 8px;border-radius:8px;background:rgba(148,163,184,.05);border:1px solid rgba(148,163,184,.12)}
.dep-node b{display:block;font-size:10.5px;color:#dbe6f4}
.dep-node span{display:block;font-size:8.8px;color:#7f8ba0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dep-arrow{color:#4f6280;font-size:12px}
.eller-facts{grid-column:1/-1;display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.eller-fact{border:1px solid var(--line);border-radius:11px;background:rgba(13,21,38,.66);padding:9px 12px;display:flex;align-items:baseline;gap:8px}
.eller-fact b{font-family:var(--mono);font-size:19px;color:#fff}
.eller-fact span{font-size:10.5px;color:#93a4bd}
.flow-examples,.error-examples{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.ex-card{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.62);padding:9px 11px}
.ex-card b{display:block;font-size:10.5px;color:#fff;margin-bottom:3px}
.ex-card code{font-size:9.5px;color:#fda4af}
.ex-card span{display:block;font-size:10px;line-height:1.35;color:#93a4bd;margin-top:3px}
.legend-dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px;vertical-align:1px}
.tree-links{margin-top:2px;border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.64);padding:10px 12px}
.tree-links b{display:block;font-size:11px;margin-bottom:4px}
.tree-links a{display:flex;justify-content:space-between;gap:8px;color:#aebbd0;font-size:10.5px;text-decoration:none;padding:2px 0}
.tree-links a span{color:#67e8f9;font-family:var(--mono);font-size:9.5px}
.ql-top{display:grid;grid-template-columns:1.5fr .5fr;gap:12px;min-height:0;flex:1.5}
.qtable-card{border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.66);padding:10px 11px;display:flex;flex-direction:column;justify-content:center}
.qt-title{font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);font-weight:900;margin-bottom:6px}
.qtable{display:grid;grid-template-columns:1fr repeat(4,34px);gap:3px;font-family:var(--mono);font-size:9.6px}
.qtable>div{padding:5px 4px;border-radius:4px;text-align:center;color:#aebbd0}
.qtable .qt-head{color:#7f8ba0;font-size:8.5px;text-transform:uppercase}
.qtable .qt-cell{text-align:left;color:#dbe6f4}
.qtable .qt-best{background:rgba(52,211,153,.14);color:#6ee7b7;font-weight:800}
.qt-note{font-size:9.3px;color:#7f8ba0;line-height:1.3;margin-top:6px}
.why-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;flex:.9;min-height:0}
.why{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.6);padding:11px 13px;display:flex;flex-direction:column;justify-content:center}
.why b{display:block;font-size:10.2px;color:#e6eefb;margin-bottom:3px}
.why span{font-size:10px;line-height:1.35;color:#93a4bd}
.example-card{display:flex;align-items:center;gap:14px;border:1px solid rgba(251,191,36,.24);border-radius:11px;background:rgba(251,191,36,.06);padding:12px 15px;flex:.45;min-height:0}
.example-card b{font-size:10.5px;color:#fcd34d;white-space:nowrap}
.example-card span{font-size:10.2px;color:#bfc9d8}
.example-card code{font-size:9.6px;color:#fde68a;margin-left:auto;white-space:nowrap}
.mini-label{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:#5f7591;font-weight:900;margin-bottom:2px}
.web-seq{border:1px solid var(--line);border-radius:10px;background:rgba(148,163,184,.05);padding:10px 11px;font-size:10.8px;color:#9fb0c7;line-height:1.4}
.web-seq b{color:#dbe6f4}
.quality-foot{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,1fr);gap:10px;border-top:1px solid rgba(148,163,184,.14);padding-top:10px;align-items:start}
.qf-card{border:1px solid var(--line);border-radius:10px;background:rgba(13,21,38,.6);padding:9px 11px}
.qf-card b{display:block;font-family:var(--mono);font-size:14px;color:#67e8f9}
.qf-card span{display:block;font-size:9.8px;color:#93a4bd;margin-top:2px;line-height:1.3}
.final-demo{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:0;flex:.85;min-height:0}
.fd-card{border:1px solid var(--line);border-radius:12px;background:rgba(13,21,38,.62);padding:12px 14px;display:flex;flex-direction:column;justify-content:center}
.fd-card b{display:block;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--cyan);margin-bottom:4px}
.fd-card span{font-size:11px;line-height:1.4;color:#b6c2d4}
.thanks{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin-top:14px;border-top:1px solid rgba(148,163,184,.14);padding-top:12px}
.thanks .th-title{font-size:38px;font-weight:900;letter-spacing:-.035em;color:#fff}
.thanks .th-sub{font-size:11.5px;color:#8fa0b8;text-align:right;line-height:1.4}

/* TOC / nav */
#hint{position:fixed;left:20px;bottom:9px;z-index:30;font-size:10px;color:#5f7088;letter-spacing:.02em}
#progress{position:fixed;left:0;bottom:0;height:3px;background:linear-gradient(90deg,#22d3ee,#a78bfa);z-index:35;transition:width .22s ease;box-shadow:0 0 12px rgba(34,211,238,.6)}
#toc{position:fixed;inset:44px 0 0 0;z-index:45;display:none;background:rgba(5,8,15,.97);backdrop-filter:blur(14px);padding:34px 56px;overflow:auto}
#toc.open{display:block}
#toc h2{margin:0 0 16px;font-size:22px}
#toc-list{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
#toc-list a{display:block;text-decoration:none;color:#c7d4e6;border:1px solid var(--line);border-radius:9px;background:rgba(13,21,38,.66);padding:8px 10px;font-size:11px;line-height:1.3}
#toc-list a:hover{border-color:rgba(34,211,238,.45);color:#fff}
#toc-list a b{font-family:var(--mono);color:#22d3ee;font-size:9px;margin-right:6px}
body.export #deckbar,body.export #hint,body.export #progress,body.export #toc{display:none!important}
body.export #viewport{inset:0}
body.export .deck{transform:none!important}
body.export .slide.active{animation:none!important}

@media print{
  @page{size:1600px 900px;margin:0}
  html,body{overflow:visible;background:#070b14;display:block}
  #deckbar,#hint,#progress,#toc{display:none!important}
  #viewport{position:static;inset:auto;display:block}
  .deck{width:auto;height:auto;transform:none!important}
  .slide{position:relative;display:flex!important;width:1600px;height:900px;page-break-after:always;break-after:page}
  .slide.active{animation:none!important}
  .slide:last-child{page-break-after:auto;break-after:auto}
}
"""


# ---------------------------------------------------------------------------
# JS
# ---------------------------------------------------------------------------

JS = r"""
const slides = Array.from(document.querySelectorAll('.slide'));
const deck = document.getElementById('deck');
const progress = document.getElementById('progress');
const toc = document.getElementById('toc');
const tocList = document.getElementById('toc-list');
let idx = 0;

function fit(){
  const vw = window.innerWidth;
  const vh = window.innerHeight - (document.body.classList.contains('export') ? 0 : 44);
  const s = Math.min(vw / 1600, vh / 900);
  deck.style.transform = `scale(${s})`;
}
function resetEditors(){
  document.querySelectorAll('.editor').forEach(e => { e.scrollTop = 0; e.scrollLeft = 0; });
}
function show(n){
  idx = Math.max(0, Math.min(slides.length - 1, n));
  slides.forEach((s, i) => s.classList.toggle('active', i === idx));
  progress.style.width = ((idx + 1) / slides.length * 100) + '%';
  const title = slides[idx].dataset.title || '';
  document.getElementById('current-title').textContent = title;
  history.replaceState(null, '', '#' + (idx + 1));
  requestAnimationFrame(resetEditors);
}
function toggleToc(open){
  toc.classList.toggle('open', open === undefined ? !toc.classList.contains('open') : open);
}
slides.forEach((s, i) => {
  const a = document.createElement('a');
  a.href = '#' + (i + 1);
  a.innerHTML = `<b>${String(i + 1).padStart(2, '0')}</b>${s.dataset.title || 'Слайд ' + (i + 1)}`;
  a.addEventListener('click', e => { e.preventDefault(); show(i); toggleToc(false); });
  tocList.appendChild(a);
});
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); show(idx + 1); }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); show(idx - 1); }
  else if (e.key === 'Home') { show(0); }
  else if (e.key === 'End') { show(slides.length - 1); }
  else if (e.key.toLowerCase() === 't') { toggleToc(); }
  else if (e.key === 'Escape') { toggleToc(false); }
  else if (e.key.toLowerCase() === 'f') {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen?.(); else document.exitFullscreen?.();
  }
});
document.getElementById('prev').addEventListener('click', () => show(idx - 1));
document.getElementById('next').addEventListener('click', () => show(idx + 1));
document.getElementById('toc-btn').addEventListener('click', () => toggleToc());
window.addEventListener('resize', fit);
const params = new URLSearchParams(location.search);
if (params.get('export') === '1') document.body.classList.add('export');
const start = parseInt(params.get('slide') || location.hash.replace('#', '') || '1', 10);
setTimeout(() => { fit(); show((start || 1) - 1); resetEditors(); }, 30);
fit();
"""


# ---------------------------------------------------------------------------
# сборка HTML
# ---------------------------------------------------------------------------

def render_slide(data: dict, number: int, total: int) -> str:
    cls = data.get("cls", "")
    if "title-slide" in cls:
        inner = f'''
<div class="slide-inner">{data["body"]}</div>'''
    elif "final-slide" in cls:
        inner = f'''
<div class="slide-inner">
  <header class="slide-head">
    <div class="kicker">{data["kicker"]}</div>
    <h1>{data["title"]}</h1>
    <p class="sub">{data["sub"]}</p>
  </header>
  <div class="content one-col">{data["body"]}</div>
  <footer class="slide-foot"><span>{data["foot"]}</span><span class="pageno">{number:02d} / {total:02d}</span></footer>
</div>'''
    else:
        foot = data.get("foot", "")
        inner = f'''
<div class="slide-inner">
  <header class="slide-head">
    <div class="kicker">{data["kicker"]}</div>
    <h1>{data["title"]}</h1>
    <p class="sub">{data["sub"]}</p>
  </header>
  <div class="content">{data["body"]}</div>
  <footer class="slide-foot"><span>{foot}</span><span class="pageno">{number:02d} / {total:02d}</span></footer>
</div>'''
    title_attr = html.escape(data["title"] or "Maze — защита проекта", quote=True)
    return f'<section class="slide {cls}" data-title="{title_attr}">{inner}</section>'


def main() -> None:
    total = len(SLIDES)
    body = "\n".join(render_slide(s, i + 1, total) for i, s in enumerate(SLIDES))
    doc = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Maze — защита проекта</title>
<style>{CSS}</style>
</head>
<body>
<div id="deckbar">
  <span class="brand">MAZE</span>
  <span class="pill"><span class="dot"></span> защита проекта</span>
  <span class="pill" id="current-title">Maze — защита проекта</span>
  <span class="spacer"></span>
  <button id="prev">← назад</button>
  <button id="next">вперёд →</button>
  <button id="toc-btn">T · оглавление</button>
</div>
<div id="viewport"><main class="deck" id="deck">
{body}
</main></div>
<div id="progress"></div>
<div id="hint">← → / Space — слайды · T — оглавление · F — полный экран</div>
<div id="toc"><h2>Оглавление</h2><div id="toc-list"></div></div>
<script>{JS}</script>
</body>
</html>
'''
    out = BASE / "index.html"
    out.write_text(doc, encoding="utf-8")
    print(f"written {out} ({len(doc)} bytes, {total} slides)")


if __name__ == "__main__":
    main()
