from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Ingredient, Effect, IngredientEffect, Vendor, VendorInventory


# Ingredient Forms and Admin
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'  # Include all fields


class IngredientEffectInline(admin.TabularInline):
    model = IngredientEffect
    extra = 4
    autocomplete_fields = ['effect']
    fields = ('effect',)  # Explicitly include the 'effect' field for clarity


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'weight', 'favorite', 'get_effects', 'image_tag')
    search_fields = ('name',)
    list_filter = ('value', 'weight', 'favorite')
    inlines = [IngredientEffectInline]

    def get_effects(self, obj):
        # Fetch effects via IngredientEffect
        return ', '.join([ie.effect.name for ie in obj.ingredienteffects.all()])

    get_effects.short_description = "Effects"

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 4px;" />', obj.image.url)
        return "No Image"

    image_tag.short_description = "Image"


# IngredientEffect Admin
@admin.register(IngredientEffect)
class IngredientEffectAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'effect')
    search_fields = ('ingredient__name', 'effect__name')


# Effect Admin
@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_negative', 'icon_tag')
    search_fields = ('name',)
    list_filter = ('is_negative',)

    def icon_tag(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 4px;" />', obj.icon.url)
        return "No Icon"

    icon_tag.short_description = "Icon"


# Vendor and Inventory Admin
class VendorInventoryInline(admin.TabularInline):
    model = VendorInventory
    extra = 1  # Allow adding one inventory item at a time
    autocomplete_fields = ['ingredient']  # Enable autocomplete for ingredient selection


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'profession', 'city', 'building', 'available_gold', 'image_tag')
    search_fields = ('name', 'city', 'building', 'profession')
    list_filter = ('city', 'profession')
    inlines = [VendorInventoryInline]

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"

    image_tag.short_description = "Image"
