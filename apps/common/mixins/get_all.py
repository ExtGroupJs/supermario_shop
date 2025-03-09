from rest_framework import mixins
from rest_framework.decorators import action


from apps.common.pagination import AllResultsSetPagination


class GetAllMixin(mixins.ListModelMixin):
    """
    This mixin adds an action to return all the elements of a list, without pagination
    """

    @action(
        detail=False,
        methods=["GET"],
        url_path="get-all",
        url_name="get-all",
    )
    def get_all(self, request):
        self.pagination_class = AllResultsSetPagination
        return self.list(request)
