import os
import csv
from django.core.management.base import BaseCommand
from prediction.models import ArimaHumidityData
from datetime import datetime

class Command(BaseCommand):
    help = 'Import humidity data for provinces from CSV files'

    def handle(self, *args, **kwargs):
        data_dir = 'data/'  # Thư mục chứa các file CSV
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                province_name = filename.replace('.csv', '')
                file_path = os.path.join(data_dir, filename)
                self.import_csv(file_path, province_name)

    def import_csv(self, file_path, province_name):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Tạo bản ghi mới trong bảng ArimaHumidityData
                    ArimaHumidityData.objects.create(
                        province=province_name,
                        humidi=float(row['humidi']),  # Đảm bảo rằng dữ liệu độ ẩm có tên 'humidi' trong CSV
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date()
                    )
                    self.stdout.write(self.style.SUCCESS(f"Imported humidity data for {province_name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {province_name}: {e}"))
