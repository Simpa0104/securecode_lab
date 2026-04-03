#proyects/forms.py
from django import forms
from .models import Project

ALLOWED_EXTENSIONS = ['.py', '.zip']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

NIVEL_CHOICES = [
    ('BASICO',     'Basico — SQL Injection, XSS, configuraciones inseguras'),
    ('INTERMEDIO', 'Intermedio — Basico + eval/exec, deserializacion, credenciales en comentarios'),
    ('AVANZADO',   'Avanzado — Todo lo anterior + hash debiles, CORS, open redirect, dependencias'),
]


class ProjectForm(forms.ModelForm):

    archivo = forms.FileField(
        label='Archivo del proyecto',
        help_text='Formatos permitidos: .py, .zip — Maximo 5 MB',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    nivel = forms.ChoiceField(
        choices=NIVEL_CHOICES,
        label='Nivel de analisis',
        help_text='El nivel Avanzado incluye todas las reglas de los niveles anteriores.',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Project
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Mi aplicacion web Django'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe brevemente tu proyecto...'
            }),
        }
        labels = {
            'name': 'Nombre del proyecto',
            'description': 'Descripcion',
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')

        if not archivo:
            raise forms.ValidationError('Debes seleccionar un archivo.')

        if archivo.size > MAX_FILE_SIZE:
            raise forms.ValidationError(
                f'El archivo supera el limite de 5 MB. '
                f'Tu archivo pesa {round(archivo.size / 1024 / 1024, 2)} MB.'
            )

        import os
        _, ext = os.path.splitext(archivo.name)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f'Tipo de archivo no permitido. '
                f'Extensiones aceptadas: {", ".join(ALLOWED_EXTENSIONS)}'
            )

        return archivo