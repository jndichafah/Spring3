from django.contrib import admin
from .models import Listing, Realtor, Genre, ListingInstance

# Register your models here.
admin.site.register(Listing)
admin.site.register(Realtor)
admin.site.register(Genre)
@admin.register(ListingInstance)
class ListingInstanceAdmin(admin.ModelAdmin):
    list_display = ('listing', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {'fields': ('listing', 'imprint', 'id')}),
        ('Availability', {'fields': ('status', 'due_back', 'borrower')}),
    )
