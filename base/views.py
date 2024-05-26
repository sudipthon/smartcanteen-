from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pytz
from django.db.models import Count

from django.db.models import Count, Sum

# local imports
from .forms import *
from .decorators import *

# python imports
from itertools import groupby
from operator import attrgetter
from collections import defaultdict


# Create your views here.
@login_required(login_url="login")
@check_student_teacher
def home(request):
    time_zone = timezone.now()
    day_of_week = time_zone.strftime("%A")
    current_time = time_zone

    day_menu = Menu.objects.get(day_of_week=day_of_week[:2].upper())
    menu_items = day_menu.menu_items.all()
    my_orders = Orders.objects.filter(user=request.user)
    context = {
        "menu": menu_items,
        "current_time": time_zone,
        "day_of_week": day_of_week,
        "my_orders": my_orders,
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


def delete_order(request, pk):
    order = Orders.objects.get(pk=pk)
    order.delete()
    return redirect("home")


def update_order(request, pk):
    order = Orders.objects.get(pk=pk)
    if request.method == "POST":
        quantity = request.POST.get("quantity")
        order.quantity = quantity
        order.save()
        return redirect("home")
    # return render(request, "edit_order.html", {"order": order})


# ########Admin
@login_required(login_url="login")
@check_admin
def admin_dashboard(request, pk=None):
    courses = Course.objects.all()
    if pk != None:
        course = Course.objects.get(id=pk)
        return render(request, "dashboards/semesters.html", {"course": course})
    context = {"courses": courses}

    return render(request, "dashboards/admin.html", context)


@check_admin
@login_required(login_url="login")
def create_breaktime(request):
    if request.method == "POST":
        name = request.POST.get("course")
        course = Course.objects.create(name=name)
        breaktimes = [
            BreakTime(course=course, semester=i, start_time="7:00", end_time="8:00")
            for i in range(1, 9)
        ]
        BreakTime.objects.bulk_create(breaktimes)
        return redirect("canteen_admin")


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
        course = Course.objects.get(id=pk)
        try:
            breaktime = BreakTime.objects.filter(course=course)
            breaktime.delete()
            course.delete()
        except:
            course.delete()
            return redirect("canteen_admin")
    return redirect("canteen_admin")


########Staff


@login_required(login_url="login")
@check_staff
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
@check_staff
def delete_fooditem(request, pk):
    item = FoodItem.objects.get(pk=pk)
    item.delete()

    return redirect("staff")


@login_required(login_url="login")
@check_staff
def update_fooditem(request, pk=None):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        available = bool(request.POST.get("available"))
        if pk == None:
            item = FoodItem.objects.create(name=name, price=price, available=available)
            item.save()
            return redirect("staff")

        item = FoodItem.objects.get(pk=pk)
        item.name = name
        item.price = price
        item.available = available
        item.save()
        return redirect("staff")
    return redirect("staff")


@login_required(login_url="login")
@check_staff
def weekly_menu(request):
    if request.GET.get("id"):
        id = request.GET.get("id")
        day = Menu.objects.get(id=id)
        all_items = FoodItem.objects.all()

        items = all_items.exclude(id__in=day.menu_items.values_list("id", flat=True))
        return render(request, "dashboards/day_menu.html", {"items": items, "day": day})

    

    days = Menu.objects.all()
    items = FoodItem.objects.all()
    context = {
        "days": days,
        "items": items,
    }
    return render(request, "dashboards/week_menu.html", context)


@login_required(login_url="login")
@check_staff
def update_day_menu(request,pk):
    if request.GET.get("item_id"):
        item_id= request.GET.get("item_id")
        # menu_id=request.GET.get("menu_id")
        item= FoodItem.objects.get(id=item_id)
        menu=Menu.objects.get(id=pk)
        menu.menu_items.remove(item)
        menu.save()
    
    if request.method == "POST":
        item_id = request.POST.get("item")
        # menu_id = request.POST.get("menu")

        item = FoodItem.objects.filter(id=int(item_id))
        menu = Menu.objects.get(id=int(pk))
        menu.menu_items.add(*item)
        menu.save()

    day = Menu.objects.get(id=pk)
    all_items = FoodItem.objects.all()
    items = all_items.exclude(id__in=day.menu_items.values_list("id", flat=True))
  
    # return redirect("update_day_menu",{"day":day,"items":items})
    return render(request,"dashboards/day_menu.html",{"day":day,"items":items})
    # return redirect("update_fooditem")


@login_required(login_url="login")
@check_staff
def list_orders(request):
    breaktime_start_times = BreakTime.objects.all().values_list("start_time", flat=True)
    # Query orders grouped by 'order_time' and 'menu_item', and calculate total quantity for each group
    orders = (
        Orders.objects.filter(order_time__in=breaktime_start_times)
        .values("order_time", "menu_item__name", "menu_item__price")
        .annotate(total_quantity=Sum("quantity"))
    )

    # Initialize an empty dictionary to hold the final result
    orders_dict = {}

    # Loop through the query results
    for order in orders:
        # Get the order_time and menu_item from the order
        order_time = order["order_time"]
        menu_item_name = order["menu_item__name"]
        menu_item__price = order["menu_item__price"]

        # If this order_time is not already in orders_dict, add it with an empty list
        if order_time not in orders_dict:
            orders_dict[order_time] = []

        # Add this order to the list for this order_time
        orders_dict[order_time].append(
            {
                menu_item_name: {
                    "quantity": order["total_quantity"],
                    "price": order["total_quantity"]
                    * menu_item__price,  # Assuming menu_item has a 'price' attribute
                }
            }
        )

    print(orders)
    return HttpResponse(orders)
    orders_dict = {
        "time": [
            {"samosa": {"quantity": 5, "price": 250}},
            {"samosa": {"quantity": 5, "price": 250}},
        ],
        "time": [
            {"samosa": {"quantity": 5, "price": 250}},
            {"samosa": {"quantity": 5, "price": 250}},
            {"samosa": {"quantity": 5, "price": 250}},
        ],
    }
    # for breaktime in breaktime_start_times:
    #     if breaktime not in orders_dict:
    #         orders_dict[breaktime] = []
    #         for order in orders:
    #             if

    # return render(request, "dashboards/orders.html", context)


@login_required(login_url="login")
@check_student_teacher
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

