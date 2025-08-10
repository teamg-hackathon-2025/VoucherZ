import logging

from django.db import models, DatabaseError

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
            coupon_id (int): 取得対象のクーポンID
        Returns:
            user_id: 該当クーポンが存在する場合、関連する店舗ユーザーのID（UUID）。
            None: 存在しない、DBエラー、予期しないエラーの場合
        """
        try:
            user_id = (
                cls.objects
                .values_list('store__user_id', flat=True)
                .get(id=coupon_id)
            )
            return user_id
        except cls.DoesNotExist:
            logger.warning(
                f"[Coupon][StoreUserIdFetch] Not found: id={coupon_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Coupon][StoreUserIdFetch] Database error: id={coupon_id}, error={e}"
            )
            return None
        except Exception as e:
            logger.exception(
                f"[Coupon][StoreUserIdFetch] Unexpected error: id={coupon_id}, error={e}"
            )
            return None

    @classmethod
    def get_for_status_check(cls, coupon_id):
        """
        指定されたクーポンIDに対応するクーポン情報（有効期限・発行数チェック用のみフィールド取得）
        Args:
            coupon_id (int): 取得対象のクーポンID
        Returns:
            coupon: 存在する場合、Couponインスタンス
                （expiration_date, max_issuance, issued_countのみ）。
            None: 存在しない、DBエラー、または予期しないエラーが発生した場合。
        """
        try:
            coupon_for_check = (
                cls.objects
                .only("expiration_date", "max_issuance", "issued_count")
                .get(id=coupon_id)
            )
            return coupon_for_check
        except cls.DoesNotExist:
            logger.warning(
                f"[Coupon][StatusCheck] Not found: id={coupon_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Coupon][StatusCheck] Database error: id={coupon_id}, error={e}"
            )
            return None
        except Exception as e:
            logger.exception(
                f"[Coupon][StatusCheck] Unexpected error: id={coupon_id}, error={e}"
            )
            return None

    @classmethod
    def get_coupon(cls, coupon_id):
        """
        指定されたクーポンIDに対応するクーポン情報（店舗名付き）を取得する
        Args:
            coupon_id (int): 取得対象のクーポンID
        Returns:
            coupon: 存在する場合、Couponインスタンス（store情報付き）。
            None: 存在しない、複数件見つかった、またはDBエラーの場合
        """
        try:
            coupon = (
                cls.objects
                .select_related("store")
                .get(id=coupon_id)
            )
            return coupon
        except cls.DoesNotExist:
            logger.warning(
                f"[Coupon][DetailFetch] Not found: id={coupon_id}"
            )
            return None
        except cls.MultipleObjectsReturned as e:
            logger.error(
                f"[Coupon][DetailFetch] Data integrity issue: id={coupon_id}, error={e}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Coupon][DetailFetch] Database error: id={coupon_id}, error={e}"
            )
            return None
        except Exception as e:
            logger.exception(
                f"[Coupon][DetailFetch] Unexpected error: id={coupon_id}, error={e}"
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

    def save(self, *args, **kwargs):
        if not self.pk:  # 新規作成時だけセット
            self.store_id = self.coupon.store_id
        super().save(*args, **kwargs)

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
