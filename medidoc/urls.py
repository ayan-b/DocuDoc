"""medidoc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls.conf import include
from ckeditor_uploader import views as ckeditor_views

from medidoc import settings

urlpatterns = [
    path('', include('cases.urls')),
    path('admin/', admin.site.urls),
    url(r'^ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', login_required(ckeditor_views.browse), name='ckeditor_browse'),
]

if not settings.IS_PROD:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
