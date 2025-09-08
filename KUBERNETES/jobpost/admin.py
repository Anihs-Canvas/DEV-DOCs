from django.contrib import admin
from .models import Skills, Author, Location, JobPost

# Register your models here.

@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'designation']
    list_filter = ['company', 'designation']
    search_fields = ['user__username', 'company', 'designation']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['city', 'state', 'country', 'zip']
    list_filter = ['country', 'state']
    search_fields = ['city', 'state', 'country']

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'location', 'salary', 'type', 'date', 'expiry']
    list_filter = ['type', 'date', 'expiry', 'author__company']
    search_fields = ['title', 'description', 'author__company']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['skills']
    date_hierarchy = 'date'
