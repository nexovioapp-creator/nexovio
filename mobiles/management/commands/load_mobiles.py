from django.core.management.base import BaseCommand
from django.db import transaction
from mobiles.models import Mobile, MobileVariant
import csv


def clean(val):
    if not val:
        return None
    val = val.replace("\ufeff", "").strip().lower()
    return val if val else None


def to_int(val):
    try:
        return int(val)
    except:
        return None


class Command(BaseCommand):
    help = "Load mobiles + variants (header-based CSV)"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options["file"]

        inserted_mobile = 0
        inserted_variant = 0
        skipped = 0

        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="}")

            for row_no, row in enumerate(reader, start=2):
                try:
                    # --------------------------
                    # CLEAN VALUES
                    # --------------------------
                    brand = clean(row.get("brand"))
                    model_name = clean(row.get("model_name"))
                    model_number = clean(row.get("model_number"))

                    color = clean(row.get("color"))
                    ram = to_int(row.get("ram"))
                    storage = to_int(row.get("storage"))

                    processor = clean(row.get("processor"))
                    battery = to_int(row.get("battery_capacity"))

                    # --------------------------
                    # VALIDATION
                    # --------------------------
                    if not all([brand, model_name, color, ram, storage]):
                        skipped += 1
                        continue

                    # --------------------------
                    # CREATE MOBILE
                    # --------------------------
                    mobile, created = Mobile.objects.get_or_create(
                        brand=brand,
                        model_name=model_name,
                        model_number=model_number,
                        defaults={
                            "processor": processor,
                            "battery_capacity": battery,
                        }
                    )

                    if created:
                        inserted_mobile += 1

                    # --------------------------
                    # CREATE VARIANT
                    # --------------------------
                    _, v_created = MobileVariant.objects.get_or_create(
                        mobile=mobile,
                        color=color,
                        ram=ram,
                        storage=storage,
                    )

                    if v_created:
                        inserted_variant += 1

                except Exception as e:
                    skipped += 1
                    self.stdout.write(f"❌ ROW {row_no}: {e}")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            f"Mobiles: {inserted_mobile} | Variants: {inserted_variant} | Skipped: {skipped}"
        )
        