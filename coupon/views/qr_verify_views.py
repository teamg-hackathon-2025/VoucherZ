from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import DatabaseError
from django.utils import timezone
import logging

from coupon.models import Coupon, CouponCode
from account.models import Store
logger = logging.getLogger(__name__)


class CouponQrVerifyView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # 1. JSからQRコードを取得
        code = kwargs.get('coupon_uuid')
        if not code:
            return JsonResponse({'error':'クーポンコードが指定されていません'}, status=400)

        # 2. sessionからstore_idを取得
        store_id = request.session.get('store_id')
        if not store_id:
            return JsonResponse({'error': '店舗情報が取得できません'}, status=400)

        # 3. 店舗の存在確認
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return JsonResponse({'error': '該当する店舗が存在しません'}, status=400)
        except DatabaseError:
            return JsonResponse({'error': 'システムエラーが発生しました'}, status=500)
        except Exception:
            return JsonResponse({'error': '予期せぬエラー'}, status=500)

        # 4. store_id,クーポンコード・UUIDを引数にクーポン情報を取得する
        try:
            coupon_code = CouponCode.get_coupon_code(store_id, code=None, uuid=code)
        except DatabaseError:
            return JsonResponse({'error': 'システムエラーが発生しました'}, status=500)
        except Exception:
            return JsonResponse({'error': '予期せぬエラー'}, status=500)
        if coupon_code is None: # 対象店舗のクーポンではない場合
            return JsonResponse({'error': '無効なクーポンコードです'}, status=400)
        if coupon_code.redeemed_at:
            return JsonResponse({'error': 'このクーポンは既に使用されています'}, status=400)
        
        # 5. Couponの情報と照合
        try:
            coupon_id = coupon_code.coupon_id
            coupon = Coupon.get_coupon(coupon_id)
        except DatabaseError:
            return JsonResponse({'error': 'システムエラーが発生しました'}, status=500)
        except Exception:
            return JsonResponse({'error': '予期せぬエラー'}, status=500)
        if coupon.deleted_at:
            return JsonResponse({'error': 'このクーポンは終了しています'}, status=400)
        if coupon.expiration_date and coupon.expiration_date < timezone.now().date():
            return JsonResponse({'error': f"期限切れ：クーポンの有効期限は{coupon.expiration_date.strftime("%Y年%-m月%-d日")}までです。"}, status=400)
        
        coupon_code.redeemed_at = timezone.now()
        coupon_code.save()

        coupon.redeemed_count += 1
        coupon.save()        

        return JsonResponse({
            'success': True,
            'target_product': coupon.target_product,
            'discount': coupon.discount,
            'coupon_code': code
            })
