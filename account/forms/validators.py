from django.core.exceptions import ValidationError

def no_whitespace_validator(value):
    if ' ' in value:
        raise ValidationError(
            "パスワードに空白を含めることはできません。",
        )
