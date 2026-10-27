"""The sitemap template is not well-formed XML until rendered, so validate the output."""

from xml.etree import ElementTree as ET

import pytest

SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


@pytest.mark.django_db
def test_rendered_sitemap_is_well_formed_xml(client):
    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    assert "xml" in response["Content-Type"]
    root = ET.fromstring(response.content)  # noqa: S314
    assert root.tag == f"{SITEMAP_NS}urlset"
    for url in root.findall(f"{SITEMAP_NS}url"):
        loc = url.find(f"{SITEMAP_NS}loc")
        assert loc is not None
        assert loc.text
        assert loc.text.startswith(("http://", "https://"))
        # Optional elements must never be emitted empty (invalid per the schema).
        for tag in ("lastmod", "changefreq", "priority"):
            el = url.find(f"{SITEMAP_NS}{tag}")
            assert el is None or (el.text and el.text.strip())
