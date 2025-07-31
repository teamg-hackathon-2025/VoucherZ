from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from account.forms.validators import no_whitespace_validator


User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Eメール",
        widget=forms.EmailInput(attrs={
            'autofocus': True, 
            'placeholder': '例：yourname@example.com'
            })
    )
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={'placeholder': '半角英数字8文字以上'}),
        strip=False, # Djangoが自動で空白を削除しないように設定
        validators=[no_whitespace_validator]
    )
