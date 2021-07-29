import stactools.core
from stactools.cli import Registry
from stactools.ga_dlcd import commands
from stactools.ga_dlcd.stac import create_collection, create_item
from stactools.ga_dlcd.cog import create_cog

__all__ = [
    create_collection.__name__, create_item.__name__, create_cog.__name__
]

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    registry.register_subcommand(commands.create_gadlcd_command)


__version__ = '0.2.0'
"""Library version"""
