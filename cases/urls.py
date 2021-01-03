from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from medidoc import settings

from . import views

app_name = 'cases'
urlpatterns = [
    # account-related stuff
    url(
        r'accounts/login/$',
        view=auth_views.LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True),
        name='login',
    ),
    url(r'accounts/logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'accounts/signup/$', view=views.sign_up, name='signup'),
    url(r'accounts/signup/medical/$', view=views.sign_up_medical, name='medical_signup'),
    url(r'accounts/change-password/$', view=views.change_password, name='change_password'),
    url(r'^add-user/$', views.add_user, name='add_user'),

    # case-related stuff
    path('', view=views.index_view, name='index'),
    path('add-user-to-case', views.add_user_to_case, name='add_user_to_case'),
    path('remove-user', views.remove_user, name='remove_user'),
    path('add-case/', view=views.add_case, name='add_case'),
    path('cases/<int:pk>', view=views.details, name='details'),
    path('cases/<int:pk>/edit', view=views.case_edit, name='edit_case'),
    path('comments/<int:pk>/edit/', view=views.comment_edit, name='edit_comment'),
    path('comments/<int:pk>/delete/', view=views.delete_comment, name='delete_comment'),
    url(r'search', view=views.search_results, name='search_results'),
    path('all', view=views.all_cases, name='all_cases'),
    path('add-to-my-library/<int:pk>', view=views.add_to_library, name='add_to_library'),
    path('bookmark-case/<int:pk>/', view=views.bookmark_case, name='bookmark_case'),

    # profile-related stuff
    url(r'profile/(?P<username>[a-zA-Z0-9-_.]+)$', view=views.view_profile, name='view_profile'),
    path('library/', view=views.show_library, name='library'),

    # admin-related stuff
    path('dashboard/', view=views.dashboard, name='dashboard'),
    path('dashboard/approve/<int:pk>', view=views.approve, name='approve'),
]
