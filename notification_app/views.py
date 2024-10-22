from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from notification_app.jobs import schedule_job
from notification_app.models import Notification, Client, Mail, Status, SendMailTo
from django.urls import reverse_lazy
from notification_app.forms import NotificationForm, ClientForm, MailForm, SendMailToForm
from django.utils import timezone
from django.forms import inlineformset_factory
from notification_app.services import send_mails
from blog.models import Blog
import random



class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.groups.filter(name='manager').exists()
        return context

    def get_queryset(self):
        if self.request.user.groups.filter(name='manager').exists():
            return Notification.objects.all()
        else:
            return Notification.objects.filter(owner=self.request.user)


class NotificationCreateView(LoginRequiredMixin, CreateView):
    model = Notification
    form_class = NotificationForm
    success_url = reverse_lazy('notification_app:notification_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Формсет для клиентов
        SendMailToFormSet = inlineformset_factory(Notification, SendMailTo, form=SendMailToForm, extra=10)

        # Создание формы с фильтрацией по пользователю
        if self.request.POST:
            formset = SendMailToFormSet(self.request.POST)
        else:
            formset = SendMailToFormSet(queryset=SendMailTo.objects.none())

        # Фильтруем Mail и Client по текущему пользователю
        for form in formset:
            form.fields['client'].queryset = Client.objects.filter(owner=self.request.user)

        context['formset'] = formset

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['mail'].queryset = Mail.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        notification = form.save(commit=False)

        # Устанавливаем владельца
        notification.owner = self.request.user
        # Получаем запланированное время из формы
        scheduled_time = form.cleaned_data['scheduled_time']

        # Устанавливаем статус уведомления



        # Привязываем время к текущему часовому поясу, не меняя значение
        current_tz = timezone.get_current_timezone()
        local_scheduled_time = timezone.make_aware(scheduled_time.replace(tzinfo=None), current_tz)

        # Сохраняем это время в UTC
        notification.scheduled_time = local_scheduled_time
        print(local_scheduled_time)
        print(timezone.now())
        notification.status = Status.objects.get(pk=2 if local_scheduled_time < timezone.now() else 1)

        notification.save()

        # Сохраняем клиентов
        formset = self.get_context_data()['formset']
        if formset.is_valid():
            send_mail_to_objects = formset.save(commit=False)
            for send_mail_to in send_mail_to_objects:
                send_mail_to.notification = notification
                send_mail_to.save()

        # Если запланированное время уже наступило или прошло, выполняем рассылку
        if notification.scheduled_time <= timezone.now():
            send_mails(notification)

        # Планируем задачу
        schedule_job(notification)

        return super().form_valid(form)


class NotificationEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Notification
    form_class = NotificationForm
    success_url = reverse_lazy('notification_app:notification_list')

    def test_func(self):
        # Check if the user is not a manager
        return not self.request.user.groups.filter(name='manager').exists()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['mail'].queryset = Mail.objects.filter(owner=self.request.user)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Формсет для клиентов
        SendMailToFormSet = inlineformset_factory(Notification, SendMailTo, form=SendMailToForm, extra=10)
        if self.request.POST:
            formset = SendMailToFormSet(self.request.POST)
        else:
            formset = SendMailToFormSet(queryset=SendMailTo.objects.none())

            # Фильтруем Mail и Client по текущему пользователю
        for form in formset:
            form.fields['client'].queryset = Client.objects.filter(owner=self.request.user)

        context['formset'] = formset

        return context

    def form_valid(self, form):
        notification = form.save(commit=False)

        # Получаем запланированное время из формы
        scheduled_time = form.cleaned_data['scheduled_time']

        # Привязываем время к текущему часовому поясу, не меняя значение
        current_tz = timezone.get_current_timezone()
        local_scheduled_time = timezone.make_aware(scheduled_time.replace(tzinfo=None), current_tz)

        # Сохраняем это время в UTC
        notification.scheduled_time = local_scheduled_time

        notification.save()

        # Сохраняем клиентов
        formset = self.get_context_data()['formset']
        if formset.is_valid():
            send_mail_to_objects = formset.save(commit=False)
            for send_mail_to in send_mail_to_objects:
                send_mail_to.notification = notification
                send_mail_to.save()

        # Планируем задачу
        schedule_job(notification)

        return super().form_valid(form)

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    send_mail_to = notification.send_mail_to.all()  # Получаем всех клиентов, к которым будет отправлено письмо
    send_logs = notification.send_log.all()  # Получаем логи отправок

    context = {
        'object': notification,
        'send_mail_to': send_mail_to,
        'send_logs': send_logs,
    }

    return render(request, 'notification_app/notification_detail.html', context)


class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    model = Notification
    success_url = reverse_lazy('notification_app:notification_list')


@require_POST
def block_unblock_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    # Check if the user is in the manager group
    if request.user.groups.filter(name='manager').exists():
        # Toggle the status based on the current status
        if notification.status.pk == 2:  # If active, block it
            notification.status = Status.objects.get(pk=3)  # Assuming pk=3 is for 'blocked'
        else:  # If blocked, unblock it
            notification.status = Status.objects.get(pk=2)  # Assuming pk=2 is for 'active'

        notification.save()

    return redirect('notification_app:notification_list')  # Redirect to the notification list


class ClientListView(LoginRequiredMixin, ListView):
    model = Client

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('notification_app:client_list')

    def form_valid(self, form):
        client = form.save(commit=False)
        client.owner = self.request.user  # Устанавливаем владельца
        return super().form_valid(form)


class ClientEditView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('notification_app:client_list')

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('notification_app:client_list')


class MailListView(LoginRequiredMixin, ListView):
    model = Mail

    def get_queryset(self):
        return Mail.objects.filter(owner=self.request.user)

class MailDetailView(LoginRequiredMixin, DetailView):
    model = Mail


class MailCreateView(LoginRequiredMixin, CreateView):
    model = Mail
    form_class = MailForm
    success_url = reverse_lazy('notification_app:mail_list')

    def form_valid(self, form):
        mail = form.save(commit=False)
        mail.owner = self.request.user  # Устанавливаем владельца
        return super().form_valid(form)


class MailEditView(LoginRequiredMixin, UpdateView):
    model = Mail
    form_class = MailForm
    success_url = reverse_lazy('notification_app:mail_list')

class MailDeleteView(LoginRequiredMixin, DeleteView):
    model = Mail
    success_url = reverse_lazy('notification_app:mail_list')


def home_view(request):
    # Общее количество рассылок
    total_notifications = Notification.objects.count()

    # Количество активных рассылок
    active_notifications = Notification.objects.filter(status__id=2).count()

    # Количество уникальных клиентов для рассылок
    unique_clients_count = Client.objects.filter(send_mail_to__isnull=False).distinct().count()

    # Три случайные статьи из блога
    all_blogs = list(Blog.objects.filter(is_published=True))
    random_blogs = random.sample(all_blogs, min(len(all_blogs), 3))

    context = {
        'total_notifications': total_notifications,
        'active_notifications': active_notifications,
        'unique_clients_count': unique_clients_count,
        'random_blogs': random_blogs,
    }
    return render(request, 'notification_app/home.html', context)

