from django.core.management.base import BaseCommand
from mobiles.models import Mobile, MobileVariant, MobilePrice
import csv

# python manage.py load_mobile_prices mobile_price_final.csv

def clean(val):
    if not val:
        return None
    return val.replace("\ufeff", "").strip().lower()


def to_int(val):
    try:
        return int(val.strip())
    except:
        return None


class Command(BaseCommand):
    help = "Load mobile prices (FINAL - using model_number)"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        file_path = options["csv_file"]

        inserted = 0
        updated = 0
        skipped = 0

        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="}")

            for row_no, row in enumerate(reader, start=2):
                try:
                    # ---------------------------
                    # CLEAN INPUT
                    # ---------------------------
                    model_number = clean(row.get("model_number"))

                    ram = to_int(row.get("ram"))
                    storage = to_int(row.get("storage"))
                    color = clean(row.get("color"))

                    seller = clean(row.get("seller"))
                    product_id = row.get("product_id")

                    list_price = to_int(row.get("list_price"))
                    final_price = to_int(row.get("final_price"))

                    product_url = row.get("product_url")
                    img_url = row.get("img_url")
                    title = row.get("product_title")
                    rating = row.get("customer_rating")
                    availability = clean(row.get("availability")) or "in stock"

                    # ---------------------------
                    # VALIDATION
                    # ---------------------------
                    if not all([model_number, ram, storage, seller]):
                        skipped += 1
                        continue

                    # ---------------------------
                    # FIND MOBILE (UNIQUE MATCH)
                    # ---------------------------
                    mobile = Mobile.objects.filter(
                        model_number=model_number
                    ).first()

                    if not mobile:
                        print(f"❌ MOBILE NOT FOUND: {model_number}")
                        skipped += 1
                        continue

                    # ---------------------------
                    # FIND VARIANT
                    # ---------------------------
                    variant = MobileVariant.objects.filter(
                        mobile=mobile,
                        color=color,
                        ram=ram,
                        storage=storage,
                    ).first()

                    # fallback (rare case)
                    if not variant:
                        variant = MobileVariant.objects.filter(
                            mobile=mobile
                        ).first()

                    if not variant:
                        print(f"❌ VARIANT NOT FOUND: {model_number}")
                        skipped += 1
                        continue

                    # ---------------------------
                    # UPSERT PRICE
                    # ---------------------------
                    obj, created = MobilePrice.objects.update_or_create(
                        variant=variant,
                        seller=seller,
                        product_id=product_id,
                        defaults={
                            "final_price": final_price,
                            "list_price": list_price,
                            "product_url": product_url,
                            "img_url": img_url,
                            "product_title": title,
                            "customer_rating": float(rating) if rating else None,
                            "availability": availability,
                        }
                    )

                    # PRICE HISTORY TRACKING
                    if final_price:

                        from mobiles.models import PriceHistory

                        last_entry = PriceHistory.objects.filter(
                            variant=variant,
                            seller=seller
                        ).order_by("-captured_at").first()

                        if not last_entry or last_entry.price != final_price:

                            PriceHistory.objects.create(
                                variant=variant,
                                seller=seller,
                                price=final_price
                            )

                    if created:
                        inserted += 1
                        self.stdout.write(f"✅ ROW {row_no}: INSERTED")
                    else:
                        updated += 1
                        self.stdout.write(f"♻ ROW {row_no}: UPDATED")

                except Exception as e:
                    skipped += 1
                    self.stdout.write(f"❌ ROW {row_no}: {e}")

        # ---------------------------
        # FINAL OUTPUT
        # ---------------------------
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            f"DONE ✅ Inserted: {inserted} | Updated: {updated} | Skipped: {skipped}"
        )