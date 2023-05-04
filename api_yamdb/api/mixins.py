from rest_framework import mixins, viewsets

from .permissions import ReadOnlyOrAdminPermission


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (ReadOnlyOrAdminPermission,)
