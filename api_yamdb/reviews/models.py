from django.core.validators import (
    MaxValueValidator, RegexValidator, MinValueValidator
)
from django.db import models
from django.db.models import Avg
from django.utils.timezone import now
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import User


class Category(models.Model):
    """Категории произведений (Фильмы, Книги, Музыка)."""

    name = models.CharField(
        'Название',
        max_length=256,
        help_text='Укажите название категории (например, "Фильмы")'
    )
    slug = models.SlugField(
        'Слаг',
        max_length=50,
        unique=True,
        validators=[RegexValidator(regex='^[-a-zA-Z0-9_]+$')],
        help_text=('Уникальный идентификатор категории'
                   '(латинские буквы, цифры, дефисы и подчёркивания)')
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанры произведений (Комедия, Драма, Фантастика)."""

    name = models.CharField(
        'Название',
        max_length=256,
        help_text='Укажите название жанра (например, "Комедия")'
    )
    slug = models.SlugField(
        'Слаг',
        max_length=50,
        unique=True,
        validators=[RegexValidator(regex='^[-a-zA-Z0-9_]+$')],
        help_text=('Уникальный идентификатор жанра '
                   '(латинские буквы, цифры, дефисы и подчёркивания)')
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для хранения отзывов на произведения."""

    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        help_text='Произведение, к которому относится отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name='reviews',
        verbose_name='Автор отзыва',
        help_text='Автор отзыва'
    )
    text = models.TextField(
        'Текст отзыва',
        help_text='Текст вашего отзыва'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        help_text='Оценка от 1 до 10'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата создания отзыва'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title}'


class Title(models.Model):
    """Произведения (фильмы, книги, музыкальные треки)."""

    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        help_text='Выберите категорию произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
        through='GenreTitle',
        help_text='Выберите жанры произведения'
    )
    name = models.CharField(
        'Название',
        max_length=256,
        help_text='Укажите название произведения'
    )
    year = models.IntegerField(
        'Год выпуска',
        validators=[MaxValueValidator(now().year)],
        help_text='Укажите год выпуска произведения'
    )
    description = models.TextField(
        'Описание',
        blank=True,
        null=True,
        help_text='Добавьте описание произведения (необязательно)'
    )
    rating = models.IntegerField(
        'Рейтинг',
        null=True,
        blank=True,
        help_text='Рейтинг произведения (вычисляется автоматически)'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name

    def update_rating(self):
        """Обновление рейтинга при изменении отзывов"""
        avg_score = self.reviews.aggregate(Avg('score'))['score__avg']
        self.rating = int(avg_score) if avg_score else None
        self.save()


class GenreTitle(models.Model):
    """Промежуточная модель для связи произведений и жанров."""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='genre_titles'
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE,
        related_name='genre_titles'
    )

    class Meta:
        verbose_name = 'Связь жанра и произведения'
        verbose_name_plural = 'Связи жанров и произведений'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            )
        ]

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Comment(models.Model):
    """Модель для хранения комментариев к отзывам."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        help_text='Отзыв, к которому относится комментарий'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Текст вашего комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор комментария'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата создания комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Комментарий от {self.author} к отзыву {self.review.id}'


@receiver([post_save, post_delete], sender=Review)
def update_title_rating(sender, instance, **kwargs):
    """
    Сигнал для обновления рейтинга произведения при изменении отзывов.

    """
    instance.title.update_rating()
