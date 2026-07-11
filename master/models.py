from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100, verbose_name='メンバー名')
    unit_price = models.PositiveIntegerField(default=0, verbose_name='単価（円/時）')

    class Meta:
        verbose_name = 'メンバー'
        verbose_name_plural = 'メンバー'

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name='プロジェクト名')
    color = models.CharField(max_length=7, default='#4a90d9', verbose_name='表示色')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='納品日')
    amount = models.PositiveIntegerField(default=0, verbose_name='金額（円）')

    class Meta:
        verbose_name = 'プロジェクト'
        verbose_name_plural = 'プロジェクト'

    def __str__(self):
        return self.name


class Task(models.Model):
    PHASE_CHOICES = [
        ('design',  '設計'),
        ('develop', '製造'),
        ('review',  'レビュー'),
        ('test',    'テスト'),
        ('other',   'その他'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='プロジェクト')
    name = models.CharField(max_length=200, verbose_name='作業名')
    planned_hours = models.PositiveIntegerField(default=0, verbose_name='予定工数（時間）')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='other', verbose_name='フェーズ')
    progress = models.PositiveSmallIntegerField(default=0, verbose_name='進捗（%）')

    class Meta:
        verbose_name = '作業'
        verbose_name_plural = '作業'

    def __str__(self):
        return f'{self.project.name} / {self.name}'
