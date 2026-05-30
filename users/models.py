from django.db import models
from django.db import models
from django.contrib.auth.models import User
from mobiles.models import MobileVariant


class RecentlyViewed(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recently_viewed"
    )

    mobile_variant = models.ForeignKey(
        MobileVariant,
        on_delete=models.CASCADE
    )

    viewed_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-viewed_at"]
        unique_together = (
            "user",
            "mobile_variant"
        )

    def __str__(self):
        return (
            f"{self.user.username} viewed "
            f"{self.mobile_variant.mobile.brand} "
            f"{self.mobile_variant.mobile.model_name}"
        )


class CompareHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="compare_history"
    )

    mobile_1 = models.ForeignKey(
        MobileVariant,
        on_delete=models.CASCADE,
        related_name="compare_mobile_1"
    )

    mobile_2 = models.ForeignKey(
        MobileVariant,
        on_delete=models.CASCADE,
        related_name="compare_mobile_2"
    )

    mobile_3 = models.ForeignKey(
        MobileVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="compare_mobile_3"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} compared mobiles"
        )

        