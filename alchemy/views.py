from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.db.models import Prefetch, F, Q
from collections import defaultdict

from .models import (
    Effect,
    Ingredient,
    IngredientEffect,
    Potion,
    Vendor,
    VendorInventory
)

# === Home and General Views ===

def home(request):
    """Render the home page."""
    return render(request, 'alchemy/home.html')


# === Ingredient Views ===

def all_ingredients(request):
    """Display all ingredients."""
    ingredients = Ingredient.objects.all().order_by('name')
    return render(request, 'alchemy/all_ingredients.html', {'ingredients': ingredients})


def ingredient_detail(request, ingredient_id):
    """Display details for a specific ingredient."""
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    vendors = VendorInventory.objects.filter(ingredient=ingredient)
    effects = Effect.objects.filter(ingredienteffects__ingredient=ingredient).distinct()
    return render(request, 'alchemy/ingredient_detail.html', {
        'ingredient': ingredient,
        'vendors': vendors,
        'effects': effects,
    })


def toggle_favorite_htmx(request, ingredient_id):
    """Toggle the 'favorite' status of an ingredient using HTMX."""
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    ingredient.favorite = not ingredient.favorite
    ingredient.save()
    html = render_to_string('alchemy/partials/ingredient_row.html', {'ingredient': ingredient})
    return HttpResponse(html)


def favorite_ingredients(request):
    """Display all favorite ingredients."""
    favorites = Ingredient.objects.filter(favorite=True).order_by('name')
    return render(request, 'alchemy/favorite_ingredients.html', {'favorites': favorites})


# === Effect Views ===

def all_effects(request):
    effects = Effect.objects.prefetch_related(
        Prefetch(
            'ingredienteffects',
            queryset=IngredientEffect.objects.select_related('ingredient').order_by(
                'ingredient__weight', 'ingredient__value'
            ),
            to_attr='sorted_ingredienteffects'
        )
    )
    if request.htmx:
        # Render only the table body for HTMX requests
        return render(request, 'alchemy/partials/effects_table_body.html', {'effects': effects})
    # Render the full page for standard requests
    return render(request, 'alchemy/all_effects.html', {'effects': effects})


def ingredients_for_effect(request, effect_id):
    """Display ingredients associated with a specific effect."""
    effect = get_object_or_404(Effect, id=effect_id)
    ingredient_effects = IngredientEffect.objects.filter(
        effect=effect
    ).select_related('ingredient').order_by('ingredient__weight', 'ingredient__value')
    return render(request, 'alchemy/ingredients_for_effect.html', {
        'effect': effect,
        'ingredient_effects': ingredient_effects,
    })


def ingredients_for_effect_modal(request, effect_id):
    """Serve a modal for ingredients associated with a specific effect."""
    effect = get_object_or_404(Effect, id=effect_id)
    ingredient_effects = effect.ingredienteffects.select_related('ingredient').order_by(
        F('ingredient__weight').asc(),
        F('ingredient__value').asc()
    )
    html = render_to_string('alchemy/partials/ingredients_modal.html', {
        'effect': effect,
        'ingredient_effects': ingredient_effects,
    })
    return HttpResponse(html)


def search_effects(request):
    query = request.GET.get('search', '').strip().lower()
    effects = Effect.objects.prefetch_related(
        Prefetch(
            'ingredienteffects',
            queryset=IngredientEffect.objects.select_related('ingredient').order_by(
                'ingredient__weight', 'ingredient__value'
            ),
            to_attr='sorted_ingredienteffects'
        )
    ).filter(
        Q(name__icontains=query) | Q(ingredienteffects__ingredient__name__icontains=query)
    ).distinct()

    # Render the table body for HTMX
    return render(request, 'alchemy/partials/effects_table_body.html', {'effects': effects})


# === Potion Views ===

def potion_start(request):
    """Displays the starting interface for potion-making."""
    effects = Effect.objects.order_by('name')
    ingredients = Ingredient.objects.order_by('name')
    return render(request, 'alchemy/potion_start.html', {
        'effects': effects,
        'ingredients': ingredients,
    })

def potion_add_ingredient(request):
    """Adds an ingredient to the potion dynamically."""
    ingredient_id = request.GET.get('ingredient_id')
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    return render(request, 'alchemy/partials/ingredient_card.html', {'ingredient': ingredient})

def potion_add_effect(request):
    """Filters ingredients by a selected effect."""
    effect_id = request.GET.get('effect_id')
    effect = get_object_or_404(Effect, id=effect_id)
    ingredients = Ingredient.objects.filter(
        ingredienteffects__effect=effect
    ).distinct().order_by('name')
    return render(request, 'alchemy/partials/ingredient_list.html', {
        'effect': effect,
        'ingredients': ingredients,
    })

def potion_review(request):
    """Show the selected ingredients and their combined effects."""
    return render(request, 'alchemy/potions/review.html')

def potion_save(request):
    """Save the potion to the database."""
    return render(request, 'alchemy/potions/save.html')


# === Vendor Views ===

def vendor_detail(request, vendor_id):
    """Display details for a specific vendor."""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    inventory = vendor.inventory.select_related('ingredient')
    return render(request, 'alchemy/vendor_detail.html', {
        'vendor': vendor,
        'inventory': inventory,
    })
