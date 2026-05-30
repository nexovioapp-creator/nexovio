from django.contrib import admin
from .models import Mobile, MobileVariant, MobilePrice


# ==========================
# MOBILE ADMIN (PRODUCT)
# ==========================
@admin.register(Mobile)
class MobileAdmin(admin.ModelAdmin):
    list_display = ("brand", "model_name", "model_number", "processor")
    search_fields = ("brand", "model_name", "model_number")


# ==========================
# VARIANT ADMIN
# ==========================
@admin.register(MobileVariant)
class MobileVariantAdmin(admin.ModelAdmin):
    list_display = ("mobile", "color", "ram", "storage")
    list_filter = ("color", "ram", "storage")
    search_fields = ("mobile__brand", "mobile__model_name")


# ==========================
# PRICE ADMIN
# ==========================
@admin.register(MobilePrice)
class MobilePriceAdmin(admin.ModelAdmin):
    list_display = ("variant", "seller", "final_price", "last_updated")
    list_filter = ("seller",)
    search_fields = ("variant__mobile__brand", "variant__mobile__model_name")
    