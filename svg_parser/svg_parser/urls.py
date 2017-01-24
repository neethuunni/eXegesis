"""svg_parser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from parse_svg import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^$', views.login),
    # url(r'^home/$', views.home),
    url(r'^logout/$', views.logout),
    url(r'^svg/', views.index),
    url(r'^svg_images/', views.svg_images),
    url(r'^projects/', views.projects),
    url(r'^create_project/', views.create_project),
    url(r'^artboards/', views.artboards),
    url(r'^share_project/', views.share_project),
    url(r'^verify_share/', views.verify_share),
    url(r'^delete_artboard/', views.delete_artboard),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
