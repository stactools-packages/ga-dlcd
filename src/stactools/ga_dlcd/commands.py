import logging
import os

import click

from stactools.ga_dlcd import cog, stac

logger = logging.getLogger(__name__)


def create_gadlcd_command(cli: click.Group) -> click.Command:
    """Creates the gadlcd command line utility."""
    @cli.group(
        "ga-dlcd",
        short_help="Commands for working with GA DLCD data",
    )
    def gadlcd() -> None:
        pass

    @gadlcd.command(
        "create-collection",
        short_help="Creates a STAC collection from GA DLCD metadata",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json",
    )
    def create_collection_command(destination: str) -> None:
        """Creates a STAC Collection from gadlcd metadata

        Args:
            destination (str): Directory used to store the collection json
        Returns:
            Callable
        """
        output_path = os.path.join(destination, "collection.json")
        collection = stac.create_collection()
        collection.set_self_href(output_path)
        collection.normalize_hrefs(destination)
        collection.save()
        collection.validate()

    @gadlcd.command(
        "create-cog",
        short_help="Transform Geotiff to Cloud-Optimized Geotiff.",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the COG",
    )
    @click.option(
        "-s",
        "--source",
        required=True,
        help="Path to an input GeoTiff",
    )
    def create_cog_command(destination: str, source: str) -> None:
        """Generate a COG from a GeoTiff. The COG will be saved in the desination directory.

        Args:
            destination (str): Local directory to save output COGs
            source (str): An input GA-DLCD GeoTiff
        """
        if not os.path.isdir(destination):
            raise IOError(f'Destination folder "{destination}" not found')

        if destination == source:
            output_path = os.path.join(
                destination,
                os.path.basename(source).replace(".tif", "_cog.tif"))
        else:
            output_path = os.path.join(destination, os.path.basename(source))

        cog.create_cog(source, output_path)

    @gadlcd.command(
        "create-item",
        short_help="Create a STAC item using JSONLD metadata and a COG",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json",
    )
    @click.option("-c", "--cog", required=True, help="COG href")
    def create_item_command(destination: str, cog: str) -> None:
        """Generate a STAC item using the metadata, with an asset url as provided.

        Args:
            destination (str): Local directory to save the STAC Item json
            cog (str): location of a COG asset for the item
        """

        output_path = os.path.join(
            destination,
            os.path.basename(cog).replace(".tif", ".json"))

        item = stac.create_item(cog)
        item.set_self_href(output_path)
        item.make_asset_hrefs_relative()
        item.save_object()
        item.validate()

    @gadlcd.command(
        "populate-full-collection",
        short_help="Create a STAC Collection with all of the Items and Assets",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory",
    )
    @click.option(
        "-s",
        "--source",
        required=True,
        help="Dataset directory",
    )
    def populate_full_collection(destination: str, source: str) -> None:
        """Convert the dataset to COGs, and build the STAC Items and Collection

        Args:
            destination (str): Local directory to save output COGs
            source (str): A directory containing the GA-DLCD dataset TIFFs
        """
        if not os.path.isdir(destination):
            raise IOError(f'Destination folder "{destination}" not found')
        if not os.path.isdir(source):
            raise IOError(f'Source folder "{source}" not found')

        collection = stac.create_collection()
        collection.normalize_hrefs(destination)
        collection.save(dest_href=destination)
        for tiff in os.listdir(source):
            if tiff.endswith(".tif"):
                logger.info(f"Processing {tiff}")
                cog_path = os.path.join(destination, tiff)
                cog.create_cog(os.path.join(source, tiff), cog_path)

                item = stac.create_item(cog_href=cog_path)
                collection.add_item(item)
                item_path = cog_path.replace(".tif", ".json")
                item.set_self_href(item_path)
                item.make_asset_hrefs_relative()
                item.validate()

        logger.info("Saving collection")
        collection.save(dest_href=destination)
        collection.validate()

    return gadlcd
