from django.core.urlresolvers import reverse

from ..utils import check_disallowed_methods

list_url = reverse('operator:v1:parking-list')


def get_detail_url(obj):
    return reverse('operator:v1:parking-detail', kwargs={'pk': obj.pk})


def test_disallowed_methods(operator_api_client, parking):
    list_disallowed_methods = ('get', 'put', 'patch', 'delete')
    check_disallowed_methods(operator_api_client, list_url, list_disallowed_methods)

    detail_disallowed_methods = ('get', 'post')
    check_disallowed_methods(operator_api_client, get_detail_url(parking), detail_disallowed_methods)
