from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic, View
from django.views.generic import FormView, UpdateView

from shortener_platform.forms.auth import LoginForm, RegisterForm, PasswordResetForm, EditProfileForm
from shortener_platform.forms.shortener import LinkForm
from shortener_platform.models import Link
from shortener_platform.tasks import send_password_reset_email


class Index(generic.TemplateView):
    template_name = 'index.html'


class DashboardView(generic.TemplateView, LoginRequiredMixin):
    template_name = 'user/home.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data()
        links = Link.objects.filter(owner=self.request.user)
        context['active'] = links.filter(expires_at__gt=timezone.now()).count()
        context['expired'] = links.filter(expires_at__lt=timezone.now()).count()
        return context


class ProfileView(generic.TemplateView, LoginRequiredMixin):
    template_name = 'user/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(ProfileView, self).dispatch(request, *args, **kwargs)


class EditProfileView(generic.TemplateView, LoginRequiredMixin, UpdateView):
    template_name = 'user/edit-profile.html'
    form_class = EditProfileForm
    model = User
    object = None

    def get_object(self, queryset=None, **kwargs):
        user = None
        try:
            user = self.model.objects.get(pk=self.request.user.pk)
        except Exception as e:
            print(e)
            pass
        return user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(self.request.POST or None, instance=self.get_object())

        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, 'Profile has been updated successfully.')
            return self.get_success_url()
        else:
            messages.error(request, 'Invalid data provided')
            return self.get_failure_url()

    def get_success_url(self):
        if self.request.GET.get('next', None) is not None:
            return HttpResponseRedirect(self.request.GET.get('next'))
        return HttpResponseRedirect(reverse('profile'))

    @staticmethod
    def get_failure_url():
        return HttpResponseRedirect(reverse('edit-profile'))

    @staticmethod
    def get_self_page_url():
        return HttpResponseRedirect(reverse('edit-profile'))

    def get_context_data(self, **kwargs):
        context = super(EditProfileView, self).get_context_data()
        context['form'] = self.form_class(self.request.POST or None, instance=self.get_object())
        context['messages'] = messages.get_messages(self.request)
        context['user'] = self.get_object()
        return context


class LinkView(generic.TemplateView, LoginRequiredMixin):
    template_name = 'user/links.html'

    def get_context_data(self, **kwargs):
        context = super(LinkView, self).get_context_data()
        context['messages'] = messages.get_messages(self.request)
        context['links'] = Link.objects.filter(owner=self.request.user)
        return context


class NewLinkView(generic.TemplateView, LoginRequiredMixin, FormView):
    template_name = 'user/new-link.html'
    form_class = LinkForm
    link = None

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST or None)

        if form.is_valid():
            url = form.cleaned_data.get('url', None)

            if url is not None:
                self.link = form.save(commit=False)
                self.link.expires_at = timezone.now() + timezone.timedelta(minutes=1)
                self.link.owner = self.request.user
                self.link.save()
                messages.success(request, 'URL has been shortened successfully.')
                return self.get_success_url()
            else:
                messages.error(request, 'URL cannot be empty')
                return self.get_failure_url()
        else:
            messages.error(request, 'Invalid URL provided')
            return self.get_failure_url()

    def get_success_url(self):
        if self.request.GET.get('next', None) is not None:
            return HttpResponseRedirect(self.request.GET.get('next'))
        return HttpResponseRedirect(reverse('links'))

    @staticmethod
    def get_failure_url():
        return HttpResponseRedirect(reverse('login'))

    def get_context_data(self, **kwargs):
        context = super(NewLinkView, self).get_context_data()
        context['form'] = self.form_class(self.request.POST or None)
        context['messages'] = messages.get_messages(self.request)
        context['link'] = self.link
        return context


class EditLinkView(generic.TemplateView, LoginRequiredMixin, UpdateView):
    template_name = 'user/new-link.html'
    form_class = LinkForm
    model = Link
    object = None

    def get_object(self, queryset=None, **kwargs):
        print(kwargs)
        link = None
        try:
            link = self.model.objects.get(pk=self.kwargs['link'])
        except Exception as e:
            print(e)
            pass
        return link

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(self.request.POST or None, instance=self.get_object())

        if form.is_valid():
            url = form.cleaned_data.get('url', None)

            if url is not None:
                link = form.save(commit=False)
                link.save()
                messages.success(request, 'URL has been updated successfully.')
                return self.get_success_url()
            else:
                messages.error(request, 'URL cannot be empty')
                return self.get_failure_url()
        else:
            messages.error(request, 'Invalid URL provided')
            return self.get_failure_url()

    def get_success_url(self):
        if self.request.GET.get('next', None) is not None:
            return HttpResponseRedirect(self.request.GET.get('next'))
        return HttpResponseRedirect(reverse('links'))

    @staticmethod
    def get_failure_url():
        return HttpResponseRedirect(reverse('login'))

    def get_self_page_url(self):
        return HttpResponseRedirect(reverse('edit-link', kwargs={'link': self.kwargs['link']}))

    def get_context_data(self, **kwargs):
        context = super(EditLinkView, self).get_context_data()
        context['form'] = self.form_class(self.request.POST or None, instance=self.get_object())
        context['messages'] = messages.get_messages(self.request)
        context['link'] = self.get_object()
        return context


class LoginView(generic.TemplateView, FormView):
    form_class = LoginForm
    template_name = 'auth/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home'))
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username', None)
            password = form.cleaned_data.get('password', None)

            if username is not None and password is not None:
                user_obj = authenticate(request, username=username, password=password)
                if user_obj:
                    login(request=request, user=user_obj)
                    return self.get_success_url()
                else:
                    messages.error(request, "Account not found, please register an account.")
                    return self.get_failure_url()
            else:
                messages.error(request, "Failed authenticating you, try again.")
                return self.get_failure_url()
        else:
            messages.error(request, "Enter valid credentials to login.")
            return self.get_failure_url()

    def get_success_url(self):
        if self.request.GET.get('next', None) is not None:
            return HttpResponseRedirect(self.request.GET.get('next'))
        return HttpResponseRedirect(reverse('home'))

    @staticmethod
    def get_failure_url():
        return HttpResponseRedirect(reverse('login'))

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data()
        context['form'] = self.form_class(self.request.POST or None)
        context['messages'] = messages.get_messages(self.request)
        return context


class RegisterView(generic.TemplateView, FormView):
    form_class = RegisterForm
    template_name = 'auth/register.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST or None)
        if form.is_valid():
            if request.POST:
                try:
                    # Saving the user
                    check = self.form_class.Meta.model.objects.filter(
                        Q(username=form.cleaned_data.get('username')) |
                        Q(email=form.cleaned_data.get('email'))
                    )
                    if check.exists():
                        messages.error(request,  "User already exists.")
                        return self.get_failure_url()
                    else:
                        if form.cleaned_data.get('password', None) and form.cleaned_data.get('confirm_password', None):
                            if form.cleaned_data.get('password', None) == form.cleaned_data.get('confirm_password', None):
                                user = form.save(commit=False)
                                user.password = make_password(form.cleaned_data.get('password'))
                                user.save()
                                messages.success(request, "Account created successfully")
                                return self.get_success_url()
                            else:
                                messages.error(request, "Passwords do not match")
                                return self.get_failure_url()
                        else:
                            messages.error(request, "One password field is empty.")
                            return self.get_failure_url()
                except Exception as e:
                    messages.error(request, "Sorry! an error occurred. \n {}".format(e))
                    return self.get_failure_url()
        else:
            messages.error(request, "{}".format(form.errors))
            return self.get_failure_url()

    def get_success_url(self):
        if self.request.GET.get('next', None) is not None:
            return HttpResponseRedirect(self.request.GET.get('next'))
        return HttpResponseRedirect(reverse('login'))

    @staticmethod
    def get_failure_url():
        return HttpResponseRedirect(reverse('register'))

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data()
        context['form'] = self.form_class(self.request.POST or None)
        context['messages'] = messages.get_messages(self.request)
        return context


class PasswordResetView(generic.TemplateView, FormView):
    form_class = PasswordResetForm
    template_name = 'auth/password-reset.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST or None)
        if form.is_valid():
            if request.POST:
                try:
                    # Saving the user
                    check = get_user_model().objects.filter(
                        Q(username=form.cleaned_data.get('email')) |
                        Q(email=form.cleaned_data.get('email'))
                    )
                    if check.exists():
                        send_password_reset_email.delay(check.first().pk)
                        messages.error(request,  "Email has been sent")
                        return self.get_success_url()
                    else:
                        messages.error(request, "Records not found.")
                        return self.get_failure_url()
                except Exception as e:
                    messages.error(request, "Sorry! an error occurred. \n {}".format(e))
                    return self.get_failure_url()
        else:
            messages.error(request, "{}".format(form.errors))
            return self.get_failure_url()

    def get_success_url(self):
        if self.request.GET.get('next', None) is not None:
            return HttpResponseRedirect(self.request.GET.get('next'))
        return HttpResponseRedirect(reverse('confirm_password_reset'))

    @staticmethod
    def get_failure_url():
        return HttpResponseRedirect(reverse('password-reset'))

    def get_context_data(self, **kwargs):
        context = super(PasswordResetView, self).get_context_data()
        context['form'] = self.form_class(self.request.POST or None)
        context['messages'] = messages.get_messages(self.request)
        return context


class LogoutView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return HttpResponseRedirect(reverse('login'))
