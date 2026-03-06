from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import Profile
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            Profile.objects.create(
                user=user,
                role="student",
            )

            return redirect('login')

    else:  # ← CORRECCIÓN: este else ahora pertenece al if request.method == 'POST'
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})