import datetime
from django.views.generic import TemplateView
from django.db.models import Sum
from master.models import Project, Task
from schedule.models import Schedule
from actual.models import Actual

BASE_DATE = datetime.date(2026, 6, 21)
MONTHLY_RATE = 1_600_000
DISPLAY_MONTHS = 12


class IndexView(TemplateView):
    template_name = 'comparison/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # 実績原価の集計（全期間・メンバー単価×実績時間）
        actual_detail = (
            Actual.objects
            .values('task__project_id', 'member_id', 'member__unit_price')
            .annotate(hours_sum=Sum('hours'))
        )
        actual_cost_map = {}
        for row in actual_detail:
            pid = row['task__project_id']
            cost = row['hours_sum'] * row['member__unit_price']
            actual_cost_map[pid] = actual_cost_map.get(pid, 0) + cost

        rows = []
        for project in Project.objects.order_by('name'):
            s = Schedule.objects.filter(task__project=project).aggregate(t=Sum('hours'))['t'] or 0
            a = Actual.objects.filter(task__project=project).aggregate(t=Sum('hours'))['t'] or 0
            if s == 0 and a == 0:
                continue
            ratio = round(a / s * 100) if s > 0 else None
            actual_cost = actual_cost_map.get(project.pk, 0)
            gross = (project.amount - actual_cost) if project.amount else None
            rows.append({
                'project': project,
                'scheduled': s,
                'actual': a,
                'ratio': ratio,
                'amount': project.amount,
                'actual_cost': actual_cost,
                'gross': gross,
            })

        # 契約充足度
        total_amount = sum(r['amount'] for r in rows)
        months_covered = total_amount / MONTHLY_RATE if total_amount else 0
        days_covered = round(months_covered * 30)
        contract_end = BASE_DATE + datetime.timedelta(days=days_covered)

        timeline_months = []
        for i in range(DISPLAY_MONTHS):
            year = BASE_DATE.year + (BASE_DATE.month - 1 + i) // 12
            month = (BASE_DATE.month - 1 + i) % 12 + 1
            first_day = datetime.date(year, month, 1)
            if month < 12:
                last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
            else:
                last_day = datetime.date(year, 12, 31)
            covered = last_day <= contract_end
            partial = first_day <= contract_end < last_day
            if partial:
                fill_pct = round((contract_end - first_day).days / (last_day - first_day + datetime.timedelta(days=1)).days * 100)
            else:
                fill_pct = 100 if covered else 0
            timeline_months.append({
                'label': f'{month}月',
                'fill_pct': fill_pct,
            })

        ctx.update({
            'rows': rows,
            'total_amount': total_amount,
            'months_covered': round(months_covered, 2),
            'contract_end': contract_end,
            'base_date': BASE_DATE,
            'timeline_months': timeline_months,
        })
        return ctx
