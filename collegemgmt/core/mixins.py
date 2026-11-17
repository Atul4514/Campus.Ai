from .models import AccessLog


class AccessLogMixin:
    """
    Mixin for DRF ViewSets. Logs every retrieve/update of an object,
    skipping the case where a user is viewing their own data (no need to log that).
    Assumes the object has a `.user` field pointing to the subject,
    or IS the User instance itself.
    """
    log_model_name = None  # override in each ViewSet, e.g. "StudentProfile"

    def _get_subject(self, obj):
        return getattr(obj, 'user', obj)

    def _log_access(self, request, obj, action='view'):
        subject = self._get_subject(obj)
        if subject == request.user:
            return  # don't log self-views
        AccessLog.objects.create(
            viewer=request.user,
            subject=subject,
            model_name=self.log_model_name or obj.__class__.__name__,
            object_id=obj.pk,
            action=action,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self._log_access(request, instance, action='view')
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._log_access(request, instance, action='update')
        return super().update(request, *args, **kwargs)