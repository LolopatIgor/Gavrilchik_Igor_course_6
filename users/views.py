from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from config import settings
from users.forms import UserRegisterForm
from users.models import User
from django.http import HttpResponse
import random
import string
import time


def generate_random_password(length=8):
    # Генерация случайного пароля из цифр и букв
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Поиск пользователя по email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("Пользователь с таким email не найден.")

        # Генерация нового пароля
        new_password = generate_random_password()

        # Захешировать новый пароль и обновить пароль пользователя
        user.password = make_password(new_password)
        user.save()

        # Отправка нового пароля на email
        subject = 'Восстановление пароля'
        message = f'Ваш новый пароль: {new_password}'
        recipient_list = [email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

        return HttpResponse("Новый пароль отправлен на вашу электронную почту.")

    return render(request, 'users/password_request.html')


def activate(request, uidb64, token):
    try:
        # Декодируем идентификатор пользователя из URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Проверяем токен
    if user is not None and default_token_generator.check_token(user, token):
        # Если токен валиден, активируем пользователя
        user.is_active = True
        user.save()
        messages.success(request, 'Ваш аккаунт успешно подтвержден!')
        return render(request, 'users/activation_confirm.html', {'message': 'Ваш аккаунт успешно подтвержден!'})
    else:
        # Если токен недействителен, выводим сообщение об ошибке
        messages.error(request, 'Ссылка активации недействительна!')
        return render(request, 'users/activation_confirm.html', {'message': 'Ссылка активации недействительна!'})


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        # Сохраняем пользователя, но не активируем его до верификации
        user = form.save(commit=False)
        user.is_active = False  # Деактивируем пользователя до верификации
        user.save()

        # Вызов родительского метода form_valid
        response = super().form_valid(form)

        # Генерация токена и активационной ссылки
        token = default_token_generator.make_token(user)
        activation_link = reverse('users:activate', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token,
        })

        # Отправка письма с активацией
        current_site = get_current_site(self.request)
        subject = 'Подтверждение регистрации'
        message = (
            f"Привет, {user.username or user.email}!\n\n"
            f"Для подтверждения регистрации на нашем сайте, перейдите по следующей ссылке:\n"
            f"http://{current_site.domain}{activation_link}\n\n"
            "Спасибо за регистрацию!"
        )
        user.email_user(subject, message)

        messages.success(self.request, 'Регистрация прошла успешно! Проверьте вашу почту для подтверждения аккаунта.')

        # Возвращаем ответ после отправки письма
        return response

def is_manager(user):
    return user.groups.filter(name='manager').exists()

class UserListView(LoginRequiredMixin, UserPassesTestMixin,ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.groups.filter(name='manager').exists()

    def get_queryset(self):
        # Получаем всех активных пользователей, которые не являются суперпользователями
        return User.objects.filter(is_superuser=False)

@user_passes_test(is_manager)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect(reverse('users:user_list'))