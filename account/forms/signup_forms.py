from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def no_whitespace_validator(value):
    if ' ' in value:
        raise ValidationError(
            "パスワードに空白を含めることはできません。",
        )


class SignUpForm(forms.Form):
    user_name = forms.CharField(
        label='名前（ニックネーム）',
        max_length=255, # Userモデルのmax_lengthに合わせる
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': '例: 山田 太郎（ニックネーム可）'}),
    )
    store_name = forms.CharField(
        label='店舗名',
        max_length=255, # モデルのmax_lengthに合わせる
        widget=forms.TextInput(attrs={'placeholder': '例: 〇〇商店'})
    )
    email = forms.EmailField(
        label='Eメール',
        widget=forms.EmailInput(attrs={'placeholder': '例：yourname@example.com'})
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'placeholder': '半角英数字8文字以上'}),
        validators=[no_whitespace_validator]
    )
    password_confirm = forms.CharField(
        label='パスワード（確認用）',
        widget=forms.PasswordInput(attrs={'placeholder': 'もう一度パスワードを入力'}),
        validators=[no_whitespace_validator]
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("このメールアドレスはすでに登録されています。")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', 'パスワードが一致しません。')

            try:
                validate_password(password, user=None)
            except ValidationError as e:
                self.add_error('password', e)


        return cleaned_data
