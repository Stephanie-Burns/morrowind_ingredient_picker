from django.shortcuts import render, get_object_or_404
from .models import Effect, IngredientEffect, Potion, Ingredient
from django.shortcuts import get_object_or_404, redirect


def ingredients_for_effect(request, effect_id):
    effect = get_object_or_404(Effect, id=effect_id)
    ingredient_effects = IngredientEffect.objects.filter(
        effect=effect
    ).select_related('ingredient').order_by('ingredient__weight', 'ingredient__value')

    context = {
        'effect': effect,
        'ingredient_effects': ingredient_effects,
    }
    return render(request, 'alchemy/ingredients_for_effect.html', context)


def favorite_ingredients(request):
    favorites = Ingredient.objects.filter(favorite=True).order_by('name')  # Get all favorites
    return render(request, 'alchemy/favorite_ingredients.html', {'favorites': favorites})


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import Ingredient

def toggle_favorite_htmx(request, ingredient_id):
    # Get the ingredient and toggle the 'favorite' field
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    ingredient.favorite = not ingredient.favorite
    ingredient.save()

    # Render the updated row
    html = render_to_string('alchemy/partials/ingredient_row.html', {'ingredient': ingredient})
    return HttpResponse(html)


def home(request):
    return render(request, 'alchemy/home.html')


def all_ingredients(request):
    ingredients = Ingredient.objects.all().order_by('name')  # Order alphabetically by name
    return render(request, 'alchemy/all_ingredients.html', {'ingredients': ingredients})

from django.db.models import Prefetch

def effect_list(request):
    # Prefetch and sort ingredients for each effect
    effects = Effect.objects.prefetch_related(
        Prefetch(
            'ingredienteffects',
            queryset=IngredientEffect.objects.select_related('ingredient').order_by(
                'ingredient__weight', 'ingredient__value'
            ),
            to_attr='sorted_ingredienteffects'
        )
    )
    return render(request, 'alchemy/effect_list.html', {'effects': effects})


from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Effect

from django.db.models import F

def ingredients_for_effect_modal(request, effect_id):
    # Fetch the selected effect
    effect = get_object_or_404(Effect, id=effect_id)

    # Fetch all related IngredientEffect objects and their Ingredients
    ingredient_effects = effect.ingredienteffects.select_related('ingredient').order_by(
        F('ingredient__weight').asc(),
        F('ingredient__value').asc()
    )

    # Render the modal's HTML content
    html = render_to_string('alchemy/partials/ingredients_modal.html', {
        'effect': effect,
        'ingredient_effects': ingredient_effects
    })

    # Return the raw HTML response
    return HttpResponse(html)



def select_effects(request):
    effects = Effect.objects.all().order_by('name')
    return render(request, 'alchemy/select_effects.html', {'effects': effects})

from collections import defaultdict
from django.shortcuts import render
from .models import Effect, Ingredient

def select_ingredients(request):
    if request.method == 'POST':
        effect_ids = request.POST.getlist('effects')
        effects = Effect.objects.filter(id__in=effect_ids)

        grouped_ingredients = {}
        seen_ingredients = set()

        for effect in effects:
            ingredients = Ingredient.objects.filter(
                ingredienteffects__effect=effect
            ).distinct()

            # Include all ingredients, but track them to disable duplicates
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
    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredients')
        if len(ingredient_ids) < 2 or len(ingredient_ids) > 4:
            return render(request, 'alchemy/select_ingredients.html', {
                'error': 'You must select between 2 and 4 ingredients.'
            })

        # Fetch the selected ingredients
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)

        # Start with the effects of the first ingredient
        common_effect_ids = set(ingredients[0].ingredienteffects.values_list('effect_id', flat=True))

        # Intersect with the effects of the other ingredients
        for ingredient in ingredients[1:]:
            ingredient_effect_ids = set(ingredient.ingredienteffects.values_list('effect_id', flat=True))
            common_effect_ids.intersection_update(ingredient_effect_ids)

        # Fetch the Effect objects for the common effect IDs
        common_effects = Effect.objects.filter(id__in=common_effect_ids)

        return render(request, 'alchemy/review_potion.html', {
            'ingredients': ingredients,
            'effects': common_effects,
        })
def save_potion(request):
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


from django.shortcuts import render
from .models import Effect

def search_effects(request):
    query = request.GET.get('search', '').strip().lower()

    # Filter effects by name or ingredients by name
    effects = Effect.objects.filter(
        name__icontains=query
    ).distinct() | Effect.objects.filter(
        ingredienteffects__ingredient__name__icontains=query
    ).distinct()

    return render(request, 'alchemy/partials/effects_table_body.html', {'effects': effects})


from .models import Ingredient, VendorInventory, IngredientEffect

def ingredient_detail(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    vendors = VendorInventory.objects.filter(ingredient=ingredient)
    # Fetch related effects
    effects = Effect.objects.filter(ingredienteffects__ingredient=ingredient).distinct()

    return render(request, 'alchemy/ingredient_detail.html', {
        'ingredient': ingredient,
        'vendors': vendors,
        'effects': effects,
    })

from django.shortcuts import render, get_object_or_404
from .models import Vendor

def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    # Fetch all inventory items for this vendor
    inventory = vendor.inventory.select_related('ingredient')

    return render(request, 'alchemy/vendor_detail.html', {
        'vendor': vendor,
        'inventory': inventory,
    })
