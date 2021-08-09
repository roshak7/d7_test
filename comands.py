# Category.objects.all().delete()

from news.models import User, Author, Category, Post, Comment

# Создание объектов
user1 = User.objects.create(username='Василий')
user2 = User.objects.create(username='Алексей')

author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)

category1 = Category.objects.create(title='Спорт')
category2 = Category.objects.get(title='Политика')
category3 = Category.objects.create(title='Развлечения')
category4 = Category.objects.create(title='Музыка')

article1 = Post.objects.create(title='Статья 1', text='Содержание статьи 1', author=author1)
article2 = Post.objects.create(title='Статья 2', text='Содержание статьи 2', author=author2)
news1 = Post.objects.create(type=True, title='Новость 1', text='Содержание новости 1', author=author1)

comment1 = Comment.objects.create(text='Комментарий 1', post=article1, user=user1)
comment2 = Comment.objects.create(text='Комментарий 2', post=article1, user=user2)
comment3 = Comment.objects.create(text='Комментарий 3', post=article2, user=user1)
comment4 = Comment.objects.create(text='Комментарий 4', post=news1, user=user1)
comment5 = Comment.objects.create(text='Комментарий 5', post=news1, user=user2)
comment6 = Comment.objects.create(text='Комментарий 6', post=news1, user=user2)
comment7 = Comment.objects.create(text='Комментарий 7', post=article2, user=user1)

# Добавление категорий
article1.category.add(category1)
article2.category.add(category2)
news1.category.add(category3, category4)

# Проверка категорий
for category in news1.category.values('title'):
    print(category)

# Работа методов like(), dislike(), update_rating()
comment1.like()
comment4.like()
for i in range(2):
    comment2.like()
    comment5.dislike()
for i in range(3):
    comment3.like()
    comment6.dislike()

article1.like()
for i in range(5):
    article2.like()
news1.dislike()
news1.dislike()

author1.update_rating()
author2.update_rating()

# Лучший автор, лучшая статья, комментарии к лучшей статье
best_author = Author.objects.all().order_by('-rating')[0]
print(best_author)

best_post = Post.objects.all().order_by('-rating')[0]
print(f'Лучший пост: \n'
      f'date: {best_post.creation_datetime} \n'
      f'author_name: {best_post.author.user} \n'
      f'post_rating: {best_post.rating} \n'
      f'title: {best_post.title} \n'
      f'preview: {best_post.preview()}')

best_post_comments = Post.objects.all().order_by('-rating')[0].comment_set.values(
    'creation_datetime', 'user', 'text', 'rating')
for comment in best_post_comments:
    print(comment)
