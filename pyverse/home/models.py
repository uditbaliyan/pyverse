from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import InlinePanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.admin.panels import PageChooserPanel
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.contrib.settings.models import register_setting
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.models import Page
from wagtail.search import index

# ════════════════════════════════════════════════════════════
#  ABSTRACT MIXINS
# ════════════════════════════════════════════════════════════


class SEOFields(models.Model):
    """Shared OG-image field so every page type can control its social preview."""

    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Shown when this page is shared on Twitter, LinkedIn, etc. "
        "Falls back to the default in Site Settings if left blank.",
    )

    class Meta:
        abstract = True


class LinkFields(models.Model):
    """Reusable pattern: internal page OR external URL, with new-tab flag."""

    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    link_external = models.URLField(
        blank=True,
        help_text="Override: use this URL instead of the page chosen above.",
    )
    open_in_new_tab = models.BooleanField(default=False)

    link_panels = [
        PageChooserPanel("link_page"),
        FieldPanel("link_external"),
        FieldPanel("open_in_new_tab"),
    ]

    class Meta:
        abstract = True

    @property
    def url(self):
        if self.link_external:
            return self.link_external
        if self.link_page:
            return self.link_page.url
        return "#"


# ════════════════════════════════════════════════════════════
#  SITE SETTINGS  (navbar · footer · global SEO)
# ════════════════════════════════════════════════════════════


class NavItem(LinkFields, Orderable):
    """One link in the top navigation bar."""

    settings = ParentalKey(
        "home.SiteSettings",
        on_delete=models.CASCADE,
        related_name="nav_items",
    )
    label = models.CharField(max_length=80)

    panels = [FieldPanel("label"), *LinkFields.link_panels]

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.label


class FooterLink(LinkFields, Orderable):
    """One link in the site footer."""

    settings = ParentalKey(
        "home.SiteSettings",
        on_delete=models.CASCADE,
        related_name="footer_links",
    )
    label = models.CharField(max_length=100)
    column = models.CharField(
        max_length=80,
        blank=True,
        help_text=(
            "Group heading. Links with the same column name are grouped together."
        ),
    )

    panels = [FieldPanel("label"), FieldPanel("column"), *LinkFields.link_panels]

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.label


@register_setting
class SiteSettings(BaseSiteSetting, ClusterableModel):
    """Edit at  /cms/settings/home/sitesettings/"""

    # ── branding ──────────────────────────────────────────
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Uploaded logo (shown beside or instead of text)",
    )
    logo_text = models.CharField(
        max_length=30,
        blank=True,
        default="PYVERSE.",
        help_text="Fallback text logo when no image is uploaded",
    )

    # ── navbar CTA ────────────────────────────────────────
    nav_cta_text = models.CharField(
        max_length=50,
        blank=True,
        default="START SESSION",
    )
    nav_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    nav_cta_external = models.URLField(blank=True)

    # ── footer ────────────────────────────────────────────
    footer_tagline = models.CharField(
        max_length=200,
        blank=True,
        default="PYVERSE POSTER BUILD · ALL MODULES RUN CLIENT-SIDE",
    )
    footer_subline = models.CharField(
        max_length=200,
        blank=True,
        default="NO SERVER, NO WAIT",
    )
    social_github = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_discord = models.URLField(blank=True)

    # ── global SEO fallback ───────────────────────────────
    default_og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Used when a page has no og_image set",
    )

    # ── panels ────────────────────────────────────────────
    panels = [
        MultiFieldPanel(
            [FieldPanel("logo"), FieldPanel("logo_text")],
            heading="Branding",
        ),
        MultiFieldPanel(
            [
                InlinePanel("nav_items", label="Nav Items", min_num=1),
                FieldPanel("nav_cta_text"),
                PageChooserPanel("nav_cta_link"),
                FieldPanel("nav_cta_external"),
            ],
            heading="Navbar",
        ),
        MultiFieldPanel(
            [
                FieldPanel("footer_tagline"),
                FieldPanel("footer_subline"),
                InlinePanel("footer_links", label="Footer Links"),
                FieldPanel("social_github"),
                FieldPanel("social_twitter"),
                FieldPanel("social_discord"),
            ],
            heading="Footer",
        ),
        MultiFieldPanel(
            [FieldPanel("default_og_image")],
            heading="SEO Defaults",
        ),
    ]

    @property
    def nav_cta_url(self):
        if self.nav_cta_external:
            return self.nav_cta_external
        if self.nav_cta_link:
            return self.nav_cta_link.url
        return "#"

    class Meta:
        verbose_name = "Site Settings"


# ════════════════════════════════════════════════════════════
#  HOME PAGE  —  orderable children
# ════════════════════════════════════════════════════════════


class ModuleCard(LinkFields, Orderable):
    """One card in the module grid on the homepage."""

    page = ParentalKey(
        "home.HomePage",
        on_delete=models.CASCADE,
        related_name="modules",
    )

    num = models.CharField(max_length=10, help_text="e.g. 01, 02, MX")
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=200)
    diff = models.CharField(
        max_length=30,
        blank=True,
        help_text="e.g. EASY · MEDIUM · HARD",
    )
    src = models.CharField(max_length=200, help_text="Source path, e.g. builtins.list")

    panels = [
        FieldPanel("num"),
        FieldPanel("title"),
        FieldPanel("desc"),
        FieldPanel("diff"),
        FieldPanel("src"),
        MultiFieldPanel(LinkFields.link_panels, heading="Link Target"),
    ]

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class StatItem(Orderable):
    """One number + label pair for the social-proof strip."""

    page = ParentalKey("home.HomePage", on_delete=models.CASCADE, related_name="stats")
    number = models.CharField(max_length=50, help_text="e.g. 10,000+")
    label = models.CharField(max_length=100, help_text="e.g. Active Learners")

    panels = [FieldPanel("number"), FieldPanel("label")]

    class Meta:
        ordering = ["sort_order"]


# ════════════════════════════════════════════════════════════
#  HOME PAGE
# ════════════════════════════════════════════════════════════


class HomePage(SEOFields, Page):
    subpage_types = [
        "lms.LMSIndexPage",
        "labs.LabsIndexPage",
        "puput.BlogFolderPage",
        "home.StandardPage",
        "topics.PracticeHubPage",
    ]
    max_count = 1

    # ── hero ──────────────────────────────────────────────
    hero_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Main H1 headline. HTML allowed for styling, e.g. "
        'PY<br>VERSE<span class="text-red">.</span>',
    )
    hero_side_text = models.CharField(
        max_length=80,
        blank=True,
        default="READ THE STACK, NOT THE GUESS",
        help_text="Vertical text bar on the left (desktop only). Leave blank to hide.",
    )
    hero_subtitle = models.CharField(
        max_length=500,
        blank=True,
        help_text="Paragraph below the headline",
    )
    hero_primary_cta_text = models.CharField(
        max_length=100,
        blank=True,
        default="START SESSION",
    )
    hero_primary_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_primary_cta_external = models.URLField(blank=True)
    hero_secondary_cta_text = models.CharField(
        max_length=100,
        blank=True,
        default="VIEW MODULES",
    )
    hero_secondary_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_secondary_cta_external = models.URLField(blank=True)

    # ── device mockup ─────────────────────────────────────
    device_code = models.TextField(
        blank=True,
        help_text=(
            "Plain-text code shown in the device screen. Separate lines with Enter."
        ),
    )
    device_model_label = models.CharField(
        max_length=60,
        blank=True,
        default="MODEL // PV-01",
    )

    # ── social proof ──────────────────────────────────────
    stats_heading = models.CharField(
        max_length=200,
        blank=True,
        default="By the numbers",
    )

    # ── search ────────────────────────────────────────────
    search_fields = [
        *Page.search_fields,
        index.SearchField("hero_subtitle"),
    ]

    # ── panels ────────────────────────────────────────────
    content_panels = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("hero_text"),
                FieldPanel("hero_side_text"),
                FieldPanel("hero_subtitle"),
                MultiFieldPanel(
                    [
                        FieldPanel("hero_primary_cta_text"),
                        PageChooserPanel("hero_primary_cta_link"),
                        FieldPanel("hero_primary_cta_external"),
                    ],
                    heading="Primary CTA (filled button)",
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("hero_secondary_cta_text"),
                        PageChooserPanel("hero_secondary_cta_link"),
                        FieldPanel("hero_secondary_cta_external"),
                    ],
                    heading="Secondary CTA (outlined button)",
                ),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [FieldPanel("device_code"), FieldPanel("device_model_label")],
            heading="Device Mockup",
        ),
        MultiFieldPanel(
            [
                FieldPanel("stats_heading"),
                InlinePanel("stats", label="Stats", max_num=4),
            ],
            heading="Social Proof Strip",
        ),
        InlinePanel("modules", label="Module Cards", min_num=1),
        MultiFieldPanel(
            [FieldPanel("og_image")],
            heading="SEO / Social Sharing",
        ),
    ]

    class Meta:
        verbose_name = "Home Page"

    def __str__(self):
        return self.title

    # ── helpers ───────────────────────────────────────────
    @property
    def primary_cta_url(self):
        if self.hero_primary_cta_external:
            return self.hero_primary_cta_external
        if self.hero_primary_cta_link:
            return self.hero_primary_cta_link.url
        return "#modules"

    @property
    def secondary_cta_url(self):
        if self.hero_secondary_cta_external:
            return self.hero_secondary_cta_external
        if self.hero_secondary_cta_link:
            return self.hero_secondary_cta_link.url
        return "#modules"


# ════════════════════════════════════════════════════════════
#  STANDARD PAGE  (About, Research, Privacy, Terms …)
# ════════════════════════════════════════════════════════════


class StandardPage(SEOFields, Page):
    """max_count removed — you can now create as many as you need."""

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    subtitle = models.CharField(max_length=255, blank=True)
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = RichTextField(blank=True)

    search_fields = [*Page.search_fields, index.SearchField("body")]

    content_panels = [
        *Page.content_panels,
        FieldPanel("subtitle"),
        FieldPanel("header_image"),
        FieldPanel("body"),
        FieldPanel("og_image"),
    ]

    class Meta:
        verbose_name = "Standard Page"
        verbose_name_plural = "Standard Pages"

    def __str__(self):
        return self.title
