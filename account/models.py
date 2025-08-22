import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError, models
import logging

logger = logging.getLogger(__name__)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, user_name=None):
        """
        ユーザーを作成するためのメソッド。
        Args:
            email (str): ユーザーのメールアドレス。
            password (str): ユーザーのパスワード。
        Returns:
            user: 作成されたユーザーオブジェクト。
        Raises:
            ValueError: メールアドレスが提供されない場合。
            ValidationError: パスワードの強度が不十分な場合。
            IntegrityError: 同じメールアドレスを持つユーザーが既に存在する場合。
        """

        if not email:
            logger.warning("User creation failed: Email not provided.")
            raise ValueError("メールアドレスが必要です。")

        try:
            validate_password(password)
        except ValidationError as e:
            logger.warning(f"User creation failed for email={email}: Password validation failed. Errors: {e.messages}") 
            raise # ValidationErrorを再発生させる

        email = self.normalize_email(email)
        user = self.model(email=email)

        if user_name:
            user.user_name = user_name

        user.set_password(password)

        try:
            user.save(using=self._db) # save()メソッドが呼び出され、user_nameが自動生成される
        except IntegrityError:
            logger.warning(f"User creation failed for email={email}: Email already exists.")
            raise IntegrityError("このメールアドレスはすでに登録されています。")
        except DatabaseError as e:
            logger.exception(f"Database error during user creation for email={email}: {e}")
            raise # その他のデータベースエラーを再発生させる
        except Exception as e:
            logger.exception(f"Unexpected error during user creation for email={email}: {e}")
            raise # その他の予期せぬエラーを再発生させる
        
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False)
    user_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    last_login = None

    USERNAME_FIELD = "email" # ログインはemailで行う
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    user_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_login = None

    USERNAME_FIELD = "email" # ログインはemailで行う
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = "users"
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
    
    # saveメソッドをオーバーライドしてuser_nameを自動生成
    def save(self, *args, **kwargs):
        # user_nameが未設定の場合のみ自動生成を試みる
        if not self.user_name:
            try:
                self.user_name = self._generate_pre_username()
            except Exception as e:
                # user_name生成失敗時のエラーハンドリング。
                # 今回は自動生成が失敗したら、DBに空文字で保存される
                logger.error(f"Failed to generate user_name for email={self.email}. Saving with empty user_name. Error: {e}")
                self.user_name = ""
        
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Unexpected error during user object save for email={self.email}: {e}")
            raise

    def _generate_pre_username(self):
        # メールアドレスからuser_nameを作成
        pre_username = self.email.split('@')[0][:10] # メールアドレスの@より前10文字
        return pre_username

    # saveメソッドをオーバーライドしてuser_nameを自動生成
    def save(self, *args, **kwargs):
        # user_nameが未設定の場合のみ自動生成を試みる
        if not self.user_name: 
            try:
                self.user_name = self._generate_pre_username()
            except Exception as e:
                # user_name生成失敗時のエラーハンドリング。
                # 今回は自動生成が失敗したら、DBに空文字で保存される
                logger.error(f"Failed to generate user_name for email={self.email}. Saving with empty user_name. Error: {e}")
                self.user_name = ""
        
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Unexpected error during user object save for email={self.email}: {e}")
            raise

    def _generate_pre_username(self):
        # メールアドレスからuser_nameを作成
        pre_username = self.email.split('@')[0][:10] # メールアドレスの@より前10文字
        return pre_username


class Store(models.Model):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='store',
        db_column='user_id',
    )

    store_name = models.CharField(max_length=255, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = 'stores'
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.store_name

    @classmethod
    def get_store_id_for_user(cls, user_id):
        """
        指定されたユーザーIDに紐づく店舗のIDを1件取得する
        Args:
            user_id (UUID): 取得対象のユーザーID
        Returns:
            store_id: 該当ユーザーに紐づく店舗ID
            None: 存在しない場合
            raise: 複数件見つかった、DBエラー、予期しないエラーの場合
        """
        try:
            store_id = (
                cls.objects
                .values_list('id', flat=True)
                .get(user=user_id)
            )
            return store_id
        except cls.DoesNotExist:
            logger.warning(
                f"[Store][GetStoreId] Not found: user_id={user_id}"
            )
            return None
        except cls.MultipleObjectsReturned as e:
            logger.error(
                f"[Store][GetStoreId] Multiple stores found: user_id={user_id}, error={e}"
            )
            raise
        except DatabaseError as e:
            logger.error(
                f"[Store][GetStoreId] Database error: user_id={user_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[Store][GetStoreId] Unexpected error: user_id={user_id}, error={e}"
            )
            raise

    @classmethod
    def get_store_name(cls, store_id):
        """
        指定された店舗IDに紐づく店舗名を取得する
        Args:
            store_id (int): 取得対象の店舗ID
        Returns:
            store_name: 店舗IDに紐づく店舗名
            None: 存在しない場合
            raise: DBエラー、予期しないエラーの場合
        """
        try:
            store_name = (
                cls.objects
                .values_list("store_name", flat=True)
                .get(id=store_id)
            )
            return store_name
        except cls.DoesNotExist:
            logger.warning(
                f"[Store][GetStoreName] Not found: store_id={store_id}"
            )
            return None
        except DatabaseError as e:
            logger.error(
                f"[Store][GetStoreName] Database error: store_id={store_id}, error={e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"[Store][GetStoreName] Unexpected error: store_id={store_id}, error={e}"
            )
            raise
