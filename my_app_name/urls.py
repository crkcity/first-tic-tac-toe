from django.conf.urls import url

from . import views

urlpatterns = [

url(r’^$’, views.first_view, name=first_view),

]
