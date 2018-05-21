from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from biblepaycentral.useraccount.forms import SignupForm
from biblepaycentral.emailalert.models import EMailAlert

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            return redirect('/')
    else:
        form = SignupForm()

    return render(request, 'useraccount/signup.html', {
            'form': form
        })

@login_required
def profile(request):
    
    emailalerts = EMailAlert.objects.filter(user=request.user)
    
    return render(request, 'useraccount/profile.html', {
            'emailalerts': emailalerts,
        })