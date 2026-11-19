"""Сборка презентации в один офлайн HTML-файл.

    npm install            # reveal.js, gsap, three (версии в package.json)
    python manim/render.py # схемы Manim -> src/diagrams/*.webp (нужен manim==0.19.0)
    python build.py        # -> dist/Prezentaciya_Aleksandr_I.html и dist/Prezentaciya_Aleksandr_I.zip

Всё (библиотеки, стили, фото, схемы) встраивается внутрь файла, поэтому
он открывается двойным щелчком с флешки без интернета.
"""
import base64, json, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from webp_speed import speed_up, total_ms  # noqa: E402
SRC, NM, DIST = ROOT / "src", ROOT / "node_modules", ROOT / "dist"
NAME = "Prezentaciya_Aleksandr_I"
# Общая скорость анимаций: 1.0 — исходная, 1.5 — всё на треть быстрее (каждая анимация 2/3 времени).
SPEED = 1.5


def text(p):
    return Path(p).read_text(encoding="utf-8")


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def safe_js(s):
    assert "</script" not in s.lower(), "в скрипте встретился </script>"
    return s


def build():
    slides = text(SRC / "slides.html")
    diagrams = {}
    for n in range(2, 8):
        slides = slides.replace("{{DIAGRAM_FINAL_%d}}" % n, "data:image/webp;base64," + b64(SRC / "diagrams" / f"s{n}_final.webp"))
        raw = (SRC / "diagrams" / f"s{n}.webp").read_bytes()
        fast = speed_up(raw, SPEED)
        print(f"  схема {n}: {total_ms(raw) / 1000:.2f} с -> {total_ms(fast) / 1000:.2f} с")
        diagrams[str(n)] = base64.b64encode(fast).decode()
    parts = {
        "REVEAL_CSS": text(NM / "reveal.js/dist/reveal.css"),
        "STYLE": text(SRC / "style.css"),
        "TREE": b64(SRC / "assets/tree.webp"),
        "APPLE": b64(SRC / "assets/apple.webp"),
        "APPLE_SKIN": b64(SRC / "assets/apple_skin.webp"),
        "SLIDES": slides,
        "REVEAL_JS": safe_js(text(NM / "reveal.js/dist/reveal.js")),
        "GSAP_JS": safe_js(text(NM / "gsap/dist/gsap.min.js")),
        "THREE_JS": safe_js(text(NM / "three/build/three.min.js")),
        "DIAGRAMS": json.dumps(diagrams),
        "SPEED": str(SPEED),
        "APP_JS": safe_js(text(SRC / "app.js")),
    }
    html = text(SRC / "template.html")
    for k, v in parts.items():
        html = html.replace("{{%s}}" % k, v)
    missing = [k for k in list(parts) + ["DIAGRAM_FINAL_%d" % n for n in range(2, 8)] if "{{%s}}" % k in html]
    assert not missing, f"остались незаполненные места: {missing}"
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{NAME}.html"
    out.write_text(html, encoding="utf-8")
    with zipfile.ZipFile(DIST / f"{NAME}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out, f"{NAME}.html")
        z.writestr("KAK_OTKRYT.txt", "﻿" + text(ROOT / "KAK_OTKRYT.txt").replace("\n", "\r\n"))
    print(f"{out.relative_to(ROOT)}: {out.stat().st_size / 1024 / 1024:.2f} МБ; zip: {(DIST / f'{NAME}.zip').stat().st_size / 1024 / 1024:.2f} МБ")


if __name__ == "__main__":
    build()
