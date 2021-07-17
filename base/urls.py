from django.urls import path
from . import views
from django.contrib import admin

admin.site.site_header = "Project Portfolio"
admin.site.site_title = "Portfolio Admin Portal"
admin.site.index_title = "Welcome to the Portel"

urlpatterns = [
    path('',views.home, name='home'),
    path('about', views.about, name='about'),
    path('sentiment', views.sentiment, name='sentiment'),
    path('electricitylr', views.electricitylr, name='electricitylr'),
    path('electricity', views.electricity, name='electricity'),
    path('electricity', views.electricity, name='electricity'),
    path('stock',views.stock,name='stock'),
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
    path('forgot',views.forgot,name='forgot'),
    path('get_data',views.get_data,name='get_data'),
    path('charts',views.charts,name='charts'),
    path('AutoUpdate',views.AutoUpdate,name='AutoUpdate'),
    path('PidOpener',views.PidOpener,name='PidOpener'),
    path('PidCloser',views.PidCloser,name='PidCloser'),
    path('powerUpdaterLr',views.powerUpdaterLr,name='powerUpdaterLr'),
    path('powerUpdater',views.powerUpdater,name='powerUpdater'),
    path('powerUpdaterV2',views.powerUpdaterV2,name='powerUpdaterV2')
]
