from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django_prose_editor.fields import ProseEditorField
from django.utils.html import mark_safe
from pytube import YouTube
import random
import string

class Program(models.Model):
    PROGRAM_TYPES = [
        ('Incubator', 'Incubator'),
        ('Accelerator', 'Accelerator'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open for Applications'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=255, null=True, blank=True)
    banner = models.ImageField(upload_to='program_banners/', null=True, blank=True)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES, null=True, blank=True)
    application_status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    key_benefits = ProseEditorField(null=True, blank=True)
    eligibility_criteria = ProseEditorField(null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    details = ProseEditorField(null=True, blank=True)

    def __str__(self):
        return self.title

class ProgramApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey('Program', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    pitch_deck = models.FileField(upload_to='applications/pitch_decks/', null=True, blank=True)
    business_plan = models.FileField(upload_to='applications/business_plans/', null=True, blank=True)
    supporting_document_1 = models.FileField(upload_to='applications/support_docs/', null=True, blank=True)
    supporting_document_2 = models.FileField(upload_to='applications/support_docs/', null=True, blank=True)
    supporting_document_3 = models.FileField(upload_to='applications/support_docs/', null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.program.title}"

class Event(models.Model):
    EVENT_TYPES = [
        ('webinar', 'Webinar'),
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
        ('seminar', 'Seminar'),
    ]

    title = models.CharField(max_length=255, null=True, blank=True)
    speaker_name = models.CharField(max_length=255, null=True, blank=True)
    speaker_bio = models.TextField(null=True, blank=True)
    speaker_photo = models.ImageField(upload_to='speaker_photos/', null=True, blank=True)
    agenda = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)
    event_time = models.TimeField(null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, null=True, blank=True)
    capacity = models.PositiveIntegerField(default=50, null=True, blank=True)
    banner = models.ImageField(upload_to='event_banners/', null=True, blank=True)
    is_past = models.BooleanField(default=False)
    recording_link = models.URLField(blank=True, null=True)
    feedback_link = models.URLField(blank=True, null=True)

    def spots_left(self):
        return self.capacity - self.applications.count()

    def __str__(self):
        return self.title


class EventApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, related_name='applications', on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

class ServiceInquiry(models.Model):
    service = models.CharField(max_length=255, blank=True, null=True)
    # Section 1: Personal & Contact Data
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    startup_company_name = models.CharField(max_length=255, blank=True, null=True)

    # Section 2: Inquiry Details
    tbido_section = models.CharField(max_length=255, blank=True, null=True)
    service = models.CharField(max_length=255, blank=True, null=True)
    subject_of_inquiry = models.CharField(max_length=255, blank=True, null=True)
    inquiry_description = models.TextField(blank=True, null=True)

    # Section 3
    previously_interacted = models.BooleanField(default=False)
    preferred_communication = models.CharField(max_length=255, blank=True, null=True)  # Will store comma-separated choices
    supporting_documents = models.FileField(upload_to='supporting_docs/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry from {self.full_name or 'Unknown'}"

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Cohort(models.Model):
    cohort_name = models.CharField(max_length=255, null=True, blank=True)
    cohort_creator = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    cohort_logo = models.ImageField(upload_to='cohort_logos/', null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    member1_email = models.EmailField(null=True, blank=True)
    member2_email = models.EmailField(null=True, blank=True)
    member3_email = models.EmailField(null=True, blank=True)
    member4_email = models.EmailField(null=True, blank=True)
    member5_email = models.EmailField(null=True, blank=True)

    # Hidden
    member6_email = models.EmailField(null=True, blank=True)
    member7_email = models.EmailField(null=True, blank=True)
    member8_email = models.EmailField(null=True, blank=True)

class CohortMember(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='cohort_memberships')
    member_number = models.PositiveIntegerField(null=True, blank=True)  # 1 to 5
    member = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    member_email = models.EmailField(null=True, blank=True)
    invite_code = models.CharField(max_length=6, default=generate_invite_code, unique=True)

def user_file_path(instance, filename):
    return f'cohort_files/{instance.cohort.id}/{filename}'

class CohortFile(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='cohort_files/', null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.filename} - {self.cohort.cohort_name}"

class CohortLink(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='links', null=True, blank=True)
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    shared_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.cohort.cohort_name}"

class Inquiry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    reason = models.TextField()
    strengths = models.TextField()
    weaknesses = models.TextField()
    field_of_expertise = models.TextField()
    supporting_document_1 = models.FileField(upload_to='inquiries/', blank=True, null=True)
    supporting_document_2 = models.FileField(upload_to='inquiries/', blank=True, null=True)
    supporting_document_3 = models.FileField(upload_to='inquiries/', blank=True, null=True)
    supporting_document_4 = models.FileField(upload_to='inquiries/', blank=True, null=True)
    supporting_document_5 = models.FileField(upload_to='inquiries/', blank=True, null=True)

    def __str__(self):
        return f"Inquiry from {self.first_name} {self.last_name}"

class Candidate(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    id_picture = models.ImageField(upload_to='candidate_pics/')
    age = models.IntegerField(null=True, blank=True)
    employment = models.CharField(max_length=255, null=True, blank=True)
    height = models.CharField(max_length=255, null=True, blank=True)
    rank = models.CharField(max_length=255, null=True, blank=True)
    employee_number = models.IntegerField(null=True, blank=True)
    amount_paid = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Logo(models.Model):
    image = models.ImageField(upload_to='tbido_pylon_logo/')

class PartnerLogo(models.Model):
    image = models.ImageField(upload_to='tbido_partner_logos/')

class Officer(models.Model):
    USER_CATEGORIES = [
        ('Student', 'Student'),
        ('Employee', 'Employee'),
        ('Business Owner', 'Business Owner'),
        ('Consulting Professional', 'Consulting Professional'),
    ]

    STATUS_CHOICES = [
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
        ('Temporary', 'Temporary'),
        ('Part-time', 'Part-time'),
        ('Designee', 'Designee'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    officerKey = models.AutoField(primary_key=True)

    lastName = models.CharField(max_length=50)
    firstName = models.CharField(max_length=50)
    mobileNumber = models.PositiveBigIntegerField()
    email = models.EmailField()
    employmentDate = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)

    IDPicture = models.ImageField(upload_to='member_id_pictures/')
    pictureFullBody = models.ImageField(upload_to='member_full_body_pictures/')

    occupation = models.CharField(max_length=50, blank=True, null=True)
    companyName = models.CharField(max_length=50, blank=True, null=True) # Affiliation

    # Modified Fields
    affiliation = models.TextField(blank=True, null=True)  # Will act as Technology or Business Skillset
    yearlevel = models.CharField(max_length=3, blank=True, null=True)  # Will act as Year Level or Years in Business

    age = models.PositiveBigIntegerField()
    salaryGrade = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=100)

    # studentNumber = models.IntegerField(blank=True, null=True)
    studentNumber = models.CharField(max_length=255, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)  # Academic Rank
    tin = models.CharField(max_length=12, blank=True, null=True)

    is_verified = models.BooleanField(default=True)
    courses = models.TextField(blank=True, null=True)
    given_consent = models.BooleanField(default=False)

    userCategory = models.CharField(max_length=30, choices=USER_CATEGORIES, blank=True, null=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName}'s Member Profile"
    # USER_CATEGORIES = [
    #     ('Student', 'Student'),
    #     ('Employee', 'Employee'),
    #     ('Business Owner', 'Business Owner'),
    #     ('Consulting Professional', 'Consulting Professional'),
    # ]

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    # officerKey = models.AutoField(primary_key=True)

    # lastName = models.CharField(max_length=50)
    # firstName = models.CharField(max_length=50)
    # mobileNumber = models.PositiveBigIntegerField()
    # email = models.EmailField()
    # employmentDate = models.DateField(blank=True, null=True)
    # status = models.BooleanField(default=False)
    # IDPicture = models.ImageField(upload_to='officer_id_pictures/')
    # pictureFullBody = models.ImageField(upload_to='officer_full_body_pictures/')
    # occupation = models.CharField(max_length=20, blank=True, null=True)
    # companyName = models.CharField(max_length=25, blank=True, null=True)
    # affiliation = models.CharField(max_length=30, blank=True, null=True)
    # age = models.PositiveBigIntegerField()
    # height = models.CharField(max_length=3)
    # salaryGrade = models.IntegerField(blank=True, null=True)
    # address = models.CharField(max_length=70)
    # studentNumber = models.IntegerField(blank=True, null=True)
    # rank = models.IntegerField(blank=True, null=True)
    # tin = models.CharField(max_length=12, blank=True, null=True)
    # is_verified = models.BooleanField(default=True)
    # courses = models.TextField(blank=True, null=True)
    # given_consent = models.BooleanField(default=False)

    # userCategory = models.CharField(max_length=30, choices=USER_CATEGORIES, blank=True, null=True)

    # def __str__(self):
    #     return f"{self.firstName} {self.lastName}'s Officer Profile"

# class Member(models.Model):
#     USER_CATEGORIES = [
#         ('Student', 'Student'),
#         ('Employee', 'Employee'),
#         ('Business Owner', 'Business Owner'),
#         ('Consulting Professional', 'Consulting Professional'),
#     ]

#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     memberKey = models.AutoField(primary_key=True)

#     lastName = models.CharField(max_length=50)
#     firstName = models.CharField(max_length=50)
#     mobileNumber = models.PositiveBigIntegerField()
#     email = models.EmailField()
#     employmentDate = models.DateField(blank=True, null=True)
#     status = models.BooleanField(default=False)
#     IDPicture = models.ImageField(upload_to='member_id_pictures/')
#     pictureFullBody = models.ImageField(upload_to='member_full_body_pictures/')
#     occupation = models.CharField(max_length=20, blank=True, null=True)
#     companyName = models.CharField(max_length=25, blank=True, null=True)
#     affiliation = models.CharField(max_length=30, blank=True, null=True)
#     age = models.PositiveBigIntegerField()
#     height = models.CharField(max_length=3)
#     salaryGrade = models.IntegerField(blank=True, null=True)
#     address = models.CharField(max_length=70)
#     studentNumber = models.IntegerField(blank=True, null=True)
#     rank = models.IntegerField(blank=True, null=True)
#     tin = models.CharField(max_length=12, blank=True, null=True)
#     is_verified = models.BooleanField(default=True)
#     courses = models.TextField(blank=True, null=True)
#     given_consent = models.BooleanField(default=False)

#     userCategory = models.CharField(max_length=30, choices=USER_CATEGORIES, blank=True, null=True)

#     def __str__(self):
#         return f"{self.firstName} {self.lastName}'s Member Profile"

class Member(models.Model):
    USER_CATEGORIES = [
        ('Student', 'Student'),
        ('Employee', 'Employee'),
        ('Business Owner', 'Business Owner'),
        ('Consulting Professional', 'Consulting Professional'),
    ]

    STATUS_CHOICES = [
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
        ('Temporary', 'Temporary'),
        ('Part-time', 'Part-time'),
        ('Designee', 'Designee'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    memberKey = models.AutoField(primary_key=True)

    lastName = models.CharField(max_length=50)
    firstName = models.CharField(max_length=50)
    mobileNumber = models.PositiveBigIntegerField()
    email = models.EmailField()
    employmentDate = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)

    IDPicture = models.ImageField(upload_to='member_id_pictures/')
    pictureFullBody = models.ImageField(upload_to='member_full_body_pictures/')

    occupation = models.CharField(max_length=50, blank=True, null=True)
    companyName = models.CharField(max_length=50, blank=True, null=True)

    # Modified Fields
    affiliation = models.TextField(blank=True, null=True)  # Will act as Technology or Business Skillset
    yearlevel = models.CharField(max_length=3, blank=True, null=True)  # Will act as Year Level or Years in Business

    age = models.PositiveBigIntegerField()
    salaryGrade = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=100)

    # studentNumber = models.IntegerField(blank=True, null=True)
    studentNumber = models.CharField(max_length=255, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)  # Academic Rank
    tin = models.CharField(max_length=12, blank=True, null=True)

    is_verified = models.BooleanField(default=True)
    courses = models.TextField(blank=True, null=True)
    given_consent = models.BooleanField(default=False)

    userCategory = models.CharField(max_length=30, choices=USER_CATEGORIES, blank=True, null=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName}'s Member Profile"

class Guest(models.Model):
    USER_CATEGORIES = [
        ('Student', 'Student'),
        ('Employee', 'Employee'),
        ('Business Owner', 'Business Owner'),
        ('Consulting Professional', 'Consulting Professional'),
    ]

    STATUS_CHOICES = [
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
        ('Temporary', 'Temporary'),
        ('Part-time', 'Part-time'),
        ('Designee', 'Designee'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    guestKey = models.AutoField(primary_key=True)

    lastName = models.CharField(max_length=50)
    firstName = models.CharField(max_length=50)
    mobileNumber = models.PositiveBigIntegerField()
    email = models.EmailField()
    employmentDate = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)

    IDPicture = models.ImageField(upload_to='member_id_pictures/')
    pictureFullBody = models.ImageField(upload_to='member_full_body_pictures/')

    occupation = models.CharField(max_length=50, blank=True, null=True)
    companyName = models.CharField(max_length=50, blank=True, null=True)

    # Modified Fields
    affiliation = models.TextField(blank=True, null=True)  # Will act as Technology or Business Skillset
    yearlevel = models.CharField(max_length=3, blank=True, null=True)  # Will act as Year Level or Years in Business

    age = models.PositiveBigIntegerField()
    salaryGrade = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=100)

    # studentNumber = models.IntegerField(blank=True, null=True)
    studentNumber = models.CharField(max_length=255, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)  # Academic Rank
    tin = models.CharField(max_length=12, blank=True, null=True)

    is_verified = models.BooleanField(default=True)
    courses = models.TextField(blank=True, null=True)
    given_consent = models.BooleanField(default=False)

    userCategory = models.CharField(max_length=30, choices=USER_CATEGORIES, blank=True, null=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName}'s Member Profile"
    # USER_CATEGORIES = [
    #     ('Student', 'Student'),
    #     ('Employee', 'Employee'),
    #     ('Business Owner', 'Business Owner'),
    #     ('Consulting Professional', 'Consulting Professional'),
    # ]

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    # guestKey = models.AutoField(primary_key=True)

    # lastName = models.CharField(max_length=50)
    # firstName = models.CharField(max_length=50)
    # mobileNumber = models.PositiveBigIntegerField()
    # email = models.EmailField()
    # employmentDate = models.DateField(blank=True, null=True)
    # status = models.BooleanField(default=False)
    # IDPicture = models.ImageField(upload_to='guest_id_pictures/')
    # pictureFullBody = models.ImageField(upload_to='guest_full_body_pictures/')
    # occupation = models.CharField(max_length=20, blank=True, null=True)
    # companyName = models.CharField(max_length=25, blank=True, null=True)
    # affiliation = models.CharField(max_length=30, blank=True, null=True)
    # age = models.PositiveBigIntegerField()
    # height = models.CharField(max_length=3)
    # salaryGrade = models.IntegerField(blank=True, null=True)
    # address = models.CharField(max_length=70)
    # studentNumber = models.IntegerField(blank=True, null=True)
    # rank = models.IntegerField(blank=True, null=True)
    # tin = models.CharField(max_length=12, blank=True, null=True)
    # is_verified = models.BooleanField(default=True)
    # courses = models.TextField(blank=True, null=True)
    # given_consent = models.BooleanField(default=False)

    # userCategory = models.CharField(max_length=30, choices=USER_CATEGORIES, blank=True, null=True)

    # def __str__(self):
    #     return f"{self.firstName} {self.lastName}'s Guest Profile"

class membershipType(models.Model):
    membershipTypeKey = models.AutoField(primary_key=True)
    membershipTypeName = models.CharField(max_length=10)
    membershipTypeDescription = models.CharField(max_length=20)

    def __str__(self):
        return self.membershipTypeName

class Request(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    requestKey = models.AutoField(primary_key=True)
    membershipTypeKey = models.ForeignKey('membershipType', on_delete=models.CASCADE)
    requestDate = models.DateField()
    requestStatus = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )

    memberKey = models.ForeignKey('Member', on_delete=models.CASCADE)
    sessionKey = models.ForeignKey('Session', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('memberKey', 'sessionKey')

class requestNote(models.Model):
    requestNoteKey = models.AutoField(primary_key=True)
    requestKey = models.ForeignKey('Request', on_delete=models.CASCADE)
    requestNoteText = models.CharField(max_length=100)

class Session(models.Model):
    STATUS_CHOICES = [
        ('null', 'Null'),
        ('c', 'C'),
        ('ns', 'NS'),
    ]
    banner = models.ImageField(upload_to='banner_img/', blank=True, null=True)
    sessionKey = models.AutoField(primary_key=True)
    sessionDateKey = models.DateField()
    sessionTimeKey = models.TimeField()
    # officerKey = models.ForeignKey('Officer', on_delete=models.CASCADE)
    membershipTypeKey = models.ForeignKey('membershipType', on_delete=models.CASCADE)
    approved_members = models.ManyToManyField('Member', through='Request', related_name='sessions')
    sessionStatus = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='null'
    )
    officerKey = models.ForeignKey('Officer', on_delete=models.CASCADE, related_name='sessions')
    sessionMaterialCovered = models.TextField()

    def __str__(self):
        return f"{self.sessionMaterialCovered}"

class Document(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    content = models.TextField()  # Store document content
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_documents")

    def __str__(self):
        return f"{self.title} - {self.session.sessionMaterialCovered}"

class officer_MembershipType(models.Model):
    officerKey = models.ForeignKey('Officer', on_delete=models.CASCADE)
    membershipTypeKey = models.ForeignKey('membershipType', on_delete=models.CASCADE)

class member_MembershipType(models.Model):
    memberKey = models.ForeignKey('Member', on_delete=models.CASCADE)
    membershipTypeKey = models.ForeignKey('membershipType', on_delete=models.CASCADE)
    memberMembershipTypeQuarter = models.BigIntegerField(primary_key=True)

class FacultyRank(models.Model):
    FacultyRankKey = models.CharField(max_length=20,primary_key=True)
    FacultyRankDescription = models.CharField(max_length=30)

    def __str__(self):
        return self.FacultyRankKey


class Announcement(models.Model):
    title = models.CharField(max_length=200, help_text="Enter the title of the announcement")
    description = models.TextField(help_text="Enter the description of the announcement")
    picture = models.ImageField(upload_to='announcement_pictures/', blank=True, help_text="Upload an image for the announcement")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order by most recent first

    def __str__(self):
        return self.title

class Invites(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    invite_code = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Invite {self.invite_code} for Session {self.session.sessionKey}"

    def is_valid(self):
        if self.used:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

class PendingRequest(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    sessionKey = models.ForeignKey(Session, on_delete=models.CASCADE)
    requestDate = models.DateTimeField(auto_now_add=True)
    approvalType = models.CharField(max_length=20, default='pending')

    def __str__(self):
        # Access the session date and time through the sessionKey relationship
        return f"{self.member.firstName} {self.member.lastName} - {self.sessionKey.sessionDateKey} {self.sessionKey.sessionTimeKey}"


class ApprovedRequest(models.Model):
    pendingRequest = models.OneToOneField(PendingRequest, on_delete=models.CASCADE)
    approvalDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pendingRequest.member.firstName} {self.pendingRequest.member.lastName} - {self.pendingRequest.sessionKey.sessionDateKey} {self.pendingRequest.sessionKey.sessionTimeKey}"

class Advisory(models.Model):
    header = models.CharField(max_length=255)
    task = ProseEditorField(null=True, blank=True)
    details = ProseEditorField(null=True, blank=True)
    session = models.ManyToManyField('Session')
    initial_date = models.DateTimeField()
    deadline = models.DateTimeField()
    # calendar_plot_img = models.ImageField(upload_to='advisory/calendar/', null=True, blank=True)
    # gantt_plot_img = models.ImageField(upload_to='advisory/gantt/', null=True, blank=True)

    def __str__(self):
        return f"{self.header} - {self.initial_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name_plural = "Advisories"
        ordering = ['-initial_date']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# class Picture(models.Model):
#     image = models.ImageField(upload_to='blog_pictures/')
#     post = models.OneToOneField('Post', related_name='related_picture', on_delete=models.CASCADE)

#     def __str__(self):
#         return f'{self.post.title} - Main Picture'

class Post(models.Model):
    title = models.CharField(max_length=255)
    related_picture = models.ImageField(upload_to='post_picture/', blank=True, null=True)
    content = ProseEditorField()
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Misc(models.Model):
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='misc/', blank=True, null=True)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post',)

class VideoPost(models.Model):
    id = models.AutoField(primary_key=True)
    Date = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to="video_files/", blank=True, null=True)
    banner = models.ImageField(upload_to='videopost_pics/', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    youtube_link = models.URLField(blank=True, null=True)
    # content = ProseEditorField()

# class FavoriteVideo(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     video_post = models.ForeignKey(VideoPost, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'video_post',)

class SponsorPost(models.Model):
    id = models.AutoField(primary_key=True)
    Date = models.DateTimeField(auto_now_add=True)
    banner = models.ImageField(upload_to='sponsorpost_pics/', blank=True, null=True)
    title = models.CharField(max_length=255)
    content = ProseEditorField()

# class FavoriteSponsor(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     sponsor_post = models.ForeignKey(SponsorPost, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'sponsor_post',)

# def save_video_to_specific_folder(instance, filename):
#     fs = FileSystemStorage(location='videos')  # Specify your desired folder name
#     base_name, file_extension = os.path.splitext(filename)
#     new_filename = f"{instance.pk}_{base_name}{file_extension}"
#     return fs.save(new_filename, instance.file)

# class Post(models.Model):
#     title = models.CharField(max_length=255)
#     subtitle = models.CharField(max_length=255)
#     content = FroalaField()
#     tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         if self.content.has_files():
#             for file in self.content.get_files():
#                 if file.type.startswith('video'):
#                     save_video_to_specific_folder(self, file.name)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.title

class MentoringSession(models.Model):  # Formerly GameResult
    cohort_name = models.CharField(max_length=100)  # Replaces main_team_name
    mentor_name = models.CharField(max_length=100)  # Replaces opposing_team_name
    session_rating = models.IntegerField()  # New field for 1-10 rating
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Mentoring Session: {self.cohort_name} with {self.mentor_name}"


class MentoringSchedule(models.Model):
    SESSION_TYPE_CHOICES = [
        ('Mentorship', 'Mentorship'),
        ('Learning', 'Learning'),
    ]
    SESSION_KIND_CHOICES = [
        ('Technology', 'Technology'),
        ('Business', 'Business'),
    ]

    session_type = models.CharField(max_length=255, choices=SESSION_TYPE_CHOICES, null=True, blank=True)
    session_kind = models.CharField(max_length=255, choices=SESSION_KIND_CHOICES, null=True, blank=True)
    session_topic = models.CharField(max_length=255, null=True, blank=True)
    session_time = models.DateTimeField(null=True, blank=True)
    cohort_name = models.CharField(max_length=255, null=True, blank=True)
    mentor_name = models.CharField(max_length=255, null=True, blank=True)
    mentor_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"Mentoring Session: {self.session_topic} on {self.session_time}"

# class EventSchedule(models.Model):
#     event_name = models.CharField(max_length=255)
#     event_time_start = models.DateTimeField()
#     event_time_end = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.event_name} on {self.event_time_start}"

class ProgressTracking(models.Model):  # Formerly TeamStandings
    picture = models.ImageField(upload_to="progress_tracking_img/", blank=True, null=True)
    cohort_name = models.CharField(max_length=255)  # Replaces team_name
    learning_sessions_attended = models.IntegerField()  # Replaces points
    mentoring_sessions_completed = models.IntegerField()  # Replaces wins
    submitted_requirements = models.IntegerField()  # Replaces losses
    progress_percentage = models.IntegerField()  # Replaces points_scored
    challenges_faced = models.IntegerField()  # Replaces points_conceded

    def __str__(self):
        return self.cohort_name

class TopPerformers(models.Model):  # Formerly TopFour
    progress_tracking = models.OneToOneField(ProgressTracking, on_delete=models.CASCADE)
    ranking = models.IntegerField()

    def __str__(self):
        return f"{self.progress_tracking.cohort_name} - Rank {self.ranking}"

class PlayerStatistic(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    player_picture = models.ImageField(upload_to='player_pictures/')
    team_picture = models.ImageField(upload_to='team_logos/')
    vs_team = models.CharField(max_length=100)
    points = models.IntegerField()
    field_goals = models.IntegerField()
    free_throws = models.IntegerField()
    assists = models.IntegerField()
    rebounds = models.IntegerField()
    steals = models.IntegerField()
    blocks = models.IntegerField()
    turnovers = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Message(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."

class ForumMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"

class CohortMessage(models.Model):
    cohort = models.ForeignKey('Cohort', related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.cohort.cohort_name}"

    class Meta:
        ordering = ['created_at']

class ForumReply(models.Model):
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.responder.username}"

class CohortPublicForumMessage(models.Model):
    addressed_cohort = models.ForeignKey('Cohort', related_name='cohort_public_forum_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    replies = models.ManyToManyField(ForumReply, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.addressed_cohort.cohort_name}"

class HelpdeskMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_helpdesk_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_helpdesk_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_from_admin = models.BooleanField(default=False)  # Distinguish messages

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.message[:30]}"

class Requirement(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='requirements', blank=True, null=True)
    req_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    desc = ProseEditorField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    files = models.ManyToManyField('File', blank=True, related_name='requirements')  # Added related_name

    def __str__(self):
        return self.name

class File(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='files', blank=True, null=True)
    file_id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='session_files/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    requirement = models.ForeignKey(Requirement, on_delete=models.SET_NULL, null=True, related_name='file_set')  # Added related_name
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.file.name} by {self.uploaded_by.username}"

class Season(models.Model):
    title = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField()

    def __str__(self):
        return f"{self.title} ({self.start_year}-{self.end_year})"

class SeasonGrouping(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    mentoring_schedules = models.ManyToManyField(MentoringSchedule, blank=True, null=True)
    mentoring_sessions = models.ManyToManyField(MentoringSession)
    progress_tracking = models.ManyToManyField(ProgressTracking)

    def __str__(self):
        return self.season.title

class TopContributor(models.Model):  # Formerly BestPlayer
    member_name = models.CharField(max_length=40, blank=True, null=True)
    member_picture = models.ImageField(upload_to='best_member_photos/', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, blank=True, null=True)
    mentoring_session = models.ForeignKey(MentoringSession, on_delete=models.CASCADE, blank=True, null=True)
    role = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.member_name

class ExpertiseTag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expert(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    profile = models.ImageField(upload_to='expert_profiles/')
    job_title = models.CharField(max_length=255)
    job_description = ProseEditorField()
    expertise = models.ManyToManyField(ExpertiseTag, related_name='experts')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    other_contacts = ProseEditorField()

    def __str__(self):
        return self.name

class Resource(models.Model):
    name = models.CharField(max_length=255)
    description = ProseEditorField()
    experts = models.ManyToManyField(Expert, related_name='resources')

    def __str__(self):
        return self.name

class Correspondence(models.Model):
    subject = models.CharField(max_length=255)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    image = models.ImageField(upload_to='correspondence_images/', blank=True, null=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject