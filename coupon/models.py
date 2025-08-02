import logging
import string
import random

from django.db import models, DatabaseError, IntegrityError, transaction

logger = logging.getLogger(__name__)


class Coupon(models.Model):
    store = models.ForeignKey(
        'account.Store',
        on_delete=models.CASCADE,
        related_name='coupons',
        db_column='store_id',
    )
    title = models.CharField(max_length=255)
    discount = models.CharField(max_length=255)
    target_product = models.CharField(max_length=255)
    message = models.CharField(max_length=255, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    max_issuance = models.IntegerField(null=True, blank=True)
    redeemed_count = models.IntegerField(default=0)
    issued_count = models.IntegerField(default=0)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "coupons"
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"{self.title} ({self.store.store_name})"

    @classmethod
    def get_store_user_id(cls, coupon_id):
        """
        指定されたクーポンIDに紐づく店舗ユーザーのIDを取得する
        Args:
            coupon_id (int | UUID): 取得対象のクーポンID
        Returns:
            UUID | None:
            - 該当クーポンが存在する場合、関連する店舗ユーザーのID（UUID）。
            - 存在しない場合は None を返す。
        """
        try:
            user_id = (
                cls.objects
                .values_list('store__user_id', flat=True)
                .get(id=coupon_id)
            )
            return user_id
        except cls.DoesNotExist:
            # データ未存在
            logger.warning(f"[Coupon] Coupon not found: id={coupon_id}")
            return None

    @classmethod
    def get_coupon(cls, coupon_id):
        """
        指定されたクーポンIDに対応するクーポン情報（店舗名付き）を取得する
        Args:
            coupon_id(int): 取得対象のクーポンID
        Returns:
            Coupon | None:
            - 存在する場合 Coupon インスタンス（store情報付き）。
            - 存在しない、複数件見つかった、またはDBエラーの場合は None を返す。
        """
        try:
            coupon = (
                cls.objects
                .select_related("store")
                .get(id=coupon_id)
            )
            return coupon
        # 指定された ID のクーポンが存在しない場合は警告ログを出力し、None を返す
        except cls.DoesNotExist:
            # データ未存在エラー
            logger.warning(
                f"[Coupon] Coupon not found: id={coupon_id}"
            )
            return None
        # 同じ ID で複数件あった場合は整合性エラーとしてログ出力し、None を返す
        except cls.MultipleObjectsReturned as e:
            # データの整合性エラー
            logger.error(
                f"[Coupon] Data integrity issue: Multiple entries found for coupon_id={coupon_id}. Error: {e}"
            )
            return None
        # DBエラーはログに記録して None を返す
        except DatabaseError as e:
            # データベース関連のエラー
            logger.error(
                f"[Coupon] DatabaseError: coupon_id={coupon_id}. Error: {e}"
            )
            return None
        # 予期しないエラーもログに残して None を返す
        except Exception as e:
            # 予期しないエラーのキャッチ
            logger.exception(
                f"[Coupon] Unexpected error: coupon_id={coupon_id}. Error: {e}"
            )
            return None


class CouponCode(models.Model):
    store_id = models.BigIntegerField()
    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.CASCADE,
        related_name='coupon_codes',
        db_column='coupon_id',
    )
    coupon_code = models.CharField(max_length=6)
    redeemed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_unique_coupon_code(store_id, length=6):
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=length))
            if not CouponCode.objects.filter(store_id=store_id, coupon_code=code).exists():
                return code

    class Meta:
        db_table = "coupon_codes"
        verbose_name = "Coupon code"
        verbose_name_plural = "Coupon codes"
        constraints = [
            models.UniqueConstraint(
                fields=['store_id', 'coupon_code'],
                name='unique_store_couponcode'
            )
        ]

    def __str__(self):
        return f"{self.coupon_code} ({self.coupon.title})"

    @classmethod
    def issue(cls, coupon_id, length=6, max_retries=10):
        """
        指定されたクーポンIDに対応するクーポンコードを発行する
        Args:
            coupon_id(int): 発行対象のクーポンID
        Returns:
            Coupon | None:
            - 存在すれば Coupon インスタンス（store情報付き）。
            - 存在しない、複数件見つかった、またはDBエラーの場合は None を返す。
        """
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            logger.warning(f"[CouponCode.issue] Coupon not found: coupon_id={coupon_id}")
            return None
        for _ in range(max_retries):
            try:
                with transaction.atomic():
                    return cls.objects.create(
                        coupon=coupon,
                        store_id=coupon.store_id,
                        coupon_code=cls.generate_unique_coupon_code(coupon.store_id, length)
                    )
            except IntegrityError:
                continue
            except DatabaseError as e:
                logger.error(f"[CouponCode.issue] DatabaseError: coupon_id={coupon_id}. Error: {e}")
                return None
            except Exception as e:
                logger.exception(f"[CouponCode.issue] Unexpected error: coupon_id={coupon_id}. Error: {e}")
                return None

        logger.error(f"[CouponCode.issue] Failed to issue after {max_retries} retries: coupon_id={coupon_id}")
        return None

        # try:
        #     coupon_code = cls.objects.create(coupon=coupon_id)
        #     return coupon_code
        # # DBエラーはログに記録して None を返す
        # except DatabaseError as e:
        #     # データベース関連のエラー
        #     logger.error(
        #         f"[Coupon] DatabaseError: coupon_id={coupon_id}. Error: {e}"
        #     )
        #     return None
        # # 予期しないエラーもログに残して None を返す
        # except Exception as e:
        #     # 予期しないエラーのキャッチ
        #     logger.exception(
        #         f"[Coupon] Unexpected error: coupon_id={coupon_id}. Error: {e}"
        #     )
        #     return None