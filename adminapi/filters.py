from rest_framework.filters import OrderingFilter
from django.db.models.functions import Lower


class CaseInsensitiveOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)[0]

        if ordering is not None:
            if ordering.startswith('-'):
                queryset = queryset.order_by(Lower(ordering[1:]).desc())
            else:
                queryset = queryset.order_by(Lower(ordering).asc())
        return queryset