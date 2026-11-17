from rest_framework.permissions import BasePermission
from rest_framework.filters import BaseFilterBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist


def _is_authenticated(request):
    return bool(request.user and request.user.is_authenticated)


class BaseRolePermission(BasePermission):
    """Grants access only to authenticated users whose `role` is in `allowed_roles`."""
    allowed_roles = frozenset()
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        return _is_authenticated(request) and getattr(request.user, 'role', None) in self.allowed_roles


class IsStudent(BaseRolePermission):
    allowed_roles = frozenset({'student'})
    message = "Only students can access this resource."


class IsFaculty(BaseRolePermission):
    allowed_roles = frozenset({'faculty'})
    message = "Only faculty can access this resource."


class IsAdmin(BaseRolePermission):
    allowed_roles = frozenset({'admin'})
    message = "Only admins can access this resource."


class IsFacultyOrAdmin(BaseRolePermission):
    allowed_roles = frozenset({'faculty', 'admin'})
    message = "Only faculty or admin can access this resource."


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: admins get full access, owners get access to their own object.

    `has_permission` only blocks anonymous users from list/create — it does NOT
    filter list results. Pair this with `OwnerOrAdminFilterBackend` (or a filtered
    `get_queryset()`) to stop non-owners from seeing other users' rows in `list`.
    """
    message = "You can only access your own data."

    def has_permission(self, request, view):
        return _is_authenticated(request)

    def has_object_permission(self, request, view, obj):
        if not _is_authenticated(request):
            return False
        if getattr(request.user, 'role', None) == 'admin':
            return True
        owner = getattr(obj, 'user', obj)
        return owner == request.user


class OwnerOrAdminFilterBackend(BaseFilterBackend):
    """
    Queryset-level counterpart to `IsOwnerOrAdmin`. `has_object_permission` is never
    called for `list`, so without this (or equivalent `get_queryset()` filtering) any
    authenticated user would see every row.

    Admins -> full queryset. Others -> rows owned by `request.user`. Anonymous -> none.
    """
    owner_field = 'user'

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not _is_authenticated(request):
            return queryset.none()

        if getattr(user, 'role', None) == 'admin':
            return queryset

        model = queryset.model

        # Model IS the user model
        if model is get_user_model():
            return queryset.filter(pk=user.pk)

        # Model has an actual FK/relation field to the user
        field_name = getattr(view, 'owner_user_field', self.owner_field)
        try:
            model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return queryset

        return queryset.filter(**{field_name: user})