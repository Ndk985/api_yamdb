from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator, RegexValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import RegexValidator


def validate_username(value):
    """Валидация: username != me"""
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )


USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class User(AbstractUser):
    """Модель - пользователи."""
    username = models.CharField(
        'Пользователь',
        validators=[
            validate_username,
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы'
            )
        ],
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        help_text=('Обязательное поле. Только буквы и цифры. До 150 символов'),
        error_messages={
            'unique': ('Пользователь с таким именем уже зарегистрирован.')
        },
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        blank=False,
        unique=True,
        null=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='[][][][][]'
    )
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        verbose_name='Группы'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        verbose_name='Права доступа'
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name='reviews',
        verbose_name='Автор'
    )
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]


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

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)


@receiver([post_save, post_delete], sender=Review)
def update_title_rating(sender, instance, **kwargs):
    """
    Сигнал для обновления рейтинга произведения при изменении отзывов.

    """
    instance.title.update_rating()
