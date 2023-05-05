from rest_framework import filters, mixins, viewsets

from .permissions import ReadOnlyOrAdminPermission


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (ReadOnlyOrAdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
