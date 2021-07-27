from django.urls import path
from . import views

urlpatterns = [
    path('',views.about,name = 'about'),
    path('customrpt/',views.generate_rpt,name = 'customrpt'),
    path('samplerpt/',views.sample_rpt,name = 'samplerpt')
]
