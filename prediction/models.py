from django.db import models


# Model lưu trữ dữ liệu thời tiết của từng tỉnh
class ProvinceData(models.Model):
    province = models.CharField(max_length=100)  # Tên tỉnh
    max_temp = models.FloatField()               # Nhiệt độ cao nhất trong ngày
    min_temp = models.FloatField()               # Nhiệt độ thấp nhất trong ngày
    wind = models.FloatField()                   # Tốc độ gió
    wind_d = models.CharField(max_length=50)     # Hướng gió
    pressure = models.FloatField()               # Áp suất
    date = models.DateField()                    # Ngày

    def __str__(self):
        return f"{self.province} - {self.date}"

# Model lưu trữ kết quả dự đoán độ ẩm
class PredictionResult(models.Model):
    province = models.CharField(max_length=100)  # Tên tỉnh
    date = models.DateField()                    # Ngày dự đoán
    humidity = models.FloatField()               # Độ ẩm dự đoán
    model_type = models.CharField(max_length=50) # Loại mô hình sử dụng

    def __str__(self):
        return f"{self.province} - {self.date} - {self.model_type}"

class ArimaHumidityData(models.Model):
    province = models.CharField(max_length=100, null=True)  
    date = models.DateField()  # Ngày của dữ liệu độ ẩm
    humidi = models.FloatField()  # Giá trị độ ẩm (humidity)

    def __str__(self):
        return f"Humidity data for {self.province} on {self.date}"