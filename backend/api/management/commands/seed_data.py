from django.core.management.base import BaseCommand
from api.models import Task, Objective, KeyResult, Trend, ReviewStep


class Command(BaseCommand):
    help = 'Siembra los datos iniciales del Centro de Mando'

    def handle(self, *args, **opts):
        if ReviewStep.objects.exists() or Objective.objects.exists():
            self.stdout.write(self.style.WARNING('Ya hay datos. Abortando para no duplicar.'))
            return

        # OKRs
        okrs = [
            ('Entregar plataforma Cloud Privado Internexa', 'Internexa', 'var(--moss)', [
                ('Documentación Veeam + AHV aprobada', 60),
                ('7 casos de uso (CU-01…CU-07) validados', 40),
                ('OpenLDAP en producción con Prism Central', 55),
            ]),
            ('Aprobar AWS SAA-C03', 'Certificación', 'var(--gold)', [
                ('Cubrir los 4 dominios del examen', 35),
                ('Simulacros consistentes ≥ 80%', 15),
            ]),
            ('Fortalecer el rol de Arquitecto de Portafolio', 'Rol', 'var(--plum)', [
                ('Rutina mensual de análisis de negocio activa', 20),
                ('Vigilancia tecnológica como hábito semanal', 30),
            ]),
        ]
        for i, (title, tag, color, krs) in enumerate(okrs):
            o = Objective.objects.create(title=title, tag=tag, color=color, order=i)
            for j, (kt, kp) in enumerate(krs):
                KeyResult.objects.create(objective=o, text=kt, progress=kp, order=j)

        # Tareas semilla
        seed_tasks = [
            ('next', 'Definir próxima acción de cada proyecto activo', ''),
            ('waiting', 'Validación documentación Veeam — equipo backup', 'esperando desde esta semana'),
            ('portfolio', 'Recuperar contexto: decisiones tomadas durante los 2 meses de ausencia', ''),
            ('portfolio', 'Inventario del portafolio actual de soluciones', ''),
            ('watch', 'Bloque semanal de vigilancia tecnológica (60–90 min)', ''),
        ]
        for lst, txt, meta in seed_tasks:
            Task.objects.create(list=lst, text=txt, meta=meta)

        # Tendencia inicial
        Trend.objects.create(
            text='¿Qué de esto impacta el portafolio de Internexa este mes?',
            source='Síntesis mensual')

        # Pasos de revisión semanal
        for i in range(6):
            ReviewStep.objects.create(index=i, done=False)

        self.stdout.write(self.style.SUCCESS('Datos iniciales sembrados correctamente.'))
