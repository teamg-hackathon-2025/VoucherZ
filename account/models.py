import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class Store(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='stores',
        db_column='user_id',
    )

    store_name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'stores'
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.store_name
