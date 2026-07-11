import csv
import io
import datetime
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from master.models import Project, Task, Member
from schedule.models import Schedule


class IndexView(TemplateView):
    template_name = 'importer/index.html'

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'ファイルを選択してください。')
            return redirect('importer:index')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'CSVファイルを選択してください。')
            return redirect('importer:index')

        decoded = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded))

        required_cols = {'type', 'ref', 'project_ref', 'task_ref', 'name'}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            messages.error(request, f'必須列が不足しています: {", ".join(sorted(missing))}')
            return redirect('importer:index')

        rows = list(reader)
        errors = []
        stats = {'project': 0, 'task': 0, 'schedule': 0}

        # ref → DB オブジェクトのマップ
        project_map = {}  # ref → Project
        task_map = {}     # ref → Task

        def get(row, col):
            return (row.get(col) or '').strip()

        # ── Pass 1: project 行 ──────────────────────────────────────────────
        for i, row in enumerate(rows, start=2):
            if get(row, 'type') != 'project':
                continue
            name = get(row, 'name')
            ref = get(row, 'ref')
            if not name:
                errors.append(f'{i}行目: name が空です。')
                continue

            delivery_raw = get(row, 'delivery_date')
            delivery = None
            if delivery_raw:
                try:
                    delivery = datetime.date.fromisoformat(delivery_raw)
                except ValueError:
                    errors.append(f'{i}行目: delivery_date の形式が不正です（YYYY-MM-DD）。')

            amount_raw = get(row, 'amount')
            amount = 0
            if amount_raw:
                try:
                    amount = int(amount_raw)
                except ValueError:
                    errors.append(f'{i}行目: amount は整数で入力してください。')

            project = Project.objects.create(
                name=name,
                delivery_date=delivery,
                amount=amount,
            )
            stats['project'] += 1
            if ref:
                project_map[ref] = project

        # ── Pass 2: task 行 ─────────────────────────────────────────────────
        for i, row in enumerate(rows, start=2):
            if get(row, 'type') != 'task':
                continue
            name = get(row, 'name')
            project_ref = get(row, 'project_ref')
            ref = get(row, 'ref')

            if not name:
                errors.append(f'{i}行目: name が空です。')
                continue

            project = project_map.get(project_ref)
            if project is None:
                errors.append(f'{i}行目: project_ref "{project_ref}" が見つかりません。')
                continue

            phase = get(row, 'phase') or 'other'
            valid_phases = [p for p, _ in Task.PHASE_CHOICES]
            if phase not in valid_phases:
                errors.append(f'{i}行目: phase "{phase}" は無効です。{valid_phases} から選んでください。')
                continue

            planned_raw = get(row, 'planned_hours')
            planned = 0
            if planned_raw:
                try:
                    planned = int(planned_raw)
                except ValueError:
                    errors.append(f'{i}行目: planned_hours は整数で入力してください。')

            task = Task.objects.create(
                project=project,
                name=name,
                phase=phase,
                planned_hours=planned,
            )
            stats['task'] += 1
            if ref:
                task_map[ref] = task

        # ── Pass 3: schedule 行 ─────────────────────────────────────────────
        for i, row in enumerate(rows, start=2):
            if get(row, 'type') != 'schedule':
                continue

            task_ref = get(row, 'task_ref')
            member_name = get(row, 'member')
            date_raw = get(row, 'date')
            hours_raw = get(row, 'hours')

            task = task_map.get(task_ref)
            if task is None:
                errors.append(f'{i}行目: task_ref "{task_ref}" が見つかりません。')
                continue

            if not member_name:
                errors.append(f'{i}行目: member が空です。')
                continue
            try:
                member = Member.objects.get(name=member_name)
            except Member.DoesNotExist:
                errors.append(f'{i}行目: メンバー "{member_name}" は登録されていません。')
                continue

            try:
                date = datetime.date.fromisoformat(date_raw)
            except (ValueError, TypeError):
                errors.append(f'{i}行目: date の形式が不正です（YYYY-MM-DD）。')
                continue

            try:
                hours = int(hours_raw)
                if hours < 1:
                    raise ValueError
            except (ValueError, TypeError):
                errors.append(f'{i}行目: hours は1以上の整数で入力してください。')
                continue

            start_slot_raw = get(row, 'start_slot')
            try:
                start_slot = max(0, min(7, int(start_slot_raw))) if start_slot_raw else 0
            except ValueError:
                start_slot = 0

            Schedule.objects.create(
                member=member,
                task=task,
                date=date,
                hours=hours,
                start_slot=start_slot,
            )
            stats['schedule'] += 1

        # ── 結果メッセージ ───────────────────────────────────────────────────
        for e in errors:
            messages.warning(request, e)

        messages.success(
            request,
            f'プロジェクト {stats["project"]}件・タスク {stats["task"]}件・'
            f'スケジュール {stats["schedule"]}件を登録しました。'
        )
        return redirect('importer:index')


def download_template(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="import_template.csv"'
    response.write('﻿')  # BOM for Excel
    writer = csv.writer(response)
    writer.writerow(['type', 'ref', 'project_ref', 'task_ref', 'name',
                     'phase', 'planned_hours', 'delivery_date', 'amount',
                     'member', 'date', 'hours', 'start_slot'])
    writer.writerow(['project', 'p1', '', '', 'サンプル案件',
                     '', '', '2026-12-31', '3000000', '', '', '', ''])
    writer.writerow(['task', 't1', 'p1', '', '要件定義',
                     'design', '16', '', '', '', '', '', ''])
    writer.writerow(['task', 't2', 'p1', '', 'API実装',
                     'develop', '24', '', '', '', '', '', ''])
    writer.writerow(['schedule', '', '', 't1', '',
                     '', '', '', '', '山田', '2026-07-07', '4', '0'])
    writer.writerow(['schedule', '', '', 't2', '',
                     '', '', '', '', '鈴木', '2026-07-08', '8', ''])
    return response
