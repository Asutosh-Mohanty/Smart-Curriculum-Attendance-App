from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .services import get_suggestions_for_student, generate_random_tasks
from .models import Suggestion, CompletedTask

# Create your views here.

@login_required
@require_GET
def free_period_suggestions(request):
    # adapt: student relation on user
    student = getattr(request.user, "student", None)
    if student is None:
        return JsonResponse({"error": "Not a student"}, status=403)

    # rate-limit per user (15s)
    rl_key = f"ai_rl:{request.user.id}"
    if not request.GET.get("force") and cache.get(rl_key):
        return JsonResponse({"error": "Rate limited"}, status=429)
    cache.set(rl_key, 1, 15)

    force = request.GET.get("force") == "1"
    suggestions = get_suggestions_for_student(student, force_refresh=force)

    # store for audit (optional) — don't store raw keys or sensitive info
    try:
        suggestion_obj = Suggestion.objects.create(student=student, payload=suggestions, source="openai")
        # Add suggestion ID to each suggestion for tracking
        for suggestion in suggestions:
            suggestion['suggestion_id'] = suggestion_obj.id
    except Exception:
        # fail silently for storage errors
        pass

    return JsonResponse({"suggestions": suggestions})


@login_required
@require_GET
def generate_random_suggestions(request):
    """Generate random tasks for the student"""
    student = getattr(request.user, "student", None)
    if student is None:
        return JsonResponse({"error": "Not a student"}, status=403)

    # Generate random tasks
    random_suggestions = generate_random_tasks(3)
    
    # Store the random suggestions
    try:
        suggestion_obj = Suggestion.objects.create(student=student, payload=random_suggestions, source="random")
        for suggestion in random_suggestions:
            suggestion['suggestion_id'] = suggestion_obj.id
    except Exception:
        pass

    return JsonResponse({"suggestions": random_suggestions})


@login_required
@require_POST
@csrf_exempt
def mark_task_completed(request):
    """Mark a task as completed and remove it from current suggestions"""
    student = getattr(request.user, "student", None)
    if student is None:
        return JsonResponse({"error": "Not a student"}, status=403)

    try:
        data = json.loads(request.body)
        task_title = data.get('task_title')
        task_reason = data.get('task_reason', '')
        time_minutes = data.get('time_minutes', 10)
        suggestion_id = data.get('suggestion_id')

        if not task_title:
            return JsonResponse({"error": "Task title is required"}, status=400)

        # Create completed task record
        suggestion_obj = None
        if suggestion_id:
            try:
                suggestion_obj = Suggestion.objects.get(id=suggestion_id)
            except Suggestion.DoesNotExist:
                pass

        CompletedTask.objects.create(
            student=student,
            task_title=task_title,
            task_reason=task_reason,
            time_minutes=time_minutes,
            suggestion_id=suggestion_obj
        )

        return JsonResponse({
            "success": True,
            "message": "Task marked as completed!",
            "completed_task": {
                "title": task_title,
                "time_minutes": time_minutes
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def get_completed_tasks(request):
    """Get completed tasks for the student"""
    student = getattr(request.user, "student", None)
    if student is None:
        return JsonResponse({"error": "Not a student"}, status=403)

    completed_tasks = CompletedTask.objects.filter(student=student)[:10]  # Last 10 tasks
    
    tasks_data = []
    for task in completed_tasks:
        tasks_data.append({
            'id': task.id,
            'task_title': task.task_title,
            'task_reason': task.task_reason,
            'time_minutes': task.time_minutes,
            'completed_at': task.completed_at.strftime('%Y-%m-%d %H:%M')
        })

    return JsonResponse({"completed_tasks": tasks_data})
