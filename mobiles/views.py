from users.models import RecentlyViewed
from users.models import CompareHistory
from django.http import JsonResponse
from .models import MobileVariant, PriceHistory
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.db.models import Count, Min
import json
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db.models import Q
from django.shortcuts import get_object_or_404
from mobiles.models import Mobile, MobileVariant
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.db.models import (
    Q,
    Min,
    Max,
    Value
)

from django.db.models.functions import (
    Concat,
    Lower,
    Replace
)

from django.core.paginator import Paginator

from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

from .models import (
    Mobile,
    MobileVariant,
    MobilePrice,
    Wishlist,
    PriceHistory,
    PriceAlert
)


# =========================
# MOBILE LIST (MAIN PAGE)
# =========================

def mobile_list(request):

    mobiles = (
        Mobile.objects
        .prefetch_related('variants__prices')
        .annotate(
            seller_count=Count(
                'variants__prices__seller',
                distinct=True
            )
        )
    )

    # =====================
    # SMART SEARCH
    # =====================

    query = request.GET.get(
        'q',
        ''
    ).strip()

    if query:

        cleaned_query = (
            query.replace(" ", "").lower()
        )

        mobiles = mobiles.annotate(

            full_name=Concat(
                'brand',
                Value(' '),
                'model_name'
            ),

            full_name_clean=Replace(
                Lower(
                    Concat(
                        'brand',
                        Value(' '),
                        'model_name'
                    )
                ),
                Value(' '),
                Value('')
            )

        ).filter(

            Q(full_name__icontains=query) |

            Q(
                full_name_clean__icontains=
                cleaned_query
            )

        )

    # =====================
    # FILTERS
    # =====================

    brand = request.GET.get('brand')

    ram = request.GET.get('ram')

    price_range = request.GET.get('price_range')

    sort = request.GET.get('sort')

    if brand:

        mobiles = mobiles.filter(
            brand__iexact=brand
        )

    if ram:

        mobiles = mobiles.filter(
            variants__ram=ram
        )

    # =====================
    # PRICE ANNOTATION
    # =====================

    mobiles = mobiles.annotate(

        min_price_val=Min(
            'variants__prices__final_price'
        ),

        max_price_val=Max(
            'variants__prices__list_price'
        )

    )

    if price_range:
        min_p, max_p = map(int, price_range.split('-'))

        mobiles = mobiles.filter(min_price_val__gte=min_p)

        if max_p != 100000:
            mobiles = mobiles.filter(min_price_val__lte=max_p)

    # =====================
    # SORT
    # =====================

    # SORT

    if sort == "price_low":

        mobiles = mobiles.order_by('min_price_val')

    elif sort == "price_high":

        mobiles = mobiles.order_by('-min_price_val')

    elif sort == "best_deals":

        mobiles = mobiles.annotate(
            discount_amount=F('max_price_val') - F('min_price_val')
        ).order_by('-discount_amount')

    elif sort == "price_drops":

        mobiles = mobiles.annotate(
            discount_amount=F('max_price_val') - F('min_price_val')
        ).order_by('-discount_amount')

    elif sort == "most_compared":

        mobiles = mobiles.order_by('-seller_count')

    elif sort == "recent":

        # mobiles = mobiles.order_by('-updated_at')
        mobiles = mobiles.order_by('-created_at')

    else:

        mobiles = mobiles.order_by(
            '-seller_count',
            '-min_price_val'
        )

    mobiles = mobiles.distinct()

    # =====================
    # PAGINATION
    # =====================

    paginator = Paginator(
        mobiles,
        12
    )

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(
        page_number
    )

    for m in page_obj:
        if m.max_price_val and m.min_price_val:
            m.savings = int(m.max_price_val) - int(m.min_price_val)
        else:
            m.savings = 0

    # =====================
    # BRANDS
    # =====================

    brands = Mobile.objects.values_list(
        'brand',
        flat=True
    ).distinct()

    # =====================
    # WISHLIST
    # =====================

    wishlist_mobile_ids = []

    if request.user.is_authenticated:

        wishlist_mobile_ids = list(
            Wishlist.objects.filter(
                user=request.user
            ).values_list(
                'mobile_id',
                flat=True
            )
        )

    # =====================
    # CONTEXT
    # =====================

    context = {

        'page_obj': page_obj,

        'brands': brands,

        'total_count': mobiles.count(),

        'search_query': query,

        'wishlist_mobile_ids': wishlist_mobile_ids,

        'brand': brand,

        'ram': ram,

        'price_range': price_range,

        'sort': sort,
    }

    # =====================
    # AJAX
    # =====================

    if request.headers.get(
        'x-requested-with'
    ) == 'XMLHttpRequest':

        return render(
            request,
            'mobiles/partials/mobile_list_partial.html',
            context
        )

    # =====================
    # NORMAL
    # =====================

    return render(
        request,
        'mobiles/mobile_list.html',
        context
    )


# =========================
# AUTOCOMPLETE
# =========================

def autocomplete(request):

    query = request.GET.get(
        'q',
        ''
    ).strip()

    results = []

    if query:

        cleaned_query = (
            query.replace(" ", "").lower()
        )

        mobiles = (

            Mobile.objects.annotate(

                full_name=Concat(
                    'brand',
                    Value(' '),
                    'model_name'
                ),

                full_name_clean=Replace(
                    Lower(
                        Concat(
                            'brand',
                            Value(' '),
                            'model_name'
                        )
                    ),
                    Value(' '),
                    Value('')
                )

            )

            .filter(

                Q(full_name__icontains=query) |

                Q(
                    full_name_clean__icontains=
                    cleaned_query
                )

            )

            .values(
                'brand',
                'model_name'
            )

            .distinct()

        )[:8]

        for m in mobiles:

            name = (
                f"{m['brand'].title()} "
                f"{m['model_name'].title()}"
            )

            results.append({

                'name': name,

                'url': f"/?q={name}"

            })

    return JsonResponse(
        results,
        safe=False
    )


# =========================
# SEARCH
# =========================

def mobile_search(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    mobiles = Mobile.objects.all()

    if query:

        mobiles = mobiles.filter(

            Q(brand__icontains=query) |

            Q(model_name__icontains=query)

        )

    paginator = Paginator(
        mobiles,
        12
    )

    page_obj = paginator.get_page(
        request.GET.get('page')
    )



    return render(
        request,
        "mobiles/mobile_list.html",
        {
            "page_obj": page_obj,
            "search_query": query,
            "total_count": mobiles.count()
        }
    )


# =========================
# MOBILE COMPARE
# =========================

def mobile_compare(request, model_number):
    try:
        mobile = Mobile.objects.get(model_number=model_number)
    except Mobile.DoesNotExist:
        variant = get_object_or_404(MobileVariant, slug=model_number)
        mobile = variant.mobile

    variants = MobileVariant.objects.filter(
        mobile=mobile
    ).prefetch_related(
        "prices",
        "price_history"
    )

    selected_color = request.GET.get("color")
    selected_ram = request.GET.get("ram")
    selected_storage = request.GET.get("storage")

    all_colors = sorted(
        set(v.color for v in variants if v.color)
    )

    selected_variant = None

    # user manually selected variant
    if selected_color and selected_ram and selected_storage:

        selected_variant = variants.filter(
            color=selected_color,
            ram=selected_ram,
            storage=selected_storage
        ).first()

    # smart default → best seller variant
    if not selected_variant:

        best_variant = None
        best_seller_count = -1

        for variant in variants:

            seller_count = variant.prices.values(
                'seller'
            ).distinct().count()

            if seller_count > best_seller_count:
                best_seller_count = seller_count
                best_variant = variant

        selected_variant = best_variant or variants.first()

    # keep UI synced
    selected_color = selected_variant.color

    color_variants = variants.filter(
        color=selected_color
    )

    variant_options = color_variants.order_by(
        "ram",
        "storage"
    )

    # if user selected RAM/storage within chosen color
    if selected_ram and selected_storage:

        manual_variant = variant_options.filter(
            ram=selected_ram,
            storage=selected_storage
        ).first()

        if manual_variant:
            selected_variant = manual_variant

    for v in variant_options:
        v.best_price = (
            v.prices
            .filter(final_price__isnull=False)
            .order_by('final_price')
            .first()
        )

        if v.best_price and v.best_price.list_price:
            v.best_price.discount_amount = (
                v.best_price.list_price - v.best_price.final_price
            )
        else:
            v.best_price.discount_amount = 0

    # =========================
    # HERO IMAGE
    # =========================
    hero_image = None

    if selected_variant:

        hero_image = (
            selected_variant.prices
            .filter(
                img_url__isnull=False
            )
            .exclude(
                img_url=""
            )
            .order_by("-customer_rating", "final_price")
            .first()
        )

        # SELLER DISCOUNT
        seller_prices = selected_variant.prices.all()

        for price in seller_prices:
            if price.list_price and price.final_price:
                price.discount_amount = int(
                    price.list_price - price.final_price
                )
            else:
                price.discount_amount = 0

    # =========================
    # WISHLIST
    # =========================
    wishlist_mobile_ids = []

    if request.user.is_authenticated:
        wishlist_mobile_ids = list(
            Wishlist.objects.filter(
                user=request.user
            ).values_list(
                "mobile_id",
                flat=True
            )
        )

    # =========================
    # PRICE INTELLIGENCE
    # =========================
    history = selected_variant.price_history.order_by("captured_at")

    history_prices = [h.price for h in history]

    lowest_price = None
    highest_price = None
    average_price = None
    price_trend = "Not enough data"
    price_change_percent = None
    buy_signal = "Not enough data"
    buy_advice = "More tracking data needed."

    if history_prices:

        lowest_price = min(history_prices)
        highest_price = max(history_prices)
        average_price = round(sum(history_prices) / len(history_prices))

        latest_price = history_prices[-1]
        earliest_price = history_prices[0]

        if len(history_prices) >= 2:

            if latest_price < earliest_price:
                price_trend = "Falling ↓"

            elif latest_price > earliest_price:
                price_trend = "Rising ↑"

            else:
                price_trend = "Stable"

        else:
            price_trend = "Stable"

        if latest_price <= average_price:
            buy_signal = "Buy Soon"
            buy_advice = (
                "Current price is below historical average. Good time to buy."
            )
        else:
            buy_signal = "Wait for Drop"
            buy_advice = (
                "Current price is above historical average. Waiting may help."
            )

    return render(
        request,
        'mobiles/mobile_compare.html',
        {
            'mobile': mobile,
            'variants': variants,
            'selected_variant': selected_variant,
            'selected_color': selected_color,
            'all_colors': all_colors,
            'variant_options': variant_options,
            'hero_image': hero_image,
            'wishlist_mobile_ids': wishlist_mobile_ids,

            'lowest_price': lowest_price,
            'highest_price': highest_price,
            'average_price': average_price,
            'price_trend': price_trend,
            'price_change_percent': price_change_percent,
            'buy_signal': buy_signal,
            'buy_advice': buy_advice,
        }
    )

# =========================
# TOGGLE WISHLIST
# =========================
@login_required
def toggle_wishlist(request, slug):

    variant = get_object_or_404(
        MobileVariant,
        slug=slug
    )

    mobile = variant.mobile

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        mobile=mobile
    )

    added = False

    if wishlist_item.exists():

        wishlist_item.delete()

        added = False

    else:

        Wishlist.objects.create(
            user=request.user,
            mobile=mobile
        )

        added = True

    # AJAX RESPONSE
    if request.headers.get(
        'x-requested-with'
    ) == 'XMLHttpRequest':

        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

        return JsonResponse({

            'success': True,

            'added': added,

            'wishlist_count': wishlist_count
        })

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            '/'
        )
    )

# =========================
# WISHLIST PAGE
# =========================

# =========================
# WISHLIST PAGE
# =========================

@login_required
def wishlist_page(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        'mobile'
    ).prefetch_related(
        'mobile__variants__prices'
    )

    valid_items = []

    for item in wishlist_items:

        mobile = item.mobile

        best_variant = (
            mobile.variants
            .annotate(
                seller_count=Count('prices')
            )
            .order_by(
                '-seller_count',
                'prices__final_price'
            )
            .first()
        )

        if best_variant:

            prices = best_variant.prices.all()

            min_price = prices.order_by(
                'final_price'
            ).first()

            max_price = prices.order_by(
                '-list_price'
            ).first()

            item.best_variant = best_variant

            item.mobile.min_price_val = (
                min_price.final_price if min_price else None
            )

            item.mobile.max_price_val = (
                max_price.list_price if max_price else None
            )

            if (
                item.mobile.max_price_val and
                item.mobile.min_price_val
            ):
                item.mobile.savings = (
                    int(item.mobile.max_price_val)
                    -
                    int(item.mobile.min_price_val)
                )
            else:
                item.mobile.savings = 0

            valid_items.append(item)

    return render(
        request,
        'mobiles/wishlist.html',
        {
            'wishlist_items': valid_items
        }
    )

# =========================
# MULTI COMPARE PAGE
# =========================
def compare_page(request):

    mobile_slugs = request.GET.get(
        'mobiles',
        ''
    )

    if not mobile_slugs:

        return render(
            request,
            'mobiles/compare.html',
            {
                'variants': []
            }
        )

    slug_list = [
        slug.strip()
        for slug in mobile_slugs.split(',')
        if slug.strip()
    ]

    variants = list(
        MobileVariant.objects.filter(
            slug__in=slug_list
        ).select_related(
            'mobile'
        ).prefetch_related(
            'prices'
        )
    )

    for variant in variants:

        variant.best_price = (
            variant.prices
            .filter(
                final_price__isnull=False
            )
            .order_by('final_price')
            .first()
        )

    # SMART COMPARISON VALUES
    prices = [
        v.best_price.final_price
        for v in variants
        if v.best_price
    ]

    rams = [
        int(str(v.ram_gb).split()[0])
        for v in variants
        if v.ram_gb
    ]

    storages = [
        int(str(v.storage_gb).split()[0])
        for v in variants
        if v.storage_gb
    ]

    batteries = [
        v.mobile.battery_capacity
        for v in variants
        if v.mobile.battery_capacity
    ]

    best_values = {
        'lowest_price': min(prices) if prices else None,
        'highest_ram': max(rams) if rams else None,
        'highest_storage': max(storages) if storages else None,
        'highest_battery': max(batteries) if batteries else None,
    }

    if request.user.is_authenticated and len(variants) >= 2:

        compare_data = {
            "user": request.user,
            "mobile_1": variants[0],
            "mobile_2": variants[1],
        }

        if len(variants) >= 3:
            compare_data["mobile_3"] = variants[2]

        already_exists = CompareHistory.objects.filter(
            user=request.user,
            mobile_1=variants[0],
            mobile_2=variants[1]
        )

        if len(variants) >= 3:
            already_exists = already_exists.filter(
                mobile_3=variants[2]
            )
        else:
            already_exists = already_exists.filter(
                mobile_3__isnull=True
            )

        if not already_exists.exists():
            CompareHistory.objects.create(**compare_data)

    return render(
        request,
        'mobiles/compare.html',
        {
            'variants': variants,
            'best_values': best_values
        }
    )

def price_history_api(request, slug):

    try:
        variant = MobileVariant.objects.get(slug=slug)

        selected_range = request.GET.get("range", "all")

        history = variant.price_history.order_by("captured_at")

        if selected_range != "all":
            try:
                days = int(selected_range)
                cutoff = timezone.now() - timedelta(days=days)
                history = history.filter(captured_at__gte=cutoff)
            except:
                pass

        grouped = defaultdict(list)

        for row in history:
            grouped[row.seller.lower()].append({
                "date": row.captured_at.strftime("%d %b"),
                "price": row.price
            })

        return JsonResponse(grouped)

    except MobileVariant.DoesNotExist:
        return JsonResponse({})

@login_required
def create_price_alert(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        })

    try:
        data = json.loads(request.body)

        variant_id = data.get("variant_id")
        target_price = data.get("target_price")

        if not variant_id or not target_price:
            return JsonResponse({
                "success": False,
                "message": "Missing data"
            })

        variant = MobileVariant.objects.get(
            id=variant_id
        )

        alert, created = PriceAlert.objects.get_or_create(
            user=request.user,
            variant=variant,
            target_price=int(target_price),
            defaults={
                "is_active": True
            }
        )

        if not created:
            alert.is_active = True
            alert.save()

        return JsonResponse({
            "success": True,
            "created": created,
            "message": (
                "Price alert created 🔔"
                if created
                else "You already have this alert"
            )
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })
    
@login_required
def delete_price_alert(request, alert_id):

    try:
        alert = PriceAlert.objects.get(
            id=alert_id,
            user=request.user
        )

        alert.delete()

    except PriceAlert.DoesNotExist:
        pass

    return redirect("alerts_dashboard")

# =========================
# STATIC PAGES
# =========================
def about_page(request):
    return render(
        request,
        "mobiles/static_page.html",
        {
            "page_title": "About Nexovio",
            "page_content": """
Nexovio is a smart mobile price comparison platform built to help buyers compare prices, track price trends, and make smarter purchase decisions.

We monitor trusted sellers, provide price intelligence, and simplify mobile buying decisions.
"""
        }
    )


def contact_page(request):
    return render(
        request,
        "mobiles/static_page.html",
        {
            "page_title": "Contact Us",
            "page_content": """
Need help, found incorrect pricing, or want to collaborate?

Email us at:
nexovioapp@gmail.com

We’d love to hear from you.
"""
        }
    )


def privacy_page(request):
    return render(
        request,
        "mobiles/static_page.html",
        {
            "page_title": "Privacy Policy",
            "page_content": """
Nexovio respects your privacy.

We only collect information required to provide account access, wishlist features, and price alerts.

We do not sell personal user data.

Third-party seller links may redirect you to external websites with their own privacy policies.
"""
        }
    )


def terms_page(request):
    return render(
        request,
        "mobiles/static_page.html",
        {
            "page_title": "Terms of Use",
            "page_content": """
Nexovio provides mobile price comparison and informational services.

Prices may change without notice depending on seller updates.

Users should verify final pricing directly with the seller before purchase.

Nexovio is not the seller of listed products.
"""
        }
    )


def help_page(request):
    return render(
        request,
        "mobiles/static_page.html",
        {
            "page_title": "Help Center",
            "page_content": """
Frequently asked questions:

How does Nexovio compare prices?
We monitor seller listings and show available pricing.

How do price alerts work?
Set a target price and get notified when pricing drops.

Why do some products show fewer sellers?
Seller availability changes dynamically.

“Still need help? Contact us”
Email us at:
nexovioapp@gmail.com
"""
        }
    )


def report_price_page(request):
    return render(
        request,
        "mobiles/static_page.html",
        {
            "page_title": "Report Wrong Price",
            "page_content": """
Found incorrect pricing or broken seller links?

Please email:
nexovioapp@gmail.com

Include product name and issue details.
"""
        }
    )

