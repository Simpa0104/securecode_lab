from django import forms
from .models import Project

# Extensiones permitidas:
ALLOWED_EXTENSIONS = ['.zip', '.py', '.js', '.php', '.java', '.html', '.ts']

# Tamaño máximo: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'file')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Mi aplicación web Django'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe brevemente tu proyecto...'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Nombre del proyecto',
            'description': 'Descripción',
            'file': 'Archivo del proyecto',
        }
        help_texts = {
            'file': f'Formatos permitidos: {", ".join(ALLOWED_EXTENSIONS)} — Máximo 5 MB',
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if not file:
            raise forms.ValidationError('Debes seleccionar un archivo.')

        # Validar tamaño
        if file.size > MAX_FILE_SIZE:
            raise forms.ValidationError(
                f'El archivo supera el tamaño máximo permitido de 5 MB. '
                f'Tu archivo pesa {round(file.size / 1024 / 1024, 2)} MB.'
            )

        # Validar extensión
        import os
        _, ext = os.path.splitext(file.name)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f'Tipo de archivo no permitido. '
                f'Extensiones aceptadas: {", ".join(ALLOWED_EXTENSIONS)}'
            )

        return file
