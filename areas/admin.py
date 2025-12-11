from django.contrib import admin
from .models import CommonArea, Reservation


@admin.register(CommonArea)
class CommonAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'cost_per_hour', 'is_available', 'opening_time', 'closing_time']
    list_filter = ['is_available']
    search_fields = ['name', 'description']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['area', 'user', 'start_time', 'end_time', 'status', 'payment_confirmed']
    list_filter = ['status', 'payment_confirmed', 'start_time']
    search_fields = ['area__name', 'user__username']
    date_hierarchy = 'start_time'
