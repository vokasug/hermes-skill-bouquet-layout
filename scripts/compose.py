#!/usr/bin/env python3
"""
Сборка брендированной раскладки букета («Кот и Клевер»).
Вход: spec.json с компонентами, палитрой и структурой.
Выход: один PNG 2048x2048.
"""
import argparse
import json
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 2048
BG = (22, 32, 30)          # тёмный зелёно-графитовый (бренд, адаптация #0E2A26 под тёмный макет)
CREAM = (250, 245, 233)    # фирменный кремовый #FAF5E9
TEAL = (94, 176, 172)      # осветлённый фирменный teal #095E5D для читаемости на тёмном
MUTED = (168, 178, 172)    # приглушённый серо-зелёный для подписей

FONT_DIR = "/Users/alexander/bouquet-layout/fonts"


def font(size, weight=500, italic=False):
    path = f"{FONT_DIR}/CormorantGaramond{'-Italic' if italic else ''}-var.ttf"
    f = ImageFont.truetype(path, size)
    f.set_variation_by_axes([weight])
    return f


def text_w(draw, s, f, tracking=0):
    w = draw.textlength(s, font=f)
    return w + tracking * max(0, len(s) - 1)


def draw_tracked(draw, xy, s, f, fill, tracking=0):
    """Текст с межбуквенным трекингом (для заголовков caps)."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking


def paste_fit(canvas, img, box, contain=True):
    """Вписать RGBA/RGB картинку в box (x0,y0,x1,y1) с сохранением пропорций."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    scale = min(bw / img.width, bh / img.height) if contain else max(bw / img.width, bh / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    im = img.resize((nw, nh), Image.LANCZOS)
    px, py = x0 + (bw - nw) // 2, y0 + (bh - nh) // 2
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    canvas.alpha_composite(im, (px, py))
    return px, py, nw, nh


def section_header(draw, x, y, width, title):
    f = font(44, 600)
    draw_tracked(draw, (x, y), title.upper(), f, CREAM, tracking=6)
    tw = text_w(draw, title.upper(), f, tracking=6)
    ly = y + 30
    draw.line([(x + tw + 28, ly), (x + width, ly)], fill=(90, 104, 98), width=2)
    return y + 74  # baseline контента


def draw_item(canvas, draw, path, box, label, sublabel=""):
    img = Image.open(path)
    px, py, nw, nh = paste_fit(canvas, img, box)
    cx = box[0] + (box[2] - box[0]) // 2
    fy = box[3] + 10
    f1 = font(34, 500)
    f2 = font(30, 400, italic=True)
    if label:
        w1 = text_w(draw, label, f1)
        draw.text((cx - w1 / 2, fy), label, font=f1, fill=CREAM)
        fy += 44
    if sublabel:
        w2 = text_w(draw, sublabel, f2)
        draw.text((cx - w2 / 2, fy), f"({sublabel})", font=f2, fill=MUTED)


def draw_items_row(canvas, draw, items, x, y, width, cell_h, img_ratio=0.72):
    """Ряд компонентов: до len(items) в одну линию, каждый с подписью."""
    n = len(items)
    if n == 0:
        return y
    gap = 24
    cell_w = (width - gap * (n - 1)) // n
    img_h = int(cell_h * img_ratio)
    for i, it in enumerate(items):
        cx0 = x + i * (cell_w + gap)
        draw_item(canvas, draw, it["img"], (cx0, y, cx0 + cell_w, y + img_h),
                  it.get("label", ""), it.get("sublabel", ""))
    return y + cell_h


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def compose(spec_path, out_path):
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    canvas = Image.new("RGBA", (W, H), BG + (255,))
    draw = ImageDraw.Draw(canvas)

    M = 80  # поля

    # ── Шапка: бренд ─────────────────────────────────────────
    brand = spec.get("brand", {})
    name = brand.get("name", "Кот и Клевер")
    tagline = brand.get("tagline", "МАСТЕРСКАЯ ЦВЕТОВ И ДЕКОРА · МОСКВА")
    f_brand = font(96, 600)
    draw.text((M, 54), name, font=f_brand, fill=CREAM)
    bw = text_w(draw, name, f_brand)
    f_tag = font(34, 500)
    draw_tracked(draw, (M + 4, 168), tagline, f_tag, TEAL, tracking=8)

    # ── Левая колонка: букет ─────────────────────────────────
    bx = (60, 300, 940, 1520)
    bouquet = Image.open(spec["bouquet"])
    paste_fit(canvas, bouquet, bx)

    # ── Правая колонка ───────────────────────────────────────
    RX, RW = 980, W - M - 980
    y = 64
    sections = spec.get("sections", [])
    # секции с сеткой по 3 (или сколько есть, максимум 2 ряда)
    for sec in sections:
        y = section_header(draw, RX, y, RW, sec["title"])
        items = sec["items"]
        rows = [items[i:i + 3] for i in range(0, len(items), 3)]
        for row in rows:
            y = draw_items_row(canvas, draw, row, RX, y, RW, cell_h=250)
            y += 8
        y += 26

    # ── Нижняя левая зона: воздушный элемент + палитра ──────
    # низ палитры должен совпасть с нижним полем 80px: 74+130+92+74+88 = 458 → ay = 1968-458
    ay = 1510
    air = spec.get("airy")
    if air:
        y2 = section_header(draw, M, ay, 800, air["title"])
        draw_item(canvas, draw, air["img"], (M, y2, M + 800, y2 + 130),
                  air.get("label", ""), air.get("sublabel", ""))
        pal_y = y2 + 130 + 92
    else:
        pal_y = ay

    # Палитра
    palette = spec.get("palette", [])
    if palette:
        py = section_header(draw, M, pal_y, 800, "Палитра")
        r = 42
        gap = 32
        for i, hexcol in enumerate(palette[:7]):
            cx = M + r + i * (2 * r + gap)
            cy = py + r + 4
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hex_to_rgb(hexcol),
                         outline=(90, 104, 98), width=2)

    # ── Нижняя правая зона: структура и форма ───────────────
    st = spec.get("structure")
    if st:
        sy = ay
        sy = section_header(draw, RX, sy, RW, st.get("title", "Структура и форма"))
        thumb = Image.open(st["img"])
        tx, ty, tw, th = paste_fit(canvas, thumb, (RX, sy, RX + 380, sy + 360))
        f_note = font(32, 500)
        f_sub = font(27, 400, italic=True)
        notes = st.get("notes", [])
        nx0 = RX + 460
        for i, note in enumerate(notes):
            ny = sy + 18 + i * 68
            # линия от букета к подписи
            draw.line([(RX + 380 + 8, ny + 18), (nx0 - 12, ny + 18)], fill=(90, 104, 98), width=2)
            draw.ellipse([nx0 - 16, ny + 14, nx0 - 8, ny + 22], fill=CREAM)
            title, _, sub = note.partition("|")
            draw.text((nx0, ny), title.strip(), font=f_note, fill=CREAM)
            if sub:
                draw.text((nx0 + text_w(draw, title.strip(), f_note) + 10, ny + 4),
                          f"({sub.strip()})", font=f_sub, fill=MUTED)

    canvas.convert("RGB").save(out_path, "PNG")
    print(json.dumps({"saved": out_path, "size": [W, H]}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    compose(a.spec, a.output)
