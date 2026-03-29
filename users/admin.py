# users/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('role', 'numero_clase')


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_clase', 'is_active')
    list_filter = ('is_active', 'is_superuser', 'profile__role', 'profile__numero_clase')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Profile.DoesNotExist:
            return '—'
    get_role.short_description = 'Rol'

    def get_clase(self, obj):
        try:
            return obj.profile.numero_clase or '—'
        except Profile.DoesNotExist:
            return '—'
    get_clase.short_description = 'Clase'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)