from __future__ import annotations

import struct
import zlib
from pathlib import Path


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_progress_png(path: Path, values: list[float], *, width: int = 720, height: int = 360) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pixels = bytearray()
    canvas = [[(250, 250, 250) for _ in range(width)] for _ in range(height)]
    for y in range(40, height - 30, 40):
        for x in range(40, width - 20):
            canvas[y][x] = (230, 230, 230)
    if values:
        low = min(values)
        high = max(values)
        if high == low:
            high = low + 1
        points = []
        for i, value in enumerate(values):
            x = 50 + int(i * (width - 90) / max(1, len(values) - 1))
            y = height - 40 - int((value - low) * (height - 90) / (high - low))
            points.append((x, y))
        for x, y in points:
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < width and 0 <= yy < height:
                        canvas[yy][xx] = (210, 40, 90)
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            steps = max(abs(x2 - x1), abs(y2 - y1), 1)
            for step in range(steps + 1):
                x = x1 + (x2 - x1) * step // steps
                y = y1 + (y2 - y1) * step // steps
                if 0 <= x < width and 0 <= y < height:
                    canvas[y][x] = (210, 40, 90)
    for row in canvas:
        pixels.append(0)
        for r, g, b in row:
            pixels.extend((r, g, b))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(bytes(pixels), level=9))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(png)
