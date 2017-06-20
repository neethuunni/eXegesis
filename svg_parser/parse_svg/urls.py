from django.conf.urls import url, include
from parse_svg import views

urlpatterns = [
    url(r'^$', views.login),
    url('^', include('social.apps.django_app.urls', namespace='social')),
    url(r'^logout/$', views.logout),
    url(r'^svg/', views.index),
    url(r'^svg_images/', views.svg_images),
    url(r'^projects/', views.projects),
    url(r'^create_project/', views.create_project),
    url(r'^artboards/', views.artboards),
    url(r'^share_project/', views.share_project),
    url(r'^delete_artboard/', views.delete_artboard),
    url(r'^rename_artboard/', views.rename_artboard),
    url(r'^delete_project/', views.delete_project),
    url(r'^download_artboard/', views.download_artboard),
    url(r'^revisions/', views.revisions),
    url(r'^write_note/', views.write_note),
    url(r'^update_artboard/', views.update_artboard),
]
