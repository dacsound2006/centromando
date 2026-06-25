from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, ObjectiveViewSet, KeyResultViewSet,
    TrendViewSet, RhythmLogViewSet, ReviewStepViewSet,
)

router = DefaultRouter()
router.register('tasks', TaskViewSet)
router.register('objectives', ObjectiveViewSet)
router.register('keyresults', KeyResultViewSet)
router.register('trends', TrendViewSet)
router.register('rhythms', RhythmLogViewSet)
router.register('review', ReviewStepViewSet)

urlpatterns = router.urls
