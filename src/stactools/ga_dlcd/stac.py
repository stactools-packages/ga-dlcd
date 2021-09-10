import logging
from datetime import datetime
import re
import shapely
import rasterio
import pytz
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.label import LabelExtension, LabelClasses, LabelTask, LabelType, LabelMethod
from stactools.ga_dlcd.constants import (CLASSIFICATION_VALUES, GADLCD_ID,
                                         GADLCD_EPSG, GADLCD_TITLE,
                                         DESCRIPTION, GADLCD_PROVIDERS,
                                         LICENSE, LICENSE_LINK,
                                         GADLCD_BOUNDING_BOX,
                                         GADLCD_START_YEAR, GADLCD_END_YEAR)

import pystac

logger = logging.getLogger(__name__)


def create_item(metadata_url: str, cog_href: str) -> pystac.Item:
    """Creates a STAC item for Geoscience Australia Dynamic Land Cover Dataset Version 2 dataset.

    Args:
        metadata_url (str): Path to provider metadata.
        cog_href (str): Path to COG asset.

    Returns:
        pystac.Item: STAC Item object.
    """

    item_id = cog_href.split(".")[0].split("/")[-1]

    match = re.search("(?<=DLCD_v2-1_MODIS_EVI_).*", item_id)
    assert match
    years = match.group().split("_")[1].split("-")

    utc = pytz.utc

    dataset_datetime = utc.localize(datetime.strptime(years[0], '%Y%m%d'))
    start_datetime = dataset_datetime
    end_datetime = utc.localize(datetime.strptime(years[1], '%Y%m%d'))

    title = f"{GADLCD_TITLE} {start_datetime.year} - {end_datetime.year}"

    polygon = shapely.geometry.box(*GADLCD_BOUNDING_BOX, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]

    geometry = {"type": "Polygon", "coordinates": [coordinates]}

    properties = {
        "title": title,
        "description": DESCRIPTION,
    }

    # Create item
    item = pystac.Item(
        id=item_id,
        geometry=geometry,
        bbox=GADLCD_BOUNDING_BOX,
        datetime=dataset_datetime,
        properties=properties,
        stac_extensions=[],
    )

    if start_datetime and end_datetime:
        item.common_metadata.start_datetime = start_datetime
        item.common_metadata.end_datetime = end_datetime

    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = GADLCD_EPSG
    with rasterio.open(cog_href) as src:
        item_projection.bbox = list(src.bounds)
        item_projection.transform = list(src.transform)
        item_projection.shape = [src.height, src.width]

    item_label = LabelExtension.ext(item, add_if_missing=True)
    item_label.label_description = "GA DLCD dataset shows land covers clustered into 22 classes."
    item_label.label_type = LabelType.RASTER
    item_label.label_tasks = [LabelTask.CLASSIFICATION]
    item_label.label_methods = [LabelMethod.AUTOMATED]
    item_label.label_properties = None
    item_label.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(list(CLASSIFICATION_VALUES.values()), "")
    ]

    item.add_asset(
        "data",
        pystac.Asset(
            href=cog_href,
            media_type=pystac.MediaType.COG,
            roles=["data"],
            title=title,
        ),
    )

    item.set_self_href(metadata_url)
    item.save_object()

    return item


def create_collection(metadata_url: str) -> pystac.Collection:
    """Create a STAC Collection.

    Args:
        metadata_url (str): Location to save the output STAC Collection json

    Returns:
        pystac.Collection: pystac collection object
    """
    # Creates a STAC collection for Geoscience Australia Dynamic Land Cover Change dataset

    utc = pytz.utc

    start_datetime = utc.localize(datetime.strptime(GADLCD_START_YEAR, "%Y"))
    end_datetime = utc.localize(datetime.strptime(GADLCD_END_YEAR, "%Y"))

    collection = pystac.Collection(
        id=GADLCD_ID,
        title=GADLCD_TITLE,
        description=DESCRIPTION,
        providers=GADLCD_PROVIDERS,
        license=LICENSE,
        extent=pystac.Extent(
            pystac.SpatialExtent([GADLCD_BOUNDING_BOX]),
            pystac.TemporalExtent(
                [[start_datetime or None, end_datetime or None]]),
        ),
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
    )
    collection.add_link(LICENSE_LINK)

    collection.set_self_href(metadata_url)
    collection.save_object()

    return collection
