from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomSimilarityValidator:
    def validate(self, password, user=None):
        if user and user.username and user.username.lower() in password.lower():
            raise ValidationError(
                _("Lozinka je previše slična korisničkom imenu."),
                code='password_too_similar',
            )

    def get_help_text(self):
        return _("Lozinka ne smije biti previše slična korisničkom imenu.")


class CustomMinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Lozinka je prekratka. Mora imati barem %(min_length)d znakova."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("Lozinka mora imati najmanje %(min_length)d znakova.") % {'min_length': self.min_length}


class CustomCommonPasswordValidator:
    def validate(self, password, user=None):
        common_passwords = ["123456", "12345678", "password",  "lozinka", "admin"]
        if password.lower() in common_passwords:
            raise ValidationError(
                _("Lozinka je previše jednostavna. Odaberi složeniju."),
                code='password_too_common',
            )

    def get_help_text(self):
        return _("Izbjegavaj najčešće lozinke poput '123456' ili 'password'.")


class CustomNumericPasswordValidator:
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Lozinka ne smije sadržavati samo brojeve."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _("Lozinka ne smije biti sastavljena samo od brojeva.")
