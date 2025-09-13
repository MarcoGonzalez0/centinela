# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#-----------librerias para el validador-----------
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, validate_ipv6_address
import re


#-----------formulario personalizado para el registro de usuarios-----------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

#-----------formulario para escaneos-----------
#----------VALIDADOR PARA IP O DOMINIO personalizado-----------

def validate_ip_or_domain(value): 
    # Intentar validar como IPv4
    try:
        validate_ipv4_address(value)
        return
    except ValidationError:
        pass
    
    # Intentar validar como IPv6
    try:
        validate_ipv6_address(value)
        return
    except ValidationError:
        pass
    
    # Validar como dominio
    domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if re.match(domain_pattern, value):
        return
    
    # Si no es ninguno, error
    raise ValidationError('Ingresa una IP válida (IPv4/IPv6) o un dominio válido')


MODULE_CHOICES = [
    ('nmap', 'Nmap'),
    ('dns', 'DNS'),
    ('dorks', 'Dorks'),
]

class ScanForm(forms.Form):
    target = forms.CharField(label="Dominio o IP", max_length=100, validators=[validate_ip_or_domain])
    modules = forms.MultipleChoiceField(
        choices=MODULE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,  # Cambiar a True
        error_messages={'required': 'Debes seleccionar al menos un módulo'}

    )