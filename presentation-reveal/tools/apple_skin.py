"""Текстура кожуры для 3D-яблока из фото «Red apple with leaf» (Wikimedia Commons, CC0).

С фото берётся ровный участок кожуры (без блика и тени), освещение на нём
выравнивается, участок зеркально повторяется в бесшовную полосу. Сверху
накладывается естественный переход цвета: снизу желтоватый, к черенку тёмно-красный.
Объём и блики даёт освещение three.js. Результат: src/assets/apple_skin.webp (1024×512).
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "src/assets/apple_photo_source.jpg").convert("RGB")
big = src.crop((560, 680, 1080, 1200)).filter(ImageFilter.GaussianBlur(.9))   # ровная кожура в нижней левой части яблока
p = np.asarray(big).astype(np.float32)
low = np.asarray(big.filter(ImageFilter.GaussianBlur(40))).astype(np.float32)
detail = (p / np.maximum(low, 1))[80:440, 80:440]              # только мелкая фактура, без краёв размытия
detail = np.repeat(1 + (detail.mean(axis=2, keepdims=True) - 1) * .5, 3, axis=2)   # мягче и без цветного шума
tile = np.concatenate([detail, detail[:, ::-1]], axis=1)       # бесшовно по долготе
tile = np.concatenate([tile, tile[::-1]], axis=0)
img = Image.fromarray(np.clip(tile * 128, 0, 255).astype(np.uint8)).resize((1024, 512), Image.LANCZOS)
d = np.asarray(img).astype(np.float32) / 128

TH = 512
v = np.linspace(0, 1, TH)[:, None]                              # строка 0 — низ яблока (как v в LatheGeometry)
def lerp(a, b, t): return a + (b - a) * t
stops = [(0.0, (196, 150, 58)), (0.14, (205, 78, 44)), (0.45, (196, 42, 34)), (0.8, (160, 26, 24)), (1.0, (96, 28, 18))]
base = np.zeros((TH, 3), np.float32)
for i in range(len(stops) - 1):
    (t0, c0), (t1, c1) = stops[i], stops[i + 1]
    m = (v[:, 0] >= t0) & (v[:, 0] <= t1)
    tt = ((v[:, 0][m] - t0) / (t1 - t0))[:, None]
    base[m] = lerp(np.array(c0, np.float32), np.array(c1, np.float32), tt)
# лёгкая неравномерность румянца по долготе
rng = np.random.default_rng(1777)
blot = np.asarray(Image.fromarray((rng.random((8, 32)) * 255).astype(np.uint8)).resize((1024, 512), Image.BICUBIC)).astype(np.float32) / 255
blot = (blot - .5) * .18
col = base[:, None, :] * (1 + blot[..., None]) * d
out = Image.fromarray(np.clip(col[::-1], 0, 255).astype(np.uint8))   # строки картинки идут сверху вниз
out.save(ROOT / "src/assets/apple_skin.webp", quality=86, method=6)
print("apple_skin.webp", out.size, (ROOT / "src/assets/apple_skin.webp").stat().st_size // 1024, "КБ")
