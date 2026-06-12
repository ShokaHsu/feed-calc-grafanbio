from ingredients.models import Ingredient
from standards.models import NutrientStandard


def make_standard():
    return NutrientStandard.objects.create(
        name="Test Swine Grower",
        species="SWINE",
        stage="GROWER",
    )


def make_ingredient_corn():
    return Ingredient.objects.create(
        name="玉米",
        category="CEREAL",
        dm_percent=88.0,
        is_public=True,
    )


def make_ingredient_sbm():
    return Ingredient.objects.create(
        name="黃豆粕",
        category="LEGUME",
        dm_percent=90.0,
        is_public=True,
    )
