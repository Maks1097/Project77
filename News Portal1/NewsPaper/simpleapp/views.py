from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from datetime import datetime
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import New
from .filters import NewFilter
from .forms import NewForm, ArticleForm
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .models import Subscription, Category
from django.core.cache import cache
from django.utils.translation import gettext as _
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import redirect
import pytz
#from django.utils.translation import activate, get_supported_language_variant, LANGUAGE_SESSION_KEY

class NewsList(ListView):
    model = New
    ordering = '-time_now'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context


class NewDetail(DetailView):
    template_name = 'new.html'
    queryset = New.objects.all()

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'new-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'new-{self.kwargs["pk"]}', obj)
            return obj


class NewSearch(ListView):
    model = New
    ordering = '-time_now'
    template_name = 'news_search.html'
    context_object_name = 'news'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context


class NewCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('simpleapp.add_new',)
    form_class = NewForm
    model = New
    template_name = 'news_edit.html'


class NewUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('simpleapp.change_new',)
    form_class = NewForm
    model = New
    template_name = 'news_edit.html'


class NewDelete(PermissionRequiredMixin, DeleteView):
    raise_exception = True
    permission_required = ('simpleapp.delete_new',)
    model = New
    template_name = 'news_delete.html'
    success_url = reverse_lazy('new_list')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('simpleapp.add_new',)
    form_class = ArticleForm
    model = New
    template_name = 'news_edit.html'


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )


class Index(View):
    def get(self, request):
        models = New.objects.all()

        context = {
            'models': models,
            'current_time': timezone.localtime(timezone.now()),
            'timezones': pytz.common_timezones #  добавляем в контекст все доступные часовые пояса
        }

        return HttpResponse(render(request, 'news.html', context))


    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')