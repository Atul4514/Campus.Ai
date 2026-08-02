from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    message = "Only students can access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student'
        )


class IsFaculty(BasePermission):
    message = "Only faculty can access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'faculty'
        )


class IsAdmin(BasePermission):
    message = "Only admins can access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsFacultyOrAdmin(BasePermission):
    message = "Only faculty or admin can access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['faculty', 'admin']
        )


class IsOwnerOrAdmin(BasePermission):
    message = "You can only access your own data."

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        owner = getattr(obj, 'user', obj)
        return owner == request.user