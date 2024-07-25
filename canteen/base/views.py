# django imports
from django.shortcuts import render, redirect, HttpResponse
from .models import (
    Menu,
    Orders,
    Course,
    Student,
    Administration,
    BreakTime,
    CustomUser,
    FoodItem,
)
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.conf import settings
from .tasks import add_users_task
from datetime import datetime
import pytz
from django.contrib import messages

# local imports
from .forms import *

from .decorators import check_admin, check_staff, check_student_teacher

# python imports
import os
import stat


# Create your views here.
@login_required(login_url="login")
@check_student_teacher
def home(request):
    """
    takes: request obj
    returns: user to their respective dashboard by checking their user type with the help of decorator

    """
    time_zone = timezone.now()
    day_of_week = time_zone.strftime("%A")
    current_time = time_zone
    day_menu = Menu.objects.get(day_of_week=day_of_week[:2].upper())
    breaktime = BreakTime.objects.get(
        course=request.user.student.course, semester=request.user.student.semester
    )
    menu_items = day_menu.menu_items.all()
    my_orders = Orders.objects.filter(user=request.user)
    context = {
        "menu": menu_items,
        "current_time": time_zone,
        "day_of_week": day_of_week,
        "my_orders": my_orders,
        "breaktime": breaktime,
    }
    return render(request, "home1.html", context)


@login_required(login_url="login")
@check_student_teacher
def profile(request):
    orders = Orders.objects.filter(user=request.user)
    return render(request, "profile.html", {"orders": orders})


def logout_view(request):
    logout(request)
    return redirect("login")


def login_view(request):
    """
    takes: request obj with college id and password
    returns: redirects logged in user to home url
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")
        
        if not CustomUser.objects.filter(college_id=user_id).exists():
            messages.error(request, "User with this college ID does not exist.")
            return redirect("login")
    
        user = authenticate(request, username=user_id, password=password)

        if user == None:
            messages.error(request, "invalid userid or password")
            return redirect("login")
        login(request, user)
        return redirect("home")
    return render(request, "login/login.html")


# ########Admin
@login_required(login_url="login")
@check_admin
def admin_dashboard(request, pk=None):
    courses = Course.objects.all()
    if pk != None:
        course = Course.objects.get(id=pk)
        return render(request, "dashboards/admin/semesters.html", {"course": course})
    context = {"courses": courses}

    return render(request, "dashboards/admin/admin.html", context)


@login_required(login_url="login")
@check_admin
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
@check_admin
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
@check_admin
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


@login_required(login_url="login")
@check_admin
def add_users(request):
    """
    if user chose to add users via file, then file is uploaded and saved in media folder and the celery task is called to add users to the database
    if user chose to add users manually, then necessary field of user is fetched, created and saved in the database
    Returns:
        redirects user to admin dashboard
    """
    if request.method == "POST":
        input_type = request.POST.get("input_type")
        user_type = request.POST.get("user_type")
        if input_type == "file":
            file = request.FILES.get("file")
            custom_folder = os.path.join(settings.MEDIA_ROOT, user_type)
            os.makedirs(
                custom_folder, exist_ok=True
            )  # Create directory if it doesn't exist
            os.chmod(
                custom_folder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
            )  # Change permissions

            fs = FileSystemStorage(location=custom_folder)
            file_name = fs.save(file.name, file)
            file_path = fs.path(file_name)
            add_users_task.delay(file_path, user_type)
            return redirect("canteen_admin")

        college_id = request.POST.get("college_id")
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # check for existing users
        if CustomUser.objects.filter(college_id=college_id).exists():
            messages.error(request, "User with this college ID already exists.")
            return redirect("add_users")
        
        user = CustomUser.objects.create(
            college_id=college_id, username=username, password=password
        )
        if user_type == "Student":
            course = request.POST.get("course")
            semester = request.POST.get("semester")
            course = Course.objects.get(name=course)
            student = Student.objects.create(
                user=user, course=course, semester=semester
            )
            student.save()
        else:
            admin = Administration.objects.create(user=user, user_type=user_type)
            admin.save()

        return redirect("home")
    courses = Course.objects.all()

    context = {"courses": courses}
    return render(request, "dashboards/admin/add_users.html", context)


def list_users(request):
    """
    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    students = Student.objects.all().order_by("user__college_id")[:9]
    teachers = Administration.objects.filter(user_type="Teacher").order_by(
        "user__college_id"
    )[:7]
    staffs = Administration.objects.filter(user_type="Staff").order_by(
        "user__college_id"
    )[:7]
    students = Student.objects.all()
    courses = Course.objects.all()
    teacher_query = request.GET.get("search_teacher", "")
    student_query = request.GET.get("search_student", "")
    staff_query = request.GET.get("search_staff", "")
    if teacher_query:
        teachers = Administration.objects.filter(user_type="Teacher").filter(
            Q(user__college_id__icontains=teacher_query)
            | Q(user__username__icontains=teacher_query)
        )
    if student_query:
        students = Student.objects.filter(
            Q(user__college_id__icontains=student_query)
            | Q(user__username__icontains=student_query)
        )
    if staff_query:
        staffs = Administration.objects.filter(user_type="Staff").filter(
            Q(user__college_id__icontains=staff_query)
            | Q(user__username__icontains=staff_query)
        )

    courses = Course.objects.all()

    context = {
        "students": students,
        "teachers": teachers,
        "staffs": staffs,
        "courses": courses,
    }
    return render(request, "dashboards/admin/users_list.html", context)


@login_required(login_url="login")
@check_admin
def delete_user(request, pk):
    user = CustomUser.objects.get(pk=pk)
    # Get the previous URL
    previous_url = request.META.get("HTTP_REFERER")
    user.delete()
    return redirect(previous_url)


@login_required(login_url="login")
@check_admin
def change_password(request, pk=None):
    if pk:
        user = CustomUser.objects.get(pk=pk)
        request.session["user_id"] = user.id
    else:
        user = CustomUser.objects.get(pk=request.session.get("user_id"))

    if request.method == "POST":
        pk = request.session.get("user_id")
        user = CustomUser.objects.get(pk=request.session.get("user_id"))
        password = request.POST.get("password")
        user.set_password(password)
        user.save()
        if "user_id" in request.session:
            del request.session["user_id"]
        return redirect(home)
    return render(request, "dashboards/change_password.html", {"user": user})


########student & teacher

##utiility function
def time_difference(order_time):
    date_time = timezone.now()
    # current_time=timezone.localtime(date_time).strftime("%H:%M:%S")
    current_time = "12:00:00"  # dummy time for testing
    format = "%H:%M:%S"
    time_difference = datetime.strptime(order_time, format) - datetime.strptime(
        current_time, format
    )
    hours_difference = time_difference.total_seconds() / 3600
    return hours_difference


@login_required(login_url="login")
@check_student_teacher
def create_order(request, pk):
    if request.method == "POST":
        item = FoodItem.objects.get(pk=pk)
        quantity = request.POST.get("quantity")
        user = request.user
        order_time = request.POST.get("order_time")

        if hasattr(user, "student"):
            order_time = str(
                user.student.course.course_breaktimes.get(
                    semester=user.student.semester
                ).start_time
            )
        hours_difference = time_difference(order_time)
        if hours_difference >= 1:
            order = Orders(
                user=user,
                menu_item=item,
                quantity=quantity,
                order_time=order_time,
            )
            order.full_clean()
            order.save()
        # condition if the order time is less than 1 hour
        return redirect("home")


@login_required(login_url="login")
@check_student_teacher
def update_order(request, pk):
    order = Orders.objects.get(pk=pk)
    user = request.user
    if hasattr(user, "student"):
        order_time = str(
            user.student.course.course_breaktimes.get(
                semester=user.student.semester
            ).start_time
        )
    hours_difference = time_difference(order_time)
    if hours_difference >= 1:

        if request.method == "POST":

            quantity = request.POST.get("quantity")
            order.quantity = quantity
            order.save()
            return redirect("profile")
    # condition if the order time is less than 1 hour
    return redirect("profile")


@login_required(login_url="login")
@check_student_teacher
def delete_order(request, pk):
    order = Orders.objects.get(pk=pk)
    user = request.user
    if hasattr(user, "student"):
        order_time = str(
            user.student.course.course_breaktimes.get(
                semester=user.student.semester
            ).start_time
        )
        hours_difference = time_difference(order_time)
        if hours_difference >= 1:
            order.delete()

    return redirect("profile")


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
    """
    takes: request obj and pk
    operation: if pk is None, then it creates a new food item else it updates the existing food item
    """
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
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
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
def update_day_menu(request, pk):
    if request.GET.get("item_id"):
        item_id = request.GET.get("item_id")
        # menu_id=request.GET.get("menu_id")
        item = FoodItem.objects.get(id=item_id)
        menu = Menu.objects.get(id=pk)
        menu.menu_items.remove(item)
        menu.save()

    if request.method == "POST":
        item_id = request.POST.get("item")

        item = FoodItem.objects.filter(id=int(item_id))
        menu = Menu.objects.get(id=int(pk))
        menu.menu_items.add(*item)
        menu.save()

    day = Menu.objects.get(id=pk)
    all_items = FoodItem.objects.all()
    items = all_items.exclude(id__in=day.menu_items.values_list("id", flat=True))

    return render(request, "dashboards/day_menu.html", {"day": day, "items": items})
    # return redirect("update_fooditem")


@login_required(login_url="login")
@check_staff
def list_orders(request):
    # breaktimes = BreakTime.objects.values_list("start_time", flat=True)
    orders = Orders.objects.filter(order_date=timezone.now().date())
    breaktimes = list(set([order.order_time for order in orders]))
    # breaktimes = list(set(breaktimes))
    orders_dict = {}
    for time in breaktimes:
        orders_at_time = orders.filter(order_time=time)
        orders_dict[time] = {}
        for order in orders_at_time:
            item_name = order.menu_item.name
            if item_name not in orders_dict[time]:
                orders_dict[time][item_name] = {"quantity": 0, "price": 0}
            orders_dict[time][item_name]["quantity"] += order.quantity
            orders_dict[time][item_name]["price"] += order.menu_item.price

    context = {"orders": orders_dict, "breaktimes": breaktimes}

    return render(request, "dashboards/orders.html", context)
