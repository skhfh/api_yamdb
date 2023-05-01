from django.shortcuts import get_object_or_404

from reviews.models import Review, Title


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        title_id = serializer_field.context["view"].kwargs.get("title_id")
        return get_object_or_404(Title, id=title_id)

    def __repr__(self):
        return "%s()" % self.__class__.__name__


class CurrentReviewDefault:
    requires_context = True

    def __call__(self, serializer_field):
        review_id = serializer_field.context["view"].kwargs.get("review_id")
        return get_object_or_404(Review, id=review_id)

    def __repr__(self):
        return "%s()" % self.__class__.__name__
