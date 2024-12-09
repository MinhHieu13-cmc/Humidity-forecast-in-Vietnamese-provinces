from django.contrib import admin
from .models import ProvinceData, PredictionResult, ArimaHumidityData

# Đăng ký mô hình ProvinceData
@admin.register(ProvinceData)
class ProvinceDataAdmin(admin.ModelAdmin):
    list_display = ('province', 'max_temp', 'min_temp', 'wind', 'wind_d', 'pressure', 'date')  # Cột hiển thị trong admin
    search_fields = ('province', 'date')  # Cung cấp tính năng tìm kiếm theo province và date

# Đăng ký mô hình PredictionResult
@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ('province', 'date', 'humidity', 'model_type')  # Cột hiển thị trong admin
    search_fields = ('province', 'date', 'model_type')  # Cung cấp tính năng tìm kiếm

# Đăng ký mô hình ArimaHumidityData
@admin.register(ArimaHumidityData)
class ArimaHumidityDataAdmin(admin.ModelAdmin):
    list_display = ('province', 'date', 'humidi')  # Cột hiển thị trong admin
    search_fields = ('province', 'date')  # Cung cấp tính năng tìm kiếm
