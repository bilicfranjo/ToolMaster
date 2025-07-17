from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Product, DIYVideo, Banner, Category, ProductAttribute, ProductImage
from django.forms import modelformset_factory, inlineformset_factory


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Korisničko ime',
            'email': 'Email',
            'password1': 'Lozinka',
            'password2': 'Ponovi lozinku'
        }
        help_texts = {field: '' for field in fields}
        error_messages = {
            'username': {
                'required': _("Unesi korisničko ime."),
            },
            'email': {
                'required': _("Unesi email adresu."),
                'invalid': _("Unesi ispravnu email adresu."),
            },
            'password1': {
                'required': _("Unesi lozinku."),
            },
            'password2': {
                'required': _("Ponovi lozinku."),
            },
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("To korisničko ime je već registrirano.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Taj email je već registriran.")
        return email
    
    

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Korisničko ime')
    password = forms.CharField(label='Lozinka', widget=forms.PasswordInput)
    
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'manufacturer', 'model','slug', 'price', 'image', 'description', 'in_stock', 'popular']
        labels = {
            'name': 'Naziv proizvoda',
            'category': 'Kategorija',
            'manufacturer': 'Proizvođač',
            'model': 'Model',
            'slug': 'Slug (opcionalno)',
            'price': 'Cijena (€)',
            'image': 'Glavna slika',
            'description': 'Opis proizvoda',
            'in_stock': 'Na stanju',
            'popular': 'Popularan proizvod?',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        

ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=('image',),
    extra=1,
    labels={'image': 'Dodatna slika'}
)


class DIYVideoForm(forms.ModelForm):
    class Meta:
        model = DIYVideo
        fields = ['title', 'description', 'video', 'thumbnail', 'video_thumbnail', 'tools_used']
        labels = {
            'title': 'Naslov',
            'description': 'Opis',
            'video': 'Video datoteka',
            'thumbnail': 'Slika (thumbnail)',
            'video_thumbnail': 'Video thumbnail (slika za početak)',
            'tools_used': 'Korišteni alati',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tools_used': forms.SelectMultiple(attrs={'class': 'form-select select2'}),
        }
        
           
class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'link']
        labels = {
            'title': 'Naslov bannera',
            'image': 'Slika bannera',
            'link': 'Poveznica',
        }
        widgets = {
            'link': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent', 'image', 'featured']
        labels = {
            'name': 'Naziv kategorije',
            'slug': 'Slug (automatski ako se ne unese)',
            'parent': 'Roditeljska kategorija (opcionalno)',
            'image': 'Slika',
            'featured': 'Istaknuta na početnoj stranici?',
        }

ProductAttributeFormSet = modelformset_factory(
    ProductAttribute,
    fields=('name',),
    extra=1,
    can_delete=True,
    labels={'name': 'Naziv atributa'}
)


class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(label="Broj mobitela", required=False)
    address = forms.CharField(label="Adresa", required=False, widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Korisničko ime',
            'email': 'Email',
        }
        help_texts = {
            'username': '',
            'email': '',
        }

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)
        self.fields['phone'].initial = self.profile.phone
        self.fields['address'].initial = self.profile.address

    def save(self, commit=True):
        user = super().save(commit)
        self.profile.phone = self.cleaned_data['phone']
        self.profile.address = self.cleaned_data['address']
        if commit:
            self.profile.save()
        return user


class CheckoutForm(forms.Form):
    use_profile_address = forms.BooleanField(required=False, label='Koristi svoju adresu')
    shipping_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label='Unesi drugu adresu')

    use_profile_phone = forms.BooleanField(required=False, label='Koristi svoj broj')
    phone = forms.CharField(required=False, label='Unesi drugi broj')