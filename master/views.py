from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Member, Project, Task


class IndexView(TemplateView):
    template_name = 'master/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['members'] = Member.objects.all()
        ctx['projects'] = Project.objects.all()
        ctx['tasks'] = Task.objects.select_related('project').order_by('project__name', 'name')
        return ctx


class MemberCreateView(CreateView):
    model = Member
    fields = ['name', 'unit_price']
    template_name = 'master/member_form.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, 'メンバーを登録しました。')
        return super().form_valid(form)


class MemberUpdateView(UpdateView):
    model = Member
    fields = ['name', 'unit_price']
    template_name = 'master/member_form.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, 'メンバーを更新しました。')
        return super().form_valid(form)


class MemberDeleteView(DeleteView):
    model = Member
    template_name = 'master/confirm_delete.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, 'メンバーを削除しました。')
        return super().form_valid(form)


class ProjectCreateView(CreateView):
    model = Project
    fields = ['name', 'color', 'delivery_date', 'amount']
    template_name = 'master/project_form.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, 'プロジェクトを登録しました。')
        return super().form_valid(form)


class ProjectUpdateView(UpdateView):
    model = Project
    fields = ['name', 'color', 'delivery_date', 'amount']
    template_name = 'master/project_form.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, 'プロジェクトを更新しました。')
        return super().form_valid(form)


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'master/confirm_delete.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, 'プロジェクトを削除しました。')
        return super().form_valid(form)


class TaskCreateView(CreateView):
    model = Task
    fields = ['project', 'name', 'planned_hours', 'phase']
    template_name = 'master/task_form.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, '作業を登録しました。')
        return super().form_valid(form)


class TaskUpdateView(UpdateView):
    model = Task
    fields = ['project', 'name', 'planned_hours', 'phase']
    template_name = 'master/task_form.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, '作業を更新しました。')
        return super().form_valid(form)


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'master/confirm_delete.html'
    success_url = reverse_lazy('master:index')

    def form_valid(self, form):
        messages.success(self.request, '作業を削除しました。')
        return super().form_valid(form)
