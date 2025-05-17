from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """ Класс для проверки, является ли пользователь администратором """

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if user is None:
            return False
        return user.is_authenticated and (user.is_admin or user.is_staff)

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_admin
            or request.user.is_staff
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """ Класс для проверки прав доступа к объектам """

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ для чтения всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для изменения проверяем, является ли пользователь автором,
        # модератором или администратором
        return (
            obj.author == request.user
            or request.user.role in ['admin', 'moderator']
        )
