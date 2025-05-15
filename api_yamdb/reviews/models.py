from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import now


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
