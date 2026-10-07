import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PHONES = [
    ("Samsung Galaxy A56 5G", "Samsung", 22500, 24000, 4.4, 14, 8, 256, 5000, 50, 6.7, "Exynos 1580", 68, 78, 66),
    ("Samsung Galaxy A36 5G", "Samsung", 17500, 18500, 4.3, 20, 8, 128, 5000, 50, 6.7, "Snapdragon 6 Gen 3", 58, 70, 56),
    ("Samsung Galaxy A26 5G", "Samsung", 13500, 14500, 4.1, 18, 6, 128, 5000, 50, 6.7, "Exynos 1380", 48, 62, 46),
    ("Samsung Galaxy A16", "Samsung", 8500, None, 4.0, 30, 4, 128, 5000, 50, 6.7, "Helio G99", 38, 52, 36),
    ("Samsung Galaxy S24 FE", "Samsung", 28500, 31000, 4.5, 9, 8, 256, 4700, 50, 6.7, "Exynos 2400e", 80, 85, 80),
    ("Samsung Galaxy S25", "Samsung", 42000, 45000, 4.7, 6, 12, 256, 4000, 50, 6.2, "Snapdragon 8 Elite", 95, 92, 96),
    ("Xiaomi 14T", "Xiaomi", 24500, 26500, 4.5, 11, 12, 256, 5000, 50, 6.67, "Dimensity 8300 Ultra", 78, 86, 78),
    ("Xiaomi 14T Pro", "Xiaomi", 31000, 33500, 4.6, 7, 12, 512, 5000, 50, 6.67, "Dimensity 9300+", 90, 88, 92),
    ("Redmi Note 14 Pro 5G", "Xiaomi", 15500, 16500, 4.3, 25, 8, 256, 5110, 200, 6.67, "Dimensity 7300 Ultra", 60, 74, 58),
    ("Redmi Note 14", "Xiaomi", 9500, None, 4.1, 28, 6, 128, 5500, 108, 6.67, "Helio G99 Ultra", 40, 58, 38),
    ("Poco X7 Pro", "Xiaomi", 17500, 18500, 4.5, 16, 8, 256, 6000, 50, 6.67, "Dimensity 8400 Ultra", 82, 66, 88),
    ("Poco F7", "Xiaomi", 25000, 27000, 4.6, 10, 12, 256, 6500, 50, 6.83, "Snapdragon 8s Gen 4", 88, 70, 93),
    ("iPhone 15", "Apple", 38000, 41000, 4.7, 8, 6, 128, 3349, 48, 6.1, "A16 Bionic", 86, 90, 88),
    ("iPhone 13", "Apple", 25500, 27500, 4.5, 5, 4, 128, 3240, 12, 6.1, "A15 Bionic", 76, 78, 76),
    ("iPhone 16", "Apple", 48000, 51000, 4.8, 4, 8, 128, 3561, 48, 6.1, "A18", 94, 93, 95),
    ("Realme 13 Pro+ 5G", "Realme", 21000, 23000, 4.3, 12, 12, 256, 5200, 50, 6.7, "Snapdragon 7s Gen 2", 62, 82, 60),
    ("Realme GT 6T", "Realme", 20500, 22500, 4.4, 9, 8, 256, 5500, 50, 6.78, "Snapdragon 7+ Gen 3", 80, 70, 84),
    ("Oppo Reno 12", "Oppo", 22000, 24000, 4.3, 10, 12, 256, 5000, 50, 6.7, "Dimensity 7300", 62, 84, 60),
    ("Oppo A3", "Oppo", 7500, None, 3.9, 0, 4, 128, 5100, 50, 6.67, "Snapdragon 680", 32, 46, 30),
]

LAPTOPS = [
    ("Lenovo IdeaPad Slim 3 15", "Lenovo", 22000, 24000, 4.2, 15, "Intel Core i5-12450H", 8, 512, 15.6, 1.62, "Intel UHD", 7, 55, 30),
    ("Lenovo LOQ 15IRX9", "Lenovo", 38500, 41000, 4.5, 8, "Intel Core i5-12450HX", 16, 512, 15.6, 2.4, "RTX 3050 6GB", 5, 72, 70),
    ("Lenovo ThinkPad E14 Gen 6", "Lenovo", 36000, 38000, 4.4, 6, "Intel Core i5-1335U", 16, 512, 14.0, 1.41, "Intel Iris Xe", 10, 62, 30),
    ("HP 15-fd", "HP", 24500, 26000, 4.1, 18, "Intel Core i5-1334U", 8, 512, 15.6, 1.59, "Intel Iris Xe", 8, 58, 30),
    ("HP Victus 15", "HP", 35500, 38000, 4.3, 10, "Ryzen 5 7535HS", 16, 512, 15.6, 2.3, "RTX 2050 4GB", 6, 68, 62),
    ("HP Pavilion 14", "HP", 31500, 33000, 4.2, 9, "Intel Core i5-1335U", 16, 512, 14.0, 1.4, "Intel Iris Xe", 9, 60, 32),
    ("Dell Inspiron 15 3530", "Dell", 27500, 29500, 4.1, 12, "Intel Core i5-1334U", 8, 512, 15.6, 1.65, "Intel Iris Xe", 7, 57, 30),
    ("Dell Vostro 3520", "Dell", 23500, 25000, 4.0, 14, "Intel Core i3-1215U", 8, 256, 15.6, 1.66, "Intel UHD", 7, 42, 22),
    ("Dell XPS 13 9340", "Dell", None, None, 4.6, 0, "Intel Core Ultra 7 155H", 16, 512, 13.4, 1.19, "Intel Arc", 12, 82, 45),
    ("ASUS Vivobook 15", "ASUS", 26500, 28000, 4.2, 16, "Intel Core i5-13420H", 16, 512, 15.6, 1.7, "Intel UHD", 8, 64, 34),
    ("ASUS TUF Gaming F15", "ASUS", 52000, 56000, 4.6, 7, "Intel Core i7-13620H", 16, 512, 15.6, 2.2, "RTX 4050 6GB", 6, 80, 82),
    ("ASUS Zenbook 14 OLED", "ASUS", 48500, 51000, 4.6, 5, "Intel Core Ultra 5 125H", 16, 512, 14.0, 1.2, "Intel Arc", 12, 74, 40),
    ("Acer Aspire 5", "Acer", 25000, 27000, 4.1, 17, "Intel Core i5-13420H", 8, 512, 15.6, 1.75, "Intel UHD", 8, 60, 32),
    ("Acer Nitro V 15", "Acer", 45000, 48000, 4.4, 8, "Intel Core i5-13420H", 16, 512, 15.6, 2.1, "RTX 4050 6GB", 6, 76, 78),
    ("Acer Swift Go 14", "Acer", 40500, 43000, 4.5, 6, "Intel Core Ultra 5 125H", 16, 512, 14.0, 1.32, "Intel Arc", 11, 72, 38),
]

HEADPHONES = [
    ("Sony WH-CH520", "Sony", 2800, 3200, 4.3, 25, "On-ear", 50, False, 30, "5.2", 60),
    ("Sony WH-1000XM5", "Sony", 15000, 17000, 4.8, 6, "Over-ear", 30, True, 30, "5.2", 95),
    ("Sony WF-C700N", "Sony", 5200, 5800, 4.3, 12, "TWS", 15, True, 5, "5.2", 72),
    ("JBL Tune 520BT", "JBL", 1800, 2100, 4.2, 30, "On-ear", 57, False, 32, "5.3", 55),
    ("JBL Tune 770NC", "JBL", 4200, 4800, 4.4, 14, "Over-ear", 70, True, 40, "5.3", 72),
    ("JBL Live Pro 2 TWS", "JBL", 5500, 6200, 4.4, 10, "TWS", 40, True, 11, "5.3", 78),
    ("Anker Soundcore Life Q30", "Anker", 3800, 4200, 4.5, 15, "Over-ear", 60, True, 40, "5.0", 74),
    ("Anker Soundcore P40i", "Anker", 2600, 3000, 4.3, 20, "TWS", 60, True, 11, "5.3", 66),
    ("Anker Soundcore Space One", "Anker", 4800, 5400, 4.5, 9, "Over-ear", 40, True, 40, "5.3", 80),
    ("Samsung Galaxy Buds FE", "Samsung", 3600, 4200, 4.2, 13, "TWS", 30, True, 12, "5.4", 70),
    ("Xiaomi Redmi Buds 6 Pro", "Xiaomi", 2400, 2800, 4.3, 19, "TWS", 36, True, 12, "5.3", 70),
    ("Apple AirPods 4 ANC", "Apple", 9500, 10500, 4.6, 7, "TWS", 30, True, 11, "5.3", 82),
]

PHONE_REV = {
    "camera": {
        2: [("The camera is superb in daylight and holds up well at night.", "الكاميرا ممتازة في النهار وكويسة جدا بالليل."),
            ("Photos look sharp with great colors, one of the best cameras at this price.", "الصور واضحة وألوانها حلوة، من أحسن الكاميرات في السعر ده.")],
        1: [("Camera is decent in good light but struggles at night.", "الكاميرا كويسة في الإضاءة الكويسة بس ضعيفة بالليل."),
            ("Photos are fine for social media, nothing special.", "الصور مناسبة للسوشيال ميديا ومفيهاش حاجة مميزة.")],
        0: [("The camera is basic and noisy in low light.", "الكاميرا عادية وفيها تشويش في الإضاءة الضعيفة."),
            ("Photo quality is disappointing for the price.", "جودة الصور مش حلوة بالنسبة للسعر.")],
    },
    "gaming": {
        2: [("Runs heavy games like PUBG and Genshin smoothly at high settings.", "بيشغل الألعاب التقيلة زي ببجي وجينشن بسلاسة على إعدادات عالية."),
            ("Excellent for gaming, stays smooth with no frame drops.", "ممتاز للجيمنج ومفيش هنج ولا نزول في الفريمات.")],
        1: [("Handles casual games fine but heavy games need medium settings.", "بيشغل الألعاب العادية كويس والتقيلة محتاجة إعدادات متوسطة."),
            ("Gaming is acceptable, it heats up a bit after long sessions.", "الجيمنج مقبول وبيسخن شوية بعد وقت طويل.")],
        0: [("Not suited to gaming, heavy titles lag noticeably.", "مش مناسب للجيمنج والألعاب التقيلة بتهنج."),
            ("Struggles with modern games.", "بيتعب مع الألعاب الحديثة.")],
    },
    "battery": {
        2: [("Battery easily lasts a full day and a half with heavy use.", "البطارية بتكمل يوم ونص بسهولة مع استخدام تقيل."),
            ("Great battery life, charging is quick as well.", "بطارية ممتازة والشحن سريع.")],
        1: [("Battery gets me through the day but needs charging every night.", "البطارية بتكمل اليوم بس لازم أشحن كل ليلة."),
            ("Battery life is average.", "عمر البطارية متوسط.")],
        0: [("Battery drains fast under heavy use.", "البطارية بتخلص بسرعة مع الاستخدام الكتير.")],
    },
    "value": {
        2: [("Excellent value for money compared with rivals.", "قيمة ممتازة مقابل السعر مقارنة بالمنافسين."),
            ("Hard to beat at this price.", "صعب تلاقي أحسن منه في السعر ده.")],
        1: [("Fair price, though similar options exist.", "سعر معقول بس فيه بدائل مشابهة.")],
        0: [("Overpriced for what it offers.", "غالي بالنسبة للي بيقدمه.")],
    },
    "display": {
        2: [("The display is bright and smooth, a joy to watch videos on.", "الشاشة مضيئة وسلسة وممتعة جدا في مشاهدة الفيديو.")],
        1: [("Display is good but not the brightest outdoors.", "الشاشة كويسة بس مش مضيئة أوي في الشمس.")],
        0: [("Display is dull compared to competitors.", "الشاشة باهتة مقارنة بالمنافسين.")],
    },
}

LAPTOP_REV = {
    "performance": {
        2: [("Very fast, handles coding, VMs and multitasking without slowdowns.", "سريع جدا وبيشغل البرمجة والـ VMs والمالتي تاسكينج بدون بطء."),
            ("Great performance for programming and heavy workloads.", "أداء ممتاز للبرمجة والشغل التقيل.")],
        1: [("Good for office work and light programming.", "كويس للشغل المكتبي والبرمجة الخفيفة."),
            ("Performance is adequate for daily tasks.", "الأداء مناسب للمهام اليومية.")],
        0: [("Slow with many tabs open, only good for basic tasks.", "بطيء مع تابات كتير ومناسب للمهام الأساسية بس.")],
    },
    "gaming": {
        2: [("The dedicated GPU runs modern games at high settings.", "كارت الشاشة المنفصل بيشغل الألعاب الحديثة على إعدادات عالية.")],
        1: [("Can play esports titles at medium settings.", "بيشغل ألعاب الإيسبورتس على إعدادات متوسطة.")],
        0: [("Not meant for gaming at all.", "مش مخصص للجيمنج خالص.")],
    },
    "battery": {
        2: [("Battery lasts a full work day, I rarely carry the charger.", "البطارية بتكمل يوم شغل كامل ونادرا بشيل الشاحن.")],
        1: [("Battery gives around five to six hours of real use.", "البطارية بتدي حوالي خمس لست ساعات استخدام فعلي.")],
        0: [("Battery is weak, it needs the charger nearby.", "البطارية ضعيفة ومحتاج الشاحن قريب.")],
    },
    "portability": {
        2: [("Light and thin, perfect to carry to university every day.", "خفيف ورفيع ومناسب جدا أشيله للجامعة كل يوم.")],
        1: [("Reasonably portable but not the lightest.", "محمول بشكل معقول بس مش الأخف.")],
        0: [("Heavy and bulky to carry around.", "تقيل وكبير في الحمل.")],
    },
    "value": {
        2: [("Great price for the specs you get.", "سعر ممتاز مقابل المواصفات.")],
        1: [("Fair price for what it is.", "سعر معقول بالنسبة للمواصفات.")],
        0: [("Expensive for the hardware offered.", "غالي بالنسبة للهاردوير.")],
    },
}

HP_REV = {
    "sound": {
        2: [("Sound quality is rich and detailed with deep bass.", "جودة الصوت غنية وتفاصيله واضحة والباص عميق.")],
        1: [("Sound is good for everyday listening.", "الصوت كويس للاستماع اليومي.")],
        0: [("Sound is average and a little flat.", "الصوت عادي وشوية مسطح.")],
    },
    "anc": {
        2: [("Noise cancelling blocks out the metro and traffic very well.", "العزل بيمنع ضوضاء المترو والشارع بشكل ممتاز.")],
        1: [("Noise cancelling is decent but not class leading.", "العزل كويس بس مش الأفضل.")],
        0: [("No noise cancelling, outside noise leaks in.", "مفيش عزل للضوضاء والصوت الخارجي بيدخل.")],
    },
    "battery": {
        2: [("Battery lasts days between charges.", "البطارية بتكمل أيام بين الشحنات.")],
        1: [("Battery is enough for a full day of use.", "البطارية كفاية لاستخدام يوم كامل.")],
        0: [("Battery life is short.", "عمر البطارية قصير.")],
    },
    "value": {
        2: [("Amazing value at this price.", "قيمة رهيبة في السعر ده.")],
        1: [("Reasonable price.", "سعر معقول.")],
        0: [("Pricey compared with alternatives.", "غالية مقارنة بالبدائل.")],
    },
}


def lvl(x, lo, hi):
    return 2 if x >= hi else (1 if x >= lo else 0)


def make_reviews(pid, rating, aspects, table, rng, count=5):
    keys = list(aspects)
    rng.shuffle(keys)
    out = []
    for i in range(count):
        asp = keys[i % len(keys)]
        level = aspects[asp]
        variants = table[asp].get(level) or next(iter(table[asp].values()))
        en, ar = rng.choice(variants)
        text = ar if rng.random() < 0.4 else en
        r = max(1, min(5, round(rating + {2: 0.4, 1: -0.2, 0: -1.3}[level] + rng.uniform(-0.3, 0.3))))
        out.append({"product_id": pid, "review_text": text, "rating": r, "source": "synthetic-sample", "aspect": asp})
    return out


def main():
    rng = random.Random(2026)
    products, reviews = [], []
    pid = 0

    for (name, brand, price, old, rating, stock, ram, sto, bat, cam, disp, chip, perf, camsc, game) in PHONES:
        pid += 1
        specs = {"ram_gb": ram, "storage_gb": sto, "battery_mah": bat, "main_camera_mp": cam, "display_inches": disp,
                 "chipset": chip, "performance_score": perf, "camera_score": camsc, "gaming_score": game}
        desc = f"{name} smartphone powered by {chip} with {ram}GB RAM, {sto}GB storage, a {disp} inch display, a {cam}MP main camera and a {bat}mAh battery."
        products.append(dict(id=pid, name=name, brand=brand, category="smartphone", price=price, old_price=old, description=desc,
                             rating=rating, stock=stock, source="catalog", url=f"https://example.com/p/{pid}", image_url="", specs=specs))
        aspects = {"camera": lvl(camsc, 60, 78), "gaming": lvl(game, 55, 78), "battery": lvl(bat, 4000, 5000),
                   "value": lvl(perf / max(price, 1) * 10000, 25, 45), "display": lvl(disp, 6.3, 6.6)}
        reviews += make_reviews(pid, rating, aspects, PHONE_REV, rng)

    for (name, brand, price, old, rating, stock, cpu, ram, sto, disp, wt, gpu, bh, perf, game) in LAPTOPS:
        pid += 1
        specs = {"cpu": cpu, "ram_gb": ram, "storage_gb": sto, "display_inches": disp, "weight_kg": wt, "gpu": gpu,
                 "battery_hours": bh, "performance_score": perf, "gaming_score": game}
        desc = f"{name} laptop with {cpu}, {ram}GB RAM, {sto}GB SSD, {gpu} graphics and a {disp} inch display weighing {wt}kg."
        products.append(dict(id=pid, name=name, brand=brand, category="laptop", price=price, old_price=old, description=desc,
                             rating=rating, stock=stock, source="catalog", url=f"https://example.com/p/{pid}", image_url="", specs=specs))
        aspects = {"performance": lvl(perf, 55, 72), "gaming": lvl(game, 45, 70), "battery": lvl(bh, 7, 10),
                   "portability": lvl(-wt, -2.0, -1.5), "value": lvl(perf / max(price or 1, 1) * 10000, 18, 24)}
        reviews += make_reviews(pid, rating, aspects, LAPTOP_REV, rng)

    for (name, brand, price, old, rating, stock, typ, bh, anc, drv, bt, snd) in HEADPHONES:
        pid += 1
        specs = {"type": typ, "battery_hours": bh, "anc": anc, "driver_mm": drv, "bluetooth": bt, "performance_score": snd}
        desc = f"{name} {typ.lower()} headphones with {'active noise cancelling' if anc else 'no active noise cancelling'}, {bh} hours of battery and Bluetooth {bt}."
        products.append(dict(id=pid, name=name, brand=brand, category="headphones", price=price, old_price=old, description=desc,
                             rating=rating, stock=stock, source="catalog", url=f"https://example.com/p/{pid}", image_url="", specs=specs))
        aspects = {"sound": lvl(snd, 62, 76), "anc": 2 if anc and snd >= 74 else (1 if anc else 0),
                   "battery": lvl(bh, 20, 45), "value": lvl(snd / max(price, 1) * 1000, 8, 16)}
        reviews += make_reviews(pid, rating, aspects, HP_REV, rng, count=4)

    for i, r in enumerate(reviews, 1):
        r["id"] = i

    (ROOT / "data/products/products.json").write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")
    (ROOT / "data/reviews/reviews.json").write_text(json.dumps(reviews, indent=2, ensure_ascii=False), encoding="utf-8")
    print(len(products), "products", len(reviews), "reviews")


if __name__ == "__main__":
    main()
