from django.shortcuts import render,HttpResponse
from .models import *
import datetime
import pytz

# Create your views here.
def home(request):
    tz=pytz.timezone('Asia/Kathmandu')
    print(tz)
    current_time = datetime.datetime.now(tz)
    day_of_week=current_time.strftime("%A")[:2].upper()  
    day_menu = MenuSchedule.objects.get(day_of_week=day_of_week)
    menu_items = day_menu.menu_items.all()
    context={
        'menu':menu_items,
        'current_time':current_time
    }
    return render(request, 'home.html', context)
    


def login(request):
    return render(request, 'login/login.html')