from django.contrib import admin
from .models import *
from .forms import *
import random
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.http import JsonResponse
import plotly.graph_objects as go
from datetime import datetime
import json
from .models import Advisory, Session
from plotly.offline import plot
import plotly.express as px
import pandas as pd
from django.core.files.base import ContentFile
import io
import base64
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

# Basic registrations
admin.site.register(Candidate)
admin.site.register(Officer)
admin.site.register(Member)
admin.site.register(membershipType)
admin.site.register(Request)
admin.site.register(requestNote)
admin.site.register(Session)
admin.site.register(Document)
admin.site.register(Misc)
admin.site.register(Cohort)
admin.site.register(CohortMember)
admin.site.register(Inquiry)
admin.site.register(CohortPublicForumMessage)
admin.site.register(ForumReply)
admin.site.register(CohortMessage)
admin.site.register(Event)
admin.site.register(EventApplication)
admin.site.register(ServiceInquiry)

admin.site.register(CohortLink)
admin.site.register(CohortFile)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'program_type', 'application_status', 'application_deadline')
    search_fields = ('title', 'program_type')

@admin.register(ProgramApplication)
class ProgramApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'program', 'submitted_at')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('experts',)

@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_title', 'email', 'phone_number')
    filter_horizontal = ('expertise',)

@admin.register(ExpertiseTag)
class ExpertiseTagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient', 'timestamp')

admin.site.register(Advisory)

# Mentoring Session Admin
class MentoringSessionAdmin(admin.ModelAdmin):
    list_display = ('cohort_name', 'mentor_name', 'session_rating', 'date')
    search_fields = ('cohort_name', 'mentor_name')
    ordering = ('-date',)

admin.site.register(MentoringSession, MentoringSessionAdmin)

# Mentoring Schedule Admin
@admin.register(MentoringSchedule)
class MentoringScheduleAdmin(admin.ModelAdmin):
    list_display = ('session_topic', 'session_type', 'session_kind', 'session_time', 'mentor_name')
    list_filter = ('session_type', 'session_kind')
    search_fields = ('session_topic', 'mentor_name', 'cohort_name')

# Progress Tracking Admin
class ProgressTrackingAdmin(admin.ModelAdmin):
    list_display = ('cohort_name', 'learning_sessions_attended', 'mentoring_sessions_completed',
                   'submitted_requirements', 'progress_percentage')
    search_fields = ('cohort_name',)
    ordering = ('-progress_percentage',)

admin.site.register(ProgressTracking, ProgressTrackingAdmin)

# Top Performers Admin
class TopPerformersAdmin(admin.ModelAdmin):
    list_display = ('progress_tracking', 'ranking')
    ordering = ('ranking',)

admin.site.register(TopPerformers, TopPerformersAdmin)

# Best Member Admin
class TopContributorAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'member_picture', 'season', 'mentoring_session', 'role')
    search_fields = ('member_name', 'season__title')
    ordering = ('-season__start_year',)

admin.site.register(TopContributor, TopContributorAdmin)

# Pending Request Admin
class PendingRequestAdmin(admin.ModelAdmin):
    form = PendingRequestForm
    list_display = ('member', 'sessionKey', 'requestDate', 'approvalType')
    list_filter = ('approvalType',)
    search_fields = ('member__firstName', 'sessionKey__sessionMaterialCovered')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.approvalType == 'approved':
            ApprovedRequest.objects.create(pendingRequest=obj)

admin.site.register(PendingRequest, PendingRequestAdmin)

# Approved Request Admin
class ApprovedRequestAdmin(admin.ModelAdmin):
    list_display = ('pendingRequest', 'approvalDate')
    ordering = ('-approvalDate',)

admin.site.register(ApprovedRequest, ApprovedRequestAdmin)

# Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'message', 'timestamp')
    list_filter = ('session', 'user')
    search_fields = ('message', 'user__username')
    ordering = ('-timestamp',)
    actions = ['approve_messages']

    def approve_messages(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"Successfully approved {queryset.count()} messages")
    approve_messages.short_description = "Approve Selected Messages"

# File Admin
class FileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_by', 'uploaded_at', 'requirement', 'is_approved')
    list_filter = ('is_approved', 'requirement')
    search_fields = ('file', 'uploaded_by__username')
    ordering = ('-uploaded_at',)
    actions = ['approve_files']

    def approve_files(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"Successfully approved {queryset.count()} files")
    approve_files.short_description = "Approve Selected Files"

    def requirement(self, obj):
        return format_html('<a href="{}">{}</a>',
            reverse('admin:app_requirement_change', args=(obj.requirement.pk,)),
            obj.requirement.name) if obj.requirement else 'No Requirement'
    requirement.short_description = "Requirement"

# Requirement Admin
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_files')
    search_fields = ('name',)
    ordering = ('name',)

    def get_files(self, obj):
        return ", ".join([file.file.name for file in obj.files.all()]) if obj.files.exists() else "No Files"
    get_files.short_description = "Files"

# Post Admin
# class PictureInline(admin.TabularInline):
#     model = Picture
#     extra = 1

# class PostAdmin(admin.ModelAdmin):
#     form = PostAdminForm
#     inlines = [PictureInline]

# Content Admin
admin.site.register(Message, MessageAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Post)
admin.site.register(Logo)
admin.site.register(Season)
admin.site.register(SeasonGrouping)
admin.site.register(PartnerLogo)
admin.site.register(FacultyRank)
admin.site.register(VideoPost)

admin.site.register(SponsorPost)
admin.site.register(ForumMessage)

@admin.register(HelpdeskMessage)
class HelpdeskMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "message", "timestamp", "is_from_admin")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.sender = request.user
            obj.is_from_admin = request.user.is_superuser
        super().save_model(request, obj, form, change)

admin.site.register(Tag)