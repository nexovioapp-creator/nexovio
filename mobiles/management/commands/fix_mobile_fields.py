from django.core.management.base import BaseCommand
from mobiles.models import Mobile
import ast

# python manage.py fix_mobile_fields

class Command(BaseCommand):
    help = "Fix list-based fields into readable strings"

    def handle(self, *args, **kwargs):
        fixed = 0

        for m in Mobile.objects.all():
            try:
                if m.primary_camera and m.primary_camera.startswith("["):
                    cams = ast.literal_eval(m.primary_camera)
                    m.primary_camera = " + ".join(f"{c} MP" for c in cams)

                if m.resolution_type and m.resolution_type.startswith("["):
                    w, h = ast.literal_eval(m.resolution_type)
                    m.resolution_type = f"{w} x {h}"

                if m.network_type and m.network_type.startswith("["):
                    nets = ast.literal_eval(m.network_type)
                    m.network_type = " / ".join(nets)

                m.save()
                fixed += 1
            except Exception:
                continue

        self.stdout.write(self.style.SUCCESS(f"Fixed {fixed} records"))
