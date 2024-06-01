from django.contrib import admin

# Register your models here.
from .models import *

# class Inlin

# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'role', 'course', 'semester')
    
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'order_date',  )
    # fields = ('user', 'menu_item', 'order_date',)
    readonly_fields = ('order_date',)
    
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Menu)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(FoodItem)
admin.site.register(Administration)
admin.site.register(BreakTime)
admin.site.register(CustomUser)