from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from game.views import (home, play, stickers, signup, add_star, profile,
                        speed, add_speed, pet_page, pet_action, set_lang,
                        tick, tasks, answer)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('lang/', set_lang),
    path('play/<str:key>/', play),
    path('speed/', speed),
    path('pet/', pet_page),
    path('tasks/', tasks),
    path('stickers/', stickers),
    path('profile/', profile),
    path('signup/', signup),
    path('login/', LoginView.as_view(template_name='game/login.html')),
    path('logout/', LogoutView.as_view()),
    path('api/star/', add_star),
    path('api/answer/', answer),
    path('api/speed/', add_speed),
    path('api/pet/', pet_action),
    path('api/tick/', tick),
]