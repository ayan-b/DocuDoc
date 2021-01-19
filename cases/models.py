import os

from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import AbstractUser
from ckeditor_uploader.fields import RichTextUploadingField

from cases import utils


class User(AbstractUser):
    GENDER_CHOICES = [
        ('F', 'Female'), ('M', 'Male'), ('O', 'Other')
    ]
    # required for patients and doctors
    gender = models.CharField(choices=GENDER_CHOICES, blank=True, max_length=1, null=True)
    # only required for patients
    birthdate = models.DateField(blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)
    emergency_mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True)
    pin_code = models.CharField(blank=True, max_length=6)
    # not required for patients
    license = models.FileField(blank=True)
    other_info = models.TextField(blank=True, null=True)
    # drchrono tokens
    access_token = models.CharField(max_length=40, blank=True, null=True)
    refresh_token = models.CharField(max_length=40, blank=True, null=True)
    expires_in = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def get_group(self):
        return utils.get_group(self)

    def __str__(self):
        return self.username


class Case(models.Model):
    users = models.ManyToManyField(User, related_name='cases')
    cases_short_name = models.CharField('Short Name', max_length=200)
    cases_description = RichTextUploadingField('Description')
    patient_username = models.CharField('Patient User Name', max_length=30)
    created_date = models.DateTimeField('Created at', auto_now_add=True, editable=False)
    updated_date = models.DateTimeField('Updated at', auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['updated_date']

    def __str__(self):
        return '{0} {1} for {2} active {3}'.format(self.cases_short_name, str(self.updated_date),
                                                   str(self.patient_username), str(self.is_active))


class Comment(models.Model):
    TREATMENT = 1
    PRESCRIPTION = 2
    DIAGNOSIS = 3
    COMMENT_CHOICES = (
        (TREATMENT, 'Treatment'),
        (PRESCRIPTION, 'Prescription'),
        (DIAGNOSIS, 'Diagnosis'),
    )

    # comment can be made by one user only
    user = models.ForeignKey(User, max_length=30, on_delete=CASCADE, editable=False)
    case = models.ForeignKey(Case, on_delete=CASCADE, related_name='comments')
    created_date = models.DateTimeField('Created at', auto_now_add=True, editable=False)
    updated_date = models.DateTimeField('Updated at', auto_now_add=True, editable=False)
    content = RichTextUploadingField('Content')
    # for treatment comments, etc.
    comment_type = models.PositiveSmallIntegerField(
        choices=COMMENT_CHOICES,
        default=TREATMENT,
    )

    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return str(self.case.id) + ' ' + self.content


def get_upload_path(instance, filename):
    return 'cases/case_{0}/{1}'.format(instance.case.id, filename)


class Document(models.Model):
    TREATMENT = 1
    PRESCRIPTION = 2
    DIAGNOSIS = 3
    COMMENT_CHOICES = (
        (TREATMENT, 'Treatment'),
        (PRESCRIPTION, 'Prescription'),
        (DIAGNOSIS, 'Diagnosis'),
    )
    user = models.ForeignKey(User, max_length=30, on_delete=CASCADE, editable=False)
    case = models.ForeignKey(Case, on_delete=CASCADE, related_name='documents')
    created_date = models.DateTimeField('Created at', auto_now_add=True, editable=False)
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=get_upload_path)
    # for treatment documents, etc.
    document_type = models.PositiveSmallIntegerField(
        choices=COMMENT_CHOICES,
        default=TREATMENT,
    )

    class Meta:
        ordering = ['created_date']

    def filename(self):
        return os.path.basename(self.document.name)

    def is_image(self):
        return self.filename().endswith(('jpg', 'png', 'jpeg'))

    def __str__(self):
        return str(self.case.id) + ' ' + self.description


class MyLibrary(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    document = models.ForeignKey(Document, on_delete=CASCADE)

    class Meta:
        verbose_name_plural = 'myLibraries'

    def __str__(self):
        return str(self.user) + ' ' + str(self.document)


class BookmarkedCase(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    case = models.ForeignKey(Case, on_delete=CASCADE)

    class Meta:
        verbose_name_plural = 'bookmarked Cases'

    def __str__(self):
        return str(self.user) + ' ' + str(self.case)
