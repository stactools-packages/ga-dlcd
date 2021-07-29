import click
import logging
import os

from stactools.ga_dlcd import cog, stac

logger = logging.getLogger(__name__)


def create_gadlcd_command(cli):
    """Creates the gadlcd command line utility."""
    @cli.group(
        "ga-dlcd",
        short_help="Commands for working with GA DLCD data",
    )
    def gadlcd():
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
    def create_collection_command(destination: str):
        """Creates a STAC Collection from gadlcd metadata

        Args:
            destination (str): Directory used to store the collection json
        Returns:
            Callable
        """
        stac.create_collection(destination)

    @gadlcd.command(
        "create-cog",
        short_help="Transform Geotiff to Cloud-Optimized Geotiff.",
    )
    @click.option("-d",
                  "--destination",
                  required=True,
                  help="The output directory for the COG")
    @click.option("-s",
                  "--source",
                  required=True,
                  help="Path to an input GeoTiff")
    def create_cog_command(destination: str, source: str):
        """Generate a COG from a GeoTiff. The COG will be saved in the desination
        with `_cog.tif` appended to the name.

        Args:
            destination (str): Local directory to save output COGs
            source (str): An input GADLCD GeoTiff
        """
        if not os.path.isdir(destination):
            raise IOError(f'Destination folder "{destination}" not found')

        output_path = os.path.join(destination,
                                   os.path.basename(source)[:-4] + "_cog.tif")

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
    def create_item_command(destination: str, cog: str):
        """Generate a STAC item using the metadata, with an asset url as provided.

        Args:
            destination (str): Local directory to save the STAC Item json
            cog (str): location of a COG asset for the item
        """

        output_path = os.path.join(destination,
                                   os.path.basename(cog)[:-4] + ".json")

        stac.create_item(output_path, cog)

    return gadlcd
