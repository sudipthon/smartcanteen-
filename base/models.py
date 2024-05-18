# from django.db import models

# # Create your models here.


# class Users(models.Model):
#     USER_TYPE_CHOICES = (
#         ("Admin", "Admin"),
#         ("Student", "Student"),
#         ("Teacher", "Teacher"),
#         ("Staff", "Staff"),
#     )

#     name = models.CharField(max_length=100)
#     user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES)
#     email = models.EmailField()
#     password = models.CharField(max_length=100)

#     class Meta:
#         abstract = True

#     def __str__(self):
#         return self.name


# class Course(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# class Student(Users):
#     SEMESTER_CHOICES = (
#         (1, "1st"),
#         (2, "2nd"),
#         (3, "3rd"),
#         (4, "4th"),
#         (5, "5th"),
#         (6, "6th"),
#         (7, "7th"),
#         (8, "8th"),
#     )
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     semester = models.IntegerField(choices=SEMESTER_CHOICES)
#     user_type = models.CharField(
#         max_length=100, choices=Users.USER_TYPE_CHOICES, default="Student"
#     )


from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Administration(User):
    USER_TYPE_CHOICES = (
        ("Admin", "Admin"),
        ("Teacher", "Teacher"),
        ("Staff", "Staff"),
    )
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES)
    
    class Meta:
        verbose_name = 'Staff,Admin,Teacher Profile'
        verbose_name_plural = 'Staff,Admin,Teacher Profile'

    def __str__(self):
        return self.username


SEMESTER_CHOICES = (   
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (5, "5th"),
        (6, "6th"),
        (7, "7th"),
        (8, "8th"),
    )
class Student(User):
    # user= models.OneToOneField(User, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=100,default="Student"
    )
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return self.user_profile.user.username


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    # description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class MenuSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('SU', 'Sunday'),
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
    ]
    day_of_week = models.CharField(max_length=2, choices=DAYS_OF_WEEK)
    menu_items = models.ManyToManyField(MenuItem)
    class Meta:
        ordering = ['day_of_week']

    def __str__(self):
        return self.get_day_of_week_display()

class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    # order_date = models.DateField(auto_now_add=True)
    order_date = models.DateField(auto_now=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.user.user.username} - {self.menu_item.name}'
        pass

class BreakTime(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester=models.IntegerField(choices=SEMESTER_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.start_time} - {self.end_time}'
        pass