from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

# ==========================
# MOBILE (PRODUCT LEVEL)
# ==========================
class Mobile(models.Model):
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    model_number = models.CharField(max_length=50, blank=True, null=True)

    processor = models.CharField(max_length=100, blank=True, null=True)
    battery_capacity = models.IntegerField(blank=True, null=True)

    screen_size = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    screen_type = models.CharField(max_length=50, blank=True, null=True)

    operating_system = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("brand", "model_name", "model_number")

    def __str__(self):
        return f"{self.brand} {self.model_name}"


# ==========================
# MOBILE VARIANT
# ==========================
class MobileVariant(models.Model):
    mobile = models.ForeignKey(
        Mobile,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    color = models.CharField(max_length=50)

    ram = models.IntegerField(help_text="RAM in MB")
    storage = models.IntegerField(help_text="Storage in MB")

    primary_camera = models.CharField(max_length=100, blank=True, null=True)
    secondary_camera = models.CharField(max_length=50, blank=True, null=True)

    slug = models.SlugField(unique=True, blank=True)

    @property
    def ram_gb(self):
        if self.ram:
            return f"{self.ram // 1024} GB"
        return ""

    @property
    def storage_gb(self):
        if self.storage:
            return f"{self.storage // 1024} GB"
        return ""

    class Meta:
        unique_together = ("mobile", "color", "ram", "storage")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.mobile.brand}-{self.mobile.model_name}-{self.color}-{self.ram}-{self.storage}"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mobile} ({self.ram} / {self.storage} - {self.color})"


# ==========================
# MOBILE PRICE
# ==========================
class MobilePrice(models.Model):
    variant = models.ForeignKey(
        MobileVariant,
        on_delete=models.CASCADE,
        related_name="prices"
    )

    seller = models.CharField(max_length=50)

    product_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    product_title = models.TextField(blank=True, null=True)
    img_url = models.URLField(blank=True, null=True)

    list_price = models.IntegerField(blank=True, null=True)
    final_price = models.IntegerField(blank=True, null=True)

    customer_rating = models.FloatField(blank=True, null=True)
    availability = models.CharField(max_length=20, default="in stock")

    product_url = models.URLField(blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.variant} - {self.seller}"

class PriceHistory(models.Model):
    variant = models.ForeignKey(
        MobileVariant,
        on_delete=models.CASCADE,
        related_name="price_history"
    )

    seller = models.CharField(max_length=50)

    price = models.IntegerField()

    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["captured_at"]

    def __str__(self):
        return f"{self.variant} - {self.seller} - ₹{self.price}"

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    mobile = models.ForeignKey(
        Mobile,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'mobile')

    def __str__(self):
        return f"{self.user} - {self.mobile}"

class PriceAlert(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="price_alerts"
    )

    variant = models.ForeignKey(
        MobileVariant,
        on_delete=models.CASCADE,
        related_name="price_alerts"
    )

    target_price = models.IntegerField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    triggered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = (
            "user",
            "variant",
            "target_price"
        )

    def __str__(self):
        return (
            f"{self.user.username} alert for "
            f"{self.variant} @ ₹{self.target_price}"
        )
    