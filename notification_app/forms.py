from django import forms
from notification_app.models import Notification, Client, Mail, SendMailTo
from django.utils import timezone

class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            elif field_name != 'scheduled_time':
                field.widget.attrs['class'] = 'form-control'
                # Добавление серого фона
                field.widget.attrs['style'] = 'background-color: #f8f9fa;'

class NotificationForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('name', 'scheduled_time', 'period', 'mail')
        widgets = {
            'scheduled_time': forms.TextInput(attrs={
                'class': 'datetimepicker form-control',
                'style': 'width: 100%; background-color: #f8f9fa;',  # Растянуть и установить серый фон
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Преобразуем время для отображения в локальном часовом поясе
        if self.instance and self.instance.pk:
            scheduled_time = self.instance.scheduled_time

            if scheduled_time and timezone.is_aware(scheduled_time):
                local_scheduled_time = scheduled_time.astimezone(timezone.get_current_timezone())
                self.fields['scheduled_time'].initial = local_scheduled_time.strftime('%Y-%m-%d %H:%M:%S')

class ClientForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['owner']

class MailForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Mail
        exclude = ['owner']


class SendMailToForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = SendMailTo
        fields = ['client']