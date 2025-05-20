from django.conf import settings
from django.core.cache import cache
from.models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
import random
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime

def logo(request):
    logo = None
    logo_id = getattr(request, 'logo_id', None)

    if logo_id is None:
        logo_id = cache.get('logo_id')
        if logo_id is None:
            try:
                logo = Logo.objects.get(id=1)  # Adjust if not always id=1
                cache.set('logo_id', logo.id, timeout=60 * 60)
                logo_id = logo.id
            except ObjectDoesNotExist:
                logo = None

    if logo is None and logo_id:
        try:
            logo = Logo.objects.get(id=logo_id)
        except ObjectDoesNotExist:
            logo = None

    return {'logo': logo}

def misc_12(request):
    misc_obj = None
    misc_id = 13  # Fixed ID you want

    # Try fetching from cache first
    cached_misc = cache.get('misc_12')
    if cached_misc:
        misc_obj = cached_misc
    else:
        try:
            misc_obj = Misc.objects.get(id=misc_id)
            cache.set('misc_12', misc_obj, timeout=60 * 60)  # cache it for 1 hour
        except ObjectDoesNotExist:
            misc_obj = None

    return {'misc_12': misc_obj}

def profile(request):
    user = request.user

    if hasattr(user, 'officer'):
        profile = user.officer
    elif hasattr(user, 'member'):
        profile = user.member
    elif hasattr(user, 'guest'):
        profile = user.guest
    else:
        profile = None

    return {'profile': profile}