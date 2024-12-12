from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    value = models.IntegerField()  # Change to IntegerField
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='ingredient_images/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    known_locations = models.TextField(blank=True, null=True)
    favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class Effect(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='effect_icons/', blank=True, null=True)  # New field for icon

    def __str__(self):
        return self.name


class IngredientEffect(models.Model):
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='ingredienteffects')
    effect = models.ForeignKey('Effect', on_delete=models.CASCADE, related_name='ingredienteffects')

    def __str__(self):
        return f"{self.ingredient.name} -> {self.effect.name}"


class Potion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ingredients = models.ManyToManyField('Ingredient')
    effects = models.ManyToManyField('Effect')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    profession = models.CharField(max_length=255)  # Example: Alchemist, Merchant
    city = models.CharField(max_length=255)  # Example: Balmora
    building = models.CharField(max_length=255)  # Example: Guild of Mages
    image = models.ImageField(upload_to='vendor_images/', blank=True, null=True)
    available_gold = models.DecimalField(max_digits=10, decimal_places=2)  # Vendor's gold amount

    def __str__(self):
        return f"{self.name} ({self.profession} in {self.city}, {self.building})"

class VendorInventory(models.Model):
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='inventory')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='vendorinventories')
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the ingredient

    class Meta:
        unique_together = ('vendor', 'ingredient')  # Ensure no duplicate ingredients per vendor

    def __str__(self):
        return f"{self.vendor.name} - {self.ingredient.name} (x{self.quantity})"
