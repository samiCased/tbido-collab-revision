from django.urls import include, path
from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Main Pages
    path('', views.landing_page, name='landing_page'),
    path('videos/', views.videos_page, name='videos'),
    path('sponsorships/', views.sponsor_page, name='sponsorships'),
    path('profile/', views.profiles, name='profile'),
    path('profiles/', views.profiles, name='profiles'),
    path('home/', views.home, name='home'),
    path('candidates_page/', views.candidates_page, name='candidates_page'),
    path('candidates_register/', views.candidates_register, name='candidates_register'),
    path('top_contributors/', views.top_contributors, name='top_contributors'),
    path('progress_tracking/', views.progress_tracking, name='progress_tracking'),
    path('sessions/', views.sessions_view, name='sessions'),
    path('services/', views.services_view, name='services_view'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('create_officer/', views.create_officer, name='create_officer'),
    path('create_member/', views.create_member, name='create_member'),
    path('create_guest/', views.create_guest, name='create_guest'),
    path('logout/', views.logout_view, name='logout'),

    # Cohorts
    path('cohorts/', views.cohorts_page, name='cohorts_page'),
    path('cohorts/create/', views.create_cohort, name='create_cohort'),
    path('cohorts/join/', views.join_cohort, name='join_cohort'),
    path('cohorts/view/<int:cohort_id>/', views.cohort_view, name='cohort_view'),
    path('cohort/<int:cohort_id>/', views.cohort_view, name='cohort_view'),
    path('send_message/<int:cohort_id>/', views.send_message, name='send_message'),
    path('cohort-message-board/', views.cohort_message_board, name='cohort_message_board'),


    path('cohort/file_upload/<int:cohort_id>/', views.handle_file_upload, name='handle_file_upload'),
    path('cohort/link_upload/<int:cohort_id>/', views.handle_link_share, name='handle_link_share'),
    path('cohort/<int:cohort_id>/download/<int:file_id>/', views.download_file, name='download_file'),


    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('verify/officer/<uidb64>/<token>/', views.verify_email_officer, name='verify_email_officer'),  # For officers
    path('verify/guest/<uidb64>/<token>/', views.verify_email_guest, name='verify_email_guest'),  # For guests
    path('dismiss-verification-overlay/', views.dismiss_verification_overlay, name='dismiss_verification_overlay'),

    # Programs & Events
    path('programs/', views.program_list, name='program_list'),
    path('events/', views.event_list, name='event_list'),
    # path('apply/', views.send_program_application_email, name='send_program_application_email'),


    # Session Management
    path('create_startup/', views.create_session, name='create_session'),
    path('startup/<int:session_id>/', views.session_view, name='session_view'),
    path('join/<int:invite_code>/', views.process_invite, name='process_invite'),
    path('join_startup/<int:session_id>/', views.join_session, name='join_session'),
    path('my_startups/', views.session_list, name='session_list'),
    path('get_document/<int:document_id>/', views.get_document, name='get_document'),
    path('save_document/', views.save_document, name='save_document'),

    # Forum and Helpdesk
    path('public-forum/', views.public_forum, name='public_forum'),
    path("helpdesk/", views.helpdesk, name="helpdesk"),
    path('helpdesk/send/', views.helpdesk_send, name='helpdesk_send'),
    path('helpdesk/messages/', views.helpdesk_messages, name='helpdesk_messages'),

    # Profiles
    path('profiles/', views.profiles, name='profiles'),
    path('my_profile/', views.profile, name='profile'),
    path('officer_profiles/', views.officer_profiles, name='officer_profiles'),
    path('member_profiles/', views.member_profiles, name='member_profiles'),

    # Content Management
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('tag/<str:tag_name>/', views.tag_posts, name='tag_posts'),
    path('mark_as_favorite/<int:post_id>/', views.mark_as_favorite, name='mark_as_favorite'),
    path('favorite-posts/', views.favorite_posts, name='favorite_posts'),
    path('announcement/<int:announcement_id>/', views.view_announcement, name='view_announcement'),

    # Resources and Inbox
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/<int:resource_id>/experts/', views.experts_by_resource, name='experts_by_resource'),
    path('experts/<int:expert_id>/', views.expert_detail, name='expert_detail'),
    path('connect/<int:expert_id>/', views.connect_to_expert, name='connect_to_expert'),
    path('inbox/', views.inbox, name='inbox'),
    path('send/', views.send_correspondence, name='send_correspondence'),
    path('mark-as-read/<int:msg_id>/', views.mark_as_read, name='mark_as_read'),

    # Static/Media Files
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)