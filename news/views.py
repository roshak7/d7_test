from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.views import View
from .tasks import hello

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post, Category, Author
from .filters import PostFilter
from .forms import NewsForm
from appointment.models import Appointment
from django.core.mail import mail_admins, mail_managers  # импортируем функцию для массовой отправки писем админам
from datetime import datetime


class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
            client_name=request.POST['client_name'],
            message=request.POST['message'],
        )
        appointment.save()

        # отправляем письмо всем админам по аналогии с send_mail, только здесь получателя указывать не надо
        mail_admins(
            subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        mail_managers(
            subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        return redirect('appointments:make_appointment')

    # связывает объекты категории и текущего пользователя
    def get(self, request, category_id, *args, **kwargs):
        print(request.GET)
        user = self.request.user
        category = Category.objects.get(pk=category_id)
        if not category.subscribers.filter(pk=user.pk):
            is_subscriber = False
            category.subscribers.add(user)
        else:
            is_subscriber = True

        context = {
            'categories': Category.objects.all(),
            'category': Category.objects.get(pk=category_id),
            'is_subscriber': is_subscriber
        }
        return render(request, 'subscribe_category.html', context)

    # def post(self, request, *args, **kwargs):
    #     user = self.request.user
    #     print(user)
    #     return render(request, 'subscribe_category.html', context)


class NewsList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-creation_datetime')
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_amount'] = len(Post.objects.all())
        context['categories'] = Category.objects.all()
        return context


class NewsOfCategory(NewsList):
    template_name = 'news_category.html'

    def get_queryset(self):
        return Post.objects.filter(category=self.kwargs['category_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = None
        return context


class NewsSearch(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-creation_datetime')
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_amount'] = len(Post.objects.all())
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['categories'] = Category.objects.all()
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_one.html'
    context_object_name = 'news_one'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['post_categories'] = self.model.category
        return context


class NewsAdd(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    template_name = 'news_add.html'
    form_class = NewsForm

    # def form_valid(self, form):
    #     # instance = form.save(commit=False)
    #     # instance.author = self.request.user.author
    #     # instance.save()
    #     post = form.save()
    #
    #     return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = NewsForm(request.POST)

        # Нужно будет реализовать для нескольких категорий
        # categories_pk = request.POST.getlist('category')
        # categories = Category.objects.filter(pk__in=categories_pk)

        category_pk = request.POST['category']
        client_text = request.POST['text']
        client_title = request.POST['title']
        category = Category.objects.get(pk=category_pk)
        subscribers = category.subscribers.all()

        if form.is_valid():
            post = form.save(commit=False)
            post.author = self.request.user.author
            post.save()
            print(post)

            # Рассылка почты
            for subscriber in subscribers:
                print(subscriber.email)
                if subscriber.email:
                    print(f'нашли юзера, отправляем ему на емаил. {subscriber.email}')

                    # Отправка HTML
                    html_content = render_to_string(
                        'mail.html', {
                            'user': subscriber,
                            'text': client_text[:50],
                            'post': post,
                        }
                    )
                    msg = EmailMultiAlternatives(
                        subject=f'Здравствуй, {subscriber.username}. Новая статья в твоём любимом разделе!',
                        body=f'{client_text[:50]}',
                        from_email='pozvizdd@yandex.ru',
                        to=[subscriber.email, 'olegmodenov@gmail.com'],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    # # Отправка простого текста
                    # send_mail(
                    #     subject=f'{subscriber.email}',
                    #     message=f'Появился новый пост!\n {client_title}: {client_text[:50]}. \n Ссылка на статью: ',
                    #     from_email='pozvizdd@yandex.ru',
                    #     recipient_list=[subscriber.email, 'olegmodenov@gmail.com'],
            return redirect(post)

        return NewsForm(request, 'news/news_add.html', {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class NewsEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    template_name = 'news_edit.html'
    form_class = NewsForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class NewsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news_delete.html'
    context_object_name = 'news_one'
    queryset = Post.objects.all()
    success_url = '/news/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class IndexView(View):
    def get(self, request):
        hello.delay()
        return HttpResponse('Hello!')