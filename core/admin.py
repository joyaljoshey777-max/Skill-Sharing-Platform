from django.contrib import admin
from .models import User, ProviderProfile, Skill, Booking, Review

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_provider', 'is_customer', 'is_staff')
    list_filter = ('is_provider', 'is_customer', 'is_staff')
    search_fields = ('username', 'email')

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1

@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'price_per_service')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    inlines = [SkillInline]
    actions = ['approve_providers', 'reject_providers']

    def approve_providers(self, request, queryset):
        queryset.update(status='Approved')
    approve_providers.short_description = "Mark selected providers as Approved"

    def reject_providers(self, request, queryset):
        queryset.update(status='Rejected')
    reject_providers.short_description = "Mark selected providers as Rejected"

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider')
    search_fields = ('name', 'provider__user__username')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'skill', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'provider__user__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'provider__user__username')
