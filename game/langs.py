from .models import Word

TR = {
    "cat": ("кошка", "Katze"), "dog": ("собака", "Hund"), "fish": ("рыба", "Fisch"),
    "bird": ("птица", "Vogel"), "horse": ("лошадь", "Pferd"), "cow": ("корова", "Kuh"),
    "sheep": ("овца", "Schaf"), "elephant": ("слон", "Elefant"), "lion": ("лев", "Löwe"),
    "monkey": ("обезьяна", "Affe"),
    "apple": ("яблоко", "Apfel"), "banana": ("банан", "Banane"),
    "grapes": ("виноград", "Trauben"), "watermelon": ("арбуз", "Wassermelone"),
    "orange": ("апельсин", "Orange"), "strawberry": ("клубника", "Erdbeere"),
    "peach": ("персик", "Pfirsich"), "carrot": ("морковь", "Karotte"),
    "tomato": ("помидор", "Tomate"), "potato": ("картофель", "Kartoffel"),
    "car": ("машина", "Auto"), "bus": ("автобус", "Bus"), "bicycle": ("велосипед", "Fahrrad"),
    "plane": ("самолет", "Flugzeug"), "train": ("поезд", "Zug"), "ship": ("корабль", "Schiff"),
    "helicopter": ("вертолет", "Hubschrauber"), "motorcycle": ("мотоцикл", "Motorrad"),
    "fire truck": ("пожарная машина", "Feuerwehrauto"), "rocket": ("ракета", "Rakete"),
    "sun": ("солнце", "Sonne"), "moon": ("луна", "Mond"), "star": ("звезда", "Stern"),
    "tree": ("дерево", "Baum"), "flower": ("цветок", "Blume"), "book": ("книга", "Buch"),
    "house": ("дом", "Haus"), "ball": ("мяч", "Ball"), "clock": ("часы", "Uhr"),
    "balloon": ("воздушный шар", "Luftballon"),
}


def load():
    n = 0
    for w in Word.objects.all():
        t = TR.get(w.en)
        if t:
            w.ru, w.de = t
            w.save()
            n += 1
    print("Tarjima qo'shildi:", n, "ta so'z")