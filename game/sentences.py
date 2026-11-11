DATA = [
    {"emoji": "🐱", "uz": "Mushuk sut ichadi.",
     "en": ("The cat drinks ___.", "milk", ["car", "book"]),
     "ru": ("Кошка пьёт ___.", "молоко", ["книгу", "машину"]),
     "de": ("Die Katze trinkt ___.", "Milch", ["Auto", "Buch"])},
    {"emoji": "🌞", "uz": "Quyosh osmonda.",
     "en": ("The sun is in the ___.", "sky", ["cup", "shoe"]),
     "ru": ("Солнце на ___.", "небе", ["столе", "полу"]),
     "de": ("Die Sonne scheint am ___.", "Himmel", ["Tisch", "Boden"])},
    {"emoji": "🐶", "uz": "It yugura oladi.",
     "en": ("The dog can ___.", "run", ["read", "cook"]),
     "ru": ("Собака умеет ___.", "бегать", ["читать", "готовить"]),
     "de": ("Der Hund kann ___.", "laufen", ["lesen", "kochen"])},
    {"emoji": "🚗", "uz": "Mashina yo'lda yuradi.",
     "en": ("The car drives on the ___.", "road", ["cloud", "wave"]),
     "ru": ("Машина едет по ___.", "дороге", ["облаку", "волне"]),
     "de": ("Das Auto fährt auf der ___.", "Straße", ["Wolke", "Welle"])},
    {"emoji": "🐟", "uz": "Baliq suvda suzadi.",
     "en": ("The fish swims in the ___.", "water", ["tree", "shoe"]),
     "ru": ("Рыба плавает в ___.", "воде", ["небе", "доме"]),
     "de": ("Der Fisch schwimmt im ___.", "Wasser", ["Baum", "Haus"])},
    {"emoji": "🍎", "uz": "Olma daraxtda o'sadi.",
     "en": ("Apples grow on ___.", "trees", ["cars", "clocks"]),
     "ru": ("Яблоки растут на ___.", "деревьях", ["машинах", "часах"]),
     "de": ("Äpfel wachsen an ___.", "Bäumen", ["Autos", "Uhren"])},
    {"emoji": "🌙", "uz": "Oy kechasi porlaydi.",
     "en": ("The moon shines at ___.", "night", ["noon", "lunch"]),
     "ru": ("Луна светит ___.", "ночью", ["днём", "утром"]),
     "de": ("Der Mond scheint in der ___.", "Nacht", ["Sonne", "Schule"])},
    {"emoji": "📘", "uz": "Biz kitob o'qiymiz.",
     "en": ("We ___ a book.", "read", ["eat", "drive"]),
     "ru": ("Мы ___ книгу.", "читаем", ["едим", "пьём"]),
     "de": ("Wir ___ ein Buch.", "lesen", ["essen", "fahren"])},
    {"emoji": "⏰", "uz": "Soat vaqtni ko'rsatadi.",
     "en": ("A clock shows the ___.", "time", ["milk", "dog"]),
     "ru": ("Часы показывают ___.", "время", ["молоко", "собаку"]),
     "de": ("Eine Uhr zeigt die ___.", "Zeit", ["Milch", "Katze"])},
    {"emoji": "🎈", "uz": "Sharcha havoda uchadi.",
     "en": ("The balloon flies in the ___.", "air", ["soup", "shoe"]),
     "ru": ("Шарик летит в ___.", "воздухе", ["супе", "чашке"]),
     "de": ("Der Ballon fliegt in der ___.", "Luft", ["Suppe", "Tasche"])},
]


def sentences_for(lang):
    if lang not in ("en", "ru", "de"):
        lang = "en"
    out = []
    for d in DATA:
        text, answer, wrong = d[lang]
        out.append({
            "emoji": d["emoji"], "uz": d["uz"], "text": text,
            "answer": answer, "options": [answer] + wrong,
        })
    return out