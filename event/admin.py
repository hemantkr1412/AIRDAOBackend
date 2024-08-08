from django import forms
from django.contrib.admin.widgets import AdminTimeWidget
from django.contrib import admin
from .models import Category, Event, PossibleResult


class EventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%d %H:%M", attrs={"type": "datetime-local"}
        )
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%d %H:%M", attrs={"type": "datetime-local"}
        )
    )
    resolution_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%d %H:%M", attrs={"type": "datetime-local"}
        )
    )

    class Meta:
        model = Event
        fields = "__all__"


# Update the EventAdmin to use the new EventForm
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


class PossibleResultInline(admin.TabularInline):
    model = PossibleResult
    extra = 1


class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = [
        "id",
        "event_name",
        "avatar",
        "market",
        "category",
        "start_date",
        "end_date",
        "resolution_date",
        "token_volume",
        "min_token_stake",
    ]
    search_fields = ["event_name"]
    inlines = [PossibleResultInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["category"]
        return []


admin.site.register(Category, CategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(PossibleResult)
