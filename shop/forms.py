from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Korisničko ime',
            'email': 'Email',
        }
        help_texts = {field: '' for field in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['password1'].label = 'Lozinka'
        self.fields['password2'].label = 'Ponovi lozinku'

        # Prevedene poruke grešaka
        self.error_messages.update({
            'password_mismatch': _("Lozinke se ne podudaraju."),
        })
        self.fields['username'].error_messages.update({
            'required': _("Unesi korisničko ime."),
            'unique': _("Korisničko ime je već zauzeto.")
        })
        self.fields['email'].error_messages.update({
            'required': _("Unesi email adresu."),
            'invalid': _("Unesi ispravnu email adresu."),
        })
        self.fields['password1'].error_messages.update({
            'required': _("Unesi lozinku."),
        })
        self.fields['password2'].error_messages.update({
            'required': _("Ponovi lozinku."),
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Taj email je već registriran.")
        return email
    
    

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Korisničko ime')
    password = forms.CharField(label='Lozinka')
    