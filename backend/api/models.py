from django.db import models


class Task(models.Model):
    """Tareas GTD. La 'lista' define en qué bandeja vive."""
    LISTS = [
        ('inbox', 'Inbox'),
        ('next', 'Próximas acciones'),
        ('waiting', 'En espera de'),
        ('meetings', 'Compromisos de reunión'),
        ('portfolio', 'Rol · Portafolio'),
        ('watch', 'Vigilancia / Algún día'),
    ]
    text = models.CharField(max_length=500)
    list = models.CharField(max_length=20, choices=LISTS, default='inbox')
    meta = models.CharField(max_length=200, blank=True, default='')
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['done', '-created_at']


class Objective(models.Model):
    """Objetivo trimestral (OKR)."""
    title = models.CharField(max_length=300)
    tag = models.CharField(max_length=60, default='')
    color = models.CharField(max_length=40, default='var(--moss)')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class KeyResult(models.Model):
    objective = models.ForeignKey(Objective, related_name='krs', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    progress = models.IntegerField(default=0)  # 0-100
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class Trend(models.Model):
    """Vigilancia tecnológica: hallazgos capturados."""
    text = models.CharField(max_length=500)
    source = models.CharField(max_length=200, blank=True, default='')
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['done', '-created_at']


class RhythmLog(models.Model):
    """Registro diario de hábitos de equilibrio. Un registro por (rhythm, day)."""
    rhythm = models.CharField(max_length=40)  # familia, gym, medita, lectura, mente, ingles
    day = models.DateField()

    class Meta:
        unique_together = ('rhythm', 'day')
        ordering = ['-day']


class ReviewStep(models.Model):
    """Pasos de la revisión semanal (estado persistente)."""
    index = models.IntegerField(unique=True)
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ['index']
