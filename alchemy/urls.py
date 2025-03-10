from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # === Home ===
    path('', views.home, name='home'),  # Home page

    # === Effects ===
    path('effects/', views.all_effects, name='all_effects'),  # All effects page
    path('effects/search/', views.search_effects, name='search_effects'),  # Search effects
    path('effects/<int:effect_id>/', views.ingredients_for_effect, name='ingredients_for_effect'),  # Effect details
    path('effects/<int:effect_id>/modal/', views.ingredients_for_effect_modal, name='ingredients_for_effect_modal'),  # Effect modal

    # === Ingredients ===
    path('ingredients/', views.all_ingredients, name='all_ingredients'),  # All ingredients page
    path('ingredient/<int:ingredient_id>/', views.ingredient_detail, name='ingredient_detail'),  # Ingredient detail
    path('ingredient/<int:ingredient_id>/toggle_favorite_htmx/', views.toggle_favorite_htmx, name='toggle_favorite_htmx'),  # Toggle favorite

    # === Favorites ===
    path('favorites/', views.favorite_ingredients, name='favorite_ingredients'),  # Favorites page

    # === Potions ===
    path('potions/start/', views.potion_start, name='potion_start'),
    path('potions/add_ingredient/', views.potion_add_ingredient, name='potion_add_ingredient'),
    path('potions/add_effect/', views.potion_add_effect, name='potion_add_effect'),
    path('potions/review/', views.potion_review, name='potion_review'),
    path('potions/save/', views.potion_save, name='potion_save'),

    # === Vendors ===
    path('vendor/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),  # Vendor detail
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
