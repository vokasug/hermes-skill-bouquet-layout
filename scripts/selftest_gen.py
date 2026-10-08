#!/usr/bin/env python3
"""Самопроверка сборщика раскладки на placeholder-изображениях."""
import json
import os
from PIL import Image, ImageDraw

BASE = os.path.join(os.getcwd(), "selftest")
os.makedirs(BASE, exist_ok=True)

colors = ["#8e2f4e", "#c65b74", "#e9a1ad", "#f3e7c9", "#7fa05a",
          "#4e6b3c", "#6b4a38", "#2f4f2f", "#a34a5e", "#d9c07a"]
for i, c in enumerate(colors):
    img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    shape = ["circle", "ellipse", "stem"][i % 3]
    if shape == "circle":
        d.ellipse([60, 60, 340, 340], fill=c)
    elif shape == "ellipse":
        d.ellipse([40, 100, 360, 300], fill=c)
    else:
        d.ellipse([150, 30, 250, 200], fill=c)
        d.rectangle([193, 180, 207, 380], fill=(60, 90, 60))
    img.save(f"{BASE}/c{i+1}.png")

img = Image.new("RGBA", (700, 1200), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.ellipse([100, 50, 600, 700], fill="#8e2f4e")
d.ellipse([180, 150, 520, 620], fill="#c65b74")
d.rectangle([330, 600, 370, 1150], fill=(60, 90, 60))
img.save(f"{BASE}/bouquet.png")

spec = {
    "brand": {"name": "Кот и Клевер", "tagline": "МАСТЕРСКАЯ ЦВЕТОВ И ДЕКОРА · МОСКВА"},
    "bouquet": f"{BASE}/bouquet.png",
    "sections": [
        {"title": "Главные цветы", "items": [
            {"img": f"{BASE}/c1.png", "label": "Георгин", "sublabel": "бордовый"},
            {"img": f"{BASE}/c2.png", "label": "Гвоздика", "sublabel": "светло-розовая"},
            {"img": f"{BASE}/c3.png", "label": "Протея", "sublabel": "королевская"},
            {"img": f"{BASE}/c4.png", "label": "Маттиола", "sublabel": "розовая"},
        ]},
        {"title": "Текстурные акценты", "items": [
            {"img": f"{BASE}/c5.png", "label": "Упаковка", "sublabel": "бумага"},
            {"img": f"{BASE}/c6.png", "label": "Тишью", "sublabel": "розовый"},
        ]},
        {"title": "Зелень", "items": [
            {"img": f"{BASE}/c7.png", "label": "Аспидистра", "sublabel": "листья"},
            {"img": f"{BASE}/c8.png", "label": "Протея", "sublabel": "декоративные"},
            {"img": f"{BASE}/c9.png", "label": "Эвкалипт", "sublabel": "ветка"},
        ]},
    ],
    "airy": {"title": "Воздушный элемент", "img": f"{BASE}/c10.png",
             "label": "Амарантус", "sublabel": "свисающий"},
    "palette": ["#8e2f4e", "#c65b74", "#e9a1ad", "#f3e7c9", "#7fa05a", "#4e6b3c", "#6b4a38"],
    "structure": {"img": f"{BASE}/bouquet.png", "notes": [
        "Вертикаль|высокие элементы",
        "Объём|многослойная композиция",
        "Плотность|сбалансированная",
        "Текстура|контраст фактур",
        "Движение|свисающие элементы",
    ]},
}
with open(f"{BASE}/spec.json", "w", encoding="utf-8") as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)
print("spec written")
