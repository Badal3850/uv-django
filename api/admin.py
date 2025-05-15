from django.contrib import admin
from .models import *
admin.site.site_header = "My Project Admin"
admin.site.site_title = "My Project Admin Portal"
admin.site.index_title = "Welcome to My Project Admin"
# Register your models here.
admin.site.register([UserProfile,Tool,Category, Tag, UserToolInteraction, Review,ToolScreenshot])


