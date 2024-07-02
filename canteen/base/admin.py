from django.contrib import admin
from .models import Course, Student, Menu, Orders, FoodItem, Administration, BreakTime, CustomUser

# class Inlin

# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'role', 'course', 'semester')


class OrdersAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "menu_item",
        "order_date",
    )
    # fields = ('user', 'menu_item', 'order_date',)
    readonly_fields = ("order_date",)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'semester')
    list_filter = ('course', 'semester')
    search_fields = ('user__username', 'course__name', 'semester')

admin.site.register(Course)
admin.site.register(Student,StudentAdmin)
admin.site.register(Menu)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(FoodItem)
admin.site.register(Administration)
admin.site.register(BreakTime)
admin.site.register(CustomUser)
