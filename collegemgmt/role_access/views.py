from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.contrib import messages

from core.models import AccessLog

User = get_user_model()


@login_required(login_url='login_page')
def manage_roles(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Only admins can manage roles and access.')
        return redirect('dashboard_page')

    users = User.objects.all().order_by('username')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        if user_id and role:
            target_user = users.filter(id=user_id).first()
            if target_user:
                if role not in dict(User.ROLE_CHOICES):
                    messages.error(request, 'Invalid role selected.')
                elif target_user.pk == request.user.pk:
                    messages.error(request, 'You cannot change your own role.')
                elif target_user.role == role:
                    messages.info(request, f'{target_user.username} already has that role.')
                else:
                    with transaction.atomic():
                        target_user.role = role
                        target_user.save(update_fields=['role'])
                        AccessLog.objects.create(
                            viewer=request.user,
                            subject=target_user,
                            model_name='User',
                            object_id=target_user.pk,
                            action='update',
                        )
                    messages.success(request, f'Role updated for {target_user.username}.')
            else:
                messages.error(request, 'User not found.')
        return redirect('role_access:manage_roles')

    return render(request, 'accounts/role_access_management.html', {'users': users})
