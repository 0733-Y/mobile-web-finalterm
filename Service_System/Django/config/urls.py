from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from blog import views

router = routers.DefaultRouter()
router.register(r'Post', views.BlogImages)
router.register(r'Space', views.SpaceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api_root/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token),
    path('', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
