"""Рендер схем Manim в анимированные WebP с прозрачностью.

python manim/render.py [номер слайда ...]
Результат: src/diagrams/sN.webp (анимация, играет один раз) и sN_final.webp (последний кадр).
"""
import glob, os, shutil, sys, tempfile
from pathlib import Path

from PIL import Image
from manim import config, tempconfig

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "diagrams"
sys.path.insert(0, str(HERE))
from diagrams import SCENES  # noqa: E402

SCALE = 1.5   # 600 px макета -> 900 px кадра (чётко на экранах до 2×)
FPS = 30


def render(n):
    cls, vh = SCENES[n]
    w, h = int(600 * SCALE), int(round(vh * SCALE / 2) * 2)
    tmp = Path(tempfile.mkdtemp(prefix=f"manim_s{n}_"))
    with tempconfig({
        "pixel_width": w, "pixel_height": h, "frame_width": 8, "frame_height": 8 * h / w,
        "frame_rate": FPS, "transparent": True, "format": "png", "background_opacity": 0,
        "media_dir": str(tmp), "disable_caching": True, "verbosity": "WARNING", "progress_bar": "none",
    }):
        cls().render()
    frames = sorted(glob.glob(str(tmp / "**" / "*.png"), recursive=True))
    ims = [Image.open(f).convert("RGBA") for f in frames]
    OUT.mkdir(parents=True, exist_ok=True)
    ims[0].save(OUT / f"s{n}.webp", save_all=True, append_images=ims[1:], duration=int(1000 / FPS),
                loop=1, quality=72, method=6, lossless=False, minimize_size=True, allow_mixed=True)
    ims[-1].save(OUT / f"s{n}_final.webp", quality=88, method=6)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"s{n}: {len(ims)} кадров, {w}x{h}, "
          f"{os.path.getsize(OUT / f's{n}.webp') // 1024} КБ + {os.path.getsize(OUT / f's{n}_final.webp') // 1024} КБ")


if __name__ == "__main__":
    for n in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else SCENES):
        render(n)
