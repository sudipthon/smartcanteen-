

from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name

# class Administration(User):
class Administration(models.Model):

    USER_TYPE_CHOICES = (
        ("Admin", "Admin"),
        ("Teacher", "Teacher"),
        ("Staff", "Staff"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES)
    
    class Meta:
        verbose_name = 'Administration'
        verbose_name_plural = 'Administration'

    def __str__(self):
        return self.user.username


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
# class Student(User):
class Student(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=100,default="Student"
    )
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return self.user.username
 

DAYS_OF_WEEK = [
        ('SU', 'Sunday'),
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
    ]

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    # description = models.TextField(blank=True, null=True)
    price = models.IntegerField( )
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class MenuSchedule(models.Model):
    day_of_week = models.CharField(max_length=2, choices=DAYS_OF_WEEK)
    menu_items = models.ManyToManyField(MenuItem,  related_name='menu_items',)
    sequence= models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['sequence']

    def __str__(self):
        return self.get_day_of_week_display()

class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now=True)
    order_time = models.TimeField()
    quantity = models.PositiveIntegerField(default=1)
    status = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering=['order_date']

    def __str__(self):
        return f'{self.user.username} - {self.menu_item.name}'

class BreakTime(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester=models.IntegerField(choices=SEMESTER_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        verbose_name = 'Break Time'
        verbose_name_plural = 'Break Times'
        ordering=['semester']

    def __str__(self):
        return f'{self.course} - semseter:{self.semester}'
