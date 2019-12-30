"""Manage config file and command line arguments."""
# https://docs.python.org/3/faq/programming.html#how-do-i-share-global-variables-across-modules
import configargparse
import os
# fprintf(stderr, "Usage %s [--noprocessing] [--png-only] [--debug] [--noofimages n]\n", name);
# fprintf(stderr, "      [--configfile filename] [--imagepath folder] [--port portno]\n");
# fprintf(stderr, "      [--disableWebcam] [--disableSpectroscopy]\n");
# fprintf(stderr, "\n");
# fprintf(stderr, "SO2-Camera Control Software \n");
# fprintf(stderr, "\n");
# fprintf(stderr, "This software comes with ABSOLUTELY NO WARRANTY. This is free software and you\n");
# fprintf(stderr, "are welcome to modify and redistribute it under certain conditions.\n");
# fprintf(stderr, "See the MIT Licence for details. \n");
# fprintf(stderr, "\n");
# fprintf(stderr, "   --help, -h                    Print this usage information and exit\n");
# fprintf(stderr, "   --noprocessing                Skip processing as much as possible and only save raw images\n");
# fprintf(stderr, "   --png-only                    Skip saving of raw files\n");
# fprintf(stderr, "   --debug                       Print debug output\n");
# fprintf(stderr, "   --noofimages n                Only save n UV image sets and exit\n");
# fprintf(stderr, "   --configfile /path/file.conf  Load config file from path. If not set config files are searched for at the usual places\n");
# fprintf(stderr, "   --imagepath /path/outfolder   Save images and logs in path\n");
# fprintf(stderr, "   --port portno                 Set port for liveview. Default: 7009\n");
# fprintf(stderr, "   --disableWebcam               Disable processing and saving of webcam images\n");
# fprintf(stderr, "   --disableSpectroscopy         Disable processing and saving of spectra\n");
#
# exit(0);

options = {
    "stop": False,
    "logfile": "spam2.log",
    "viscam_driver": None
}


class Conf():
    """Parse config file and command line arguments."""

    def __init__(self):
        self.parser = None

    def get_config_file_paths(self):
        """Find, load and parse a config file.

        The first config file that is found is used, it is searched for (in
        this order), at:
         - config, if set (e.g. from the cli)
         - from the default source path (./configurations/so2-camera.conf)
         - home path
           - XDG_CONFIG_HOME/so2-camera/so2-camera.conf (linux only)
         - system path
           - XDG_CONFIG_DIRS/so2-camera/so2-camera.conf (linux only)

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

        default_filename = "so2-camera.conf"

        default_path = "./configurations"
        paths = [default_path]
        paths.append(xdg_home)
        paths.extend(xdg_config_dirs)
        return [os.path.join(p, default_filename) for p in paths if p]

    def parse(self):
        """Define and parse config file and cli arguments.

        The config file is parsed as a simple key=value syntax. Lines
        starting with '#' are ignored, as are unknown keys.
        """
        self.parser = configargparse.ArgParser(
            default_config_files=self.get_config_file_paths(),
            args_for_writing_out_config_file=["-w", "--write-out-config-file"])
        # fixme use arg for configfilepath
        self.parser.add("--configfile", is_config_file=True,
                        help="configuration file path")

        self.parser.add("--InterFrameDelay", default=10,
                        help="delay between two frames in ms")
        self.parser.add("--FixTime", default=0,
                        help="fix exposure time 1 = yes 0 = no")

        # contains the Exposuretime in [us]
        # min = 2.4 max = 1004400
        self.parser.add("--ExposureTime_a", default=1004400)
        self.parser.add("--ExposureTime_b", default=1004400)

        # rotate the captured images by N degrees clockwise. This applies only
        # to png images, raw files will not be modified. PNG meta data will
        # contain the `rotated` value, raw meta files will contain a `rotate`
        # values. At the moment, images can only be rotated by 180degrees.
        self.parser.add("--rotate_a", default=180)
        self.parser.add("--rotate_b", default=180)
        self.parser.add("--rotate_webcam", default=180)

        # prefix for all images in this session
        self.parser.add("--FileNamePrefix", default="testing")

        # path to images and logs - can be either a relative path from the
        # working directory or an absolute path
        # eg.
        #     ./measurement-stromboli-2016
        #     /home/so2/measurements
        #
        # Trailing "/" will be stripped.
        # Files will be saved in a subfolder of the form
        # `ImagePath`/YYYY-MM-DD_HH_MM/
        # Log files will be saved in a subfolder of the form `ImagePath/logs`
        self.parser.add("--ImagePath", default="images")

        # processing mode
        # 1 = no processing, save only raw images
        # 2 = do processing, save png images, but no raw images
        # else = do processing and save both png and raw images (default)
        self.parser.add("--processing", default=0)

        # filterwheel device descriptor
        # filterwheel_device = \\\\.\\COM22
        self.parser.add("--filterwheel_device", default="/dev/serial/by-id/usb"
                        "-FTDI_FT232R_USB_UART_A402X19O-if00-port0")

        # Intervall (in images) between dark images
        # a dark image is taken every N images (int, >0)
        self.parser.add("--darkframeintervall", default=1000)

        # spectrometer shutter device descriptor
        # eg.
        # windows
        #     \\\\.\\COM6
        #     \\\\.\\USBSER000
        # linux
        #     /dev/serial/by-id/usb-Pololu_Corporation_Pololu_Micro_Maestro_6-Servo_
        #                       Controller_00135615-if00";
        #     /dev/ttyACM3
        self.parser.add("--spectrometer_shutter_device",
                        default="/dev/serial/by-id/usb-Pololu_Corporation"
                        "_Pololu_Micro_Maestro_6-Servo_Controller"
                        "_00135615-if00")

        # spectrometer shutter device channel - used for the pololu maestro
        # servo controller
        self.parser.add("--spectrometer_shutter_channel", default=5)

        # recalibrate (= take a dark measurement every N measurements)
        self.parser.add("--spectrometer_calibrate_intervall", default=10)

        # The DOAS method depends on a good exposure in the region of SO2
        # absorption (region of interest, roi). An appropriate saturation is
        # at about 70% of the maximum value of the spectrometer (typically
        # 16bit, 65535). This is calculated from the highest value in the
        # roi at a given exposure time.
        # The upper and lower bounds of the roi are important, because SO2
        # absorption drops over ~310nm, but sunlight dramatically diminishes
        # with wavelengths <340. If the upper limit is set too low, not enough
        # sunlight is present. If it is too high, SO2 absorption is negligible.
        self.parser.add("--spectroscopy_roi_lower", default=300)
        self.parser.add("--spectroscopy_roi_upper", default=320)

        self.parser.add("--enableSpectroscopy", default=1,
                        help="switch to disable spectroscopy and spectrometer")
        self.parser.add("--enableWebcam", default=1,
                        help="switch to disable webcam code")
        self.parser.add("--port", default="8080", help="comm port")

        self.parser.add("--viscam_driver", default="mock",
                        help="which viscam driver to use")
        self.options = self.parser.parse_args()
        global options
        options = self.options
