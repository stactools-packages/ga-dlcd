import logging
from subprocess import CalledProcessError, check_output

import rasterio

from stactools.ga_dlcd.constants import COLOUR_MAP, NO_DATA_VALUE

logger = logging.getLogger(__name__)


def create_cog(
    input_path: str,
    output_path: str,
    raise_on_fail: bool = True,
    dry_run: bool = False,
) -> str:
    """Create COG from a tif

    Args:
        input_path (str): Path to the Natural Resources Canada Land Cover data.
        output_path (str): The path to which the COG will be written.
        raise_on_fail (bool, optional): Whether to raise error on failure.
            Defaults to True.
        dry_run (bool, optional): Run without downloading tif, creating COG,
            and writing COG. Defaults to False.

    Returns:
        str: The path to the output COG.
    """

    output = None
    try:
        if dry_run:
            logger.info(
                "Would have downloaded TIF, created COG, and written COG")
        else:
            logger.info("Converting TIFF to COG")
            logger.debug(f"input_path: {input_path}")
            logger.debug(f"output_path: {output_path}")
            cmd = [
                "gdal_translate",
                "-of",
                "COG",
                "-co",
                "NUM_THREADS=ALL_CPUS",
                "-co",
                "BLOCKSIZE=512",
                "-co",
                "COMPRESS=DEFLATE",
                "-co",
                "LEVEL=9",
                "-co",
                "PREDICTOR=YES",
                "-co",
                "OVERVIEWS=IGNORE_EXISTING",
                "-a_nodata",
                str(NO_DATA_VALUE),
                input_path,
                output_path,
            ]

            try:
                output = check_output(cmd)
            except CalledProcessError as e:
                output = e.output
                raise
            finally:
                logger.info(f"output: {str(output)}")
            with rasterio.open(output_path, "r+") as dataset:
                dataset.write_colormap(1, COLOUR_MAP)

    except Exception:
        logger.error("Failed to process {}".format(output_path))

        if raise_on_fail:
            raise

    return output_path
