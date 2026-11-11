from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Topic(models.Model):
    key = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Word(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="words")
    emoji = models.CharField(max_length=10)
    en = models.CharField("Inglizcha", max_length=50)
    uz = models.CharField("O'zbekcha", max_length=80)
    ru = models.CharField("Ruscha", max_length=80, blank=True)
    de = models.CharField("Nemischa", max_length=80, blank=True)

    def __str__(self):
        return f"{self.emoji} {self.en} = {self.uz}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)
    spent = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_day = models.DateField(null=True, blank=True)
    best_speed = models.IntegerField(default=0)
    lang = models.CharField(max_length=2, default="en")
    active_pet = models.IntegerField(null=True, blank=True)
    win_start = models.DateTimeField(null=True, blank=True)
    win_used = models.IntegerField(default=0)
    last_tick = models.DateTimeField(null=True, blank=True)
    task_day = models.DateField(null=True, blank=True)
    task_prog = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.stars}"


class WordStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wordstats")
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    box = models.IntegerField(default=0)      # 0 = qiyin ... 4 = yaxshi biladi
    right = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "word")

    def __str__(self):
        return f"{self.user.username} {self.word.en}: box {self.box}"


class Pet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    kind = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    fullness = models.IntegerField(default=60)
    updated = models.DateTimeField(default=timezone.now)
    items = models.JSONField(default=list)
    equipped = models.JSONField(default=dict)

    def current_fullness(self):
        hours = (timezone.now() - self.updated).total_seconds() / 3600
        return max(0, int(self.fullness - hours * 5))

    def __str__(self):
        return f"{self.user.username}: {self.kind} {self.name}"