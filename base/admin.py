from django.contrib import admin

# Register your models here.
from .models import *

# class Inlin

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'course', 'semester')
    
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(MenuSchedule)
admin.site.register(Order)
admin.site.register(MenuItem)
admin.site.register(Administration)
admin.site.register(BreakTime)