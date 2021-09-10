# flake8: noqa

from pyproj import CRS
from pystac import Link, Provider, ProviderRole

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

NO_DATA_VALUE = 0

CLASSIFICATION_VALUES = {
    0: "No Data",
    2: "Mines and Quarries",
    35: "Urban Areas",
    3: "Lakes and dams",
    4: "Salt lakes",
    5: "Irrigated cropping",
    8: "Rain fed cropping",
    6: "Irrigated pasture",
    9: "Rain fed pasture",
    7: "Irrigated sugar",
    10: "Rain fed sugar",
    11: "Wetlands",
    15: "Alpine meadows",
    16: "Open Hummock Grassland",
    14: "Closed Tussock Grassland",
    18: "Open Tussock Grassland",
    19: "Scattered shrubs and grasses",
    24: "Dense Shrubland",
    25: "Open Shrubland",
    31: "Closed Forest",
    32: "Open Forest",
    34: "Woodland",
    33: "Open Woodland",
}

COLOUR_MAP = {
    0: (0, 0, 0, 0),
    1: (130, 130, 130, 255),
    35: (200, 200, 200, 255),
    3: (0, 70, 173, 255),
    4: (150, 225, 255, 255),
    5: (90, 36, 90, 255),
    8: (198, 141, 153, 255),
    6: (166, 38, 170, 255),
    9: (226, 194, 199, 255),
    7: (183, 18, 52, 255),
    10: (219, 77, 105, 255),
    11: (0, 178, 160, 255),
    15: (255, 255, 255, 255),
    16: (255, 255, 115, 255),
    14: (255, 121, 0, 255),
    18: (255, 169, 82, 255),
    19: (255, 255, 190, 255),
    24: (175, 136, 80, 255),
    25: (193, 168, 117, 255),
    31: (0, 133, 0, 255),
    32: (20, 194, 0, 255),
    34: (186, 232, 96, 255),
    33: (214, 255, 138, 255),
}
