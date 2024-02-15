"""
Tests for the Tag API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user for tests."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving tags."""
        res = self.client.get(TAGS_URL)
        # This test case basically means an unauthenticated request
        # to the tags-list endpoint. And what we would expect in our situation
        # is to just get a 401 unauthorized. We don't expect to see
        # any tags because we haven't authenticated, so it doesn't know which
        # user to send the tags for. So this is the thing we're testing here is
        # just that the API requires authentication.
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API."""
    def setUp(self):
        """That's just the setup here. So we create a user, we create a client
        and then we authenticate the user on the clients or request are made
        to the client, are authenticated as a user that we created."""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        # So this is just two sample tags that we're going to use to test with.
        # That's the setup that we need to do.
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # Now we're actually execute the code by calling the API.
        res = self.client.get(TAGS_URL)

        # And then we're going to assert that the response is what we expect.
        # We will check the results.
        tags = Tag.objects.all().order_by('-name')
        # And then we're going to serialize the tags and then compare the
        # response data to the serialized data.
        # So it will be a list of objects.
        serializer = TagSerializer(tags, many=True)
        # We're going to compare the response data to the serialized data.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # We're going to compare the response data to the serialized data.
        self.assertEqual(res.data, serializer.data)
        # So that's testing the retrieve tags, basic test.

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        # Here we've created another user.
        user2 = create_user(email='user2@example.com')
        # And then we've created a tag for that particular user.
        # It's going to be a fruity tag :)
        Tag.objects.create(user=user2, name='Fruity')
        # And then we're going to create another tag for our authenticated user
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
