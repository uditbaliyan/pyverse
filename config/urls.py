from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from pyverse.seo import CodingProblemSitemap
from pyverse.seo import LivePageSitemap
from pyverse.seo import robots_txt

SITEMAPS = {
    "pages": LivePageSitemap,
    "problems": CodingProblemSitemap,
}

urlpatterns = [
    # Crawler plumbing, in front of everything else so the Wagtail catch-all
    # below never swallows it. Both are what the static export freezes verbatim.
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap_views.sitemap,
        {"sitemaps": SITEMAPS},
        name="sitemap",
    ),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("pyverse.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # === ADD THIS LINE RIGHT HERE ===
    # This intercepts the reload event before Wagtail tries to catch it!
    path("__reload__/", include("django_browser_reload.urls")),
    # Your stuff: custom urls includes go here
    # ...
    #
    path("", include("pyverse.puput.urls")),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include(wagtail_urls)),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
