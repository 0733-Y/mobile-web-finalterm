from django.contrib import admin

from .models import Post, Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'floor', 'capacity', 'has_outlet')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'space', 'person_count', 'level', 'published_date')
    list_filter = ('space', 'level')
