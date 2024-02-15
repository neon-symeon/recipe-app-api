"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
)


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

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    # These nested serializers, those are read only. So that means you can read
    # he values, but you can't create items with those values. We want to add
    # the feature to be able to create them. We're going to do that by adding
    # a new method to the class that allows us to override the behavior of
    # the create functionality.
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
        # With the rest of the validated data - everything excluding tags -
        # we're going to create a new recipe with `**validated_data` values.
        recipe = Recipe.objects.create(**validated_data)
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

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
