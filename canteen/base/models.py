from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone



from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    college_id = models.IntegerField( unique=True)

    USERNAME_FIELD = (
        "college_id"
    )
    REQUIRED_FIELDS = [
        "username"
    ]
    def __str__(self):
        return f"{self.college_id} -{self.username}"
    class Meta:
        ordering = ["college_id"]

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.set_password(self.password)
        super(CustomUser, self).save(*args, **kwargs)


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# class Administration(User):
class Administration(models.Model):
    USER_TYPE_CHOICES = (
        ("Admin", "Admin"),
        ("Teacher", "Teacher"),
        ("Staff", "Staff"),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES)

    class Meta:
        verbose_name = "Administration"
        verbose_name_plural = "Administration"

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


# class Student(CustomUser):
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, default="Student")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return self.user.username
    


DAYS_OF_WEEK = [
    ("SU", "Sunday"),
    ("MO", "Monday"),
    ("TU", "Tuesday"),
    ("WE", "Wednesday"),
    ("TH", "Thursday"),
    ("FR", "Friday"),
    ("SA", "Saturday"),
]


class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    # description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    day_of_week = models.CharField(max_length=2, choices=DAYS_OF_WEEK)
    menu_items = models.ManyToManyField(
        FoodItem,
        related_name="menu_items",
    )
    sequence = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sequence"]

    def __str__(self):
        return self.get_day_of_week_display()


class Orders(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    menu_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    order_time = models.TimeField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.BooleanField(default=False)

    # def clean(self):
    #     if self.order_date < timezone.now().date():
    #         raise ValidationError("Order date cannot be in the past")


    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["order_date"]

    def total_cost(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name}"
    
    # def save(self, *args, **kwargs):
    #     if self.order_date<timezone.now().date():
    #         raise ValidationError("Order date cannot be in the past")
    #     super(Orders, self).save(*args, **kwargs)


class BreakTime(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_breaktimes"
    )
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name = "Break Time"
        verbose_name_plural = "Break Times"
        ordering = ["semester"]

    def __str__(self):
        return f"{self.course} - semester:{self.semester}"
