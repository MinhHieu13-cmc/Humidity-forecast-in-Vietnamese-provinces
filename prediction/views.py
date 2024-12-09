import folium
from django.shortcuts import render
from .models import  ArimaHumidityData
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pandas as pd
import json
from django.db.models.functions import ExtractYear
from django.db.models import Sum
from django.core.paginator import Paginator
# Hàm hiển thị bản đồ và form chọn mô hình dự đoán
def home(request):
    vietnam_map = folium.Map(location=(14.0583, 108.2772), zoom_start=6,width="100%",height="100%",)
    provinces = [
        'Bac Lieu', 'Ho Chi Minh City', 'Tam Ky', 'Ben Tre', 'Hoa Binh', 'Tan An', 
        'Bien Hoa', 'Hong Gai', 'Thai Nguyen', 'Buon Me Thuot', 'Hue', 'Thanh Hoa', 
        'Ca Mau', 'Long Xuyen', 'Tra Vinh', 'Cam Pha', 'My Tho', 'Tuy Hoa', 'Cam Ranh', 
        'Nam Dinh', 'Uong Bi', 'Can Tho', 'Nha Trang', 'Viet Tri', 'Chau Doc', 
        'Phan Rang', 'Vinh', 'Da Lat', 'Phan Thiet', 'Vinh Long', 'Ha Noi', 'Play Cu', 
        'Vung Tau', 'Hai Duong', 'Qui Nhon', 'Yen Bai', 'Hai Phong', 'Rach Gia', 'Soc Trang'
    ]

    for province in provinces:
        folium.Marker(
            location=get_province_location(province),
            popup=province,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(vietnam_map)

    map_html = vietnam_map._repr_html_()
    return render(request, 'prediction/home.html', {
        'map_html': map_html,
        'provinces': provinces,
    })

def get_province_location(province):
    geolocator = Nominatim(user_agent="province_locator")
    try:
        location = geolocator.geocode(province + ', Vietnam')
        if location:
            return (location.latitude, location.longitude)
        else:
            return (14.0583, 108.2772)
    except GeocoderTimedOut:
        return (14.0583, 108.2772)

import joblib
import os
from django.http import JsonResponse

@csrf_exempt
def predict(request):
    if request.method == 'POST':
        province = request.POST.get('province')
        model_type = request.POST.get('model_type')
        date_str = request.POST.get('date')

        # Chuyển đổi chuỗi ngày sang kiểu timestamp của pandas
        try:
            selected_date = pd.to_datetime(date_str)
        except ValueError:
            return JsonResponse({'error': 'Ngày không hợp lệ'})

        if model_type == 'ARIMA':
            model, last_humidi_value, last_date = load_model(model_type, province)
            
            if model and last_humidi_value is not None and last_date is not None:
                try:
                    # Thiết lập lại chỉ mục thời gian nếu thiếu
                    last_date = pd.to_datetime(last_date)
                    days_difference = (selected_date - last_date).days

                    if days_difference > 0:
                        # Tạo tập dữ liệu dự đoán
                        forecast_diff = model.forecast(steps=days_difference)
                        forecast_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days_difference, freq='D')
                        forecast_series = pd.Series(forecast_diff, index=forecast_dates)

                        # Đảm bảo dự báo sắp xếp đúng thứ tự thời gian
                        forecast_series = forecast_series.sort_index()

                        # Tính toán giá trị cuối cùng
                        forecast_humidi = last_humidi_value + forecast_series.iloc[-1]
                        return JsonResponse({'result': f'Dự báo độ ẩm cho ngày {selected_date}: {forecast_humidi:.2f}'})
                    else:
                        return JsonResponse({'error': 'Ngày dự báo phải lớn hơn ngày cuối cùng trong dữ liệu.'})
                except Exception as e:
                    return JsonResponse({'error': f'Dự đoán thất bại: {str(e)}'})
            else:
                return JsonResponse({'error': 'Không thể tải mô hình ARIMA hoặc thiếu dữ liệu'})

        # Nếu là Random Forest hoặc Linear Regression
        elif model_type in ['Random Forest', 'Linear Regression']:
            model = load_model(model_type, province)
            if not model:
                return JsonResponse({'error': f'Không thể tải mô hình {model_type}.'})

            # Lấy thông tin các đặc trưng đầu vào từ request
            try:
                cloud = float(request.POST.get('cloud', ''))
                max_temp = float(request.POST.get('max', ''))
                rain = float(request.POST.get('rain', ''))
            except ValueError as e:
                return JsonResponse({'error': f'Giá trị đặc trưng không hợp lệ: {str(e)}'})

            # Dự đoán
            input_data = [[cloud, max_temp, rain]]
            try:
                prediction = model.predict(input_data)
                return JsonResponse({
                    'result': f'Dự báo độ ẩm cho ngày {selected_date.strftime("%Y-%m-%d")}: {prediction[0]:.2f}'
                })
            except Exception as e:
                return JsonResponse({'error': f'Lỗi khi dự đoán với mô hình {model_type}: {str(e)}'})

        else:
            return JsonResponse({'error': 'Loại mô hình không hợp lệ.'})

    return JsonResponse({'error': 'Yêu cầu không hợp lệ. Vui lòng sử dụng phương thức POST.'})

def load_model(model_type, province):
    province = province.replace(" ", "_")
    model_type = model_type.replace(" ", "_").lower()
    model_path = f"prediction/models/{province}_{model_type}.pkl"

    if not os.path.exists(model_path):
        print(f"ERROR: Tệp mô hình {model_path} không tồn tại!")
        return None

    try:
        if model_type == "arima":
            # Dành riêng cho ARIMA
            model_data = joblib.load(model_path)
            model = model_data.get("model")
            last_humidi_value = model_data.get("last_humidi_value", None)
            last_date = model_data.get("last_date", None)

            if model:
                print(f"SUCCESS: Mô hình {model_path} đã được tải thành công.")
                return model, last_humidi_value, last_date
            else:
                print(f"ERROR: Không tìm thấy dữ liệu mô hình trong file {model_path}.")
                return None, None, None
        else:  # LinearRegression và RandomForest
            model = joblib.load(model_path)  # Dùng joblib cho RF và LR

            if model:
                print(f"SUCCESS: Mô hình {model_path} đã được tải thành công.")
                return model  # Trả về mô hình đã tải
            else:
                print(f"ERROR: Không tìm thấy dữ liệu mô hình trong file {model_path}.")
                return None
    except Exception as e:
        print(f"ERROR: Không thể tải mô hình {model_path}: {e}")
        return None



def dashboard_view(request):
    query = request.GET.get('q', '')  # Lấy từ khóa tìm kiếm từ thanh tìm kiếm

    if query:
        # Lọc dữ liệu theo tỉnh nếu có tìm kiếm
        data = (
            ArimaHumidityData.objects.filter(province__icontains=query)
            .annotate(year=ExtractYear('date'))  # Thêm trường năm
            .values('province', 'year')
            .annotate(total_humidity=Sum('humidi'))  # Tổng hợp độ ẩm theo năm
        )
    else:
        # Lấy dữ liệu của tất cả các tỉnh
        data = (
            ArimaHumidityData.objects.annotate(year=ExtractYear('date'))
            .values('province', 'year')
            .annotate(total_humidity=Sum('humidi'))
        )

    # Phân trang: mỗi trang hiển thị dữ liệu của 15 tỉnh
    provinces = {item['province'] for item in data}
    paginator = Paginator(list(provinces), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Chuyển dữ liệu thành JSON
    chart_data = [
        {
            "province": province,
            "years": [
                {"year": item['year'], "humidity": item['total_humidity']}
                for item in data if item['province'] == province
            ]
        }
        for province in page_obj
    ]

    return render(request, 'prediction/dashbroad.html', {
        'page_obj': page_obj,
        'chart_data': json.dumps(chart_data),  # Truyền JSON vào template
        'query': query,
    })