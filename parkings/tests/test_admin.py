from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from ..factories import PermitFactory
from ..models import ParkingCheck


class ObjAdminTestCase(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser('admin', '', 'admin')

        self.obj = self.create_object()
        self.url = '{admin_root}{app_label}/{model}/{obj_id}/change/'.format(
            admin_root=reverse('admin:index'),
            app_label=self.obj._meta.app_label,
            model=self.obj._meta.model_name,
            obj_id=self.obj.id)

        self.client = Client()
        self.client.force_login(self.user)

        self.response = self.client.get(self.url)
        self.response_text = self.response.content.decode('utf-8')

        assert self.response.status_code == HTTP_200_OK


class TestParkingCheckAdmin(ObjAdminTestCase):
    def create_object(self):
        return ParkingCheck.objects.create(
            performer=self.user,
            time='2019-01-01T12:00:00Z',
            time_overridden=True,
            registration_number='ABC-123',
            location=Point(60.193609, 24.951394),
            result={},
            allowed=False,
            found_parking=None,
        )

    def test_location_rendered_as_map(self):
        assert '<div id="id_location_map">' in self.response_text
        assert "OpenLayers.Map('id_location_map'" in self.response_text

    def test_location_not_modifiable(self):
        assert 'geodjango_location.modifiable = false;' in self.response_text


class TestPermitLookupItemAdmin(ObjAdminTestCase):
    def create_object(self):
        permit = PermitFactory()
        return permit.lookup_items.first()

    def test_is_readonly(self):
        assert '<input type="text"' not in self.response_text
