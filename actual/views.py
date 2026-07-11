import datetime
import json
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from master.models import Member, Task, Project
from schedule.models import Schedule
from .models import Actual


class IndexView(TemplateView):
    template_name = 'actual/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = datetime.date.today()

        try:
            date = datetime.date.fromisoformat(self.request.GET.get('date', str(today)))
        except ValueError:
            date = today

        members = Member.objects.all()
        try:
            member_id = int(self.request.GET.get('member_id', 0))
            member = members.get(pk=member_id)
        except (ValueError, TypeError, Member.DoesNotExist):
            member = members.first()

        actuals = []
        schedules = []
        total_hours = 0
        total_planned = 0
        avg_progress = 0

        if member:
            actuals = list(
                Actual.objects.filter(date=date, member=member)
                .select_related('task__project')
                .order_by('task__project__name', 'task__name')
            )
            schedules = list(
                Schedule.objects.filter(date=date, member=member)
                .select_related('task__project')
                .order_by('task__project__name', 'task__name')
            )
            total_hours = sum(a.hours for a in actuals)
            total_planned = sum(s.hours for s in schedules)
            avg_progress = round(sum(a.task.progress for a in actuals) / len(actuals)) if actuals else 0

        # タスクデータをJS用に構築（プロジェクト→フェーズ→タスク）
        all_tasks = list(
            Task.objects.select_related('project').order_by('project__name', 'name')
        )
        task_data = [
            {
                'id': t.pk,
                'name': t.name,
                'project_id': t.project_id,
                'project_name': t.project.name,
                'phase': t.phase,
                'phase_label': dict(Task.PHASE_CHOICES).get(t.phase, t.phase),
                'progress': t.progress,
            }
            for t in all_tasks
        ]
        projects = list(Project.objects.order_by('name').values('id', 'name'))

        # 既存の実績タスクIDセット（重複登録防止用）
        actual_task_ids = {a.task_id for a in actuals}

        ctx.update({
            'date': date,
            'today': today,
            'members': members,
            'member': member,
            'actuals': actuals,
            'schedules': schedules,
            'total_hours': total_hours,
            'total_planned': total_planned,
            'avg_progress': avg_progress,
            'task_count': len(actuals),
            'task_data_json': json.dumps(task_data, ensure_ascii=False),
            'projects': projects,
            'phase_choices': Task.PHASE_CHOICES,
            'actual_task_ids_json': json.dumps(list(actual_task_ids)),
        })
        return ctx


class ActualSaveView(View):
    """実績の登録・更新（AJAX）"""
    def post(self, request):
        try:
            task_id = int(request.POST.get('task_id'))
            date = datetime.date.fromisoformat(request.POST.get('date'))
            member_id = int(request.POST.get('member_id'))
            hours = int(request.POST.get('hours', 1))
            progress = int(request.POST.get('progress', 0))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'invalid'}, status=400)

        hours = max(1, min(24, hours))
        progress = max(0, min(100, progress))

        actual, _ = Actual.objects.update_or_create(
            member_id=member_id,
            task_id=task_id,
            date=date,
            defaults={'hours': hours},
        )
        # タスクの進捗を更新
        Task.objects.filter(pk=task_id).update(progress=progress)

        return JsonResponse({
            'pk': actual.pk,
            'hours': actual.hours,
            'progress': progress,
        })


class ActualDeleteView(View):
    """実績削除（AJAX）"""
    def post(self, request, pk):
        actual = get_object_or_404(Actual, pk=pk)
        actual.delete()
        return JsonResponse({'ok': True})
