from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .models import Case, Comment, User, Document, MyLibrary, BookmarkedCases


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Personal info',
            {
                'fields': [
                    'address',
                    'birthdate',
                    'mobile_no',
                    'emergency_mobile',
                    'gender',
                    'other_info',
                    'license',
                ],
            }
        )
    )


# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Case)
admin.site.register(Comment)
admin.site.register(Document)
admin.site.register(MyLibrary)
admin.site.register(BookmarkedCases)
