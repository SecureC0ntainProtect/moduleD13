from django.urls import path

from .views import NoticeList, NoticeDetailView, NoticeUpdateView, NoticeCreate, NoticeDelete, NoticeComment, register_code_view, home_view


urlpatterns = [
    path('', home_view, name='login'),
    path('notice/', NoticeList.as_view()),
    path('notice/announce_create', NoticeCreate.as_view()),
    path('notice/<int:pk>', NoticeDetailView.as_view()),
    path('notice/<int:pk>/edit', NoticeUpdateView.as_view()),
    path('notice/<int:pk>/delete', NoticeDelete.as_view()),
    path('notice/<int:pk>/comments', NoticeComment.as_view()),
    path('notice/notice_create/', NoticeCreate.as_view()),
    path('notice/register_code/', register_code_view),
    path('comments/', NoticeComment.as_view()),
    path('notice_create/', NoticeCreate.as_view()),
]
