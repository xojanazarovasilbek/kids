import json
from datetime import timedelta
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Profile, Topic, Word, Pet, WordStat
from .sentences import sentences_for

STICKERS = [
    {"need": 5, "emoji": "🐣", "name": "Jo'ja"},
    {"need": 10, "emoji": "🐢", "name": "Toshbaqa"},
    {"need": 20, "emoji": "🦄", "name": "Yagona ot"},
    {"need": 30, "emoji": "🐼", "name": "Panda"},
    {"need": 40, "emoji": "🦖", "name": "Dinozavr"},
    {"need": 50, "emoji": "🚀", "name": "Raketa"},
    {"need": 75, "emoji": "🐉", "name": "Ajdaho"},
    {"need": 100, "emoji": "👑", "name": "Toj"},
    {"need": 150, "emoji": "🏆", "name": "Kubok"},
    {"need": 200, "emoji": "🌈", "name": "Kamalak"},
]

LANGS = [
    {"code": "en", "name": "English", "speech": "en-US"},
    {"code": "ru", "name": "Русский", "speech": "ru-RU"},
    {"code": "de", "name": "Deutsch", "speech": "de-DE"},
]

PET_KINDS = ["🐱", "🐶", "🐰", "🦊", "🐼", "🦖", "🐯", "🐸", "🐵", "🦄", "🐧", "🐲"]
MAX_PETS = 6
ADOPT_COST = 25
SHOP = [
    {"id": "cap", "emoji": "🧢", "name": "Kepka", "price": 8, "slot": "hat"},
    {"id": "bow", "emoji": "🎀", "name": "Bant", "price": 8, "slot": "hat"},
    {"id": "tophat", "emoji": "🎩", "name": "Shlyapa", "price": 12, "slot": "hat"},
    {"id": "crown", "emoji": "👑", "name": "Toj", "price": 30, "slot": "hat"},
    {"id": "glasses", "emoji": "🕶️", "name": "Ko'zoynak", "price": 10, "slot": "face"},
    {"id": "nerd", "emoji": "🤓", "name": "Aqlli ko'zoynak", "price": 15, "slot": "face"},
    {"id": "scarf", "emoji": "🧣", "name": "Sharf", "price": 12, "slot": "neck"},
    {"id": "medal", "emoji": "🏅", "name": "Medal", "price": 20, "slot": "neck"},
]
FEED_COST = 2
FEED_AMOUNT = 25

LEVEL_STARS = [0, 10, 25, 50, 80, 120, 170, 230]
REWARD = {"pick": 1, "listen": 1, "spell": 2, "memory": 3, "sentence": 2, "say": 2}

# Kunlik vazifalar (min_level: shu darajadan boshlab ko'rinadi)
TASKS = [
    {"id": "correct", "emoji": "✅", "text": "10 ta to'g'ri javob ber", "need": 10, "reward": 5, "min_level": 1},
    {"id": "say", "emoji": "🎤", "text": "3 ta so'zni ovozda ayt", "need": 3, "reward": 5, "min_level": 2},
    {"id": "sentence", "emoji": "🧩", "text": "3 ta gapni to'ldir", "need": 3, "reward": 5, "min_level": 3},
    {"id": "memory", "emoji": "🧠", "text": "Xotira o'yinini yut", "need": 1, "reward": 5, "min_level": 4},
]

# O'yin vaqti: har 3 soat ichida 20 daqiqa
WINDOW = timedelta(hours=3)
LIMIT = 20 * 60


def level_of(stars):
    return sum(1 for n in LEVEL_STARS if stars >= n)


def get_profile(user):
    return Profile.objects.get_or_create(user=user)[0]


def lang_info(code):
    return next((l for l in LANGS if l["code"] == code), LANGS[0])


def lang_words(lang, qs, user=None):
    """Tanlangan tildagi so'zlar. 'en' kaliti ichida o'sha tildagi so'z turadi.
    box: -1 = yangi so'z, 0 = qiyin ... 4 = yaxshi biladi."""
    if lang not in ("en", "ru", "de"):
        lang = "en"
    boxes = {}
    if user is not None:
        boxes = dict(WordStat.objects.filter(user=user).values_list("word_id", "box"))
    out = []
    for w in qs.values("id", "emoji", "en", "ru", "de", "uz"):
        target = w[lang]
        if target:
            out.append({
                "id": w["id"], "emoji": w["emoji"], "en": target,
                "uz": w["uz"], "box": boxes.get(w["id"], -1),
            })
    return out


# ---------- Kunlik vazifalar ----------

def task_state(p):
    today = timezone.localdate()
    if p.task_day != today:
        p.task_day = today
        p.task_prog = {}
        p.save()
    lv = level_of(p.stars)
    out = []
    for t in TASKS:
        if lv >= t["min_level"]:
            have = min(p.task_prog.get(t["id"], 0), t["need"])
            out.append({**t, "have": have, "done": have >= t["need"],
                        "pct": int(have / t["need"] * 100)})
    return out


def bump_task(p, key, n=1):
    """Vazifa progressini oshiradi. Bajarilgan vazifalar ro'yxatini qaytaradi.
    p.save() ni chaqiruvchi bajaradi."""
    task_state(p)
    t = next((x for x in TASKS if x["id"] == key), None)
    if not t or level_of(p.stars) < t["min_level"]:
        return []
    prog = dict(p.task_prog)
    before = prog.get(key, 0)
    after = before + n
    prog[key] = after
    p.task_prog = prog
    if before < t["need"] <= after:
        p.stars += t["reward"]
        return [t]
    return []


# ---------- O'yin vaqti ----------

def play_time(p):
    """(qolgan soniya, kutish soniyasi) ni qaytaradi."""
    now = timezone.now()
    if p.win_start and now - p.win_start >= WINDOW:
        p.win_start = None
        p.win_used = 0
        p.last_tick = None
        p.save()
    left = max(0, LIMIT - p.win_used)
    wait = 0
    if left == 0 and p.win_start:
        wait = max(0, int((p.win_start + WINDOW - now).total_seconds()))
    return left, wait


def time_text(left, wait):
    if left > 0:
        return f"⏳ Hozir o'ynash mumkin: {left // 60 + (1 if left % 60 else 0)} daqiqa"
    h, m = divmod(wait // 60 + 1, 60)
    return f"🌙 Dam olish vaqti. Keyingi o'yin: {h} soat {m} daqiqadan keyin"


def home_ctx(p, **extra):
    left, wait = play_time(p)
    ts = task_state(p)
    ctx = {
        "topics": Topic.objects.all(),
        "stars": p.stars, "level": level_of(p.stars), "streak": p.streak,
        "lang": p.lang, "langs": LANGS,
        "time_text": time_text(left, wait),
        "tasks_text": f"{sum(1 for t in ts if t['done'])}/{len(ts)}",
    }
    ctx.update(extra)
    return ctx


def claim_daily(p):
    """Kunlik bonusni beradi. Bugun allaqachon olingan bo'lsa None qaytaradi."""
    today = timezone.localdate()
    if p.last_day == today:
        return None
    if p.last_day == today - timedelta(days=1):
        p.streak += 1
    else:
        p.streak = 1
    p.last_day = today
    base = 3
    extra = 0
    if p.streak % 7 == 0:
        extra = 15
    elif p.streak % 3 == 0:
        extra = 5
    p.stars += base + extra
    p.save()
    return {"base": base, "extra": extra, "total": base + extra}


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()
    return render(request, "game/signup.html", {"form": form})


@login_required
def home(request):
    p = get_profile(request.user)
    bonus = claim_daily(p)
    return render(request, "game/home.html", home_ctx(p, bonus=bonus))


@login_required
@require_POST
def set_lang(request):
    code = request.POST.get("lang")
    if code in [l["code"] for l in LANGS]:
        p = get_profile(request.user)
        p.lang = code
        p.save()
    return redirect("/")


@login_required
@require_POST
def tick(request):
    """O'yin sahifasi har 10 soniyada chaqiradi. Vaqtni server hisoblaydi."""
    p = get_profile(request.user)
    left, wait = play_time(p)
    if left > 0:
        now = timezone.now()
        if p.win_start is None:
            p.win_start = now
        if p.last_tick:
            gap = (now - p.last_tick).total_seconds()
            if 0 < gap <= 20:
                p.win_used += int(gap)
        p.last_tick = now
        p.save()
        left, wait = play_time(p)
    return JsonResponse({"left": left, "wait": wait})


@login_required
def play(request, key):
    topic = Topic.objects.filter(key=key).first()
    if not topic:
        return redirect("/")
    p = get_profile(request.user)
    left, wait = play_time(p)
    if left <= 0:
        return render(request, "game/rest.html", {"wait": wait})
    words = lang_words(p.lang, topic.words.all(), request.user)
    if len(words) < 6:
        return render(request, "game/home.html", home_ctx(
            p, error="Bu mavzuda shu tilda kamida 6 ta so'z bo'lishi kerak."))
    return render(request, "game/play.html", {
        "words": words, "title": topic.title,
        "stars": p.stars, "level_stars": LEVEL_STARS,
        "speech": lang_info(p.lang)["speech"],
        "sentences": sentences_for(p.lang),
        "time_left": left,
    })


@login_required
@require_POST
def answer(request):
    """Har bir so'z bo'yicha to'g'ri/xato natijani saqlaydi (takrorlash tizimi)."""
    try:
        body = json.loads(request.body)
        wid = int(body.get("word"))
        ok = bool(body.get("ok"))
    except (ValueError, TypeError, AttributeError):
        return JsonResponse({"ok": False}, status=400)
    w = Word.objects.filter(id=wid).first()
    if not w:
        return JsonResponse({"ok": False}, status=404)
    st, _ = WordStat.objects.get_or_create(user=request.user, word=w)
    if ok:
        st.right += 1
        st.box = min(4, st.box + 1)
    else:
        st.wrong += 1
        st.box = 0
    st.save()
    return JsonResponse({"ok": True})


@login_required
def tasks(request):
    p = get_profile(request.user)
    ts = task_state(p)
    return render(request, "game/tasks.html", {
        "tasks": ts, "done": sum(1 for t in ts if t["done"]),
    })


@login_required
def stickers(request):
    p = get_profile(request.user)
    return render(request, "game/stickers.html", {
        "stickers": STICKERS, "stars": p.stars,
    })


@login_required
def profile(request):
    p = get_profile(request.user)
    lv = level_of(p.stars)
    nxt = LEVEL_STARS[lv] if lv < len(LEVEL_STARS) else None
    opened = [s for s in STICKERS if p.stars >= s["need"]]
    stats = WordStat.objects.filter(user=request.user).select_related("word")
    learned = stats.filter(box__gte=3).count()
    hard = []
    for s in stats.filter(wrong__gt=0, box__lte=1).order_by("box", "-wrong")[:5]:
        hard.append({
            "emoji": s.word.emoji,
            "text": getattr(s.word, p.lang, "") or s.word.en,
            "uz": s.word.uz,
        })
    return render(request, "game/profile.html", {
        "p": p, "level": lv,
        "to_next": (nxt - p.stars) if nxt else 0,
        "opened": opened, "total_stickers": len(STICKERS),
        "learned": learned, "hard": hard,
    })


@login_required
@require_POST
def add_star(request):
    try:
        kind = json.loads(request.body).get("kind")
    except ValueError:
        kind = None
    amount = REWARD.get(kind, 0)
    p = get_profile(request.user)
    old = p.stars
    p.stars += amount
    done = []
    if amount:
        p.correct += 1
        done += bump_task(p, "correct")
        if kind in ("memory", "sentence", "say"):
            done += bump_task(p, kind)
    p.save()
    new_sticker = next((s for s in STICKERS if old < s["need"] <= p.stars), None)
    return JsonResponse({
        "stars": p.stars,
        "level": level_of(p.stars),
        "sticker": new_sticker,
        "tasks": [{"emoji": t["emoji"], "text": t["text"], "reward": t["reward"]} for t in done],
    })


@login_required
def speed(request):
    p = get_profile(request.user)
    left, wait = play_time(p)
    if left <= 0:
        return render(request, "game/rest.html", {"wait": wait})
    words = lang_words(p.lang, Word.objects.all())
    if len(words) < 8:
        return redirect("/")
    return render(request, "game/speed.html", {
        "words": words, "best": p.best_speed, "stars": p.stars,
        "level_stars": LEVEL_STARS,
        "speech": lang_info(p.lang)["speech"],
        "time_left": left,
    })


@login_required
@require_POST
def add_speed(request):
    try:
        count = int(json.loads(request.body).get("count", 0))
    except (ValueError, TypeError, AttributeError):
        count = 0
    count = max(0, min(count, 40))
    p = get_profile(request.user)
    old = p.stars
    gained = count // 2
    record = count > p.best_speed
    if record:
        p.best_speed = count
        gained += 3
    p.stars += gained
    p.correct += count
    p.save()
    new_sticker = next((s for s in STICKERS if old < s["need"] <= p.stars), None)
    return JsonResponse({
        "stars": p.stars, "gained": gained, "record": record,
        "best": p.best_speed, "level": level_of(p.stars),
        "sticker": new_sticker,
    })


# ---------- Uy hayvonlari ----------

def active_pet(user, p):
    pets = list(Pet.objects.filter(user=user).order_by("id"))
    pet = next((x for x in pets if x.id == p.active_pet), None)
    if pet is None and pets:
        pet = pets[0]
    return pet, pets


def pet_state(user):
    p = get_profile(user)
    pet, pets = active_pet(user, p)
    data = {
        "stars": p.stars - p.spent,
        "shop": SHOP, "kinds": PET_KINDS,
        "adopt_cost": ADOPT_COST if pets else 0,
        "max_pets": MAX_PETS,
        "pet": None,
        "pets": [{"id": x.id, "kind": x.kind, "name": x.name,
                  "fullness": x.current_fullness()} for x in pets],
        "words": lang_words(p.lang, Word.objects.all()),
        "speech": lang_info(p.lang)["speech"],
    }
    if pet:
        data["pet"] = {
            "id": pet.id, "kind": pet.kind, "name": pet.name,
            "fullness": pet.current_fullness(),
            "items": pet.items, "equipped": pet.equipped,
        }
    return data


@login_required
def pet_page(request):
    return render(request, "game/pet.html", {"state": pet_state(request.user)})


@login_required
@require_POST
def pet_action(request):
    try:
        body = json.loads(request.body)
    except ValueError:
        body = {}
    action = body.get("action")
    p = get_profile(request.user)
    pet, pets = active_pet(request.user, p)
    free = p.stars - p.spent
    error = None

    if action == "adopt":
        kind = body.get("kind")
        name = str(body.get("name", "")).strip()[:20] or "Do'stim"
        cost = ADOPT_COST if pets else 0
        if kind not in PET_KINDS:
            error = "Hayvonni tanlang"
        elif len(pets) >= MAX_PETS:
            error = "Hayvonlar soni to'ldi"
        elif free < cost:
            error = "Yulduz yetmaydi. O'ynab yulduz yig'ing! ⭐"
        else:
            new = Pet.objects.create(user=request.user, kind=kind, name=name)
            p.spent += cost
            p.active_pet = new.id
            p.save()
    elif action == "switch":
        target = next((x for x in pets if x.id == body.get("id")), None)
        if target:
            p.active_pet = target.id
            p.save()
    elif pet and action == "rename":
        name = str(body.get("name", "")).strip()[:20]
        if name:
            pet.name = name
            pet.save()
    elif pet and action == "feed":
        if free < FEED_COST:
            error = "Yulduz yetmaydi. O'ynab yulduz yig'ing! ⭐"
        else:
            pet.fullness = min(100, pet.current_fullness() + FEED_AMOUNT)
            pet.updated = timezone.now()
            pet.save()
            p.spent += FEED_COST
            p.save()
    elif pet and action == "buy":
        item = next((s for s in SHOP if s["id"] == body.get("id")), None)
        if not item or item["id"] in pet.items:
            error = "Xato"
        elif free < item["price"]:
            error = "Yulduz yetmaydi. O'ynab yulduz yig'ing! ⭐"
        else:
            p.spent += item["price"]
            p.save()
            pet.items = pet.items + [item["id"]]
            eq = dict(pet.equipped)
            eq[item["slot"]] = item["id"]
            pet.equipped = eq
            pet.save()
    elif pet and action == "equip":
        item = next((s for s in SHOP if s["id"] == body.get("id")), None)
        if item and item["id"] in pet.items:
            eq = dict(pet.equipped)
            if eq.get(item["slot"]) == item["id"]:
                eq.pop(item["slot"])
            else:
                eq[item["slot"]] = item["id"]
            pet.equipped = eq
            pet.save()

    data = pet_state(request.user)
    data["error"] = error
    return JsonResponse(data)