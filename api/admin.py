from django.contrib import admin
from .models import Movie
# Register your models here.

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Admin interface for the Movie model.
    """
    list_display = ('id', 'title', 'description', 'release_date', 'rating')
    search_fields = ('title',)
    list_filter = ('release_date', 'rating')
    ordering = ('-release_date',)
    list_per_page = 10
    