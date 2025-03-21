from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    def ready(self):
        import api.models  # Đảm bảo rằng mô hình được tải khi ứng dụng được khởi động