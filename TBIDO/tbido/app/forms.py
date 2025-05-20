from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=[
            ('officer', 'Startup Founder'),
            ('member', 'Registered User'),  # Changed from 'player'
            # ('guest', 'Guest User'),
        ],
        widget=forms.Select(attrs={'placeholder': 'Select user type'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('user_type',)
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        }

class CohortFileForm(forms.ModelForm):
    class Meta:
        model = CohortFile
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'style': 'display: none;',
            })
        }

class CohortLinkForm(forms.ModelForm):
    class Meta:
        model = CohortLink
        fields = ('url', 'title', 'description')
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter URL'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description (optional)'}),
            }

class ProgramApplicationForm(forms.ModelForm):
    class Meta:
        model = ProgramApplication
        fields = [
            'first_name', 'last_name',
            'pitch_deck', 'business_plan',
            'supporting_document_1',
            'supporting_document_2',
            'supporting_document_3',
        ]

class ServiceInquiryForm(forms.ModelForm):
    PREFERRED_COMM_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('meeting_in_person', 'Meeting in person'),
        ('virtual_meeting', 'Virtual meeting'),
    ]

    preferred_communication = forms.MultipleChoiceField(
        choices=PREFERRED_COMM_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = ServiceInquiry
        fields = '__all__'
        widgets = {
            'service': forms.HiddenInput(),  # This hides it from Django’s {{ form.service }}
        }

class EventApplicationForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ['full_name', 'email']

class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
        fields = [
            'cohort_name', 'cohort_logo', 'short_description',
            'member1_email', 'member2_email', 'member3_email',
            'member4_email', 'member5_email'
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
        }

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = [
            'first_name',
            'last_name',
            'reason',
            'strengths',
            'weaknesses',
            'field_of_expertise',
            'supporting_document_1',
            'supporting_document_2',
            'supporting_document_3',
            'supporting_document_4',
            'supporting_document_5'
        ]

class CohortJoinForm(forms.Form):
    invite_code = forms.CharField(max_length=6, label='Enter Invite Code')

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'id_picture', 'age', 'employment', 'height', 'rank', 'employee_number', 'amount_paid']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Surname, First Name, M.I.'}),
            'employment': forms.TextInput(attrs={'placeholder': 'Type "Yes", "No", or "To Apply"'}),
            'height': forms.TextInput(attrs={'placeholder': 'E.g.: 5-11'}),
            'rank': forms.TextInput(attrs={'placeholder': 'Enter rank number (1-5)'}),
            'employee_number': forms.TextInput(attrs={'placeholder': 'Enter employee/student number'}),
            'amount_paid': forms.TextInput(attrs={'placeholder': 'IN PHP; (E.g.: 350)'}),
        }

# class OfficerForm(forms.ModelForm):
#     employmentDate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter officer employment date'}))

#     class Meta:
#         model = Officer
#         exclude = ['user', 'status', 'is_verified']

class OfficerForm(forms.ModelForm):
    employmentDate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3'}),
        label="Employment / Enrollment Date"
    )
    status = forms.ChoiceField(
        choices=Member.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        label="Status of Employment"
    )
    userCategory = forms.ChoiceField(
        choices=Member.USER_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        label="Select your User Category"
    )
    given_consent = forms.BooleanField(
        required=True,
        label="I give consent to provide my personal data."
    )
    IDPicture = forms.ImageField(label="Profile Picture (2x2)")
    pictureFullBody = forms.ImageField(label="Proof of Identification (Students ID, Employee ID, or any valid gov't ID)")

    class Meta:
        model = Officer
        exclude = ['user']
        fields = [
            'firstName', 'lastName', 'age', 'address', 'mobileNumber', 'email', 'IDPicture', 'pictureFullBody', 'userCategory',
            'courses', 'yearlevel', 'employmentDate', 'status', 'studentNumber', 'rank', 'affiliation',
            'occupation', 'companyName', 'salaryGrade', 'tin', 'given_consent'
        ]
        labels = {
            'firstName': 'First Name',
            'lastName': 'Last Name',
            'age': 'Age',
            'address': 'Address',
            'mobileNumber': 'Mobile Number',
            'email': 'Email Address',
            'courses': 'Course (if student) ',
            'yearlevel': 'Section & Year Level (student) or Years In Employment or Business (non-student)',
            'employmentDate': 'Employment or Enrollment Date',
            'status': 'Status of Employment',
            'studentNumber': 'Student Number (if applicable)',
            'rank': 'Academic Rank (if applicable)',
            'affiliation': 'Technology or Business Skillset',
            'occupation': 'Occupation or Job Title',
            'companyName': 'Affiliation (if student) or Company Name (if employed or entrepreneur)',
            'salaryGrade': 'Salary Grade (if employed)',
            'tin': 'Tax Identification Number (TIN)',
        }
    # employmentDate = forms.DateField(
    #     widget=forms.DateInput(attrs={'type': 'date'}),
    #     label="Employment / Enrollment Date"
    # )

    # status = forms.BooleanField(
    #     required=False,
    #     widget=forms.CheckboxInput(),
    #     label="Status"
    # )

    # given_consent = forms.BooleanField(
    #     required=True,
    #     label="I give consent to provide my personal data."
    # )

    # IDPicture = forms.ImageField(label="Profile Picture")
    # pictureFullBody = forms.ImageField(label="Proof of Identification (Students ID, Employee ID, or any valid gov't ID)")

    # class Meta:
    #     model = Officer
    #     exclude = ['user']
    #     fields = [
    #         'userCategory', 'firstName', 'lastName', 'mobileNumber', 'email', 'courses',
    #         'age', 'height', 'address', 'employmentDate', 'status',
    #         'IDPicture', 'pictureFullBody', 'affiliation', 'companyName',
    #         'rank', 'salaryGrade', 'tin', 'occupation', 'studentNumber',
    #         'given_consent'  # add here
    #     ]
    #     labels = {
    #         'firstName': 'First Name',
    #         'lastName': 'Last Name',
    #         'mobileNumber': 'Mobile Number',
    #         'userCategory': 'User Category',
    #         'email': 'Email you are using to access this web app',
    #     }

# class MemberForm(forms.ModelForm):
#     employmentDate = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         label="Employment / Enrollment Date"
#     )

#     status = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(),
#         label="Status"
#     )

#     given_consent = forms.BooleanField(
#         required=True,
#         label="I give consent to provide my personal data."
#     )

#     IDPicture = forms.ImageField(label="Profile Picture")
#     pictureFullBody = forms.ImageField(label="Proof of Identification (Students ID, Employee ID, or any valid gov't ID)")

#     class Meta:
#         model = Member
#         exclude = ['user']
#         fields = [
#             'userCategory', 'firstName', 'lastName', 'mobileNumber', 'email', 'courses',
#             'age', 'height', 'address', 'employmentDate', 'status',
#             'IDPicture', 'pictureFullBody', 'affiliation', 'companyName',
#             'rank', 'salaryGrade', 'tin', 'occupation', 'studentNumber',
#             'given_consent'  # add here
#         ]
#         labels = {
#             'firstName': 'First Name',
#             'lastName': 'Last Name',
#             'mobileNumber': 'Mobile Number',
#             'userCategory': 'User Category',
#         }

class MemberForm(forms.ModelForm):
    employmentDate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3'}),
        label="Employment / Enrollment Date"
    )
    status = forms.ChoiceField(
        choices=Member.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        label="Status of Employment"
    )
    userCategory = forms.ChoiceField(
        choices=Member.USER_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        label="Select your User Category"
    )
    given_consent = forms.BooleanField(
        required=True,
        label="I give consent to provide my personal data."
    )
    IDPicture = forms.ImageField(label="Profile Picture (2x2)")
    pictureFullBody = forms.ImageField(label="Proof of Identification (Students ID, Employee ID, or any valid gov't ID)")

    class Meta:
        model = Member
        exclude = ['user']
        fields = [
            'firstName', 'lastName', 'age', 'address', 'mobileNumber', 'email', 'IDPicture', 'pictureFullBody', 'userCategory',
            'courses', 'yearlevel', 'employmentDate', 'status', 'studentNumber', 'rank', 'affiliation',
            'occupation', 'companyName', 'salaryGrade', 'tin', 'given_consent'
        ]
        labels = {
            'firstName': 'First Name',
            'lastName': 'Last Name',
            'age': 'Age',
            'address': 'Address',
            'mobileNumber': 'Mobile Number',
            'email': 'Email Address',
            'courses': 'Course (if student) ',
            'yearlevel': 'Section & Year Level (student) or Years In Employment or Business (non-student)',
            'employmentDate': 'Employment or Enrollment Date',
            'status': 'Status of Employment',
            'studentNumber': 'Student Number (if applicable)',
            'rank': 'Academic Rank (if applicable)',
            'affiliation': 'Technology or Business Skillset',
            'occupation': 'Occupation or Job Title',
            'companyName': 'Affiliation (if student) or Company Name (if employed or entrepreneur)',
            'salaryGrade': 'Salary Grade (if employed)',
            'tin': 'Tax Identification Number (TIN)',
        }

class GuestForm(forms.ModelForm):
    employmentDate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3'}),
        label="Employment / Enrollment Date"
    )
    status = forms.ChoiceField(
        choices=Member.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        label="Status of Employment"
    )
    userCategory = forms.ChoiceField(
        choices=Member.USER_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        label="Select your User Category"
    )
    given_consent = forms.BooleanField(
        required=True,
        label="I give consent to provide my personal data."
    )
    IDPicture = forms.ImageField(label="Profile Picture (2x2)")
    pictureFullBody = forms.ImageField(label="Proof of Identification (Students ID, Employee ID, or any valid gov't ID)")

    class Meta:
        model = Guest
        exclude = ['user']
        fields = [
            'firstName', 'lastName', 'age', 'address', 'mobileNumber', 'email', 'IDPicture', 'pictureFullBody', 'userCategory',
            'courses', 'yearlevel', 'employmentDate', 'status', 'studentNumber', 'rank', 'affiliation',
            'occupation', 'companyName', 'salaryGrade', 'tin', 'given_consent'
        ]
        labels = {
            'firstName': 'First Name',
            'lastName': 'Last Name',
            'age': 'Age',
            'address': 'Address',
            'mobileNumber': 'Mobile Number',
            'email': 'Email Address',
            'courses': 'Course (if student) ',
            'yearlevel': 'Section & Year Level (student) or Years In Employment or Business (non-student)',
            'employmentDate': 'Employment or Enrollment Date',
            'status': 'Status of Employment',
            'studentNumber': 'Student Number (if applicable)',
            'rank': 'Academic Rank (if applicable)',
            'affiliation': 'Technology or Business Skillset',
            'occupation': 'Occupation or Job Title',
            'companyName': 'Affiliation (if student) or Company Name (if employed or entrepreneur)',
            'salaryGrade': 'Salary Grade (if employed)',
            'tin': 'Tax Identification Number (TIN)',
        }
    # employmentDate = forms.DateField(
    #     widget=forms.DateInput(attrs={'type': 'date'}),
    #     label="Employment / Enrollment Date"
    # )

    # status = forms.BooleanField(
    #     required=False,
    #     widget=forms.CheckboxInput(),
    #     label="Status"
    # )

    # given_consent = forms.BooleanField(
    #     required=True,
    #     label="I give consent to provide my personal data."
    # )

    # IDPicture = forms.ImageField(label="Profile Picture")
    # pictureFullBody = forms.ImageField(label="Proof of Identification (Students ID, Employee ID, or any valid gov't ID)")

    # class Meta:
    #     model = Guest
    #     exclude = ['user']
    #     fields = [
    #         'userCategory', 'firstName', 'lastName', 'mobileNumber', 'email', 'courses',
    #         'age', 'height', 'address', 'employmentDate', 'status',
    #         'IDPicture', 'pictureFullBody', 'affiliation', 'companyName',
    #         'rank', 'salaryGrade', 'tin', 'occupation', 'studentNumber',
    #         'given_consent'  # add here
    #     ]
    #     labels = {
    #         'firstName': 'First Name',
    #         'lastName': 'Last Name',
    #         'mobileNumber': 'Mobile Number',
    #         'userCategory': 'User Category',
    #     }

# class GuestForm(forms.ModelForm):
#     employmentDate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter guest employment date'}))

#     class Meta:
#         model = Guest
#         exclude = ['user', 'status', 'is_verified']

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['banner', 'sessionDateKey', 'sessionTimeKey', 'membershipTypeKey', 'sessionStatus', 'sessionMaterialCovered']
        exclude = ['officerKey']
        widgets = {
            'sessionDateKey': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter session date'}),
            'sessionTimeKey': forms.TimeInput(attrs={'type': 'time', 'placeholder': 'Enter session time'}),
        }

class OfficerEditForm(forms.ModelForm):
    class Meta:
        model = Officer
        exclude = ['user', 'officerKey']
        widgets = {
            'employmentDate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'custom-date-input'
            }),
            'IDPicture': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input'
            }),
            'pictureFullBody': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input'
            }),
            # For other text fields, add class in your template or via widget attrs if you want
        }

class MemberEditForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ['user', 'memberKey']
        widgets = {
            'employmentDate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'custom-date-input'
            }),
            'IDPicture': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input'
            }),
            'pictureFullBody': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input'
            }),
        }

class GuestEditForm(forms.ModelForm):
    class Meta:
        model = Guest
        exclude = ['user', 'guestKey']
        widgets = {
            'employmentDate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'custom-date-input'
            }),
            'IDPicture': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input'
            }),
            'pictureFullBody': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input'
            }),
        }

# class OfficerEditForm(forms.ModelForm):
#     class Meta:
#         model = Officer
#         exclude = ['user', 'officerKey']
#         widgets = {
#             'employmentDate': forms.DateInput(attrs={'type': 'date'}),
#             'IDPicture': forms.ClearableFileInput(),
#             'pictureFullBody': forms.ClearableFileInput(),
#         }

# class MemberEditForm(forms.ModelForm):
#     class Meta:
#         model = Member
#         exclude = ['user', 'memberKey']
#         widgets = {
#             'employmentDate': forms.DateInput(attrs={'type': 'date'}),
#             'IDPicture': forms.ClearableFileInput(),
#             'pictureFullBody': forms.ClearableFileInput(),
#         }

# class GuestEditForm(forms.ModelForm):
#     class Meta:
#         model = Guest
#         exclude = ['user', 'guestKey']
#         widgets = {
#             'employmentDate': forms.DateInput(attrs={'type': 'date'}),
#             'IDPicture': forms.ClearableFileInput(),
#             'pictureFullBody': forms.ClearableFileInput(),
#         }

class RequestJoinSessionForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['membershipTypeKey', 'requestDate']
        widgets = {
            'requestDate': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter request date'}),
        }

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('file', 'requirement')
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'requirement': forms.Select(attrs={'class': 'form-control'})
        }

class PendingRequestForm(forms.ModelForm):
    class Meta:
        model = PendingRequest
        fields = '__all__'
        widgets = {
            'approvalType': forms.Select(choices=[
                ('pending', 'Pending'),
                ('approved', 'Approved'),
            ]),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class CorrespondenceForm(forms.ModelForm):
    class Meta:
        model = Correspondence
        fields = ['subject', 'image', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'What is the subject of your inquiry?'}),
        }

# class PostAdminForm(forms.ModelForm):
#     content = forms.CharField(widget=CKEditorUploadingWidget())
#     class Meta:
#         model = Post
#         fields = '__all__'

# class VideoPostAdminForm(forms.ModelForm):
#     content = forms.CharField(widget=CKEditorUploadingWidget())
#     class Meta:
#         model = VideoPost
#         fields = '__all__'

# class SponsorPostAdminForm(forms.ModelForm):
#     content = forms.CharField(widget=CKEditorUploadingWidget())
#     class Meta:
#         model = SponsorPost
#         fields = '__all__'