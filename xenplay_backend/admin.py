from django.contrib import admin
from .models import Event, PossibleResult

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'start_date', 'end_date', 'real_result')
    search_fields = ('event_name',)
    list_filter = ('real_result',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        
        # Filter real_result field to show only PossibleResults related to the current Event
        if db_field.name == 'real_result':
            if request._obj_ is not None:
                possible_results = PossibleResult.objects.filter(event=request._obj_)
                formfield.queryset = possible_results
            else:
                formfield.queryset = PossibleResult.objects.none()

        return formfield

admin.site.register(Event, EventAdmin)
admin.site.register(PossibleResult)