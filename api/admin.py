from django.contrib import admin
from .models import Activity, User, Weather


class ActivityAdmin(admin.ModelAdmin):
    pass


class UserAdmin(admin.ModelAdmin):
    pass


class WeatherAdmin(admin.ModelAdmin):
    pass


admin.site.register(Activity, ActivityAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Weather, WeatherAdmin)
