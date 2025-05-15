from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'bio',
        'first_name',
        'last_name',
        'confirmation_code',
    ) #указывает поля модели, которые будут отображаться в списке пользователей в админке.
    search_fields = ('username', 'role',) #поле поиска 
    list_filter = ('username',)  #боковую панель фильтров по полю username
    empty_value_display = '-пусто-' #задает отображение пустых значений 


admin.site.register(User, UserAdmin)
#Регистрация модели User с настройками UserAdmin