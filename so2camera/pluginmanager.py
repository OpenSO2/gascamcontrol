import os
import asyncio
import logging
from importlib import import_module
import configargparse
import conf


_PLUGIN_PATH = "plugins/"


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    plugins = ", ".join([f.replace("plugin_", "").replace(".py", "")
                         for f in os.listdir(_PLUGIN_PATH)
                         if os.path.isfile(os.path.join(_PLUGIN_PATH, f))
                         and "plugin_" in f])

    parser.add("--plugins", nargs='+',
               help=f"Plugins to load from {_PLUGIN_PATH}. "
                    f"Available Plugins: {plugins}")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Pluginmanager():
    """Locate and load plugins."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.logging = logging.getLogger("myLog")
        self.options = conf.Conf().options

        self.plugins = [import_module(f"{_PLUGIN_PATH}.{name}.plugin").Plugin()
                        for name in self.options.plugins]

    async def init(self):
        for plugin in self.plugins:
            await plugin.init()

    async def uninit(self):
        for plugin in self.plugins:
            await plugin.uninit()
