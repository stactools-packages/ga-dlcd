
import logging
import os
from datetime import datetime
import re
import shapely
import rasterio
from dateutil.relativedelta import relativedelta
import pytz
from pystac.extensions.projection import ProjectionExtension
from stactools.ga_dlcd.constants import (
    GADLCD_ID,
    GADLCD_EPSG,
    GADLCD_TITLE,
    DESCRIPTION,
    GADLCD_PROVIDER,
    LICENSE,
    LICENSE_LINK,
    GADLCD_BOUNDING_BOX,
    GADLCD_START_YEAR,
    GADLCD_END_YEAR
)

import pystac
from shapely.geometry import Polygon

logger = logging.getLogger(__name__)

def create_item(metadata_url: str,cog_href: str) -> pystac.Item:
    """Creates a STAC item for Geoscience Australia Dynamic Land Cover Dataset Version 2 dataset.

    Args:
        metadata_url (str): Path to provider metadata.
        cog_href (str): Path to COG asset.

    Returns:
        pystac.Item: STAC Item object.
    """

    item_id = cog_href.split(".")[0].split("/")[-1]

    try:
        years = re.search("(?<=DLCD_v2-1_MODIS_EVI_).*",item_id).group().split("_")[1].split("-")
    except:
        print("COG file name is not in the correct format. File name must start with 'DLCD_v2-1_MODIS_EVI_'")

    
    utc = pytz.utc

    dataset_datetime = utc.localize(datetime.strptime(years[0],'%Y%m%d'))
    start_datetime = utc.localize(datetime.strptime(years[0],'%Y%m%d'))
    end_datetime = utc.localize(datetime.strptime(years[1],'%Y%m%d'))

    title = f"{GADLCD_TITLE} {start_datetime.year} - {end_datetime.year}"
    
    polygon = shapely.geometry.box(*GADLCD_BOUNDING_BOX, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]

    geometry = {
                "type":"Polygon",
                "coordinates": [coordinates]
                }

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
    item_projection.bbox = GADLCD_BOUNDING_BOX

    src = rasterio.open(cog_href)

    item_projection.transform = list(src.transform)
    item_projection.shape = [src.height, src.width]


    item.add_asset(
        "landcover change",
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


def create_collection(metadata_url: str):
    """Create a STAC Collection.

    Args:
        metadata_url (str): Location to save the output STAC Collection json

    Returns:
        pystac.Collection: pystac collection object
    """
    # Creates a STAC collection for Geoscience Australia Dynamic Land Cover Change dataset

    utc = pytz.utc

    dataset_datetime = utc.localize(datetime.strptime(GADLCD_START_YEAR, "%Y"))
    end_datetime = utc.localize(datetime.strptime(GADLCD_END_YEAR, "%Y"))
    start_datetime = dataset_datetime

    collection = pystac.Collection(
        id=GADLCD_ID,
        title=GADLCD_TITLE,
        description=DESCRIPTION,
        providers=[GADLCD_PROVIDER],
        license=LICENSE,
        extent=pystac.Extent(
            pystac.SpatialExtent(GADLCD_BOUNDING_BOX),
            pystac.TemporalExtent([start_datetime, end_datetime]),
        ),
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
    )
    collection.add_link(LICENSE_LINK)

    collection.set_self_href(metadata_url)
    collection.save_object()

    return collection
