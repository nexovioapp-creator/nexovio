from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone

from mobiles.models import PriceAlert


class Command(BaseCommand):
    help = "Check active price alerts and send notifications"


    def handle(self, *args, **kwargs):

        alerts = PriceAlert.objects.filter(
            is_active=True
        ).select_related(
            "user",
            "variant"
        )

        sent_count = 0

        for alert in alerts:

            current_prices = alert.variant.prices.all()

            if not current_prices.exists():
                continue

            best_price = min(
                p.final_price for p in current_prices
                if p.final_price
            )

            if best_price <= alert.target_price:

                send_mail(
                    subject="🔔 Nexovio Price Alert Triggered!",
                    message=(
                        f"Good news {alert.user.username},\n\n"
                        f"{alert.variant.mobile.brand} "
                        f"{alert.variant.mobile.model_name}\n"
                        f"has dropped to ₹{best_price}.\n\n"
                        f"Your target price was ₹{alert.target_price}.\n\n"
                        f"Visit Nexovio now."
                    ),
                    from_email=None,
                    recipient_list=[alert.user.email],
                    fail_silently=False
                )

                alert.is_active = False
                alert.triggered_at = timezone.now()
                alert.save()

                sent_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Sent {sent_count} alerts."
            )
        )
        