from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import generic, View
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.views.generic import TemplateView, ListView, FormView, DeleteView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from simple_search import search_filter

from .endpoints import AppointmentEndpoint, ClinicalNotes, PatientEndpoint, ClinicalNotesField
from .models import Case, Comment, User, MyLibrary, Document, BookmarkedCase
from .forms import (
    NewCaseForm, NewCommentForm, CreateUserForm, AddUserForm, SignUpFormPatient, CaseEditForm, UploadFileForm,
    EditProfileForm, SignUpFormMedical, EditProfileFormMedical, AddToClinicalNoteForm
)
from .decorators import unauthenticated_user
from .utils import get_group, GROUP_TO_IDX, get_token, get_clinical_note_field


class IndexView(LoginRequiredMixin, View):
    template_name = 'cases/index.html'
    context_object_name = 'latest_cases_list'
    form_class = NewCaseForm

    # can be moved to setup()
    @method_decorator(login_required)
    def check_group(self, request):
        group = get_group(request.user)
        if not group:
            group_name = 'doctor'
            group = Group.objects.get(name=group_name)
            request.user.groups.add(group)

    def get_queryset(self):
        # Last 20
        return Case.objects.filter(
            users=self.request.user,
            is_active=True,
        ).order_by('-updated_date')[:20]

    def get(self, request, *args, **kwargs):
        self.check_group(request)
        form = self.form_class()
        bookmarked_cases = BookmarkedCase.objects.filter(user=request.user)
        latest_cases_list = self.get_queryset()
        return render(request, 'cases/index.html', {
            'latest_cases_list': latest_cases_list,
            'add_case': form,
            'bookmarked_cases': bookmarked_cases,
            'group': get_group(request.user),
        })

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            patient_username = form.cleaned_data.get('patient_username')
            # this is email
            # if this patient doesn't exist create an account for them
            if not User.objects.filter(email=patient_username).exists():
                # get the patient info
                try:
                    validate_email(patient_username)
                except ValidationError as e:
                    params = {'chart_id': patient_username}
                else:
                    params = {'email': patient_username}
                access_token = get_token()
                patient_info = next(PatientEndpoint(access_token).list(params))
                new_user = User(
                    username=patient_info.get('email') or patient_info.get('chart_id'),
                    id=patient_info['id'],
                    first_name=patient_info['first_name'],
                    last_name=patient_info['last_name'],
                    email=patient_info.get('email'),
                    gender=patient_info['gender'],
                    birthdate=patient_info['date_of_birth'],
                    mobile_no=patient_info['cell_phone'],
                    emergency_mobile=patient_info['home_phone'],
                    address=patient_info['address'],
                )
                new_user.save()
                # Add to patient group
                group = Group.objects.get(name='patient')
                new_user.groups.add(group)
            new_case = form.save(commit=False)
            new_case.save()
            # TODO: Handle username
            try:
                patient_obj = User.objects.get(username=patient_username)
            except ObjectDoesNotExist:
                patient_obj = User.objects.get(email=patient_username)
            new_case.users.set([request.user.pk, patient_obj.pk])
            new_case = form.save(commit=False)
            new_case.save()
            return HttpResponseRedirect(reverse_lazy('cases:index'))


class SearchResults(LoginRequiredMixin, ListView):
    template_name = 'cases/search-results.html'
    context_object_name = 'latest_cases_list'

    def get_queryset(self):
        query = self.request.GET.get('q')
        search_fields = ['cases_short_name', 'cases_description']
        return Case.objects.filter(
            search_filter(search_fields, query),
            users=self.request.user,
        )


class SearchMedical(ListView):
    template_name = 'cases/search-medical.html'
    context_object_name = 'users'
    queries = ''

    def get_queryset(self):
        self.queries = self.request.GET.get('q')
        search_fields = ['username', 'address', 'mobile_no', 'emergency_mobile', 'pin_code', 'other_info']
        split_queries = self.queries.split()
        users = None
        for query in split_queries:
            current_users = User.objects.filter(
                search_filter(search_fields, query),
                is_active=True,
                groups__name__in=['doctor', 'pharmacy', 'diagnosis_center'],
            )
            if users is None:
                users = current_users
            else:
                users = users.union(current_users)
        return users

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.queries
        return context


class AllCases(LoginRequiredMixin, ListView):
    template_name = 'cases/all_cases.html'
    context_object_name = 'latest_cases_list'

    def get_queryset(self):
        return Case.objects.filter(users=self.request.user).order_by('-updated_date')


class AddCase(LoginRequiredMixin, FormView):
    form_class = NewCaseForm
    template_name = 'cases/add_case.html'
    success_url = reverse_lazy('cases:add_case')

    def form_valid(self, form):
        patient_username = form.cleaned_data.get('patient_username')
        # this is email
        # if this patient doesn't exist create an account for them
        if not User.objects.filter(email=patient_username).exists():
            # get the patient info
            params = {'email': patient_username}
            patient_info = (PatientEndpoint(params).list())[0]
            print(patient_info)
            new_user = User(
                username=patient_info['email'],
                first_name=patient_info['first_name'],
                last_name=patient_info['last_name'],
                email=patient_info['email'],
                gender=patient_info['gender'],
                birthdate=patient_info['date_of_birth']
            )
            new_user.save()
        new_case = form.save(commit=False)
        new_case.save()
        # TODO: Handle username
        patient_obj = User.objects.get(email=patient_username)
        new_case.users.set([self.request.user.pk, patient_obj.pk])
        super().form_valid(form)


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
                'doctor': comments.filter(comment_type=1),
                'prescription': comments.filter(comment_type=2),
                'diagnosis': comments.filter(comment_type=3),
            },
            'files': {
                'doctor': documents.filter(document_type=1),
                'prescription': documents.filter(document_type=2),
                'diagnosis': documents.filter(document_type=3),
            },
            'new_comment_form': new_comment_form,
            'add_user_form': add_user_form,
            'upload_file_form': upload_file_form,
            'add_to_clinical_note': AddToClinicalNoteForm(),
            'group': get_group(request.user),
            'users': case.users.filter(groups__name__in=['pharmacy', 'diagnosis_center']),
            'patient_username': case.patient_username,
            'doctors': case.users.filter(groups__name='doctor'),
            'all_user': User.objects.exclude(username=[user.username for user in case.users.all()]),
        },
    )


class GetAppointments(LoginRequiredMixin, View):

    # get clinical notes for this user
    def get(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        params = {'patient': user_id}
        end_date = datetime.today()
        start_date = datetime.today() - timedelta(189)
        print(get_token())
        notes = AppointmentEndpoint(get_token()).list(start=start_date, end=end_date, params=params)
        context_notes = []
        for note in notes:
            context_notes.append(note)
            print(note)
        data = {
            'html': render_to_string(template_name='cases/clinical-note-modal.html', context={'notes': context_notes})
        }
        return JsonResponse(data)


class AddToClinicalNote(LoginRequiredMixin, View):

    # add this comment to clinical note
    def post(self, request, *args, **kwargs):
        appointment = request.POST.get('appointment_id')
        clinical_note_field_text = request.POST.get('clinical_note_field_text')
        clinical_note_field = clinical_note_field_text
        comment_id = kwargs.get('pk')
        value = strip_tags(Comment.objects.get(pk=comment_id).content)
        # send post request
        data = {
            'appointment': appointment,
            'clinical_note_field': clinical_note_field,
            'value': value,
        }
        print(data)
        ret = ClinicalNotesField(get_token()).create(data=data)
        print(ret)
        data = {'message': ret['value'] == value}
        return JsonResponse(data)


@login_required
def add_user(request):
    if request.user.is_staff:
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
                return redirect('/add-user')
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


class RemoveUser(LoginRequiredMixin, View):

    def post(self, request):
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
                message = 'Cannot remove doctor or patient!'
            else:
                case.users.remove(user_to_remove)
                message = f"Removed {username}"
        data['message'] = message
        return JsonResponse(data=data)


class SignUp(FormView):
    template_name = 'registration/sign_up.html'
    form_class = SignUpFormPatient
    success_url = '/accounts/login'

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('username')
        group_name = 'patient'
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return super().form_valid(form)


class SignUpMedical(View):
    template_name = 'registration/sign_up.html'
    success_url = 'signup/medical/approval-required'
    sign_up_form_medical = SignUpFormMedical

    def post(self, request):
        form = self.sign_up_form_medical(request.POST, request.FILES)
        user = form.save()
        group_name = form.cleaned_data.get('group_name')
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        user.is_active = False
        user.save()
        return redirect('cases:approval_required')

    def get(self, request):
        return render(request, 'registration/sign_up.html', {'form': self.sign_up_form_medical(), 'medical': True})


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
                    'doctor': comments.filter(comment_type=1),
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
    if not user.is_active or user.is_staff:
        return redirect('cases:index')
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


class ShowLibrary(LoginRequiredMixin, ListView):
    template_name = 'cases/library.html'
    context_object_name = 'library'

    def get_queryset(self):
        return MyLibrary.objects.filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['remove'] = True
        return context


class Dashboard(LoginRequiredMixin, ListView):
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'users'

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.filter(is_active=False)
        else:
            raise PermissionDenied()


class Approve(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        print(kwargs)
        if request.user.is_staff:
            user = User.objects.get(id=kwargs['pk'])
            user.is_active = True
            user.save()
            data = {'message': f'Approved user {user.username}'}
            return JsonResponse(data=data)
        else:
            raise PermissionDenied()


class DeleteComment(LoginRequiredMixin, DeleteView):
    model = Comment

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        data = {'message': 'Comment deleted'}
        return JsonResponse(data=data)


# Error code: 400
def bad_request(request, exception):
    return render(request, template_name='error/error.html', context={'code': '400', 'message': 'Bad request.'})


# Error code: 403
def permission_denied(request, exception):
    return render(
        request, template_name='error/error.html', context=
        {
            'code': '403',
            'message': "Sorry, but looks like you don't have permission to view this page :(",
        }
    )


# Error code 404
def page_not_found(request, exception):
    return render(
        request,
        template_name='error/error.html',
        context={
            'code': '404',
            'message': "Sorry, but we couldn't find this page :(",
        }
    )


# Error code 500
def server_error(request):
    return render(
        request,
        template_name='error/error.html',
        context={
            'code': '500',
            'message': "Sorry, our server encountered some error :(",
        }
    )
