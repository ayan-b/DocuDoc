from django import forms
from django.contrib.auth.forms import UserCreationForm
from material import Layout, Fieldset, Row
from simple_search import search_form_factory

from .models import Case, Comment, User, Document
from .utils import TEXT_TO_ID


class NewCaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['patient_username', 'cases_short_name', 'cases_description']


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'comment_type']


class SignUpFormPatient(UserCreationForm):
    username = forms.CharField()
    email = forms.EmailField(label="Email Address")
    # password1 = forms.CharField(widget=forms.PasswordInput)
    # password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    gender = forms.ChoiceField(choices=((None, ''), ('F', 'Female'), ('M', 'Male'), ('O', 'Other')), required=False)
    # agree_toc = forms.BooleanField(required=True, label='I agree with the Terms and Conditions.')
    birthdate = forms.DateField(required=False)
    mobile_no = forms.CharField(required=False)
    emergency_mobile = forms.CharField(required=False)
    other_info = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Any other information you want us to know (for example, allergy)'}
        ),
        required=False
    )

    layout = Layout('username', 'email',
                    Row('password1', 'password2'),
                    Fieldset('Personal details',
                             Row('first_name', 'last_name'),
                             Row('gender', 'birthdate'),
                             Row('mobile_no', 'emergency_mobile'),
                             'other_info',
                             ))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'gender', 'birthdate',
                  'mobile_no', 'emergency_mobile', 'other_info']


class SignUpFormMedical(UserCreationForm):
    username = forms.CharField()
    email = forms.EmailField(label="Email Address")
    first_name = forms.CharField(required=True, label='Name')
    group_name = forms.ChoiceField(
        choices=(('doctor', 'Doctor'), ('pharmacy', 'Pharmacy'), ('diagnosis_center', 'Diagnosis Center')),
        required=True,
        label='Sign Up as'
    )
    address = forms.CharField(required=True)
    pin_code = forms.CharField(required=True)
    mobile_no = forms.CharField(required=True)
    emergency_mobile = forms.CharField(required=True)
    other_info = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'About your institution, add info regarding services you provide etc.'}
        ),
        required=False
    )
    license = forms.FileField(required=True)

    layout = Layout(
        'username', 'email',
        Row('password1', 'password2'),
        'group_name',
        Fieldset(
            'More Details',
            'first_name',
            'address',
            'pin_code',
            Row('mobile_no', 'emergency_mobile'),
            'other_info',
            'license',
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'mobile_no', 'emergency_mobile', 'address', 'pin_code', 'other_info', 'license']


class CreateUserForm(SignUpFormMedical):
    group_name = forms.ChoiceField(
        choices=(('doctor', 'Doctor'), ('pharmacy', 'Pharmacy'), ('diagnosis_center', 'Diagnosis Center')),
        required=True,
        label='Add this user as'
    )
    other_info = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'About the institution, add info regarding services it provides etc.'}
        ),
        required=False,
        label='About',
    )
    license = forms.FileField(required=False)

    layout = Layout(
        'username', 'email',
        Row('password1', 'password2'),
        'group_name',
        Fieldset(
            'More Details',
            'first_name',
            'address',
            'pin_code',
            Row('mobile_no', 'emergency_mobile'),
            'other_info',
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'mobile_no', 'emergency_mobile', 'address', 'pin_code', 'other_info']


class AddUserForm(forms.Form):
    user_name = forms.CharField(label='User Name', max_length=250)


class AddAdminForm(UserCreationForm):
    username = forms.CharField()
    email = forms.EmailField(label="Email Address")

    layout = Layout(
        'username', 'email',
        Row('password1', 'password2'),
    )

    class Meta:
        model = User
        fields = ['username', 'email']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'


CaseSearchForm = search_form_factory(Case.objects.all(), ['cases_short_name', 'cases_description'])


class CaseEditForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['cases_short_name', 'cases_description', 'is_active']


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['description', 'document', 'document_type']


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(label="Email Address")
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    gender = forms.ChoiceField(choices=((None, ''), ('F', 'Female'), ('M', 'Male'), ('O', 'Other')), required=False)
    birthdate = forms.DateField(required=False)
    mobile_no = forms.CharField(required=False)
    emergency_mobile = forms.CharField(required=False)
    other_info = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Any other information you want us to know (for example, allergy)'}
        ),
        required=False
    )

    layout = Layout('email',
                    Fieldset('Personal details',
                             Row('first_name', 'last_name'),
                             Row('gender', 'birthdate'),
                             Row('mobile_no', 'emergency_mobile'),
                             'other_info',
                             ))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'gender', 'birthdate',
                  'mobile_no', 'emergency_mobile', 'other_info']


class EditProfileFormMedical(forms.ModelForm):
    email = forms.EmailField(label="Email Address")
    first_name = forms.CharField(required=True, label='Name')
    mobile_no = forms.CharField(required=True)
    emergency_mobile = forms.CharField(required=True, label='Secondary Phone Number')
    address = forms.CharField(required=True)
    pin_code = forms.CharField(required=True)
    other_info = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Any other information you want us to know.'}
        ),
        required=False
    )

    layout = Layout('email',
                    Fieldset('More Details',
                             Row('first_name'),
                             Row('mobile_no', 'emergency_mobile'),
                             'address',
                             'pin_code',
                             'other_info',
                             ))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'mobile_no', 'emergency_mobile', 'address', 'pin_code', 'other_info']


class AddToClinicalNoteForm(forms.Form):
    appointment_id = forms.CharField(required=True, label='Appointment ID')
    clinical_note_field_text = forms.ChoiceField(
        choices=((v, k) for k, v in TEXT_TO_ID.items()),
        required=True, label='Clinical Note Field'
    )
