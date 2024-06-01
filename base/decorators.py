from django.shortcuts import redirect


def check_student_teacher(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if hasattr(user, "administration"):
            admin = user.administration
            if admin.user_type == "Admin":
                return redirect("canteen_admin")
            elif admin.user_type == "Staff":
                return redirect("staff")
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    # wrap.__name__ = function.__name__
    return wrap


def check_admin(function):
    def wrap(request, *args, **kwargs):
        user = request.user

        if hasattr(user, "administration"):
            admin = user.administration
            if admin.user_type == "Staff":
                return redirect("staff")
        else:
            return redirect("home")
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    return wrap


def check_staff(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if hasattr(user, "administration"):
            admin = user.administration
            if admin.user_type == "Admin":
                return redirect("canteen_admin")
        elif hasattr(user, "student"):
            return redirect("home")
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    # wrap.__name__ = function.__name__
    return wrap
