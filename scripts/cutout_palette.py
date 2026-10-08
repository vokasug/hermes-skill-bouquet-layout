#!/usr/bin/env python3
"""
Вырезание букета с фона (rembg) + извлечение палитры (PIL quantize).
Использование:
  cutout_palette.py --input photo.jpg --cutout bouquet.png --palette-json palette.json [--n-colors 7]
"""
import argparse
import json

from PIL import Image
from rembg import remove


def cutout(inp, outp):
    img = Image.open(inp).convert("RGBA")
    cut = remove(img)  # u2net по умолчанию
    # обрезать по альфа-каналу с небольшим полем
    bbox = cut.getchannel("A").getbbox()
    if bbox:
        pad = 12
        l, t, r, b = bbox
        l = max(0, l - pad); t = max(0, t - pad)
        r = min(cut.width, r + pad); b = min(cut.height, b + pad)
        cut = cut.crop((l, t, r, b))
    cut.save(outp)
    return cut


def palette(img, n=7):
    """Доминирующие цвета по непрозрачным пикселям.

    Буст насыщенным кластерам (цветы), а не только крупным пятнам (обёртка);
    жадный отбор с минимальной дистанцией между цветами; итог по оттенку.
    """
    import colorsys

    rgba = img.convert("RGBA")
    # только непрозрачные пиксели — фон не должен влиять на кластеры
    rgba.thumbnail((220, 220))
    px = [(r, g, b) for r, g, b, a in rgba.getdata() if a > 128]
    if not px:
        return []
    step = max(1, len(px) // 20000)
    px = px[::step]
    stripe = Image.new("RGB", (len(px), 1))
    stripe.putdata(px)
    q = stripe.quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: 24 * 3]
    counts = sorted(q.getcolors(), reverse=True)  # (count, index)

    clusters = []
    for count, idx in counts:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        if max(r, g, b) < 30:  # чисто чёрный (тени); тёмные ягодно-пурпурные тона оставляем
            continue
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        score = count * (0.25 + s ** 1.2)  # насыщенные цветы выше пастельной обёртки
        clusters.append((score, (r, g, b)))
    clusters.sort(key=lambda x: -x[0])

    def dist(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

    picked = []
    for score, c in clusters:
        if all(dist(c, p) > 42 for p in picked):
            picked.append(c)
        if len(picked) >= n:
            break
    picked.sort(key=lambda c: colorsys.rgb_to_hls(*(v / 255 for v in c))[0])
    return ["#%02x%02x%02x" % c for c in picked]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--cutout", required=True)
    ap.add_argument("--palette-json", required=True)
    ap.add_argument("--n-colors", type=int, default=7)
    a = ap.parse_args()
    cut = cutout(a.input, a.cutout)
    pal = palette(cut, a.n_colors)
    with open(a.palette_json, "w") as f:
        json.dump(pal, f, ensure_ascii=False, indent=2)
    print(json.dumps({"cutout": a.cutout, "size": list(cut.size), "palette": pal}))
