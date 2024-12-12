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
    """Display all effects with associated ingredients."""
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
        return render(request, 'alchemy/partials/effect_row.html', {'effects': effects})
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
    """Search effects or ingredients by name."""
    query = request.GET.get('search', '').strip().lower()
    effects = Effect.objects.filter(
        Q(name__icontains=query) | Q(ingredienteffects__ingredient__name__icontains=query)
    ).distinct()
    return render(request, 'alchemy/partials/effects_table_body.html', {'effects': effects})


# === Potion Views ===

def select_effects(request):
    """Allow users to select effects for potion making."""
    effects = Effect.objects.all().order_by('name')
    return render(request, 'alchemy/select_effects.html', {'effects': effects})


def select_ingredients(request):
    """Allow users to select ingredients for potion making."""
    if request.method == 'POST':
        effect_ids = request.POST.getlist('effects')
        effects = Effect.objects.filter(id__in=effect_ids)

        grouped_ingredients = {}
        seen_ingredients = set()

        for effect in effects:
            ingredients = Ingredient.objects.filter(
                ingredienteffects__effect=effect
            ).distinct()

            grouped_ingredients[effect] = [
                {"ingredient": ingredient, "disabled": ingredient.id in seen_ingredients}
                for ingredient in ingredients
            ]
            seen_ingredients.update(ingredient.id for ingredient in ingredients)

        return render(request, 'alchemy/select_ingredients.html', {
            'effects': effects,
            'grouped_ingredients': grouped_ingredients,
        })


def review_potion(request):
    """Review the effects of the selected potion ingredients."""
    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredients')
        if len(ingredient_ids) < 2 or len(ingredient_ids) > 4:
            return render(request, 'alchemy/select_ingredients.html', {
                'error': 'You must select between 2 and 4 ingredients.'
            })

        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        common_effect_ids = set(ingredients[0].ingredienteffects.values_list('effect_id', flat=True))

        for ingredient in ingredients[1:]:
            ingredient_effect_ids = set(ingredient.ingredienteffects.values_list('effect_id', flat=True))
            common_effect_ids.intersection_update(ingredient_effect_ids)

        common_effects = Effect.objects.filter(id__in=common_effect_ids)
        return render(request, 'alchemy/review_potion.html', {
            'ingredients': ingredients,
            'effects': common_effects,
        })


def save_potion(request):
    """Save a created potion."""
    if request.method == 'POST':
        name = request.POST.get('name')
        ingredient_ids = request.POST.get('ingredients').split(',')
        effect_ids = request.POST.get('effects').split(',')

        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        effects = Effect.objects.filter(id__in=effect_ids)

        potion = Potion.objects.create(name=name)
        potion.ingredients.set(ingredients)
        potion.effects.set(effects)

        return redirect('view_potions')


# === Vendor Views ===

def vendor_detail(request, vendor_id):
    """Display details for a specific vendor."""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    inventory = vendor.inventory.select_related('ingredient')
    return render(request, 'alchemy/vendor_detail.html', {
        'vendor': vendor,
        'inventory': inventory,
    })
