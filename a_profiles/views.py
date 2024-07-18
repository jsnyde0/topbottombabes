from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile
import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def view_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profiles/view_profile.html', {'profile': profile})