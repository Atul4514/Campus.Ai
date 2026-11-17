class OwnerOrAdminQuerysetMixin:
    """Restrict a ViewSet's base queryset to its owner, except for admins.

    Override ``owner_user_field`` for models whose owner relation is not named
    ``user``. User records themselves are scoped by primary key.
    """
    owner_user_field = 'user'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)
        if not (user and user.is_authenticated):
            return queryset.none()
        if getattr(user, 'role', None) == 'admin':
            return queryset

        if queryset.model == type(user):
            return queryset.filter(pk=user.pk)
        if any(field.name == self.owner_user_field for field in queryset.model._meta.get_fields()):
            return queryset.filter(**{self.owner_user_field: user})
        return queryset.none()
