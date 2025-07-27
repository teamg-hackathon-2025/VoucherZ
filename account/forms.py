from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def no_whitespace_validator(value):
    if ' ' in value:
        raise ValidationError(
            "パスワードに空白を含めることはできません。",
        )

# 新規登録フォーム
class CustomUserCreationForm(UserCreationForm):
    store_name = forms.CharField(
        label="店舗名",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '例: 〇〇商店'})
    )
    email = forms.EmailField(
        label="Eメール",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': '例：yourname@example.com'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'username' in self.fields:
            self.fields['username'].label = "名前（ニックネーム）"
            self.fields['username'].widget = forms.TextInput(
                attrs={
                    'autofocus': True,
                    'placeholder': '例: 山田 太郎（ニックネーム可）'
                }
            )

        # password フィールドのplaceholderを変更
        if 'password' in self.fields:
            self.fields['password'].label = "パスワード"
            self.fields['password'].widget = forms.PasswordInput(
                attrs={'placeholder': '半角英数字8文字以上'}
            )
            self.fields['password'].strip = False # 空白を削除しない設定
            self.fields['password'].validators.append(no_whitespace_validator)

        # password2 フィールドのplaceholderを変更
        if 'password2' in self.fields:
            self.fields['password2'].label = "パスワード (確認用)"
            self.fields['password2'].widget = forms.PasswordInput(
                attrs={'placeholder': 'もう一度パスワードを入力'}
            )
            self.fields['password2'].strip = False # 空白を削除しない設定
            self.fields['password2'].validators.append(no_whitespace_validator)


    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは既に使用されています。")
        return email
    
    

# ログインフォーム
class CustomAuthenticationForm(AuthenticationForm):
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
