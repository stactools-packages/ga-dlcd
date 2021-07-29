import stactools.core
from stactools.ga_dlcd.stac import create_collection, create_item
from stactools.ga_dlcd.cog import create_cog

__all__ = [
    create_collection.__name__, create_item.__name__, create_cog.__name__
]

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.ga_dlcd import commands
    registry.register_subcommand(commands.create_gadlcd_command)


__version__ = '0.2.3'
"""Library version"""
