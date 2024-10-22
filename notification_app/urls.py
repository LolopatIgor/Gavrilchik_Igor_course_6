from django.urls import path
from django.views.decorators.cache import cache_page

from notification_app.apps import NotificationAppConfig
from notification_app.views import NotificationListView, NotificationCreateView, NotificationEditView, ClientListView, \
    ClientEditView, ClientCreateView, MailListView, MailCreateView, MailEditView, NotificationDeleteView, \
    notification_detail, ClientDetailView, ClientDeleteView, MailDetailView, MailDeleteView, home_view, \
    block_unblock_notification

#Test
app_name = NotificationAppConfig.name

urlpatterns = [
    path('', cache_page(120)(home_view), name='home'),
    path('notification', NotificationListView.as_view(), name='notification_list'),
    path('edit_notification/<int:pk>/', NotificationEditView.as_view(), name='notification_edit'),
    path('detail_notification/<int:notification_id>/', notification_detail, name='notification_detail'),
    path('create_notification', NotificationCreateView.as_view(), name='notification_create'),
    path('delete_notification/<int:pk>/', NotificationDeleteView.as_view(), name='notification_delete'),
    path('notification/block_unblock/<int:pk>/', block_unblock_notification, name='block_unblock_notification'),
    path('client', ClientListView.as_view(), name='client_list'),
    path('edit_client/<int:pk>/', ClientEditView.as_view(), name='client_edit'),
    path('detail_client/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('delete_client/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
    path('create_client', ClientCreateView.as_view(), name='client_create'),
    path('mail', MailListView.as_view(), name='mail_list'),
    path('edit_mail/<int:pk>/', MailEditView.as_view(), name='mail_edit'),
    path('detail_mail/<int:pk>/', MailDetailView.as_view(), name='mail_detail'),
    path('delete_mail/<int:pk>/', MailDeleteView.as_view(), name='mail_delete'),
    path('create_mail', MailCreateView.as_view(), name='mail_create'),
]
