import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import fsspec
import pystac
import rasterio
import shapely
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.label import (
    LabelClasses,
    LabelExtension,
    LabelMethod,
    LabelTask,
    LabelType,
)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (
    DataType,
    RasterBand,
    RasterExtension,
    Sampling,
)
from stactools.core.io import ReadHrefModifier

from stactools.ga_dlcd.constants import (
    CLASSIFICATION_VALUES,
    DESCRIPTION,
    GADLCD_BOUNDING_BOX,
    GADLCD_CRS_WKT,
    GADLCD_DESC,
    GADLCD_END_YEAR,
    GADLCD_EPSG,
    GADLCD_ID,
    GADLCD_PROVIDERS,
    GADLCD_START_YEAR,
    GADLCD_TITLE,
    GADLCD_VERSION,
    KEYWORDS,
    LICENSE,
    LICENSE_LINK,
    NO_DATA_VALUE,
    THUMBNAIL_URL,
    WMS_CAPABILITIES_LINK,
)

logger = logging.getLogger(__name__)


def create_item(
    cog_href: str,
    cog_href_modifier: Optional[ReadHrefModifier] = None,
) -> pystac.Item:
    """Creates a STAC item for Geoscience Australia Dynamic Land Cover Dataset Version 2 dataset.

    Args:
        metadata_url (str): Path to provider metadata.
        cog_href (str): Path to COG asset.

    Returns:
        pystac.Item: STAC Item object.
    """

    if cog_href_modifier:
        cog_access_href = cog_href_modifier(cog_href)
    else:
        cog_access_href = cog_href

    item_id = os.path.basename(cog_href).replace(".tif", "")
    logger.info(f"Creating Item {item_id}")
    match = re.search(
        r"DLCD_v(.+)_MODIS_EVI_(\d+)_(\d\d\d\d)(\d\d)(\d\d)-(\d\d\d\d)(\d\d)(\d\d)",
        item_id)
    if match is None:
        raise ValueError("Could not extract necessary values from {cog_href}")
    v, _, start_year, start_month, start_day, end_year, end_month, end_day = match.groups(
    )
    version = v.replace('-', '.')
    if version != GADLCD_VERSION:
        raise ValueError(
            f"Provided version {version} is not the expected {GADLCD_VERSION}")

    dataset_datetime = datetime(
        int(start_year),
        int(start_month),
        int(start_day),
        tzinfo=timezone.utc,
    )
    start_datetime = dataset_datetime
    end_datetime = datetime(
        int(end_year),
        int(end_month),
        int(end_day),
        tzinfo=timezone.utc,
    ) + timedelta(days=1) - timedelta(seconds=1)

    title = f"GA DLCD {start_datetime.year} - {end_datetime.year}"

    polygon = shapely.geometry.box(*GADLCD_BOUNDING_BOX, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]

    geometry = {"type": "Polygon", "coordinates": [coordinates]}

    properties = {
        "title": title,
        "description": DESCRIPTION,
    }

    logger.debug("Create Item")
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
    item_projection.wkt2 = GADLCD_CRS_WKT
    logger.debug(f"Opening COG with rasterio: {cog_access_href}")
    with rasterio.open(cog_access_href) as src:
        item_projection.bbox = list(src.bounds)
        item_projection.transform = list(src.transform)
        item_projection.shape = [src.height, src.width]

    item_label = LabelExtension.ext(item, add_if_missing=True)
    item_label.label_description = GADLCD_DESC
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

    # COG Asset
    cog_asset = pystac.Asset(
        href=cog_href,
        media_type=pystac.MediaType.COG,
        roles=[
            "data",
            "labels",
            "labels-raster",
        ],
        title=title,
    )
    item.add_asset("landcover", cog_asset)

    # File Extension
    cog_asset_file = FileExtension.ext(cog_asset, add_if_missing=True)
    # The following odd type annotation is needed
    mapping: List[Any] = [{
        "values": [value],
        "summary": summary
    } for value, summary in CLASSIFICATION_VALUES.items()]
    cog_asset_file.values = mapping
    logger.debug(f"Opening COG with fsspec: {cog_access_href}")
    with fsspec.open(cog_access_href) as file:
        size = file.size
        if size is not None:
            cog_asset_file.size = size

    # Raster Extension
    cog_asset_raster = RasterExtension.ext(cog_asset, add_if_missing=True)
    cog_asset_raster.bands = [
        RasterBand.create(nodata=0,
                          sampling=Sampling.AREA,
                          data_type=DataType.UINT8,
                          spatial_resolution=250)
    ]

    # Projection Extension
    cog_asset_projection = ProjectionExtension.ext(cog_asset,
                                                   add_if_missing=True)
    cog_asset_projection.epsg = item_projection.epsg
    cog_asset_projection.bbox = item_projection.bbox
    cog_asset_projection.transform = item_projection.transform
    cog_asset_projection.shape = item_projection.shape

    logger.debug("Done Creating Item")

    return item


def create_collection(thumbnail_url: str = THUMBNAIL_URL) -> pystac.Collection:
    """Create a STAC Collection.

    Args:

    Returns:
        pystac.Collection: pystac collection object
    """
    # Creates a STAC collection for Geoscience Australia Dynamic Land Cover Change dataset

    start_datetime = datetime(GADLCD_START_YEAR, 1, 1)
    end_datetime = datetime(GADLCD_END_YEAR + 1, 1, 1) - timedelta(seconds=1)

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
        keywords=KEYWORDS,
    )
    collection.add_link(LICENSE_LINK)
    collection.add_link(WMS_CAPABILITIES_LINK)

    if thumbnail_url.endswith(".png"):
        thumb_media_type = pystac.MediaType.PNG
    elif thumbnail_url.endswith(".jpg") or thumbnail_url.endswith(".jpeg"):
        thumb_media_type = pystac.MediaType.JPEG
    else:
        raise ValueError(f"Unrecognized file type for {thumbnail_url}")
    collection.add_asset(
        "thumbnail",
        pystac.Asset(
            href=thumbnail_url,
            media_type=thumb_media_type,
            roles=["thumbnail"],
            title=GADLCD_TITLE,
        ),
    )

    collection_label = LabelExtension.summaries(collection,
                                                add_if_missing=True)
    collection_label.label_type = [LabelType.RASTER]
    collection_label.label_tasks = [LabelTask.CLASSIFICATION]
    collection_label.label_methods = [LabelMethod.AUTOMATED]
    collection_label.label_properties = None
    collection_label.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(list(CLASSIFICATION_VALUES.values()), "")
    ]

    collection_proj = ProjectionExtension.summaries(collection,
                                                    add_if_missing=True)
    collection_proj.epsg = [GADLCD_EPSG]

    collection_item_asset = ItemAssetsExtension.ext(collection,
                                                    add_if_missing=True)
    collection_item_asset.item_assets = {
        "landcover":
        AssetDefinition({
            "type":
            pystac.MediaType.COG,
            "roles": [
                "data",
                "labels",
                "labels-raster",
            ],
            "raster:bands": [
                RasterBand.create(nodata=NO_DATA_VALUE,
                                  sampling=Sampling.AREA,
                                  data_type=DataType.UINT8,
                                  spatial_resolution=250).to_dict()
            ],
            "file:values": [{
                "values": [value],
                "summary": summary
            } for value, summary in CLASSIFICATION_VALUES.items()],
            "proj:epsg":
            collection_proj.epsg[0]
        }),
    }

    return collection
