from django.conf.urls import url
from django.contrib import admin


from app.views import *

urlpatterns = [
	url(r'^$', index.as_view(), name="index"),
	url(r'^b_day$', b_day, name="b_day"),
	url(r'^time_in$', time_in, name="time_in"),
	url(r'^was_born$', was_born, name="was_born"),
	url(r'^calories_on$', calories_on, name="calories_on"),
	url(r'^weather$', weather, name="weather"),
	url(r'^report$', report, name="report"),
	url(r'^about$', about, name="about"),
    url(r'^admin/', admin.site.urls),
]
