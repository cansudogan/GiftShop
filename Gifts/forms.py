from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

'''
    Kullanıcıya doldurması için vereceğimiz formu burda customize ediyoruz
'''
class UserRegistrationForm(forms.Form):
    username = forms.CharField(
        required=True,
        label='Kullanıcı Adı',
        max_length=150
    )
    first_name = forms.CharField(
        label='İsim',
        max_length=30
    )
    last_name = forms.CharField(
        label='Soyisim',
        max_length=30
    )
    email = forms.CharField(
        required=True,
        label='Email',
        max_length=150
    )
    password = forms.CharField(
        required=True,
        label='Parola',
        max_length=128,
        widget=forms.PasswordInput()
    )
    address = forms.CharField(
        required=True,
        label='Adres',
        max_length=100
    )

    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
            raise forms.ValidationError("Username or password exists")


class UserLoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label='Kullanıcı Adı',
        max_length=150
    )
    password = forms.CharField(
        required=True,
        label='Parola',
        max_length=128,
        widget=forms.PasswordInput()
    )

class UserEditForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        label='İsim',
        max_length=30,
    )
    last_name = forms.CharField(
        required=True,
        label='Soyisim',
        max_length=30,
    )

    email = forms.CharField(
        required=True,
        label='Email',
        max_length=150
    )
    address = forms.CharField(
        required=True,
        label='Adres',
        max_length=100
    )

class ReportForm(forms.Form):
    STATUS_CHOICES = (
                    (1, ("Dilek")),
                    (2, ("Şikayet")),
                    )
    type = forms.ChoiceField(choices=STATUS_CHOICES, label="Dilek/Şikayet", required=True)
    content = forms.CharField(
        required=True,
        label="Bize iletin",
        max_length=512,
        widget=forms.Textarea(attrs={'cols': 60, 'rows': 5})
        )
