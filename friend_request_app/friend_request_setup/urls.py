"""
URL configuration for accuknox_assesment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from accuknox_assesment import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from user_account.authentication import CustomRefreshTokenPairView, CustomTokenObtainPairView
from user_account.views import FriendRequestViewSet, SignupViewSet, UserViewSet


schema_view = get_schema_view(
   openapi.Info(
      title="PEXMiner API",
      default_version='v1',
      description="PEXMiner API description",
      contact=openapi.Contact(email="raghu.annudurai@iopex.com,sudipta.rajak@iopex.com"),
   ),
   url=settings.API_URL+"/swagger/",
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('admin/', admin.site.urls),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomRefreshTokenPairView.as_view(), name='token_refresh'),


    path('user/list', UserViewSet.as_view({'post': 'list'})),
    path('user/create', SignupViewSet.as_view({'post': 'signup'})),



    path('friendrequest/send', FriendRequestViewSet.as_view({'post': 'send'})),
    path('friendrequest/accept', FriendRequestViewSet.as_view({'post': 'accept'})),
    path('friendrequest/reject', FriendRequestViewSet.as_view({'post': 'reject'})),
    path('friendrequest/list', FriendRequestViewSet.as_view({'post': 'friendList'})),
    path('friendrequest/pendinglist', FriendRequestViewSet.as_view({'post': 'pendingFriendList'})),


]
