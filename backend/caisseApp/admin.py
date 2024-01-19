from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Product,AppUser,Code,Gift,Message,Transaction,Facture,Category
# Register your models here.

class AppUserAdmin(UserAdmin):
    model = AppUser
    list_display = ('username', 'email', 'points', 'is_active',)
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'points')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'points', 'is_active')}
        ),
    )
    search_fields = ('username', 'email',)
    ordering = ('username',)

admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Product)
admin.site.register(Code)
admin.site.register(Gift)
admin.site.register(Message)
admin.site.register(Transaction)
admin.site.register(Facture)
admin.site.register(Category)

