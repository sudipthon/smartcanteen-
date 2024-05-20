from .views import *
from django.urls import path

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
]
