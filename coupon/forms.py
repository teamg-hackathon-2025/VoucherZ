from .models import Coupon
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import unicodedata
import re


class CouponForm(forms.ModelForm):
    no_max_issuance = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "id": "noMaxIssuance",
                "class": "input-checkbox"
            }
        )
    )
    no_expiration_date = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "id": "noExpirationDate",
                "class": "input-checkbox"
            }
        )
    )

    class Meta:
        model = Coupon
        fields = ["title", "discount", "target_product", "message", "expiration_date", "max_issuance"]
        widgets = {
            "title": forms.TextInput(attrs={
                "id": "title",
                "class": "input",
                "placeholder": "例）夏休みキャンペーン",
                "autofocus": True
            }),
            "target_product": forms.TextInput(attrs={
                "id": "targetProduct",
                "class": "input",
                "placeholder": "例）アイスクリーム"
            }),
            "discount": forms.TextInput(attrs={
                "id": "discount",
                "class": "input",
                "placeholder": "例）5% OFF, 100円引"
            }),
            "max_issuance": forms.TextInput(attrs={
                "id": "maxIssuance",
                "class": "input",
            }),
            "expiration_date": forms.TextInput(attrs={
                "id": "expirationDate",
                "class": "input js-flatpickr",
            }),
            "message": forms.Textarea(attrs={
                "id": "message",
                "class": "input",
                "placeholder": "お客様へのメッセージをこちらに入力できます。",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].error_messages["required"] = "タイトルを入力してください。"
        self.fields["target_product"].error_messages["required"] = "対象商品を入力してください。"
        self.fields["discount"].error_messages["required"] = "割引内容を入力してください。"
        self.fields["expiration_date"].widget.attrs["data-min"] = timezone.localdate().strftime("%Y-%m-%d")

    def clean_title(self):
        """
        タイトル欄のバリデーションを行う。

        Returns:
            str | None: バリデーション済みのタイトルの文字列
        Raises:
            ValidationError: タイトルが255文字を超えている場合
        """
        title = self.cleaned_data.get("title")
        if title is not None and len(title) > 255:
            raise ValidationError("タイトルは255文字以内で入力してください。")
        return title

    def clean_target_product(self):
        """
        対象商品欄のバリデーションを行う。

        Returns:
            str | None: バリデーション済みの対象商品の文字列
        Raises:
            ValidationError: 対象商品が255文字を超えている場合
        """
        target_product = self.cleaned_data.get("target_product")
        if target_product is not None and len(target_product) > 255:
            raise ValidationError("対象商品は255文字以内で入力してください。")
        return target_product

    def clean_discount(self):
        """
        割引内容欄のバリデーションを行う。

        Returns:
            str | None: バリデーション済みの割引内容の文字列
        Raises:
            ValidationError: 割引内容が255文字を超えている場合
        """
        discount = self.cleaned_data.get("discount")
        if discount is not None and len(discount) > 255:
            raise ValidationError("割引内容は255文字以内で入力してください。")
        return discount

    def clean_max_issuance(self):
        """
        発行数の上限欄のバリデーションを行う。

        Returns:
            int | None: バリデーション済みの発行数（整数）、または未入力時は None
        Raises:
            ValidationError: 半角数字以外が含まれている場合
        """
        max_issuance = self.cleaned_data.get("max_issuance")
        if not max_issuance:
            return max_issuance
        # 全角→半角
        max_issuance = unicodedata.normalize("NFKC", str(max_issuance))
        # 数字のみか判定
        if not re.match(r'^\d+$', max_issuance):
            raise forms.ValidationError("発行数の上限は半角数字のみで入力してください。")
        return int(max_issuance)

    def clean_expiration_date(self):
        """
        有効期限欄のバリデーションを行う。

        Returns:
            datetime.date | None: バリデーション済みの有効期限（日付）または None
        Raises:
            ValidationError: 今日より前の日付が入力された場合
        """
        expiration_date = self.cleaned_data.get("expiration_date")
        if expiration_date is None:
            return expiration_date
        today = timezone.localdate()
        if expiration_date < today:
            raise forms.ValidationError("有効期限には今日以降の日付を指定してください。")
        return expiration_date

    def clean_message(self):
        """
        メッセージ欄のバリデーションを行う。

        Returns:
            str | None: バリデーション済みのメッセージの文字列
        Raises:
            ValidationError: メッセージが255文字を超えている場合
        """
        message = self.cleaned_data.get("message")
        if message is not None and len(message) > 255:
            raise ValidationError("メッセージは255文字以内で入力してください。")
        return message

    def clean(self):
        """
        フォーム全体の相関バリデーションを行う。

        - 発行数の上限（max_issuance）と「無制限」（no_max_issuance）の両方が未入力の場合はエラー
        - 発行数の上限と「無制限」の両方が入力されている場合はエラー
        - 有効期限（expiration_date）と「無期限」（no_expiration_date）の両方が未入力の場合はエラー
        - 有効期限と「無期限」の両方が入力されている場合はエラー

        Returns:
            dict: バリデーション済みのフォームデータ
        """
        cleaned_data = super().clean()
        max_issuance = cleaned_data.get("max_issuance")
        no_max_issuance = cleaned_data.get("no_max_issuance")
        expiration_date = cleaned_data.get("expiration_date")
        no_expiration_date = cleaned_data.get("no_expiration_date")

        if not max_issuance and not no_max_issuance:
            self.add_error("max_issuance", "発行数の上限を入力するか、チェックを入れてください。")
        if max_issuance and no_max_issuance:
            self.add_error("max_issuance", "発行数の上限の入力とチェックは同時にできません。")
        if not expiration_date and not no_expiration_date:
            self.add_error("expiration_date", "有効期限を入力するか、チェックを入れてください。")
        if expiration_date and no_expiration_date:
            self.add_error("expiration_date", "有効期限の入力とチェックは同時にできません。")
        return cleaned_data
