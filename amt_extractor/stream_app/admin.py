from django.contrib import admin
from stream_app.models import Stream, Song
# Register your models here.

admin.site.register([Stream, Song])