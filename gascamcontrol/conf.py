"""Manage config file and command line arguments.

This file only manages global config settings, device specific settings are
handled in the individual device managers (eg. viscam/viscam.py).
"""
import os
import configargparse


class Conf():
    """Parse config file and command line arguments."""

    __monostate = None  # borg pattern

    def __init__(self):
        if Conf.__monostate:
            self.__dict__ = Conf.__monostate
        else:
            Conf.__monostate = self.__dict__
            self.options = {}

        self.parser = None

    def get_config_file_paths(self):
        """Find, load and parse a config file.

        The first config file that is found is used, it is searched for (in
        this order), at:
         - config, if set (e.g. from the cli)
         - from the default source path (./configurations/gascamcontrol.conf)
         - home path
           - XDG_CONFIG_HOME/gascamcontrol/gascamcontrol.conf (linux only)
         - system path
           - XDG_CONFIG_DIRS/gascamcontrol/gascamcontrol.conf (linux only)

        >>> c = Conf()
        >>> type(c.get_config_file_paths())
        <class 'list'>
        """
        env = os.environ
        xdg_home = None
        if 'XDG_CONFIG_HOME' in env:
            xdg_home = env['XDG_CONFIG_HOME']
        elif 'HOME' in env:
            xdg_home = env['HOME'] + '/.config'

        xdg_config_dirs = None
        if 'XDG_CONFIG_DIRS' in env:
            xdg_config_dirs = env['XDG_CONFIG_DIRS'].split(':')
        elif 'HOME' in env:
            xdg_config_dirs = ['/etc/xdg']

        default_filename = "gascamcontrol.conf"

        default_path = "./configurations"
        paths = [default_path, xdg_home]
        paths.extend(xdg_config_dirs)
        return [os.path.join(p, default_filename) for p in paths if p]

    def parse(self):
        """Define and parse config file and cli arguments.

        The config file is parsed as a simple key=value syntax. Lines
        starting with '#' are ignored, as are unknown keys.
        """
        self.parser = configargparse.get_argument_parser()

        # pylint: disable=W0212
        self.parser._default_config_files = self.get_config_file_paths()
        self.parser.description = """Gas Cam Control Software.

        This software comes with ABSOLUTELY NO WARRANTY.
        This is free software and you
        are welcome to modify and redistribute it under certain conditions.
        See the MIT Licence for details."""

        self.parser.add("--configfile",
                        is_config_file=True,
                        help="Load config file from path. If not set config "
                             "files are searched for at the usual places")

        self.parser.add("-w", "--write-out-config-file",
                        metavar="CONFIG_OUTPUT_PATH",
                        help="takes the current command line args and writes "
                        "them out to a config file at the given path, "
                        "then exits",
                        is_write_out_config_file_arg=True)

        self.parser.add("--simpletui", action="store_true",
                        help="No interface, just log msgs.")

        self.options = self.parser.parse_args()

        # validate
        # TODO:
        #   - #camera_drivers = #camera_identifiers

        configargparse.options = self.options

    def write_config(self, namespace, filename):
        """Write config file from current config options."""
        self.parser.write_config_file(namespace, filename,
                                      exit_after=True)
