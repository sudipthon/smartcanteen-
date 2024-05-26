from .views import *
from django.urls import path

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    # 
    path("delete_order/<int:pk>",delete_order,name="delete_order"),
    path("update_order/<int:pk>",update_order,name="update_order"),
    # 
    path("admin/<int:pk>", admin_dashboard, name="canteen_admin"),
    path("admin/", admin_dashboard, name="canteen_admin"),
    path("update_breaktime/<int:pk>", update_breaktime, name="update_breaktime"),
    path("create_breaktime/", create_breaktime, name="create_breaktime"),
    path("delete_breaktime/<int:pk>", delete_breaktime, name="delete_breaktime"),
    
    # 
    path("staff/", staff_dashboard, name="staff"),
    path("orders/", list_orders, name="list_orders"),
    path("order/<int:pk>/", create_order, name="create_order"),
    
    path('update_fooditem/<int:pk>/', update_fooditem, name='update_fooditem'),
]
