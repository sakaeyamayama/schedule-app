import datetime
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum
from master.models import Member, Task, Project
from .models import Schedule
from actual.models import Actual


class IndexView(TemplateView):
    template_name = 'schedule/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mode = self.request.GET.get('mode', 'week')
        today = datetime.date.today()

        try:
            base = datetime.date.fromisoformat(self.request.GET.get('date', str(today)))
        except ValueError:
            base = today

        if mode == 'day':
            start, end = base, base
            prev_date = base - datetime.timedelta(days=1)
            next_date = base + datetime.timedelta(days=1)
        elif mode == 'month':
            start = base.replace(day=1)
            # 月末
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1, day=1) - datetime.timedelta(days=1)
            else:
                end = start.replace(month=start.month + 1, day=1) - datetime.timedelta(days=1)
            prev_date = (start - datetime.timedelta(days=1)).replace(day=1)
            next_date = end + datetime.timedelta(days=1)
        else:  # week
            start = base - datetime.timedelta(days=base.weekday())
            end = start + datetime.timedelta(days=6)
            prev_date = start - datetime.timedelta(weeks=1)
            next_date = start + datetime.timedelta(weeks=1)

        schedules = (
            Schedule.objects
            .filter(date__range=(start, end))
            .select_related('member', 'task__project')
            .order_by('date', 'member__name', 'task__name')
        )

        all_days = [start + datetime.timedelta(days=i) for i in range((end - start).days + 1)]
        # 週・月表示では土日を除外
        days = [d for d in all_days if mode == 'day' or d.weekday() < 5]
        members = Member.objects.all()

        cell_map = {}
        day_totals = {}
        for s in schedules:
            cell_map.setdefault(s.member_id, {}).setdefault(s.date, []).append(s)
            day_totals[s.date] = day_totals.get(s.date, 0) + s.hours

        actuals_qs = (
            Actual.objects
            .filter(date__range=(start, end), date__lt=today)
            .select_related('member', 'task__project')
            .order_by('date', 'task__name')
        )
        actual_map = {}
        for a in actuals_qs:
            actual_map.setdefault(a.member_id, {}).setdefault(a.date, []).append(a)

        rows = []
        for m in members:
            cells = []
            for d in days:
                is_past = d < today
                if is_past:
                    day_actuals = actual_map.get(m.pk, {}).get(d, [])
                    day_schedules = cell_map.get(m.pk, {}).get(d, [])
                    total = sum(a.hours for a in day_actuals)
                    cells.append({
                        'day': d,
                        'is_today': False,
                        'is_past': True,
                        'schedules': day_schedules,
                        'actuals': day_actuals,
                        'total_hours': total,
                        'over_capacity': total > 8,
                    })
                else:
                    day_schedules = cell_map.get(m.pk, {}).get(d, [])
                    total = sum(sc.hours for sc in day_schedules)
                    cells.append({
                        'day': d,
                        'is_today': d == today,
                        'is_past': False,
                        'schedules': day_schedules,
                        'actuals': [],
                        'total_hours': total,
                        'over_capacity': total > 8,
                    })
            rows.append({'member': m, 'cells': cells})

        slot_px = {'day': 48, 'week': 24, 'month': 14}.get(mode, 24)
        days_with_totals = [(d, day_totals.get(d, 0)) for d in days]

        # 表示期間内で使われているプロジェクトを重複なく収集（凡例用）
        seen_proj_ids = set()
        legend_projects = []
        for s in schedules:
            p = s.task.project
            if p.pk not in seen_proj_ids:
                seen_proj_ids.add(p.pk)
                legend_projects.append(p)
        legend_projects.sort(key=lambda p: p.name)

        # 予定工数が設定されているタスクの割当状況（全期間集計）、フェーズ順にグループ化
        PHASE_ORDER = ['design', 'develop', 'review', 'test', 'other']
        task_scheduled_map = {
            r['task_id']: r['total']
            for r in Schedule.objects.values('task_id').annotate(total=Sum('hours'))
        }
        task_actual_map = {
            r['task_id']: r['total']
            for r in Actual.objects.values('task_id').annotate(total=Sum('hours'))
        }
        phase_labels = dict(Task.PHASE_CHOICES)
        project_map = {}  # project_id -> {project, phases: {phase -> [items]}}
        for task in Task.objects.select_related('project').filter(planned_hours__gt=0).order_by('project__name', 'name'):
            scheduled = task_scheduled_map.get(task.pk, 0)
            actual = task_actual_map.get(task.pk, 0)
            pct = min(100, round(scheduled / task.planned_hours * 100))
            actual_pct = min(100, round(actual / task.planned_hours * 100))
            item = {
                'task': task,
                'scheduled': scheduled,
                'actual': actual,
                'remaining': max(0, task.planned_hours - scheduled),
                'pct': pct,
                'actual_pct': actual_pct,
            }
            proj_id = task.project_id
            if proj_id not in project_map:
                project_map[proj_id] = {'project': task.project, 'phases': {}}
            project_map[proj_id]['phases'].setdefault(task.phase, []).append(item)

        task_progress_by_project = []
        for proj_data in project_map.values():
            phase_groups = [
                {'phase': p, 'label': phase_labels.get(p, p), 'items': proj_data['phases'][p]}
                for p in PHASE_ORDER if p in proj_data['phases']
            ]
            task_progress_by_project.append({
                'project': proj_data['project'],
                'phases': phase_groups,
            })

        ctx.update({
            'mode': mode,
            'base': base,
            'start': start,
            'end': end,
            'days': days,
            'days_with_totals': days_with_totals,
            'rows': rows,
            'prev_date': prev_date,
            'next_date': next_date,
            'today': today,
            'slot_px': slot_px,
            'legend_projects': legend_projects,
            'task_progress_by_project': task_progress_by_project,
        })
        return ctx


class ScheduleCreateView(CreateView):
    model = Schedule
    fields = ['member', 'task', 'date', 'hours']
    template_name = 'schedule/form.html'
    success_url = reverse_lazy('schedule:index')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tasks'] = Task.objects.select_related('project').order_by('project__name', 'name')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, '予定を登録しました。')
        return super().form_valid(form)


class ScheduleUpdateView(UpdateView):
    model = Schedule
    fields = ['member', 'task', 'date', 'hours']
    template_name = 'schedule/form.html'
    success_url = reverse_lazy('schedule:index')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tasks'] = Task.objects.select_related('project').order_by('project__name', 'name')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, '予定を更新しました。')
        return super().form_valid(form)


class ScheduleDeleteView(DeleteView):
    model = Schedule
    template_name = 'schedule/confirm_delete.html'
    success_url = reverse_lazy('schedule:index')

    def form_valid(self, form):
        messages.success(self.request, '予定を削除しました。')
        return super().form_valid(form)


class HoursUpdateView(View):
    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        try:
            hours = int(request.POST.get('hours', schedule.hours))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'invalid'}, status=400)
        hours = max(1, min(24, hours))
        schedule.hours = hours
        schedule.save()
        return JsonResponse({'pk': pk, 'hours': hours})


class ScheduleResizeView(View):
    """
    合計工数を受け取り、同メンバー・同タスクの開始日以降に8h/日で自動分割する。
    開始日以降の既存エントリは一旦削除してから再生成。
    """
    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        try:
            total_hours = int(request.POST.get('total_hours'))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'invalid'}, status=400)
        total_hours = max(1, min(total_hours, 8 * 30))

        member_id = schedule.member_id
        task_id   = schedule.task_id
        start_date = schedule.date

        # 開始日より後の同タスク・同メンバーエントリを削除
        Schedule.objects.filter(
            member_id=member_id, task_id=task_id, date__gt=start_date
        ).delete()

        remaining = total_hours
        current   = start_date
        first     = True
        while remaining > 0:
            day_hours = min(remaining, 8)
            if first:
                schedule.hours = day_hours
                schedule.save()
                first = False
            else:
                Schedule.objects.update_or_create(
                    member_id=member_id, task_id=task_id, date=current,
                    defaults={'hours': day_hours},
                )
            remaining -= day_hours
            current   += datetime.timedelta(days=1)

        return JsonResponse({'pk': pk, 'total_hours': total_hours})


class ScheduleQuickCreateView(View):
    def post(self, request):
        try:
            task_id = int(request.POST.get('task_id'))
            date = datetime.date.fromisoformat(request.POST.get('date'))
            member_id = int(request.POST.get('member_id'))
            start_slot = int(request.POST.get('start_slot', 0))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'invalid'}, status=400)
        start_slot = max(0, min(7, start_slot))
        schedule = Schedule.objects.create(
            task_id=task_id,
            date=date,
            member_id=member_id,
            hours=1,
            start_slot=start_slot,
        )
        return JsonResponse({'pk': schedule.pk})


class ScheduleMoveView(View):
    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        try:
            date_str = request.POST.get('date')
            member_id = request.POST.get('member_id')
            start_slot = request.POST.get('start_slot')
            if date_str:
                schedule.date = datetime.date.fromisoformat(date_str)
            if member_id:
                schedule.member_id = int(member_id)
            if start_slot is not None:
                schedule.start_slot = max(0, min(7, int(start_slot)))
            schedule.save()
        except (ValueError, TypeError):
            return JsonResponse({'error': 'invalid'}, status=400)
        return JsonResponse({'pk': pk, 'date': str(schedule.date), 'member_id': schedule.member_id})
