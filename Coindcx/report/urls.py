from django.urls import path
from . import views

urlpatterns = [
    path('',views.about),
    path('customrpt/',views.generate_rpt,name = 'customrpt')

    
]
