from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from notification_app.apps import NotificationAppConfig
from users.views import RegisterView, password_reset_view, activate, UserListView, toggle_user_status

app_name = NotificationAppConfig.name
urlpatterns = [
    path('', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_request/', password_reset_view, name='password_request'),
    path('active_users/', UserListView.as_view(), name='user_list'),
    path('toggle_user_status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
]
