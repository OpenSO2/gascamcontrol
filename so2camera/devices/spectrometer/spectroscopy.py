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

        # recalibrate (= take a dark measurement every N measurements)
        self.parser.add("--spectrometer_calibrate_intervall", default=10)
