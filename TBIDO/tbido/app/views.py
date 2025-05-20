from datetime import datetime
import json
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import mimetypes
import os
from django.http import FileResponse, Http404

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from dateutil import parser as date_parser
from django.forms.models import model_to_dict
from django.core.serializers import serialize
from django.db.models import Q
from collections import defaultdict, namedtuple

from django.http import HttpResponseBadRequest

from .utils import email_verification_token
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
# from datetime import isoformat

from .forms import *
from .models import *

# def program_list_view(request):
#     programs = Program.objects.all()
#     selected_program_id = request.GET.get('program')
#     selected_program = Program.objects.filter(id=selected_program_id).first() if selected_program_id else None
#     return render(request, 'program_list.html', {
#         'programs': programs,
#         'selected_program': selected_program
#     })

def program_list(request):
    programs = Program.objects.all()
    selected_program = None
    form = None
    applied = False
    show_apply_button = False  # New flag!

    program_id = request.GET.get('program')
    if program_id:
        selected_program = Program.objects.get(id=program_id)

        # Check if user has already applied to this program
        existing_application = ProgramApplication.objects.filter(
            user=request.user, program=selected_program
        ).exists()

        applied = existing_application
        show_apply_button = not existing_application

        # Handle application submission
        if request.method == 'POST' and not existing_application:
            form = ProgramApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                application = form.save(commit=False)
                application.user = request.user
                application.program = selected_program
                application.save()

                send_program_application_email(application)
                applied = True
                show_apply_button = False
                messages.success(request, 'Sent your application to the TBIDO email successfully!')
                return redirect(f'{request.path}?program={selected_program.id}&applied=1')
        else:
            form = ProgramApplicationForm()

    # Check if user just applied (via ?applied=1 in URL)
    if request.GET.get('applied') == '1':
        applied = True
        show_apply_button = False

    context = {
        'programs': programs,
        'selected_program': selected_program,
        'application_form': form,
        'applied': applied,
        'show_apply_button': show_apply_button,
        'today': now().date(),
    }
    return render(request, 'program_list.html', context)

def event_list(request):
    events = Event.objects.all().order_by('-event_date')
    upcoming_events = events.filter(is_past=False)
    past_events = events.filter(is_past=True)

    selected_event = None
    form = None
    applied = False

    event_id = request.GET.get('event')
    if event_id:
        selected_event = Event.objects.get(id=event_id)

        # Handle registration submission
        if request.method == 'POST':
            form = EventApplicationForm(request.POST)
            if form.is_valid():
                application = form.save(commit=False)
                application.user = request.user
                application.event = selected_event
                application.save()

                # Send confirmation email
                send_mail(
                    subject='Event Registration Confirmation',
                    message=f'Thank you for registering for {selected_event.title}!',
                    from_email='tbido.pylon@gmail.com',
                    recipient_list=[application.email],
                    fail_silently=True,
                )

                applied = True
                messages.success(request, 'You are given a successful confirmation email!')
                return redirect(f'{request.path}?event={selected_event.id}&applied=1')

        else:
            form = EventApplicationForm()

    if request.GET.get('applied') == '1':
        applied = True

    context = {
        'events': events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'selected_event': selected_event,
        'form': form,
        'applied': applied,
        'today': now().date(),
    }
    return render(request, 'event_list.html', context)

def send_program_application_email(application):
    # Get user profile email
    user = application.user
    if hasattr(user, 'officer'):
        recipient_email = user.officer.email
    elif hasattr(user, 'member'):
        recipient_email = user.member.email
    elif hasattr(user, 'guest'):
        recipient_email = user.guest.email
    else:
        recipient_email = None

    if not recipient_email:
        print("❌ No recipient email found! Email not sent.")
        return

    subject = "New Program Application"
    html_message = render_to_string('program_apply_email.html', {'application': application})
    plain_message = strip_tags(html_message)

    email = EmailMessage(
        subject,
        html_message,
        'tbido.pylon@gmail.com',  # Sender
        [recipient_email],        # Recipient (user profile)
        cc=['tbido.pylon@gmail.com'],  # Also send to admin
    )
    email.content_subtype = "html"

    # Attach uploaded files
    doc_fields = [
        application.pitch_deck,
        application.business_plan,
        application.supporting_document_1,
        application.supporting_document_2,
        application.supporting_document_3,
    ]

    for doc in doc_fields:
        if doc:
            try:
                doc.open()
                file_content = doc.read()
                doc.close()

                filename = os.path.basename(doc.name)
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                email.attach(filename, file_content, mime_type)
                print(f"✅ Attached file {filename}")
            except Exception as e:
                print(f"❌ Failed to attach {doc.name}: {e}")

    email.send()

@login_required
def mark_as_favorite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.is_authenticated:
        Favorite.objects.create(user=request.user, post=post)
        return HttpResponseRedirect(reverse('favorite_posts'))
    else:
        return redirect('login')

@login_required
def favorite_posts(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'favorite_posts.html', {'favorites': favorites})
    else:
        return redirect('login')

def videos_page(request):
    videoposts = VideoPost.objects.order_by('-Date')
    misc = Misc.objects.all()

    context = {
        'videoposts': videoposts,
        'misc': misc,
    }

    return render(request, 'videos.html', context)

def services_view(request):
    misc = Misc.objects.all()
    if request.method == 'POST':
        form = ServiceInquiryForm(request.POST, request.FILES)
        if form.is_valid():
            # Save preferred communication as comma-separated string
            inquiry = form.save(commit=False)
            comms = form.cleaned_data.get('preferred_communication')
            inquiry.preferred_communication = ', '.join(comms)
            inquiry.save()

            messages.success(request, "Your inquiry has been sent successfully!")
            return redirect('services_view')  # Replace with your services URL name
    else:
        form = ServiceInquiryForm()
    context = {
        'misc': misc,
        'form': form,
    }

    return render(request, 'services.html', context)


def sponsor_page(request):
    sponsorposts = SponsorPost.objects.order_by('-Date')

    context = {
        'sponsorposts': sponsorposts,
    }

    return render(request, 'sponsors.html', context)

def candidates_page(request):
    candidates = Candidate.objects.all()
    return render(request, 'candidates.html', {'candidates': candidates})

@login_required
def candidates_register(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.save()
            return redirect('candidates_page')
    else:
        form = CandidateForm()

    return render(request, 'candidate_register.html', {'form': form})

def landing_page(request):
    logo = Logo.objects.get(id=1)
    all_posts = Post.objects.all()
    misc = Misc.objects.all()
    misc1 = Misc.objects.filter(id=1)
    random_post = random.choice(all_posts) if all_posts else None
    other_posts = Post.objects.exclude(id=random_post.id) if random_post else []

    current_season = Season.objects.filter(start_year__lte=timezone.now().year, end_year__gte=timezone.now().year).first()
    if current_season:
        future_schedules = MentoringSchedule.objects.filter(seasongrouping__season=current_season, session_time__gte=timezone.now()).order_by('session_time')
        most_recent_schedule = future_schedules.first()
        schedules = MentoringSchedule.objects.filter(seasongrouping__season=current_season).order_by('session_time')
        mentoring_sessions = MentoringSession.objects.filter(seasongrouping__season=current_season).order_by('-date')[:5]
    else:
        schedules = MentoringSchedule.objects.none()
        # event_schedules = EventSchedule.objects.none()
        most_recent_schedule = None
        mentoring_sessions = MentoringSession.objects.none()

    partner_logos = PartnerLogo.objects.all()

    context = {
        'random_post': random_post,
        'other_posts': other_posts,
        'schedules': schedules,
        # 'event_schedules': event_schedules,
        'current_season': current_season,
        'mentoring_sessions': mentoring_sessions,
        'most_recent_schedule': most_recent_schedule,
        'most_recent_schedule_date': most_recent_schedule.session_time.strftime('%Y-%m-%d %H:%M:%S') if most_recent_schedule else '',
        'logo': logo,
        'misc': misc,
        'misc1': misc1,
        'partner_logos': partner_logos,
    }

    return render(request, 'landing_page.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'officer':
                return redirect('create_officer')
            elif user_type == 'member':
                return redirect('create_member')
            elif user_type == 'guest':
                return redirect('create_guest')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            officer = Officer.objects.filter(user=user).first()
            member = Member.objects.filter(user=user).first()
            guest = Guest.objects.filter(user=user).first()

            if not officer and not member and not guest:
                return redirect('register')
            else:
                return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')

def process_invite(request, invite_code):
    try:
        invite = Invites.objects.get(invite_code=invite_code)

        if not invite.is_valid():
            messages.error(request, "This invite link has expired or has already been used.")
            return redirect('landing_page')

        ApprovedRequest.objects.create(
            pendingRequest=PendingRequest.objects.create(
                member=request.user.member,
                sessionKey=invite.session,
                requestDate=timezone.now(),
                approvalType='approved'  # Changed from 'pending' to 'approved'
            )
        )

        # Mark invite as used
        invite.used = True
        invite.save()

        messages.success(request, "You have been successfully added to the session!")
        return redirect('session_view', session_id=invite.session.sessionKey)

    except Invites.DoesNotExist:
        messages.error(request, "Invalid invite code.")
        return redirect('landing_page')

def logout_view(request):
    logout(request)
    return redirect('landing_page')

def create_officer(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            officer = form.save(commit=False)
            officer.user = request.user
            officer.is_verified = False
            officer.save()

            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Verify your TBIDO account'
            uid = urlsafe_base64_encode(force_bytes(officer.user.pk))
            token = default_token_generator.make_token(officer.user)
            verify_link = f"http://{current_site.domain}{reverse('verify_email_officer', args=[uid, token])}"
            logo = Logo.objects.get(id=1)
            logo_url = request.build_absolute_uri(logo.image.url)
            message = render_to_string('verify_email.html', {
                'user': officer.user,
                'verify_link': verify_link,
                'logo_url': logo_url,
            })
            email = EmailMessage(
                subject=mail_subject,
                body=message,
                from_email='tbido.pylon@gmail.com',
                to=[officer.email]
            )
            email.content_subtype = "html"
            email.send()

            # Clear unfinished registration if successful
            request.session.pop('incomplete_registration', None)

            messages.success(request, 'Verification email sent! Please check your inbox and spam folders.')
            request.session['show_verification_overlay'] = True
            return redirect('home')
    else:
        form = OfficerForm()
        # Save progress
        request.session['incomplete_registration'] = {
            'type': 'officer'
        }

    return render(request, 'create_officer.html', {'form': form})


def create_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            member.user = request.user
            member.is_verified = False
            member.save()

            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Verify your TBIDO account'
            uid = urlsafe_base64_encode(force_bytes(member.user.pk))
            token = default_token_generator.make_token(member.user)
            verify_link = f"http://{current_site.domain}{reverse('verify_email', args=[uid, token])}"
            logo = Logo.objects.get(id=1)
            logo_url = request.build_absolute_uri(logo.image.url)
            message = render_to_string('verify_email.html', {
                'user': member.user,
                'verify_link': verify_link,
                'logo_url': logo_url,
            })
            email = EmailMessage(
                subject=mail_subject,
                body=message,
                from_email='tbido.pylon@gmail.com',
                to=[member.email]
            )
            email.content_subtype = "html"
            email.send()

            # Clear unfinished registration if successful
            request.session.pop('incomplete_registration', None)

            messages.success(request, 'Verification email sent! Please check your inbox and spam folders.')
            request.session['show_verification_overlay'] = True
            return redirect('home')
    else:
        form = MemberForm()
        # Save progress
        request.session['incomplete_registration'] = {
            'type': 'member'
        }

    return render(request, 'create_member.html', {'form': form})


def create_guest(request):
    if request.method == 'POST':
        form = GuestForm(request.POST, request.FILES)
        if form.is_valid():
            guest = form.save(commit=False)
            guest.user = request.user
            guest.is_verified = False
            guest.save()

            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Verify your TBIDO account'
            uid = urlsafe_base64_encode(force_bytes(guest.user.pk))
            token = default_token_generator.make_token(guest.user)
            verify_link = f"http://{current_site.domain}{reverse('verify_email_guest', args=[uid, token])}"
            logo = Logo.objects.get(id=1)
            logo_url = request.build_absolute_uri(logo.image.url)
            message = render_to_string('verify_email.html', {
                'user': guest.user,
                'verify_link': verify_link,
                'logo_url': logo_url,
            })
            email = EmailMessage(
                subject=mail_subject,
                body=message,
                from_email='tbido.pylon@gmail.com',
                to=[guest.email]
            )
            email.content_subtype = "html"
            email.send()

            # Clear unfinished registration if successful
            request.session.pop('incomplete_registration', None)

            messages.success(request, 'Verification email sent! Please check your inbox and spam folders.')
            request.session['show_verification_overlay'] = True
            return redirect('home')
    else:
        form = GuestForm()
        # Save progress
        request.session['incomplete_registration'] = {
            'type': 'guest'
        }

    return render(request, 'create_guest.html', {'form': form})

@csrf_exempt
def dismiss_verification_overlay(request):
    if request.method == 'POST':
        request.session['show_verification_overlay'] = False
        return JsonResponse({'status': 'success'})

def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.member.is_verified = True
        user.member.save()

        if 'show_verification_overlay' in request.session:
            request.session['show_verification_overlay'] = False

        messages.success(request, 'Email verified successfully!')
        return redirect('home')
    else:
        messages.error(request, 'Verification link invalid or expired.')
        return redirect('home')

def verify_email_officer(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.officer.is_verified = True
        user.officer.save()

        if 'show_verification_overlay' in request.session:
            request.session['show_verification_overlay'] = False

        messages.success(request, 'Email verified successfully!')
        return redirect('home')
    else:
        messages.error(request, 'Verification link invalid or expired.')
        return redirect('home')

def verify_email_guest(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.guest.is_verified = True
        user.guest.save()

        if 'show_verification_overlay' in request.session:
            request.session['show_verification_overlay'] = False

        messages.success(request, 'Email verified successfully!')
        return redirect('home')
    else:
        messages.error(request, 'Verification link invalid or expired.')
        return redirect('home')

@login_required
def cohorts_page(request):
    cohorts = Cohort.objects.all()
    user_created_cohort = Cohort.objects.filter(cohort_creator=request.user).exists()
    return render(request, 'cohorts_page.html', {
        'cohorts': cohorts,
        'user_created_cohort': user_created_cohort,
        }
    )

@login_required
def cohort_message_board(request):
    posts = CohortPublicForumMessage.objects.all().order_by('-created_at').prefetch_related('replies', 'replies__responder', 'addressed_cohort')
    cohorts = Cohort.objects.all()

    # For each post, annotate its replies with an extra flag
    for post in posts:
        for reply in post.replies.all():
            # Check if reply.responder is part of the post's addressed cohort
            is_member = CohortMember.objects.filter(
                member=reply.responder,
                cohort=post.addressed_cohort
            ).exists()
            reply.is_member_of_addressed_cohort = is_member  # Dynamically add this flag

    if request.method == "POST":
        if "create_post" in request.POST:
            addressed_id = request.POST.get('addressed_cohort')
            message = request.POST.get('message')
            addressed_cohort = Cohort.objects.get(id=addressed_id)
            CohortPublicForumMessage.objects.create(
                addressed_cohort=addressed_cohort,
                sender=request.user,
                message=message
            )
            return redirect('cohort_message_board')

        if "reply_post" in request.POST:
            post_id = request.POST.get('post_id')
            reply_msg = request.POST.get('reply_message')
            post = CohortPublicForumMessage.objects.get(id=post_id)
            reply = ForumReply.objects.create(
                responder=request.user,
                message=reply_msg
            )
            post.replies.add(reply)
            return redirect('cohort_message_board')

    return render(request, 'cohort_message_board.html', {'posts': posts, 'cohorts': cohorts})

@login_required
def create_cohort(request):
    if request.method == 'POST':
        form = CohortForm(request.POST, request.FILES)
        if form.is_valid():
            cohort = form.save(commit=False)
            cohort.cohort_creator = request.user
            cohort.save()

            member_emails = [
                cohort.member1_email,
                cohort.member2_email,
                cohort.member3_email,
                cohort.member4_email,
                cohort.member5_email,
            ]

            for idx, email in enumerate(member_emails):
                if email:
                    member = CohortMember.objects.create(
                        cohort=cohort,
                        member_number=idx + 1,
                        member_email=email
                    )

                    # Prepare the invite email
                    mail_subject = f"Invitation to join {cohort.cohort_name}"

                    # Generate an invite link or just show the code (based on your flow)
                    invite_link = f"https://www.puptbicollab.com/register/"

                    # Load logo (optional like in guest email)
                    logo = Logo.objects.get(id=1)
                    logo_url = request.build_absolute_uri(logo.image.url)

                    message = render_to_string('invite_email.html', {
                        'user': request.user,
                        'invite_link': invite_link,
                        'invite_code': member.invite_code,
                        'cohort_name': cohort.cohort_name,
                        'logo_url': logo_url,
                    })

                    email_message = EmailMessage(
                        subject=mail_subject,
                        body=message,
                        from_email='tbido.pylon@gmail.com',
                        to=[email]
                    )
                    email_message.content_subtype = "html"  # Important: Send as HTML
                    email_message.send()

            return redirect('cohorts_page')
    else:
        form = CohortForm()
    return render(request, 'create_cohort.html', {'form': form})

@login_required
def join_cohort(request):
    if request.method == 'POST':
        form = CohortJoinForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['invite_code'].strip().upper()
            try:
                member_instance = CohortMember.objects.get(invite_code=code, member__isnull=True)
                member_instance.member = request.user
                member_instance.save()

                return redirect('cohort_view', cohort_id=member_instance.cohort.id)

            except CohortMember.DoesNotExist:
                form.add_error('invite_code', 'Invalid or already used invite code.')
    else:
        form = CohortJoinForm()
    return render(request, 'join_cohort.html', {'form': form})

@login_required
def cohort_view(request, cohort_id):
    cohort = get_object_or_404(Cohort, id=cohort_id)

    # Attach creator_profile (Officer > Member > Guest)
    creator_user = cohort.cohort_creator
    if hasattr(creator_user, 'officer'):
        cohort.creator_profile = creator_user.officer
        cohort.creator_profile_role = 'Officer'
    elif hasattr(creator_user, 'member'):
        cohort.creator_profile = creator_user.member
        cohort.creator_profile_role = 'Member'
    elif hasattr(creator_user, 'guest'):
        cohort.creator_profile = creator_user.guest
        cohort.creator_profile_role = 'Guest'
    else:
        cohort.creator_profile = None
        cohort.creator_profile_role = 'Unknown'

    # Get members and attach .user_profile
    memberships = CohortMember.objects.filter(cohort=cohort).select_related(
        'member',
        'member__officer',
        'member__member',
        'member__guest'
    )

    messages = CohortMessage.objects.filter(cohort=cohort).order_by('created_at')
    files = CohortFile.objects.filter(cohort=cohort).order_by('-uploaded_at')
    links = CohortLink.objects.filter(cohort=cohort).order_by('-shared_at')

    # Move creator to the first position
    creator_membership = None
    for membership in memberships:
        if membership.member == cohort.cohort_creator:
            creator_membership = membership
            memberships = memberships.exclude(id=membership.id)
            break
    if creator_membership:
        memberships = [creator_membership] + list(memberships)

    for membership in memberships:
        user = membership.member
        if hasattr(user, 'officer'):
            membership.user_profile = user.officer
            membership.user_profile_role = 'Officer'
        elif hasattr(user, 'member'):
            membership.user_profile = user.member
            membership.user_profile_role = 'Member'
        elif hasattr(user, 'guest'):
            membership.user_profile = user.guest
            membership.user_profile_role = 'Guest'
        else:
            membership.user_profile = None
            membership.user_profile_role = 'Unknown'

    # Check if logged-in user is a member
    is_member = CohortMember.objects.filter(cohort=cohort, member=request.user).exists()

    # Handling the Inquiry form submission
    if request.method == 'POST':
        form = InquiryForm(request.POST, request.FILES)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.save()

            # Send email with supporting documents attached
            send_inquiry_email(inquiry, cohort)

            return redirect('cohorts_page')
    else:
        form = InquiryForm()

    return render(request, 'cohort_view.html', {
        'cohort': cohort,
        'memberships': memberships,
        'is_member': is_member,
        'messages': messages,
        'inquiry_form': form,  # Pass the form to the template
        'links': links,
        'files': files,
        'file_form': CohortFileForm(),
        'link_form': CohortLinkForm(),
    })

@require_http_methods(['POST'])
@login_required
def handle_file_upload(request, cohort_id):
    cohort = get_object_or_404(Cohort, id=cohort_id)
    if not CohortMember.objects.filter(cohort=cohort, member=request.user).exists() and \
       request.user != cohort.cohort_creator:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    form = CohortFileForm(request.POST, request.FILES)
    if form.is_valid():
        file_obj = form.save(commit=False)
        file_obj.cohort = cohort
        file_obj.uploaded_by = request.user
        file_obj.filename = request.FILES['file'].name
        file_obj.save()
        return JsonResponse({
            'success': True,
            'filename': file_obj.filename,
            'id': file_obj.id,
            'uploaded_by': file_obj.uploaded_by.username,
            'uploaded_at': file_obj.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'error': 'Invalid form submission'}, status=400)

@require_http_methods(['POST'])
@login_required
def handle_link_share(request, cohort_id):
    cohort = get_object_or_404(Cohort, id=cohort_id)
    if not CohortMember.objects.filter(cohort=cohort, member=request.user).exists() and \
       request.user != cohort.cohort_creator:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    form = CohortLinkForm(request.POST)
    if form.is_valid():
        link_obj = form.save(commit=False)
        link_obj.cohort = cohort
        link_obj.shared_by = request.user
        link_obj.save()
        return JsonResponse({
            'success': True,
            'title': link_obj.title,
            'url': link_obj.url,
            'description': link_obj.description,
            'id': link_obj.id,
            'shared_by': link_obj.shared_by.username,
            'shared_at': link_obj.shared_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'error': 'Invalid form submission'}, status=400)

@login_required
def download_file(request, cohort_id, file_id):
    cohort = get_object_or_404(Cohort, id=cohort_id)
    file_obj = get_object_or_404(CohortFile, id=file_id, cohort=cohort)

    # Check: is user the creator or a member?
    is_creator = (request.user == cohort.cohort_creator)
    is_member = CohortMember.objects.filter(cohort=cohort, member=request.user).exists()

    if not (is_creator or is_member):
        return HttpResponseForbidden("You do not have permission to download this file.")

    # Serve file
    file_path = file_obj.file.path  # Assumes FileField
    if not os.path.exists(file_path):
        raise Http404("File does not exist.")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_obj.filename)

@login_required
def send_message(request, cohort_id):
    if request.method == "POST":
        message_content = request.POST.get('message')
        cohort_id = request.POST.get('cohort_id')
        cohort = get_object_or_404(Cohort, id=cohort_id)

        message = CohortMessage.objects.create(
            cohort=cohort,
            sender=request.user,
            message=message_content
        )

        return JsonResponse({
            'message': message.message,  # Updated field name
            'sender': message.sender.username,
            'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)

def send_inquiry_email(inquiry, cohort):
    # Find cohort creator's profile to get the correct email
    creator_user = cohort.cohort_creator
    if hasattr(creator_user, 'officer'):
        recipient_email = creator_user.officer.email
    elif hasattr(creator_user, 'member'):
        recipient_email = creator_user.member.email
    elif hasattr(creator_user, 'guest'):
        recipient_email = creator_user.guest.email
    else:
        recipient_email = None  # Fallback

    if not recipient_email:
        print("❌ No recipient email found! Email not sent.")
        return

    # Render email content using a template
    subject = "New Inquiry Received"
    html_message = render_to_string('inquiry_email.html', {'inquiry': inquiry})
    plain_message = strip_tags(html_message)

    # Create an email message
    email = EmailMessage(
        subject,
        html_message,
        'tbido.pylon@gmail.com',  # Sender email
        [recipient_email],  # Correct recipient email
    )

    email.content_subtype = "html"

    # List of supporting document fields
    doc_fields = [
        inquiry.supporting_document_1,
        inquiry.supporting_document_2,
        inquiry.supporting_document_3,
        inquiry.supporting_document_4,
        inquiry.supporting_document_5,
    ]

    # Attach files if they exist
    for index, doc in enumerate(doc_fields, start=1):
        if doc:
            try:
                doc.open()  # Open the file properly
                file_content = doc.read()
                doc.close()

                # Get original filename
                filename = os.path.basename(doc.name)

                # Guess MIME type
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = 'application/octet-stream'  # default fallback

                # Attach
                email.attach(filename, file_content, mime_type)
                print(f"✅ Attached file {filename}")

            except Exception as e:
                print(f"❌ Failed to attach {doc.name}: {e}")

    # Send the email
    email.send()
    print(f"✅ Inquiry email sent to {recipient_email}")

def home(request):
    user = request.user
    officer = Officer.objects.filter(user=user).first()
    member = Member.objects.filter(user=user).first()
    guest = Guest.objects.filter(user=user).first()

    if officer:
        profile = officer
    elif member:
        profile = member
    elif guest:
        profile = guest
    else:
        profile = None

    sessions = Session.objects.all()
    announcements = Announcement.objects.all()

    return render(request, 'home.html', {
        'profile': profile,
        'sessions': sessions,
        'announcements': announcements,
        'is_home_page': True,
    })

@login_required
def create_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST, request.FILES)
        if form.is_valid():
            session = form.save(commit=False)
            session.officerKey = request.user.officer
            session.save()
            return redirect('home')
    else:
        form = SessionForm()
    return render(request, 'create_session.html', {'form': form})

def join_session(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    if request.method == 'POST':
        form = RequestJoinSessionForm(request.POST)
        if form.is_valid():
            # Determine the user type and set the appropriate key
            if hasattr(request.user, 'officer'):
                user = request.user.officer.user
            elif hasattr(request.user, 'guest'):
                user = request.user.guest.user
            elif hasattr(request.user, 'member'):
                user = request.user.member.user
            else:
                # Handle the case where the user is not an officer, guest, or member
                # This might involve redirecting the user to a registration page or showing an error message
                return redirect('register')

            PendingRequest.objects.create(
                member=user.member, # Use the related User instance
                sessionKey=session,
                requestDate=form.cleaned_data['requestDate'],
                approvalType='pending'
            )
            return redirect('home')
    else:
        form = RequestJoinSessionForm()
    return render(request, 'join_session.html', {'form': form, 'session': session})

@login_required
def session_view(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    documents = Document.objects.filter(session=session)
    pending_requests = PendingRequest.objects.filter(sessionKey=session, approvalType='pending')
    approved_requests = ApprovedRequest.objects.filter(pendingRequest__sessionKey=session)
    pending_member_details = []
    for pending_request in pending_requests:
        member_profile = pending_request.member
        if member_profile:
            member_details = {
                'memberKey': member_profile.memberKey,
                'fname': member_profile.firstName,
                'lname': member_profile.lastName,
                'IDPicture': member_profile.IDPicture.url if member_profile.IDPicture else '',
            }
        pending_member_details.append(member_details)

    approved_member_details = []
    for approved_request in approved_requests:
        member_profile = approved_request.pendingRequest.member
        if member_profile:
            member_details = {
                'memberKey': member_profile.memberKey,
                'fname': member_profile.firstName,
                'lname': member_profile.lastName,
                'IDPicture': member_profile.IDPicture.url if member_profile.IDPicture else '',
            }
        approved_member_details.append(member_details)

    requirements = Requirement.objects.filter(session=session)

    # for requirement in requirements:
    #     requirement.event_time_start_iso = requirement.deadline.isoformat()
    #     requirement.event_time_end_iso = requirement.deadline.isoformat()

    files = File.objects.filter(session=session)
    current_tab = request.GET.get('tab', 'chat')
    advisories = Advisory.objects.filter(session=session)

    pending_files = files.filter(is_approved=False)
    approved_files = files.filter(is_approved=True)

    if request.method == 'POST' and 'file' in request.FILES:
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.uploaded_by = request.user
            file.session = session
            file.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('session_view', session_id=session_id)
    else:
        form = FileUploadForm()

    if request.method == 'POST' and 'message' in request.POST:
        message_text = request.POST.get('message')
        if message_text.strip():
            Message.objects.create(
                session=session,
                user=request.user,
                message=message_text
            )
            return redirect('session_view', session_id=session_id)

    # View Logic

    # Logic: who can access the tabs?
    show_tabs = False
    show_send_request_button = False
    show_pending_message = False
    is_officer_creator = False
    is_officer_other = False

    if hasattr(request.user, 'officer'):
        if session.officerKey == request.user.officer.officerKey:
            is_officer_creator = True
            show_tabs = True
        else:
            is_officer_other = True
            # No access for other officers
    elif hasattr(request.user, 'member'):
        member = request.user.member
        is_approved = ApprovedRequest.objects.filter(
            pendingRequest__sessionKey=session,
            pendingRequest__member=member
        ).exists()

        if is_approved:
            show_tabs = True
        else:
            has_pending = PendingRequest.objects.filter(sessionKey=session, member=member).exists()
            if has_pending:
                show_pending_message = True
            else:
                show_send_request_button = True

    context = {
        'session': session,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'requirements': requirements,
        'pending_files': pending_files,
        'approved_files': approved_files,
        'current_tab': current_tab,
        'advisories': advisories,
        'form': form,
        'pending_member_details': pending_member_details,
        'approved_member_details': approved_member_details,
        'documents': documents,

        # Access flags
        'show_tabs': show_tabs,
        'show_send_request_button': show_send_request_button,
        'show_pending_message': show_pending_message,
        'is_officer_creator': is_officer_creator,
        'is_officer_other': is_officer_other,
    }
    return render(request, 'session_view.html', context)

def save_document(request):
    if request.method == 'POST' and request.is_ajax():
        data = json.loads(request.body)
        document_id = data.get('documentId')
        title = data.get('title')
        content = data.get('content')

        # Save or update the document
        if document_id:
            document = Document.objects.get(id=document_id)
            document.title = title
            document.content = content
            document.save()
        else:
            session = Session.objects.get(id=data['session_id'])
            document = Document.objects.create(session=session, title=title, content=content, created_by=request.user)

        return JsonResponse({'success': True})

def get_document(request, document_id):
    document = Document.objects.get(id=document_id)
    return JsonResponse({'content': document.content})

@login_required
def session_list(request):
    user_sessions = set()

    # If the user is a Member, get sessions they joined
    if hasattr(request.user, 'member'):
        approved_requests = ApprovedRequest.objects.filter(
            pendingRequest__member=request.user.member
        ).select_related('pendingRequest__sessionKey')
        member_sessions = [ar.pendingRequest.sessionKey for ar in approved_requests]
        user_sessions.update(member_sessions)

    # If the user is an Officer, get sessions they created
    if hasattr(request.user, 'officer'):
        officer_sessions = Session.objects.filter(officerKey=request.user.officer)
        user_sessions.update(officer_sessions)

    return render(request, 'session_list.html', {
        'user_sessions': list(user_sessions)
    })

def sessions_view(request):
    session_type = request.GET.get('session_type')
    session_kind = request.GET.get('session_kind')

    schedules = MentoringSchedule.objects.all().order_by('session_time')

    if session_type:
        schedules = schedules.filter(session_type=session_type)
    if session_kind:
        schedules = schedules.filter(session_kind=session_kind)

    for schedule in schedules:
        if schedule.session_time:
            schedule.session_time_iso = schedule.session_time.isoformat()
        else:
            schedule.session_time_iso = ""

    return render(request, 'sessions.html', {
        'schedules': schedules,
        'selected_type': session_type,
        'selected_kind': session_kind,
    })

def progress_tracking(request):
    current_season = Season.objects.filter(start_year__lte=timezone.now().year, end_year__gte=timezone.now().year).first()
    progress = ProgressTracking.objects.filter(seasongrouping__season=current_season).order_by('-progress_percentage') if current_season else ProgressTracking.objects.none()
    top_performers = TopPerformers.objects.select_related('progress_tracking').order_by('ranking')[:4]  # Top 4 spotlight

    return render(request, 'progress_tracking.html', {
        'progress': progress,
        'top_performers': top_performers,
        'current_season': current_season,
    })

def top_contributors(request):
    top_contributors = TopContributor.objects.all()
    return render(request, 'top_contributors.html', {'top_contributors': top_contributors})

# @login_required
# def profile(request):
#     user = request.user
#     officer = Officer.objects.filter(user=user).first()
#     member = Member.objects.filter(user=user).first()
#     guest = Guest.objects.filter(user=user).first()

#     if officer:
#         profile = officer
#     elif member:
#         profile = member
#     elif guest:
#         profile = guest
#     else:
#         profile = None

#     return render(request, 'profile.html', {'profile': profile})

@login_required
def profile(request):
    user = request.user
    officer = Officer.objects.filter(user=user).first()
    member = Member.objects.filter(user=user).first()
    guest = Guest.objects.filter(user=user).first()

    profile = None
    form = None

    if officer:
        profile = officer
        FormClass = OfficerEditForm
    elif member:
        profile = member
        FormClass = MemberEditForm
    elif guest:
        profile = guest
        FormClass = GuestEditForm
    else:
        profile = None
        FormClass = None

    if request.method == 'POST' and FormClass:
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        if FormClass:
            form = FormClass(instance=profile)

    return render(request, 'profile.html', {'profile': profile, 'form': form})

def profiles(request):
    officers = Officer.objects.all()
    members = Member.objects.all()
    guests = Guest.objects.all()
    return render(request, 'profiles.html', {'officers': officers, 'members': members, 'guests': guests})

def officer_profiles(request):
    officers = Officer.objects.all()
    return render(request, 'officer_profiles.html', {'officers': officers})

def member_profiles(request):
    members = Member.objects.all()
    return render(request, 'member_profiles.html', {'members': members})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Fetch a random set of posts excluding the current post
    all_posts = Post.objects.exclude(pk=post.pk)
    related_posts = random.sample(list(all_posts), min(5, all_posts.count())) # Fetch 5 random posts or fewer if there are less than 5
    return render(request, 'post_detail.html', {'post': post, 'related_posts': related_posts})

def tag_posts(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    posts = Post.objects.filter(tag=tag)
    return render(request, 'tag_posts.html', {'posts': posts})

def view_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    comments = Comment.objects.filter(announcement=announcement)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.announcement = announcement
            comment.save()
            return redirect('view_announcement', announcement_id=announcement.id)
    else:
        form = CommentForm()

    return render(request, 'announcement_detail.html', {
        'announcement': announcement,
        'comments': comments,
        'form': form,
    })

@login_required
@require_http_methods(["GET", "POST"])
def public_forum(request):
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        if message_text:
            ForumMessage.objects.create(
                user=request.user,
                message=message_text,
                timestamp=timezone.now()
            )
        # No redirect for AJAX
        return JsonResponse({"status": "success"})

    # If GET with AJAX polling
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        since = request.GET.get("since")
        messages = ForumMessage.objects.all().order_by("timestamp")
        if since:
            try:
                since = since.replace(' ', '+')
                since_dt = date_parser.isoparse(since)
                messages = messages.filter(timestamp__gt=since_dt)
            except (ValueError, TypeError):
                # Fallback: just return the last 50 messages
                messages = messages.order_by("-timestamp")[:50]

        data = [
            {
                "user": m.user.username,
                "message": m.message,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
        return JsonResponse(data, safe=False)

    # Normal render
    messages = ForumMessage.objects.all().order_by("timestamp")
    return render(request, "public_forum.html", {"messages": messages})


def helpdesk(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        return JsonResponse({"error": "No admin user found."}, status=404)

    if request.method == "POST" and request.is_ajax():
        msg = request.POST.get("message")
        HelpdeskMessage.objects.create(
            sender=request.user,
            recipient=admin_user,
            message=msg,
            is_from_admin=False
        )
        return JsonResponse({"status": "Message sent."})

    # Get all messages between user and admin
    messages = HelpdeskMessage.objects.filter(
        sender=request.user, recipient=admin_user
    ) | HelpdeskMessage.objects.filter(
        sender=admin_user, recipient=request.user
    )
    messages = messages.order_by("timestamp")

    return render(request, "helpdesk_chat.html", {"messages": messages})

def helpdesk_send(request):
    if request.method == "POST" and request.user.is_authenticated:
        message_text = request.POST.get("message", "").strip()
        if message_text:
            admin_user = User.objects.filter(is_superuser=True).first()
            HelpdeskMessage.objects.create(
                sender=request.user,
                recipient=admin_user,
                message=message_text,
                timestamp=timezone.now(),
                is_from_admin=False
            )
            return JsonResponse({"status": "sent"})
    return JsonResponse({"status": "error"})

def helpdesk_messages(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)

    since = request.GET.get("since")
    messages = HelpdeskMessage.objects.filter(Q(sender=request.user) | Q(recipient=request.user)).order_by("timestamp")
    messages = messages.order_by("timestamp")

    if since:
        try:
            since_dt = parse_datetime(since)
            if since_dt:
                messages = messages.filter(timestamp__gt=since_dt)
        except:
            pass

    data = [{
        "id": msg.id,
        "user": msg.sender.username,
        "message": msg.message,
        "timestamp": msg.timestamp.isoformat(),
        "is_admin": msg.is_from_admin
    } for msg in messages]

    return JsonResponse(data, safe=False)

def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'resource_list.html', {'resources': resources})

def experts_by_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    experts = resource.experts.all()
    return render(request, 'experts_by_resource.html', {'resource': resource, 'experts': experts})

def expert_detail(request, expert_id):
    expert = get_object_or_404(Expert, id=expert_id)
    return render(request, 'expert_detail.html', {'expert': expert})

@login_required
def connect_to_expert(request, expert_id):
    expert = get_object_or_404(Expert, id=expert_id)
    if expert.user:
        if request.method == 'POST':
            form = CorrespondenceForm(request.POST, request.FILES)
            if form.is_valid():
                correspondence = form.save(commit=False)
                correspondence.sender = request.user
                correspondence.recipient = expert.user
                correspondence.save()
                return redirect('inbox')
        else:
            form = CorrespondenceForm()
        return render(request, 'connect_form.html', {'form': form, 'expert': expert})

@login_required
def inbox(request):
    # Get all messages where user is sender or recipient
    all_messages = Correspondence.objects.filter(
        models.Q(sender=request.user) | models.Q(recipient=request.user)
    ).select_related('recipient', 'sender')

    threads = defaultdict(list)

    for msg in all_messages:
        # The other participant in the conversation
        other_user = msg.recipient if msg.recipient != request.user else msg.sender
        threads[other_user].append(msg)

    # Pass dict for easy iteration in template
    return render(request, "inbox.html", {'threads': dict(threads), 'user': request.user})

@require_POST
@login_required
def send_correspondence(request):
    subject = request.POST.get('subject')
    body = request.POST.get('body')
    recipient_username = request.POST.get('recipient_username')
    image = request.FILES.get('image')

    if not recipient_username:
        return HttpResponseBadRequest("Recipient username is required")

    recipient = get_object_or_404(User, username=recipient_username)

    Correspondence.objects.create(
        subject=subject,
        body=body,
        recipient=recipient,
        sender=request.user,
        image=image
    )

    return redirect('inbox')

@require_POST
@login_required
def mark_as_read(request, msg_id):
    try:
        msg = Correspondence.objects.get(id=msg_id, recipient=request.user)
        msg.is_read = True
        msg.save()
        return JsonResponse({'status': 'success'})
    except Correspondence.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found or unauthorized'}, status=404)

