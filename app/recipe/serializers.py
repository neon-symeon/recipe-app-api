"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)  # many=True this is
    # going to be a list of items.
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        # Then we're getting the authenticate user. Because we're doing this in
        # a sterilizer and not the view, we need to use this self.context
        # request.
        auth_user = self.context['request'].user
        # Then we're going to loop through all of the tags that we popped off
        # the loop is going to give us functionality to not create duplicate
        # tags in the system.
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)
    # These nested serializers, those are read only. So that means you can read
    # he values, but you can't create items with those values. We want to add
    # the feature to be able to create them. We're going to do that by adding
    # a new method to the class that allows us to override the behavior of
    # the create functionality.

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        # So the idea is that it's going to either get an existing ingredient
        # or create a new ingredient. Ultimately, it's going to be adding an
        # ingredient to the recipe object. So we start by retrieving the
        # authenticated user so we can assign the ingredient to the correct
        # user. Then we're looping through all of the ingredients that were
        # passed in as an argument here at the top. And then we are calling
        # the get_or_create helper method on the objects manager for our
        # ingredient model.
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe."""
        # So this is why we are using pop here because we want to make sure we
        # remove the tags before we create the recipe using this here. Because
        # if you were to just pass in tags directly to the recipe model, that's
        # not going to work because it's a recipe model and expects only the
        # values for the recipe and it expects tags to be assigned as a related
        # field, so expects it to be created separately and added as a
        # relationship to recipe from the many. Too many field that we added.
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        # With the rest of the validated data - everything excluding tags -
        # we're going to create a new recipe with `**validated_data` values.
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):  # instance is the existing
        # object that we're going to update with the validated data.
        """Update a recipe."""
        # We're going to pop the tags off the validated data. We're going to
        # assign the tags to a variable. We're going to use the get method to
        # get the tags from the validated data. If it doesn't exist, we're
        # going to default to an None value.
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        # We're going to call the parent class update method. This is going to
        # update the instance with the validated data. So it's going to update
        # the title, time_minutes, price, link, and any other fields that we
        # pass in.
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
