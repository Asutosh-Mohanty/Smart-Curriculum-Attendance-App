from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse

from core.models import Announcement
from students.models import Student
from teachers.models import Teacher, Subject
from .models import Branch, Degree, Group, GroupSubjectAssignment


def _require_staff(user):
    return user.is_staff


@login_required
def admin_dashboard(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get all users
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    
    # Get recent announcements
    announcements = Announcement.objects.all().order_by('-created_at')[:5]
    
    branches_count = Branch.objects.count()
    degrees_count = Degree.objects.count()
    groups_count = Group.objects.count()
    subjects_count = Subject.objects.count()
    
    context = {
        'students': students,
        'teachers': teachers,
        'announcements': announcements,
        'branches_count': branches_count,
        'degrees_count': degrees_count,
        'groups_count': groups_count,
        'subjects_count': subjects_count,
    }
    return render(request, 'admins/admin_dashboard.html', context)


# --- Lightweight JSON endpoints for dependent dropdowns ---
@login_required
def api_groups_by_degree_branch(request):
    if not _require_staff(request.user):
        return JsonResponse({'detail': 'Forbidden'}, status=403)
    degree_id = request.GET.get('degree')
    branch_id = request.GET.get('branch')
    qs = Group.objects.all()
    if degree_id:
        qs = qs.filter(degree_id=degree_id)
    if branch_id:
        qs = qs.filter(branch_id=branch_id)
    data = [
        {
            'id': g.id,
            'name': g.name,
            'branch_id': g.branch_id,
            'degree_id': g.degree_id,
            'label': f"{g.name} - {g.branch.name} ({g.degree.name})"
        }
        for g in qs.select_related('branch', 'degree')
    ]
    return JsonResponse({'results': data})


@login_required
def api_branches_by_degree(request):
    if not _require_staff(request.user):
        return JsonResponse({'detail': 'Forbidden'}, status=403)
    degree_id = request.GET.get('degree')
    qs = Branch.objects.all()
    if degree_id:
        qs = qs.filter(degree_id=degree_id)
    data = [
        {'id': b.id, 'name': b.name, 'degree_id': b.degree_id}
        for b in qs.select_related('degree')
    ]
    return JsonResponse({'results': data})


@login_required
def create_announcement(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        target_audience = request.POST.get('target_audience', 'all')
        
        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return render(request, 'admins/create_announcement.html')
        
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            target_audience=target_audience,
            created_by=request.user
        )
        
        # Get target audience count for success message
        if target_audience == 'all':
            target_count = Student.objects.count() + Teacher.objects.count()
            target_name = "all users"
        elif target_audience == 'students':
            target_count = Student.objects.count()
            target_name = "students"
        else:  # teachers
            target_count = Teacher.objects.count()
            target_name = "teachers"
        
        messages.success(request, f'Announcement created successfully! Sent to {target_count} {target_name}.')
        return redirect('admins:dashboard')
    
    return render(request, 'admins/create_announcement.html')


@login_required
def add_user(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        if role == 'student':
            roll_number = request.POST.get('roll_number')
            interests = request.POST.get('interests', '')
            branch_id = request.POST.get('branch')
            degree_id = request.POST.get('degree')
            group_id = request.POST.get('group')

            # Validate consistency: branch belongs to degree, group matches both
            branch = Branch.objects.filter(id=branch_id).first() if branch_id else None
            degree = Degree.objects.filter(id=degree_id).first() if degree_id else None
            group = Group.objects.filter(id=group_id).first() if group_id else None
            if degree and branch and branch.degree_id and int(branch.degree_id) != int(degree.id):
                messages.error(request, 'Selected Branch does not belong to the selected Degree.')
                return render(request, 'admins/add_user.html', {
                    'branches': Branch.objects.all(),
                    'degrees': Degree.objects.all(),
                    'groups': Group.objects.all(),
                })
            if group:
                if degree and int(group.degree_id) != int(degree.id):
                    messages.error(request, 'Selected Group does not match the selected Degree.')
                    return render(request, 'admins/add_user.html', {
                        'branches': Branch.objects.all(),
                        'degrees': Degree.objects.all(),
                        'groups': Group.objects.all(),
                    })
                if branch and int(group.branch_id) != int(branch.id):
                    messages.error(request, 'Selected Group does not match the selected Branch.')
                    return render(request, 'admins/add_user.html', {
                        'branches': Branch.objects.all(),
                        'degrees': Degree.objects.all(),
                        'groups': Group.objects.all(),
                    })

            Student.objects.create(
                user=user,
                roll_number=roll_number,
                interests=interests,
                branch_id=branch_id or None,
                degree_id=degree_id or None,
                group_id=group_id or None,
            )
        elif role == 'teacher':
            employee_id = request.POST.get('employee_id')
            department = request.POST.get('department')
            Teacher.objects.create(
                user=user,
                employee_id=employee_id,
                department=department
            )
        
        messages.success(request, f'{role.title()} created successfully!')
        return redirect('admins:dashboard')
    
    context = {
        'branches': Branch.objects.all(),
        'degrees': Degree.objects.all(),
        'groups': Group.objects.all(),
    }
    return render(request, 'admins/add_user.html', context)


# User Management: list, edit, delete
@login_required
def users_list(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    students = Student.objects.select_related('user', 'branch', 'degree', 'group')
    teachers = Teacher.objects.select_related('user')
    return render(request, 'admins/users_list.html', {'students': students, 'teachers': teachers})


@login_required
@transaction.atomic
def user_edit(request, user_id):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    user = get_object_or_404(User, id=user_id)
    # Determine role
    is_student = hasattr(user, 'student')
    is_teacher = hasattr(user, 'teacher')
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        if is_student:
            s = user.student
            s.roll_number = request.POST.get('roll_number', s.roll_number)
            s.interests = request.POST.get('interests', s.interests)
            branch_id = request.POST.get('branch') or None
            degree_id = request.POST.get('degree') or None
            group_id = request.POST.get('group') or None

            # Validate consistency as above
            branch = Branch.objects.filter(id=branch_id).first() if branch_id else None
            degree = Degree.objects.filter(id=degree_id).first() if degree_id else None
            group = Group.objects.filter(id=group_id).first() if group_id else None
            if degree and branch and branch.degree_id and int(branch.degree_id) != int(degree.id):
                messages.error(request, 'Selected Branch does not belong to the selected Degree.')
                return render(request, 'admins/user_edit.html', {
                    'edit_user': user,
                    'branches': Branch.objects.all(),
                    'degrees': Degree.objects.all(),
                    'groups': Group.objects.all(),
                })
            if group:
                if degree and int(group.degree_id) != int(degree.id):
                    messages.error(request, 'Selected Group does not match the selected Degree.')
                    return render(request, 'admins/user_edit.html', {
                        'edit_user': user,
                        'branches': Branch.objects.all(),
                        'degrees': Degree.objects.all(),
                        'groups': Group.objects.all(),
                    })
                if branch and int(group.branch_id) != int(branch.id):
                    messages.error(request, 'Selected Group does not match the selected Branch.')
                    return render(request, 'admins/user_edit.html', {
                        'edit_user': user,
                        'branches': Branch.objects.all(),
                        'degrees': Degree.objects.all(),
                        'groups': Group.objects.all(),
                    })

            s.branch_id = branch_id
            s.degree_id = degree_id
            s.group_id = group_id
            s.save()
        elif is_teacher:
            t = user.teacher
            t.employee_id = request.POST.get('employee_id', t.employee_id)
            t.department = request.POST.get('department', t.department)
            t.save()
        messages.success(request, 'User updated successfully!')
        return redirect('admins:users_list')
    context = {
        'edit_user': user,
        'branches': Branch.objects.all(),
        'degrees': Degree.objects.all(),
        'groups': Group.objects.all(),
    }
    return render(request, 'admins/user_edit.html', context)


@login_required
@transaction.atomic
def user_delete(request, user_id):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('admins:users_list')
    return render(request, 'admins/user_delete_confirm.html', {'delete_user': user})


# Branch CRUD
@login_required
def branches_list(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    return render(request, 'admins/branches_list.html', {'branches': Branch.objects.select_related('degree')})


@login_required
def branch_create(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        degree_id = request.POST.get('degree')
        if name and degree_id:
            Branch.objects.create(name=name, degree_id=degree_id)
            messages.success(request, 'Branch created!')
            return redirect('admins:branches_list')
        messages.error(request, 'Please provide Branch name and Degree.')
    return render(request, 'admins/branch_form.html', {'degrees': Degree.objects.all()})


@login_required
def branch_edit(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name)
        obj.degree_id = request.POST.get('degree') or obj.degree_id
        obj.save()
        messages.success(request, 'Branch updated!')
        return redirect('admins:branches_list')
    return render(request, 'admins/branch_form.html', {'branch': obj, 'degrees': Degree.objects.all()})


@login_required
def branch_delete(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Branch deleted!')
        return redirect('admins:branches_list')
    return render(request, 'admins/confirm_delete.html', {'object': obj, 'type': 'Branch'})


# Degree CRUD
@login_required
def degrees_list(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    return render(request, 'admins/degrees_list.html', {'degrees': Degree.objects.all()})


@login_required
def degree_create(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Degree.objects.create(name=name)
            messages.success(request, 'Degree created!')
            return redirect('admins:degrees_list')
    return render(request, 'admins/degree_form.html')


@login_required
def degree_edit(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Degree, pk=pk)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name)
        obj.save()
        messages.success(request, 'Degree updated!')
        return redirect('admins:degrees_list')
    return render(request, 'admins/degree_form.html', {'degree': obj})


@login_required
def degree_delete(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Degree, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Degree deleted!')
        return redirect('admins:degrees_list')
    return render(request, 'admins/confirm_delete.html', {'object': obj, 'type': 'Degree'})


# Group CRUD
@login_required
def groups_list(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    groups = Group.objects.select_related('branch', 'degree')
    return render(request, 'admins/groups_list.html', {'groups': groups})


@login_required
def group_create(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        branch_id = request.POST.get('branch')
        degree_id = request.POST.get('degree')
        if name and branch_id and degree_id:
            Group.objects.create(name=name, branch_id=branch_id, degree_id=degree_id)
            messages.success(request, 'Group created!')
            return redirect('admins:groups_list')
    context = {'branches': Branch.objects.all(), 'degrees': Degree.objects.all()}
    return render(request, 'admins/group_form.html', context)


@login_required
def group_edit(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name)
        obj.branch_id = request.POST.get('branch') or obj.branch_id
        obj.degree_id = request.POST.get('degree') or obj.degree_id
        obj.save()
        messages.success(request, 'Group updated!')
        return redirect('admins:groups_list')
    context = {'group': obj, 'branches': Branch.objects.all(), 'degrees': Degree.objects.all()}
    return render(request, 'admins/group_form.html', context)


@login_required
def group_delete(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Group deleted!')
        return redirect('admins:groups_list')
    return render(request, 'admins/confirm_delete.html', {'object': obj, 'type': 'Group'})


# Subject CRUD (using teachers.Subject)
@login_required
def subjects_list(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    subjects = Subject.objects.select_related('teacher', 'teacher__user')
    return render(request, 'admins/subjects_list.html', {'subjects': subjects})


@login_required
def subject_create(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        teacher_id = request.POST.get('teacher') or None
        if name and code:
            Subject.objects.create(name=name, code=code, teacher_id=teacher_id)
            messages.success(request, 'Subject created!')
            return redirect('admins:subjects_list')
    context = {'teachers': Teacher.objects.select_related('user')}
    return render(request, 'admins/subject_form.html', context)


@login_required
def subject_edit(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name)
        obj.code = request.POST.get('code', obj.code)
        obj.teacher_id = request.POST.get('teacher') or None
        obj.save()
        messages.success(request, 'Subject updated!')
        return redirect('admins:subjects_list')
    context = {'subject': obj, 'teachers': Teacher.objects.select_related('user')}
    return render(request, 'admins/subject_form.html', context)


@login_required
def subject_delete(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Subject deleted!')
        return redirect('admins:subjects_list')
    return render(request, 'admins/confirm_delete.html', {'object': obj, 'type': 'Subject'})


# Group-Subject-Teacher assignments
@login_required
def assignments_list(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    assignments = GroupSubjectAssignment.objects.select_related('group', 'subject', 'teacher', 'teacher__user')
    return render(request, 'admins/assignments_list.html', {'assignments': assignments})


@login_required
def assignment_create(request):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        group_id = request.POST.get('group')
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher')
        # Validate consistency: subject.teacher must match chosen teacher
        subj = Subject.objects.filter(id=subject_id).first()
        if not subj:
            messages.error(request, 'Invalid subject.')
        elif str(subj.teacher_id) != str(teacher_id):
            messages.error(request, 'Selected subject is not taught by the chosen teacher.')
        else:
            GroupSubjectAssignment.objects.get_or_create(group_id=group_id, subject_id=subject_id, teacher_id=teacher_id)
            messages.success(request, 'Assignment created!')
            return redirect('admins:assignments_list')
    context = {
        'groups': Group.objects.select_related('branch', 'degree'),
        'subjects': Subject.objects.select_related('teacher', 'teacher__user'),
        'teachers': Teacher.objects.select_related('user'),
    }
    return render(request, 'admins/assignment_form.html', context)


@login_required
def assignment_delete(request, pk):
    if not _require_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    obj = get_object_or_404(GroupSubjectAssignment, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Assignment deleted!')
        return redirect('admins:assignments_list')
    return render(request, 'admins/confirm_delete.html', {'object': obj, 'type': 'Assignment'})