import requests

from django.core.cache import cache

GEOIP_URL = "https://api.country.is/{ip}"
GEOIP_TIMEOUT = 2
GEOIP_HIT_TIMEOUT = 60 * 60 * 24
GEOIP_MISS_TIMEOUT = 60 * 5


def get_client_ip(request):
    """Client IP, trusting the first value of the nginx X-Forwarded-For header."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "").strip()


def get_country_code(request):
    """ISO country code of the request IP, empty string when unknown.

    Empty means "cannot tell": callers must treat it as a blocked visitor.
    """
    ip = get_client_ip(request)
    if not ip:
        return ""
    key = f"geoip:{ip}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        response = requests.get(GEOIP_URL.format(ip=ip), timeout=GEOIP_TIMEOUT)
        code = str(response.json()["country"]).strip().upper()
        valid = bool(response.ok and len(code) == 2 and code.isalpha())
    except (requests.RequestException, ValueError, KeyError, TypeError):
        valid, code = False, ""
    # shortcut: proxies/VPNs are invisible to IP geolocation, upgrade to a local
    # MaxMind DB only if that produces false positives.
    cache.set(key, code, GEOIP_HIT_TIMEOUT if valid else GEOIP_MISS_TIMEOUT)
    return code if valid else ""
