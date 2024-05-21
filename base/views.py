from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pytz

# python imports
from itertools import groupby
from operator import attrgetter
from collections import defaultdict


# Create your views here.
@login_required(login_url="login")
def home(request):
    time_zone = timezone.now()
    # print("Time Zone: ", time_zone)
    day_of_week = time_zone.strftime("%A")
    current_time = time_zone
    # print("Current Time: ", current_time)

    day_menu = Menu.objects.get(day_of_week=day_of_week[:2].upper())
    menu_items = day_menu.menu_items.all()
    context = {
        "menu": menu_items,
        "current_time": time_zone,
        "day_of_week": day_of_week,
    }
    return render(request, "home.html", context)

def logout_view(request):
    logout(request)
    return redirect("login")

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
                    return redirect("canteen_admin")
                elif admin.user_type == "Staff":
                    return redirect("staff")
                else:
                    return redirect("home")
        else:
            return HttpResponse("Invalid Credentials")
    return render(request, "login/login.html")

@login_required(login_url="login")
def admin_dashboard(request):
    courses = Course.objects.all()
    breaktime = BreakTime.objects.all()
    context = {"courses": courses, "breaktime": breaktime}

    return render(request, "dashboards/admin.html", context)

@login_required(login_url="login")
def create_breaktime(request):
    if request.method == "POST":
        name = request.POST.get('course')
        course = Course.objects.create(name=name)
        breaktimes = [BreakTime(course=course, semester=i,start_time='7:00',end_time='8:00') for i in range(1, 9)]
        BreakTime.objects.bulk_create(breaktimes)
        return redirect('canteen_admin')
    
@login_required(login_url="login")
def update_breaktime(request, pk):
    if request.method == "POST":
        course = request.POST.get("course")
        course = Course.objects.get(name=course)
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        semester = request.POST.get("semester")

        breaktime = BreakTime.objects.get(id=pk)
        breaktime.start_time = start_time
        breaktime.end_time = end_time
        breaktime.semester = int(semester)
        breaktime.course = course
        breaktime.save()

    return redirect("canteen_admin")

@login_required(login_url="login")
def delete_breaktime(request, pk):
    if request.method == "POST":
        course=Course.objects.get(id=pk)
        try:
            breaktime = BreakTime.objects.filter(course=course)
            breaktime.delete()
            course.delete()
        except:
            course.delete()
            return redirect("canteen_admin")
    return redirect("canteen_admin")

@login_required(login_url="login")
def staff_dashboard(request):
    food_item = FoodItem.objects.all()
    time_zone = timezone.now()
    day_of_week = time_zone.strftime("%A")

    day_menu = Menu.objects.get(day_of_week=day_of_week[:2].upper())
    today_menu_items = day_menu.menu_items.all()
    context = {
        "food_item": food_item,
        "today_menu": today_menu_items,
        "date": day_of_week,
    }

    return render(request, "dashboards/staff.html", context)

@login_required(login_url="login")
def update_fooditem(request,pk):
    if request.method == "POST":
        item=FoodItem.objects.get(pk=pk)
        item.name=request.POST.get('name')
        item.price=request.POST.get('price')
        item.available=bool(request.POST.get('available'))
        item.save()
        return redirect('staff')
    return redirect('staff')
        
    

@login_required(login_url="login")
def list_orders(request):
    breaktime_start_times = BreakTime.objects.all().values_list("start_time", flat=True)
    orders = Orders.objects.filter(order_time__in=breaktime_start_times).order_by(
        "order_time"
    )
    orders_dict = {
        "ti": [
            {"samosa": {"quantity": 5, "price": 250}},
            {"samosa": {"quantity": 5, "price": 250}},
        ],
        "j": [
            {"samosa": {"quantity": 5, "price": 250}},
            {"samosa": {"quantity": 5, "price": 250}},
            {"samosa": {"quantity": 5, "price": 250}},
        ],
    }

    # for order in orders:
    #     if order.order_time not in orders_dict:
    #         orders_dict[order.order_time] = []
    #         for i in orders_dict[order.order_time]:
    #             if order.menu_item.name:
    #                 orders_dict[order.order_time].append(
    #                     {
    #                         order.menu_item.name: {
    #                             "quantity": order.quantity,
    #                             "price": order.menu_item.price,
    #                         }
    #                     }
    #                 )
    #             else:
    #                 orders_dict[order.order_time][order.menu_item.name][
    #                     "quantity"
    #                 ] += order.quantity
    #                 orders_dict[order.order_time][order.menu_item.name][
    #                     "price"
    #                 ] += order.menu_item.price
    for order in orders:
        if order.order_time not in orders_dict:
            orders_dict[order.order_time] = []

        # Check if the item name already exists in the orders for this timestamp
        item_exists = False
        for item in orders_dict[order.order_time]:
            if order.menu_item.name in item:
                item[order.menu_item.name]["quantity"] += order.quantity
                item[order.menu_item.name]["price"] += order.menu_item.price
                item_exists = True
                break

        # If the item name does not exist, add a new item
        if not item_exists:
            orders_dict[order.order_time].append(
                {
                    order.menu_item.name: {
                        "quantity": order.quantity,
                        "price": order.menu_item.price,
                    }
                }
            )

    print(orders_dict)
    context = {"orders": orders_dict}

    print(orders_dict)
    context = {"orders": orders_dict}

    # return render(request, "dashboards/orders.html", context)

@login_required(login_url="login")
def create_order(request, pk):
    if request.method == "POST":
        item = FoodItem.objects.get(pk=pk)
        quantity = request.POST.get("quantity")
        print("Quantity: ", quantity)
        user = request.user
        order = Orders.objects.create(
            user=user,
            menu_item=item,
            quantity=quantity,
            order_time=user.student.course.course_breaktimes.get(
                semester=user.student.semester
            ).start_time,
        )
        order.save()
    return redirect("home")


# {datetime.time(7, 30): {'samosa': {'quantity': 5, 'price': 250}}}
