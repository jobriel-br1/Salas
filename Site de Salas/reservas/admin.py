from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Sala, Reserva

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Dados USP', {'fields': ('nusp', 'funcao')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados USP', {'fields': ('nusp', 'funcao')}),
    )

admin.site.register(Sala)
admin.site.register(Reserva)

