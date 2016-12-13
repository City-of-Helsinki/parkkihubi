from rest_framework.authentication import TokenAuthentication


class ApiKeyAuthentication(TokenAuthentication):
    keyword = 'ApiKey'
