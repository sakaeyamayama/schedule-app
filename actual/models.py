from django.db import models
from master.models import Member, Task


class Actual(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='メンバー')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='作業')
    date = models.DateField(verbose_name='日付')
    hours = models.PositiveSmallIntegerField(verbose_name='実績時間')

    class Meta:
        verbose_name = '実績'
        verbose_name_plural = '実績'
        unique_together = ('member', 'task', 'date')

    def __str__(self):
        return f'{self.date} {self.member} {self.task} {self.hours}h'
