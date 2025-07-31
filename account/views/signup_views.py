from django.views.generic.edit import FormView
from account.forms.signup_forms import SignUpForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
import logging
from account.models import Store
from django.db import transaction

logger = logging.getLogger(__name__)

# AUTH_USER_MODEL = 'account.User'を適用
User = get_user_model()

class SignUpView(FormView):
    template_name = "account/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("coupon:coupon_list")

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        store_name = form.cleaned_data['store_name']

        try:
            # トランザクションを開始(user,storeどちらも作成成功したら完了)
            with transaction.atomic():
                # CustomUserManagerのcreate_userを呼び出す
                # raise：メール重複、パスワードバリデーション、DBエラー、予期せぬエラー
                # メール重複、パスワードバリデーションは予期せぬケースへのセーフティネットとして記述
                user = User.objects.create_user(email=email, password=password)
                Store.objects.create(user=user, store_name=store_name)

            return super().form_valid(form)
        except IntegrityError:
            # このメールアドレスはすでに登録されています（CustomUserManagerから再発生）
            # フォームにエラーを追加して再レンダリングする
            form.add_error('email', "このメールアドレスはすでに登録されています。")
            return self.form_invalid(form)
        except ValidationError as e:
            # パスワードバリデーションエラー（CustomUserManagerから再発生）
            form.add_error('password', e.messages)
            return self.form_invalid(form)
        except DatabaseError as e:
            logger.exception(f"Database error during user signup for email={email}: {e}")
            # 本番では500エラーページにリダイレクトする
            raise # HttpResponseServerError() 
        except Exception as e:
            logger.exception(f"Unexpected error during user signup for email={email}: {e}")
            raise #  HttpResponseServerError() など
