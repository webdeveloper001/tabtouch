from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^testws/$', views.index, name='index')
]