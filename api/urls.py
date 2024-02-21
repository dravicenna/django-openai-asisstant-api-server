from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from hotel_bot.integrations.default import ChatDefaultView, StartChatDefaultView
from hotel_bot.integrations.telegram import StartTelegramView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/default/start', StartChatDefaultView.as_view()),
    path('api/default/chat', ChatDefaultView.as_view()),
    # TODO add secret token
    path('api/telegram/start', csrf_exempt(StartTelegramView.as_view())),
]
