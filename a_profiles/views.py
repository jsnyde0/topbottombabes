from django.shortcuts import render
from .models import Profile

# Create your views here.
def view_profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profiles/view_profile.html', {'profile': profile})