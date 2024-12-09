from django.urls import path
from . import views
from .views import dashboard_view  
urlpatterns = [
    path('', views.home, name='home'),          # Trang chủ với bản đồ và form dự đoán
    path('predict/', views.predict, name='predict'),  # Đường dẫn xử lý dự đoán
    path('dashboard/', dashboard_view, name='dashboard'),
]
