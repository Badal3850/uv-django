from django.urls import path
from .views import *

urlpatterns = [
    path('movies/<pk>/',movie_list, name='movie-list'),
    path('load/',load_movies, name='load-movies'),
    path('jobs/',get_active_jobs, name='get-active-jobs'),
    path('stocks/news/',get_stock_news, name='get-stock-jobs'),
]