from rest_framework.permissions import BasePermission
from rest_framework.filters import BaseFilterBackend


class BaseRolePermission(BasePermission):
    """
    Base permission class for role-based access control.
    Subclasses only need to define `allowed_roles` and an optional `message`.
    """
    allowed_roles = ()
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in self.allowed_roles
        )


class IsStudent(BaseRolePermission):
    allowed_roles = ('student',)
    message = "Only students can access this resource."


class IsFaculty(BaseRolePermission):
    allowed_roles = ('faculty',)
    message = "Only faculty can access this resource."


class IsAdmin(BaseRolePermission):
    allowed_roles = ('admin',)
    message = "Only admins can access this resource."


class IsFacultyOrAdmin(BaseRolePermission):
    allowed_roles = ('faculty', 'admin')
    message = "Only faculty or admin can access this resource."


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission class allowing admins full access, or owners access to their own data.

    NOTE ON DRF BEHAVIOR:
    `has_permission` blocks unauthenticated users from list/create views.
    However, `has_object_permission` is NEVER called by DRF during list actions.
    To prevent data leakage on list responses, pair this with `OwnerOrAdminFilterBackend`
    or override `get_queryset()` in your view!
    """
    message = "You can only access your own data."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        if getattr(request.user, 'role', None) == 'admin':
            return True

        owner = getattr(obj, 'user', obj)
        return owner == request.user


class OwnerOrAdminFilterBackend(BaseFilterBackend):
    """
    DRF Filter Backend that enforces list-level data isolation.

    WHY THIS IS NEEDED:
    DRF's `has_object_permission` is NEVER called during list actions (`GET /api/items/`).
    `IsOwnerOrAdmin.has_permission` only checks if the user is authenticated.
    Without this filter backend (or explicit `get_queryset()` filtering), any authenticated user
    requesting a list endpoint would receive ALL records in the database.

    BEHAVIOR:
    - Admins: See all records in the queryset.
    - Regular Users: See ONLY their own records.
    - Unauthenticated: Returns empty queryset.
    """
    owner_field = 'user'

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not (user and user.is_authenticated):
            return queryset.none()

        if getattr(user, 'role', None) == 'admin':
            return queryset

        model = queryset.model

        # Case 1: The model IS the User model
        if model == type(user):
            return queryset.filter(pk=user.pk)

        # Case 2: The model has a foreign key to User (e.g. `user`)
        field_name = getattr(view, 'owner_user_field', self.owner_field)
        if hasattr(model, field_name):
            return queryset.filter(**{field_name: user})

        return queryset