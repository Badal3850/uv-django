from django.urls import path
from .views import *

urlpatterns = [
    path('jobs/',get_active_jobs, name='get-active-jobs'),
    path('stocks/news/',get_stock_news, name='get-stock-jobs'),
]