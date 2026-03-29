# users/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    GRUPO_CHOICES = [
        ('student', 'Estudiante'),
        ('monitor', 'Monitor'),
    ]

    grupo = forms.ChoiceField(
        choices=GRUPO_CHOICES,
        label='Tipo de usuario',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_grupo'})
    )

    numero_clase = forms.ChoiceField(
        choices=Profile.CLASE_CHOICES,
        label='Numero de clase',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_numero_clase'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, mostrar_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        if mostrar_admin:
            self.fields['grupo'].choices = [
                ('student', 'Estudiante'),
                ('monitor', 'Monitor'),
                ('admin', 'Profesor / Administrador'),
            ]