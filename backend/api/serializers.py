from rest_framework import serializers
from .models import Task, Objective, KeyResult, Trend, RhythmLog, ReviewStep


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'text', 'list', 'meta', 'done', 'created_at', 'updated_at']


class KeyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyResult
        fields = ['id', 'objective', 'text', 'progress', 'order']


class ObjectiveSerializer(serializers.ModelSerializer):
    krs = KeyResultSerializer(many=True, read_only=True)

    class Meta:
        model = Objective
        fields = ['id', 'title', 'tag', 'color', 'order', 'krs']


class TrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trend
        fields = ['id', 'text', 'source', 'done', 'created_at']


class RhythmLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RhythmLog
        fields = ['id', 'rhythm', 'day']


class ReviewStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewStep
        fields = ['id', 'index', 'done']
