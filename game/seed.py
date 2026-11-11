from .models import Topic, Word

DATA = {
    "animals": ("Hayvonlar", "🐾", [
        ("🐱", "cat", "mushuk"), ("🐶", "dog", "it"), ("🐟", "fish", "baliq"),
        ("🐦", "bird", "qush"), ("🐴", "horse", "ot"), ("🐄", "cow", "sigir"),
        ("🐑", "sheep", "qo'y"), ("🐘", "elephant", "fil"), ("🦁", "lion", "sher"),
        ("🐵", "monkey", "maymun"),
    ]),
    "fruits": ("Meva va sabzavotlar", "🍎", [
        ("🍎", "apple", "olma"), ("🍌", "banana", "banan"), ("🍇", "grapes", "uzum"),
        ("🍉", "watermelon", "tarvuz"), ("🍊", "orange", "apelsin"),
        ("🍓", "strawberry", "qulupnay"), ("🍑", "peach", "shaftoli"),
        ("🥕", "carrot", "sabzi"), ("🍅", "tomato", "pomidor"), ("🥔", "potato", "kartoshka"),
    ]),
    "transport": ("Transport", "🚗", [
        ("🚗", "car", "mashina"), ("🚌", "bus", "avtobus"), ("🚲", "bicycle", "velosiped"),
        ("✈️", "plane", "samolyot"), ("🚂", "train", "poyezd"), ("🚢", "ship", "kema"),
        ("🚁", "helicopter", "vertolyot"), ("🏍️", "motorcycle", "mototsikl"),
        ("🚒", "fire truck", "o't o'chirish mashinasi"), ("🚀", "rocket", "raketa"),
    ]),
    "things": ("Buyumlar va tabiat", "🌞", [
        ("🌞", "sun", "quyosh"), ("🌙", "moon", "oy"), ("⭐", "star", "yulduz"),
        ("🌳", "tree", "daraxt"), ("🌸", "flower", "gul"), ("📘", "book", "kitob"),
        ("🏠", "house", "uy"), ("⚽", "ball", "to'p"), ("⏰", "clock", "soat"),
        ("🎈", "balloon", "sharcha"),
    ]),
}


def load():
    for i, (key, (title, icon, words)) in enumerate(DATA.items()):
        t, _ = Topic.objects.get_or_create(
            key=key, defaults={"title": title, "icon": icon, "order": i})
        for emoji, en, uz in words:
            Word.objects.get_or_create(topic=t, en=en, defaults={"emoji": emoji, "uz": uz})
    print("Tayyor:", Topic.objects.count(), "mavzu,", Word.objects.count(), "so'z")