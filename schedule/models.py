from django.db import models
from master.models import Member, Task


class Schedule(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='メンバー')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='作業')
    date = models.DateField(verbose_name='日付')
    hours = models.PositiveSmallIntegerField(verbose_name='予定時間')
    start_slot = models.PositiveSmallIntegerField(default=0, verbose_name='開始コマ目')

    class Meta:
        verbose_name = '予定'
        verbose_name_plural = '予定'

    def __str__(self):
        return f'{self.date} {self.member} {self.task} {self.hours}h'
