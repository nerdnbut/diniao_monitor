from django.urls import path
from .views import FileManagementViewSet

urlpatterns = [
    path('servers/<int:server_id>/files/list/', FileManagementViewSet.as_view({'get': 'list_files'})),
    path('servers/<int:server_id>/files/content/', FileManagementViewSet.as_view({'get': 'content'})),
    path('servers/<int:server_id>/files/save/', FileManagementViewSet.as_view({'post': 'save'})),
    path('servers/<int:server_id>/files/delete/', FileManagementViewSet.as_view({'delete': 'delete'})),
    path('servers/<int:server_id>/files/download/', FileManagementViewSet.as_view({'get': 'download'})),
    path('servers/<int:server_id>/files/upload/', FileManagementViewSet.as_view({'post': 'upload'})),
] 