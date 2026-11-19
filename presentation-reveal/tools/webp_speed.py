"""Ускорение анимированного WebP без пережатия: делим длительность каждого кадра.

В контейнере WebP у каждого кадра (чанк ANMF) записана длительность в мс
(3 байта, смещение 12 от начала данных чанка). Картинки кадров не трогаются.
"""
import struct


def speed_up(data: bytes, factor: float) -> bytes:
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", "не WebP"
    out = bytearray(data)
    pos, frames = 12, 0
    while pos + 8 <= len(out):
        tag = bytes(out[pos:pos + 4]); size = struct.unpack("<I", out[pos + 4:pos + 8])[0]
        if tag == b"ANMF":
            d = pos + 8 + 12
            dur = int.from_bytes(out[d:d + 3], "little")
            out[d:d + 3] = max(1, round(dur / factor)).to_bytes(3, "little")
            frames += 1
        pos += 8 + size + (size & 1)
    assert frames, "в файле нет кадров анимации"
    return bytes(out)


def total_ms(data: bytes) -> int:
    pos, t = 12, 0
    while pos + 8 <= len(data):
        tag = data[pos:pos + 4]; size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        if tag == b"ANMF":
            t += int.from_bytes(data[pos + 20:pos + 23], "little")
        pos += 8 + size + (size & 1)
    return t
