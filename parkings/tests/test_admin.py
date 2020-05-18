from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from ..factories.permit import create_permit, create_permit_series
from ..models import ParkingCheck


class AdminTestCase(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser('admin', '', 'admin')

        url_end = '{obj_id}/change/' if self.kind == 'change' else ''

        self.obj = self.create_object()
        self.url = ('{admin_root}{app_label}/{model}/' + url_end).format(
            admin_root=reverse('admin:index'),
            app_label=self.obj._meta.app_label,
            model=self.obj._meta.model_name,
            obj_id=self.obj.id)

        self.client = Client()
        self.client.force_login(self.user)

        self.response = self.client.get(self.url)
        self.response_text = self.response.content.decode('utf-8')

        assert self.response.status_code == HTTP_200_OK


class ListAdminTestCase(AdminTestCase):
    kind = 'list'

    def get_first_value(self, name):
        """
        Get value of a field in the first row of the table.
        """
        td_text = '<td class="field-{}">'.format(name)
        assert td_text in self.response_text
        return self.response_text.split(td_text, 1)[1].split('<', 1)[0]


class ObjAdminTestCase(AdminTestCase):
    kind = 'change'


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


class TestPermitListAdmin(ListAdminTestCase):
    def create_object(self):
        return create_permit(subject_count=7, area_count=6)

    def test_item_count_has_correct_value(self):
        assert self.get_first_value('item_count') == str(7 * 6)


class TestPermitLookupItemAdmin(ObjAdminTestCase):
    def create_object(self):
        permit = create_permit()
        return permit.lookup_items.first()

    def test_is_readonly(self):
        assert '<input type="text"' not in self.response_text


class TestPermitLookupItemListAdmin(ListAdminTestCase):
    def create_object(self):
        return create_permit().lookup_items.first()

    def test_series_column_exists(self):
        assert '>Series<' in self.response_text
        assert '<th scope="col"  class="column-series">' in self.response_text

    def test_series_has_correct_value(self):
        expected_val = '{id}{star}'.format(
            id=self.obj.permit.series.id,
            star='*' if self.obj.permit.series.active else '')
        assert self.get_first_value('series') == expected_val


class TestPermitSeriesListAdmin(ListAdminTestCase):
    def create_object(self):
        series = create_permit_series()
        self.permit1 = create_permit(series=series)
        self.permit2 = create_permit(series=series)
        self.permit3 = create_permit(series=series)
        return series

    def test_permit_count_has_correct_value(self):
        assert self.get_first_value('permit_count') == '3'
