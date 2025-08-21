import logging
import string
import random
import uuid
from django.db.models import F

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
    redeemed_count = models.IntegerField(default=0, editable=False)
    issued_count = models.IntegerField(default=0, editable=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = "coupons"
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"{self.title} ({self.store.store_name})"

    @classmethod
    def create(cls, store_id, title, discount, target_product, message, expiration_date, max_issuance):
        """
        新しいクーポンを作成する
        Args:
            store_id(int): クーポンを紐づける店舗ID
            title(str): クーポン名のタイトル
            discount(str): 割引率
            target_product(str): 割引対象商品の識別情報
            message(str): メッセージ
            expiration_date(date): クーポンの有効期限
            max_issuance(int): 発行数の上限
        Returns:
            Coupon: 正常に作成された場合、作成した Coupon インスタンス
            raise: 作成に失敗した場合（DBエラー、例外発生など）
        """
        try:
            with transaction.atomic():
                coupon = cls.objects.create(
                    store_id=store_id,
                    title=title,
                    discount=discount,
                    target_product=target_product,
                    message=message,
                    expiration_date=expiration_date,
                    max_issuance=max_issuance,
                )
            return coupon
        except DatabaseError as e:
            logger.error(
                f"[Coupon][create] DatabaseError: Error: {e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[Coupon][create] Unexpected error: Error: {e}"
            )
            raise

    @classmethod
    def get_store_user_id(cls, coupon_id):
        """
        指定されたクーポンIDに紐づく店舗ユーザーのIDを取得する
        Args:
            coupon_id (int): 取得対象のクーポンID
        Returns:
            user_id: 該当クーポンが存在する場合、関連する店舗ユーザーのID（UUID）。
            None: 存在しない場合
        Raises:
            DatabaseError: データベース操作中にエラーが発生した場合
            Exception: その他の予期しないエラーが発生した場合
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
                f"[Coupon][StoreUserIdFetch] Not found: coupon_id={coupon_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Coupon][StoreUserIdFetch] Database error: coupon_id={coupon_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[Coupon][StoreUserIdFetch] Unexpected error: coupon_id={coupon_id}, error={e}"
            )
            raise

    @classmethod
    def get_for_expiration_check(cls, coupon_id):
        """
        指定されたクーポンIDに対応するクーポン情報（有効期限のみフィールド取得）
        Args:
            coupon_id (int): 取得対象のクーポンID
        Returns:
            coupon: 存在する場合、Couponインスタンス
                （expiration_dateのみ）。
            None: 存在しない場合
        Raises:
            DatabaseError: データベース操作中にエラーが発生した場合
            Exception: その他の予期しないエラーが発生した場合
        """
        try:
            coupon_for_expiration_date = (
                cls.objects
                .only("expiration_date")
                .get(id=coupon_id)
            )
            return coupon_for_expiration_date
        except cls.DoesNotExist:
            logger.warning(
                f"[Coupon][ExpirationCheck] Not found: coupon_id={coupon_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Coupon][ExpirationCheck] Database error: coupon_id={coupon_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[Coupon][ExpirationCheck] Unexpected error: coupon_id={coupon_id}, error={e}"
            )
            raise

    @classmethod
    def get_for_issuance_check(cls, coupon_id):
        """
        指定されたクーポンIDに対応するクーポン情報（発行数チェック用のみフィールド取得）
        Args:
            coupon_id (int): 取得対象のクーポンID
        Returns:
            coupon: 存在する場合、Couponインスタンス
                （max_issuance, issued_countのみ）。
            None: 存在しない場合
        Raises:
            DatabaseError: データベース操作中にエラーが発生した場合
            Exception: その他の予期しないエラーが発生した場合
        """
        try:
            coupon_for_issuance_check = (
                cls.objects
                .only("max_issuance", "issued_count")
                .get(id=coupon_id)
            )
            return coupon_for_issuance_check
        except cls.DoesNotExist:
            logger.warning(
                f"[Coupon][IssuanceCheck] Not found: coupon_id={coupon_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Coupon][IssuanceCheck] Database error: coupon_id={coupon_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[Coupon][IssuanceCheck] Unexpected error: coupon_id={coupon_id}, error={e}"
            )
            raise

    @classmethod
    def get_coupon(cls, coupon_id):
        """
        指定されたクーポンIDに対応するクーポン情報（店舗名付き）を取得する
        Args:
            coupon_id (int): 取得対象のクーポンID
        Returns:
            coupon: 存在する場合、Couponインスタンス（store情報付き）。
            None: 存在しない、複数件見つかった、またはDBエラーの場合
        Raises:
            DatabaseError: データベース操作でエラーが発生した場合
            Exception: 上記以外の予期しないエラーが発生した場合
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
                f"[Coupon][DetailFetch] Not found: coupon_id={coupon_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Coupon][DetailFetch] Database error: coupon_id={coupon_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[Coupon][DetailFetch] Unexpected error: coupon_id={coupon_id}, error={e}"
            )
            raise


class CouponCode(models.Model):
    store_id = models.BigIntegerField()
    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.CASCADE,
        related_name='coupon_codes',
        db_column='coupon_id',
    )
    coupon_code = models.CharField(max_length=6, editable=False)
    coupon_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    redeemed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

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

    @staticmethod
    def generate_code(length=6):
        """
        指定された長さのランダムなクーポンコードを生成する
        Args:
            length (int): 生成するクーポンコードの文字数（デフォルト: 6）
        Returns:
            str: 英大文字と数字からなるランダムなクーポンコード
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=length))

    @classmethod
    def issue(cls, coupon_id, length=6, max_retries=10):
        """
        指定されたクーポンIDに対応するクーポンコードを発行する
        Args:
            coupon_id(int): 発行対象のクーポンID
        Returns:
            coupon_code: 存在すれば CouponCode インスタンス（store情報付き）
            None: クーポンが存在しない場合、リトライ上限に達した場合、その他のDBエラー
        Raises:
            DatabaseError: データベース操作に失敗した場合
            Exception: 予期しないエラーが発生した場合
        """
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            logger.warning(
                f"[CouponCode][Issue] Not found: coupon_id={coupon_id}"
            )
            return None
        for _ in range(max_retries):
            code = cls.generate_code(length)
            try:
                with transaction.atomic():
                    # クーポンコード発行
                    coupon_code = cls.objects.create(
                        coupon=coupon,
                        store_id=coupon.store_id,
                        coupon_code=code
                    )
                    # 発行数を +1
                    Coupon.objects.filter(id=coupon_id).update(
                        issued_count=F('issued_count') + 1
                    )
                    return coupon_code
            except IntegrityError:
                continue
            except DatabaseError as e:
                logger.error(
                    f"[CouponCode][Issue] DatabaseError: coupon_id={coupon_id}. Error: {e}"
                )
                raise
            except Exception as e:
                logger.exception(
                    f"[CouponCode][Issue] Unexpected error: coupon_id={coupon_id}. Error: {e}"
                )
                raise

        logger.error(
            f"[CouponCode][Issue] Failed to issue after {max_retries} retries: coupon_id={coupon_id}"
        )
        return None

    @classmethod
    def get_coupon_id_by_id(cls, coupon_code_id):
        """
        指定されたクーポンコードIDに対応するクーポンIDを取得
        Args:
            coupon_code_id (int): 取得対象のクーポンコードID
        Returns:
            coupon_id: 存在する場合、クーポンID
            None: 存在しない場合。
        Raises:
            DatabaseError: データベース操作でエラーが発生した場合
            Exception: その他の予期しないエラーが発生した場合
        """
        try:
            coupon_id = (
                cls.objects
                .values_list("coupon", flat=True)
                .get(id=coupon_code_id)
            )
            return coupon_id
        except cls.DoesNotExist:
            logger.warning(
                f"[CouponCode][RelationFetch] Not found: coupon_code_id={coupon_code_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[CouponCode][RelationFetch] Database error: coupon_code_id={coupon_code_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[CouponCode][RelationFetch] Unexpected error: coupon_code_id={coupon_code_id}, error={e}"
            )
            raise

    @classmethod
    def get_coupon_id_by_code_uuid(cls, coupon_code_uuid):
        """
        指定されたクーポンコードのUUIDに対応するクーポンIDを取得
        Args:
            coupon_code_uuid (uuid): 取得対象のクーポンコードのUUID
        Returns:
            coupon_id: 存在する場合、クーポンID
            None: 存在しない場合。
        Raises:
            DatabaseError: データベース操作でエラーが発生した場合
            Exception: その他の予期しないエラーが発生した場合
        """
        try:
            coupon_id = (
                cls.objects
                .values_list("coupon", flat=True)
                .get(coupon_uuid=coupon_code_uuid)
            )
            return coupon_id
        except cls.DoesNotExist:
            logger.warning(
                f"[CouponCode][RelationFetch] Not found: coupon_code_uuid={coupon_code_uuid}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[CouponCode][RelationFetch] Database error: coupon_code_uuid={coupon_code_uuid}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[CouponCode][RelationFetch] Unexpected error: coupon_code_uuid={coupon_code_uuid}, error={e}"
            )
            raise

    @classmethod
    def get_coupon_code_by_id(cls, coupon_code_id):
        """
        指定されたクーポンコードIDに対応するクーポンコード情報を取得する
        Args:
            coupon_code_id (int): 取得対象のクーポンID
        Returns:
            coupon_code: 存在する場合、CouponCodeインスタンス。
            None: 存在しない場合
        Raises:
            DatabaseError: データベース操作でエラーが発生した場合
            Exception: その他の予期しないエラーが発生した場合
        """
        try:
            coupon_code = cls.objects.get(id=coupon_code_id)
            return coupon_code
        except cls.DoesNotExist:
            logger.warning(
                f"[CouponCode][DetailFetch] Not found: coupon_code_id={coupon_code_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[CouponCode][DetailFetch] Database error: coupon_code_id={coupon_code_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[CouponCode][DetailFetch] Unexpected error: coupon_code_id={coupon_code_id}, error={e}"
            )
            raise

    @classmethod
    def get_coupon_code_by_code_uuid(cls, coupon_code_uuid):
        """
        指定されたクーポンコードUUIDに対応するクーポンコード情報を取得する
        Args:
            coupon_code_uuid (uuid): 取得対象のクーポンUUID
        Returns:
            coupon_code: 存在する場合、CouponCodeインスタンス。
            None: 存在しない場合
        Raises:
            DatabaseError: データベース操作でエラーが発生した場合
            Exception: その他の予期しないエラーが発生した場合
        """
        try:
            coupon_code = cls.objects.get(coupon_uuid=coupon_code_uuid)
            return coupon_code
        except cls.DoesNotExist:
            logger.warning(
                f"[CouponCode][DetailFetch] Not found: coupon_code_uuid={coupon_code_uuid}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[CouponCode][DetailFetch] Database error: coupon_code_uuid={coupon_code_uuid}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[CouponCode][DetailFetch] Unexpected error: coupon_code_uuid={coupon_code_uuid}, error={e}"
            )
            raise
