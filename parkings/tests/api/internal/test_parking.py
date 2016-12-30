from django.core.urlresolvers import reverse

from ..utils import ALL_METHODS, check_method_status_codes

list_url = reverse('internal:v1:parking-list')


def get_detail_url(obj):
    return reverse('internal:v1:parking-detail', kwargs={'pk': obj.pk})


def test_other_than_staff_cannot_do_anything(unauthenticated_api_client, operator_api_client, parking):
    urls = (list_url, get_detail_url(parking))
    check_method_status_codes(unauthenticated_api_client, urls, ALL_METHODS, 401)
    check_method_status_codes(operator_api_client, urls, ALL_METHODS, 403)


def test_disallowed_methods(staff_api_client, parking):
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    urls = (list_url, get_detail_url(parking))
    check_method_status_codes(staff_api_client, urls, disallowed_methods, 405)
