from django.conf.urls import url
from django.contrib import admin


from app.views import *

urlpatterns = [
	url(r'^$', index.as_view(), name="index"),
	url(r'^b_day$', b_day, name="b_day"),
    url(r'^admin/', admin.site.urls),

]
