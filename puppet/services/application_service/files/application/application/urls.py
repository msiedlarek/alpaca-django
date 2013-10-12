from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'application.views.home', name='home'),
)
