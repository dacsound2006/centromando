from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task, Objective, KeyResult, Trend, RhythmLog, ReviewStep
from .serializers import (
    TaskSerializer, ObjectiveSerializer, KeyResultSerializer,
    TrendSerializer, RhythmLogSerializer, ReviewStepSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        t = self.get_object()
        t.done = not t.done
        t.save()
        return Response(self.get_serializer(t).data)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        t = self.get_object()
        target = request.data.get('list')
        if target not in dict(Task.LISTS):
            return Response({'error': 'lista inválida'}, status=400)
        t.list = target
        if target == 'waiting' and not t.meta:
            from datetime import date
            t.meta = f'esperando desde {date.today().isoformat()}'
        t.save()
        return Response(self.get_serializer(t).data)


class ObjectiveViewSet(viewsets.ModelViewSet):
    queryset = Objective.objects.prefetch_related('krs').all()
    serializer_class = ObjectiveSerializer


class KeyResultViewSet(viewsets.ModelViewSet):
    queryset = KeyResult.objects.all()
    serializer_class = KeyResultSerializer

    @action(detail=True, methods=['post'])
    def progress(self, request, pk=None):
        kr = self.get_object()
        try:
            p = int(request.data.get('progress'))
        except (TypeError, ValueError):
            return Response({'error': 'progress inválido'}, status=400)
        kr.progress = max(0, min(100, p))
        kr.save()
        return Response(self.get_serializer(kr).data)


class TrendViewSet(viewsets.ModelViewSet):
    queryset = Trend.objects.all()
    serializer_class = TrendSerializer

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        t = self.get_object()
        t.done = not t.done
        t.save()
        return Response(self.get_serializer(t).data)


class RhythmLogViewSet(viewsets.ModelViewSet):
    queryset = RhythmLog.objects.all()
    serializer_class = RhythmLogSerializer

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Marca/desmarca un hábito en un día. Body: {rhythm, day}."""
        rhythm = request.data.get('rhythm')
        day = request.data.get('day')
        if not rhythm or not day:
            return Response({'error': 'rhythm y day requeridos'}, status=400)
        obj = RhythmLog.objects.filter(rhythm=rhythm, day=day).first()
        if obj:
            obj.delete()
            return Response({'rhythm': rhythm, 'day': day, 'on': False})
        RhythmLog.objects.create(rhythm=rhythm, day=day)
        return Response({'rhythm': rhythm, 'day': day, 'on': True})


class ReviewStepViewSet(viewsets.ModelViewSet):
    queryset = ReviewStep.objects.all()
    serializer_class = ReviewStepSerializer

    @action(detail=False, methods=['post'])
    def reset(self, request):
        ReviewStep.objects.update(done=False)
        return Response({'status': 'reset'})

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        s = self.get_object()
        s.done = not s.done
        s.save()
        return Response(self.get_serializer(s).data)
