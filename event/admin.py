from django.contrib import admin
from .models import Category, Event, PossibleResult

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

class PossibleResultInline(admin.TabularInline):
    model = PossibleResult
    extra = 1

class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_name', 'avatar', 'market', 'category', 'start_date', 'end_date', 'resolution_date']
    search_fields = ['event_name']
    inlines = [PossibleResultInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['category']
        return []

admin.site.register(Category, CategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(PossibleResult)
