from django.views.generic import DetailView
from django.http import Http404
from django.utils import timezone
import logging

from ..models import Coupon, CouponCode
logger = logging.getLogger(__name__)


class CouponCodeCustomerView(DetailView):
    template_name = "coupon/detail-code-customer.html"

    def get_object(self):
        """
        URLパスからクーポンコードUUIDを取得し、対応するクーポン情報を返す
        Returns:
            dict: {"coupon_code": CouponCode, "coupon": Coupon}
        Raises:
            Http404: 対応するcoupon_idやクーポンコードまたはクーポンが存在しない場合
        """
        coupon_code_uuid = self.kwargs.get("coupon_code_uuid")
        coupon_id = CouponCode.get_coupon_id_by_code_uuid(coupon_code_uuid)
        if coupon_id is None:
            raise Http404()

        coupon_code = CouponCode.get_coupon_code_by_code_uuid(coupon_code_uuid)
        if coupon_code is None:
            raise Http404()

        coupon = Coupon.get_coupon(coupon_id)
        if coupon is None:
            raise Http404()
        return {"coupon_code": coupon_code, "coupon": coupon}

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡すコンテキスト変数を設定する。
        self.object が dict（coupon, coupon_code を含む）の場合、
        その中身を context に展開してテンプレートで直接使えるようにする。
        Returns:
            dict: テンプレートに渡すコンテキスト（coupon, coupon_code などを含む）
        """
        context = super().get_context_data(**kwargs)
        if isinstance(self.object, dict):
            context.update(self.object)
        # 今日の日付を追加
        context["today"] = timezone.localdate()
        return context
