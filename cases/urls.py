from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from docudoc import settings

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
    url(r'accounts/signup/$', view=views.SignUp.as_view(), name='signup'),
    url(r'accounts/signup/medical/$', view=views.SignUpMedical.as_view(), name='medical_signup'),
    url(
        r'accounts/change-password/$',
        view=auth_views.PasswordChangeView.as_view(
            template_name='registration/change_password.html',
            success_url=reverse_lazy('cases:index')
        ),
        name='change_password'),
    url(
        'accounts/signup/medical/approval-required',
        view=TemplateView.as_view(template_name='registration/approval_required.html'),
        name='approval_required'
    ),
    url(r'^add-user/$', views.add_user, name='add_user'),

    # case-related stuff
    path('', view=views.IndexView.as_view(), name='index'),
    path('add-user-to-case', views.add_user_to_case, name='add_user_to_case'),
    path('remove-user', views.RemoveUser.as_view(), name='remove_user'),
    path('add-case/', view=views.AddCase.as_view(), name='add_case'),
    path('add-admin/', view=views.add_admin, name='add_admin'),
    path('cases/<int:pk>', view=views.details, name='details'),
    path('cases/<int:pk>/edit', view=views.case_edit, name='edit_case'),
    path('comments/<int:pk>/edit/', view=views.comment_edit, name='edit_comment'),
    path('comments/<int:pk>/delete/', view=views.DeleteComment.as_view(), name='delete_comment'),
    url(r'search-medical', view=views.search_medical, name='search_medical'),
    url(r'search', view=views.SearchResults.as_view(), name='search_results'),
    path('all', view=views.AllCases.as_view(), name='all_cases'),
    path('add-to-my-library/<int:pk>', view=views.add_to_library, name='add_to_library'),
    path('bookmark-case/<int:pk>/', view=views.bookmark_case, name='bookmark_case'),

    # profile-related stuff
    url(r'profile/(?P<username>[a-zA-Z0-9-_.]+)$', view=views.view_profile, name='view_profile'),
    path('library/', view=views.ShowLibrary.as_view(), name='library'),

    # admin-related stuff
    path('dashboard/', view=views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/approve/<int:pk>', view=views.Approve.as_view(), name='approve'),

    # drchrono related
    path('notes/<int:pk>/', view=views.GetAppointments.as_view(), name='clinical-notes'),
    path('add-clinical-note/<int:pk>', view=views.AddToClinicalNote.as_view(), name='add-clinical-note'),
]
