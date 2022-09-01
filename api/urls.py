from rest_framework import routers

from .views import PseudoPyViewset

router = routers.SimpleRouter()
router.register("", PseudoPyViewset, basename="psuedopy")


urlpatterns = router.urls
