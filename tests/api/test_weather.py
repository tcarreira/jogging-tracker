from unittest import mock

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from api.models import Weather


class TestWeather(TestCase):
    def setUp(self):
        Weather.objects.create(id=5, title="Titl", description="Desc")

    def test_get_or_create_empty_id(self):
        none_activity = Weather.get_or_create()
        self.assertIsNone(none_activity)

        none_activity = Weather.get_or_create(id=5)
        self.assertIsNone(none_activity)

        none_activity = Weather.get_or_create(id=5, title="Titl")
        self.assertIsNone(none_activity)

        none_activity = Weather.get_or_create(id=15, title="Titl")
        self.assertIsNone(none_activity)

        none_activity = Weather.get_or_create(title="Titl")
        self.assertIsNone(none_activity)

        none_activity = Weather.get_or_create(description="Desc")
        self.assertIsNone(none_activity)

        none_activity = Weather.get_or_create(title="Titl", description="Desc")
        self.assertIsNone(none_activity)

    def test_get_or_create_get(self):
        activity = Weather.get_or_create(id=5, title="Titl", description="Desc")
        self.assertEqual(activity.id, 5)
        self.assertEqual(activity.title, "Titl")
        self.assertEqual(activity.description, "Desc")

    def test_get_or_create_create(self):
        activity = Weather.get_or_create(
            id=499, title="Titl 499", description="Full Desc"
        )
        self.assertEqual(activity.id, 499)
        self.assertEqual(activity.title, "Titl 499")
        self.assertEqual(activity.description, "Full Desc")

    def test_get_or_create_existing_id(self):
        activity = Weather.get_or_create(
            id=5, title="Titl 499", description="Full Desc"
        )
        self.assertEqual(activity.id, 5)
        self.assertEqual(activity.title, "Titl")
        self.assertEqual(activity.description, "Desc")
