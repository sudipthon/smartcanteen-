from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.utils import timezone
from django.contrib.auth import authenticate, login
import pytz


# Create your views here.
def home(request):
    time_zone = timezone.now()
    print("Time Zone: ", time_zone)
    day_of_week = time_zone.strftime("%A")
    current_time = time_zone
    print("Current Time: ", current_time)

    day_menu = MenuSchedule.objects.get(day_of_week=day_of_week[:2].upper())
    menu_items = day_menu.menu_items.all()
    context = {
        "menu": menu_items,
        "current_time": current_time,
        "day_of_week": day_of_week,
    }
    return render(request, "home.html", context)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if hasattr(user, "student"):
                return redirect("home")
            elif hasattr(user, "administration"):
                admin = user.administration
                if admin.user_type == "Admin":
                    return render(request, "dashboards/admin.html")
                elif admin.user_type == "Staff":
                    return render(request, "dashboards/staff.html")
                else:
                    return redirect("home")
        else:
            return HttpResponse("Invalid Credentials")
    return render(request, "login/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        user_type = request.POST.get("user_type")
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        if user_type:
            user.user_type = user_type
            user.save()
        return redirect("login")
    return render(request, "register/register.html")
