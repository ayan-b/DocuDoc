from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import generic
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from simple_search import search_filter

from .models import Case, Comment, User, MyLibrary, Document, BookmarkedCase
from .forms import (
    NewCaseForm, NewCommentForm, CreateUserForm, AddUserForm, SignUpFormPatient, CaseEditForm, UploadFileForm,
    EditProfileForm, SignUpFormMedical, EditProfileFormMedical
)
from .decorators import admin_only, unauthenticated_user, allowed_users
from .utils import get_group, GROUP_TO_IDX


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'cases/index.html'
    context_object_name = 'latest_cases_list'

    def get_queryset(self):
        # Last 20
        return Case.objects.filter(
            users=self.request.user,
            is_active=True,
        ).order_by('-updated_date')[:20]


@login_required()
def index_view(request):
    latest_cases_list = Case.objects.filter(
        users=request.user,
        is_active=True
    ).order_by('-updated_date')[:20]
    form = None
    if request.method == 'POST':
        form = NewCaseForm(request.POST)
        if form.is_valid():
            patient_username = form.cleaned_data.get('patient_username')
            new_case = form.save(commit=False)
            new_case.save()
            patient_obj = User.objects.get(username=patient_username)
            new_case.users.set([request.user.pk, patient_obj.pk])
            return HttpResponseRedirect(reverse('cases:index'))
    else:
        form = NewCaseForm()
    bookmarked_cases = BookmarkedCase.objects.filter(user=request.user)
    return render(request, 'cases/index.html', {
        'latest_cases_list': latest_cases_list,
        'add_case': form,
        'bookmarked_cases': bookmarked_cases,
        'group': get_group(request.user),
    })


@login_required()
def search_results(request):
    query = request.GET.get('q')
    search_fields = ['cases_short_name', 'cases_description']
    cases = Case.objects.filter(
        search_filter(search_fields, query),
        users=request.user,
    )
    return render(request, 'cases/search-results.html', {'latest_cases_list': cases})


@login_required()
def all_cases(request):
    cases = Case.objects.filter(
        users=request.user,
    )
    return render(request, 'cases/all_cases.html', {'latest_cases_list': cases})


@login_required
def add_case(request):
    if request.method == 'POST':
        form = NewCaseForm(request.POST)
        if form.is_valid():
            patient_username = form.cleaned_data.get('patient_username')
            new_case = form.save(commit=False)
            new_case.save()
            patient_obj = User.objects.get(username=patient_username)
            new_case.users.set([request.user.pk, patient_obj.pk])
            return HttpResponseRedirect(reverse('cases:add_case'))
    else:
        form = NewCaseForm()
    return render(request, 'cases/add_case.html', {'form': form})


@login_required
def details(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.user not in case.users.all():
        raise PermissionDenied()
    comments = case.comments.all()
    documents = case.documents.all()
    new_comment_form = NewCommentForm(prefix='new-comment')
    add_user_form = AddUserForm(prefix='add-user')
    upload_file_form = UploadFileForm(prefix='upload-file')
    if request.method == 'POST':
        if 'new-comment' in request.POST:
            new_comment_form = NewCommentForm(data=request.POST, prefix='new-comment')
            if new_comment_form.is_valid():
                new_comment_form.instance.user = request.user
                new_comment = new_comment_form.save(commit=False)
                new_comment.case = case
                new_comment.save()
        elif 'add-user' in request.POST:
            add_user_form = AddUserForm(data=request.POST, prefix='add-user')
            if add_user_form.is_valid():
                user_to_add = add_user_form.cleaned_data.get('user_name')
                user_obj = User.objects.get(username=user_to_add)
                case.users.add(user_obj.pk)
        elif 'upload-file' in request.POST:
            upload_file_form = UploadFileForm(request.POST, request.FILES, prefix='upload-file')
            print(upload_file_form.errors)
            if upload_file_form.is_valid():
                print('test')
                upload_file_form.instance.user = request.user
                uploaded_file = upload_file_form.save(commit=False)
                uploaded_file.case = case
                uploaded_file.save()
    return render(
        request,
        'cases/details.html',
        {
            'case': case,
            'patient': User.objects.get(username=case.patient_username),
            'comments': {
                'hospital': comments.filter(comment_type=1),
                'prescription': comments.filter(comment_type=2),
                'diagnosis': comments.filter(comment_type=3),
            },
            'files': {
                'hospital': documents.filter(document_type=1),
                'prescription': documents.filter(document_type=2),
                'diagnosis': documents.filter(document_type=3),
            },
            'new_comment_form': new_comment_form,
            'add_user_form': add_user_form,
            'upload_file_form': upload_file_form,
            'group': get_group(request.user),
            'users': case.users.filter(groups__name__in=['pharmacy', 'diagnosis_center']),
            'patient_username': case.patient_username,
            'hospitals': case.users.filter(groups__name='hospital'),
            'all_user': User.objects.exclude(username=[user.username for user in case.users.all()]),
        },
    )


@login_required
def add_user(request):
    if request.user.is_superuser:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            print(form.errors)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                group_name = form.cleaned_data.get('group_name')
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                messages.success(request, 'Account created: ' + username)
                return redirect('/')
        return render(request, 'registration/add_user.html', {'form': form})
    else:
        raise PermissionDenied()


@login_required
def add_user_to_case(request):
    data = {}
    user_to_add = request.POST.get('username')
    case_id = request.POST.get('case_id')
    case = Case.objects.get(id=case_id)
    if request.user not in case.users.all():
        message = "You are not authorized to add user."
    else:
        user_obj = User.objects.get(username=user_to_add)
        case.users.add(user_obj.pk)
        message = f"Successfully added user {user_to_add}"
    data["message"] = message
    return JsonResponse(data)


@login_required
def remove_user(request):
    data = {}
    group = get_group(request.user)
    username = request.POST.get('username')
    case_id = request.POST.get('case_id')
    case = Case.objects.get(id=case_id)
    # make sure user is part of case
    if request.user not in case.users.all() or group > 2:
        message = "You're not authorized to remove a user!"
    elif group == 1:
        message = "Patient cannot be removed from a case!"
    else:
        user_to_remove = User.objects.get(username=username)
        if get_group(user_to_remove) == 2:
            message = 'Cannot remove hospital!'
        else:
            case.users.remove(user_to_remove)
            message = f"Removed {username}"
    data['message'] = message
    return JsonResponse(data=data)


@unauthenticated_user
def sign_up(request):
    form = SignUpFormPatient()
    if request.method == 'POST':
        form = SignUpFormPatient(request.POST)
        print(form.errors)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group_name = 'patient'
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            return redirect('/accounts/login')
    return render(request, 'registration/sign_up.html', {'form': form})


def sign_up_medical(request):
    form = SignUpFormMedical()
    if request.method == 'POST':
        form = SignUpFormMedical(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            user = form.save()
            group_name = form.cleaned_data.get('group_name')
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            user.is_active = False
            user.save()
            return redirect('/accounts/login')
            # TODO: Redirect to a page "You're account will be approved in few days"
    return render(request, 'registration/sign_up.html', {'form': form, 'medical': True})


def save_comment_form(request, form, pk, template_name):
    data = {}
    current_case = Comment.objects.get(id=pk).case
    if request.user not in current_case.users.all():
        raise PermissionDenied()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            comments = current_case.comments.all()
            data['comments_list'] = render_to_string('comment/comments.html', {
                    'comments': {
                        'hospital': comments.filter(comment_type=1),
                        'prescription': comments.filter(comment_type=2),
                        'diagnosis': comments.filter(comment_type=3),
                    },
                    'group': get_group(request.user)
                }
                                                     )
            current_case.updated_date = now()
            current_case.save()
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user not in comment.case.users.all():
        raise PermissionDenied()
    if request.method == 'POST':
        form = NewCommentForm(request.POST, instance=comment)
    else:
        form = NewCommentForm(instance=comment)
    return save_comment_form(request, form, pk, 'comment/edit_modal_template.html')


def save_case_form(request, form, pk, template_name):
    data = {}
    case = Case.objects.get(id=pk)
    if request.method == 'POST':
        print(form.errors)
        if form.is_valid():
            form.save()
            case_short_name = form.cleaned_data['cases_short_name']
            case_description = form.cleaned_data['cases_description']
            is_active = form.cleaned_data['is_active']
            case.cases_short_name = case_short_name
            case.cases_description = case_description
            case.is_active = is_active
            case.updated_date = now()
            case.save()
            data['form_is_valid'] = True
            data['cases_detail'] = render_to_string('cases/case_description.html', {
                'case': case,
                'group': get_group(request.user),
            })
            return redirect("cases:details", case.id)
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


@login_required
def case_edit(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.user not in case.users.all():
        raise PermissionDenied()
    if request.method == 'POST':
        form = CaseEditForm(request.POST, instance=case)
    else:
        form = CaseEditForm(instance=case)
    return save_case_form(request, form, pk, 'cases/case_edit_modal_template.html')


@login_required
def add_to_library(request, pk):
    data = {'form_is_valid': False}
    if request.method == 'POST':
        if 'remove' in request.POST:
            data['form_is_valid'] = True
            MyLibrary.objects.filter(user=request.user).get(document=pk).delete()
            current_library = MyLibrary.objects.filter(user=request.user)
            data['library_html'] = render_to_string(
                'cases/library.html',
                {
                    'library': current_library,
                    'remove': True
                },
                request=request
            )
        else:
            obj, created = MyLibrary.objects.get_or_create(user=request.user, document=Document.objects.get(id=pk))
            data['form_is_valid'] = True
    return JsonResponse(data)


@login_required
def bookmark_case(request, pk):
    data = {'form_is_valid': False}
    if request.method == 'POST':
        print(request.POST)
        if 'remove' in request.POST:
            BookmarkedCase.objects.filter(user=request.user).get(case=pk).delete()
        else:
            obj, created = BookmarkedCase.objects.get_or_create(user=request.user, case=Case.objects.get(id=pk))
        data['form_is_valid'] = True
        data['bookmarked_cases_html'] = render_to_string('cases/bookmarked_cases.html', context={
            'bookmarked_cases': BookmarkedCase.objects.filter(user=request.user)
        }, request=request)
    return JsonResponse(data)


def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    if not user.is_active or user.is_superuser:
        return redirect('/')
    # patient profiles can be viewed by themselves only
    # medical profiles are publicly visible, however editable by account holders only
    group = get_group(user)
    if group == 1:
        edit_form = EditProfileForm
    else:
        edit_form = EditProfileFormMedical
    if request.user == user:  # patient or user viewing their own profile
        form = None
        if request.method == 'POST':
            form = edit_form(request.POST, instance=user)
        else:
            form = edit_form(instance=user)
        if form.is_valid():
            form.save()
        return render(request=request, template_name='profile/profile.html', context={'form': form, 'user': user})
    elif group != 1:
        return render(
            request=request,
            template_name='profile/show_profile.html',
            context={'user': user, 'type': GROUP_TO_IDX[group].replace('_', ' ')}
        )
    else:
        raise PermissionDenied()


@login_required
def show_library(request):
    current_library = MyLibrary.objects.filter(user=request.user)
    return render(request, 'cases/library.html', {'library': current_library, 'remove': True})


@login_required()
def dashboard(request):
    if request.user.is_superuser:
        unapproved_users = User.objects.filter(is_active=False)
        return render(request, 'dashboard/dashboard.html', {'users': unapproved_users})
    else:
        raise PermissionDenied()


@login_required()
def approve(request, pk):
    if request.user.is_superuser:
        user = User.objects.get(id=pk)
        user.is_active = True
        user.save()
        data = {'message': f'Approved user {user.username}'}
        return JsonResponse(data=data)
    else:
        raise PermissionDenied()


@login_required()
def delete_comment(request, pk):
    Comment.objects.filter(id=pk).delete()
    data = {'message': 'Comment deleted'}
    return JsonResponse(data=data)


# Error code: 400
def bad_request(request, exception):
    return render(request, template_name='error/error.html', context={'code': '400'})


# Error code: 403
def permission_denied(request, exception):
    return render(request, template_name='error/error.html', context={'code': '403'})


# Error code 404
def page_not_found(request, exception):
    return render(request, template_name='error/error.html', context={'code': '404'})


# Error code 500
def server_error(request):
    return render(request, template_name='error/error.html', context={'code': '500'})
