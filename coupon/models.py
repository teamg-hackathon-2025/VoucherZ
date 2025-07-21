from django.db import models
from account.model import Store


class Coupon(models.Model):
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    discount = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255, null=True, blank=True)
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


class CouponCode(models.Model):
    coupon_id = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=6)
    redeemed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "coupon_codes"
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'coupon_code'],
                name='unique_store_couponcode'
            )
        ]
