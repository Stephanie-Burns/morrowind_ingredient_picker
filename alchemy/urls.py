from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('effect/<int:effect_id>/', views.ingredients_for_effect, name='ingredients_for_effect'),
    path('effects/', views.effect_list, name='effect_list'),
    path('favorites/', views.favorite_ingredients, name='favorite_ingredients'),
    # path('ingredient/<int:ingredient_id>/toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('ingredient/<int:ingredient_id>/toggle_favorite_htmx/', views.toggle_favorite_htmx, name='toggle_favorite_htmx'),
    path('ingredients/', views.all_ingredients, name='all_ingredients'),  # All ingredients page
    path('effects/<int:effect_id>/modal/', views.ingredients_for_effect_modal, name='ingredients_for_effect_modal'),
    path('potions/select_effect/', views.select_effects, name='select_effect'),
    path('potions/select_ingredients/', views.select_ingredients, name='select_ingredients'),

    path('potions/review/', views.review_potion, name='review_potion'),
    path('potions/save/', views.save_potion, name='save_potion'),
    path('effects/search/', views.search_effects, name='search_effects'),
    path('ingredient/<int:ingredient_id>/', views.ingredient_detail, name='ingredient_detail'),
    path('vendor/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
]

# Add this at the end of your urlpatterns
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:  # Only serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
