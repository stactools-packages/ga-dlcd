# flake8: noqa

from pyproj import CRS
from pystac import Provider, ProviderRole
from pystac import Link

GADLCD_ID = "GADLCD"
GADLCD_EPSG = 4326
GADLCD_CRS = CRS.from_epsg(GADLCD_EPSG)
GADLCD_TITLE = "Geoscience Australia Dynamic Land Cover Change"
LICENSE = "CC-BY-4.0"
LICENSE_LINK = Link(
    rel="license",
    target="https://creativecommons.org/licenses/by/4.0/legalcode",
    title="Creative Commons Attribution 4.0 International",
)

DESCRIPTION = """The Dynamic Land Cover Dataset uses a standard land cover classification to show the change in behaviour of land cover across Australia. The DLCD includes data for every 250m by 250m area on the ground, for the period 2001 to 2015."""

GADLCD_PROVIDER = Provider(
    name="Geoscience Australia",
    roles=[ProviderRole.PRODUCER, ProviderRole.PROCESSOR, ProviderRole.HOST],
    url=
    "https://ecat.ga.gov.au/geonetwork/srv/eng/catalog.search#/metadata/83868")

GADLCD_BOUNDING_BOX = [96.00, -44.00, 168.00, -9.00]
GADLCD_START_YEAR = '2001'
GADLCD_END_YEAR = '2015'
