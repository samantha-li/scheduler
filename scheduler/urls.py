from django.conf.urls import include, url
from django.urls import path
from django.contrib.auth import views as auth_views

from django.contrib import admin
admin.autodiscover()

import scheduler_app.views

urlpatterns = [
    url(r'^$', scheduler_app.views.index, name='index'),
    path('accounts/', include('accounts.urls')), # new
    url(r'^select', scheduler_app.views.select, name='select'),
    url(r'^shift-selection', scheduler_app.views.select_shifts, name='shift-selection'),
    url(r'^change-availability', scheduler_app.views.change_availability, name='change-availability'),
    url(r'^set-shifts', scheduler_app.views.set_shifts, name='set-shifts'),
    url(r'^set-availability', scheduler_app.views.set_availability, name='set-availability'),
    url(r'^see-availability', scheduler_app.views.see_availability, name='see-availability'),
    url(r'^see-shifts', scheduler_app.views.see_shifts, name='see_shifts'),
    path('admin/', admin.site.urls),
    url(r"^account/", include("account.urls")),
    url(r'', scheduler_app.views.index, name='index'),
]
