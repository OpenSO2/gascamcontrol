import signal
import sys
import os
import asyncio
import configargparse
import matplotlib.pyplot as plt

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.spectrometer.spectrometer import Spectrometer  # noqa: E402,E501 pylint: disable=C0413,E0401
import conf

EXPOSURE = 4000000
SCANS = 1


def shutdown():
    """Kill program and cleanup."""
    loop = asyncio.get_event_loop()
    pending = asyncio.all_tasks()
    for task in pending:
        task.cancel()

    asyncio.gather(*pending)
    loop.stop()
    sys.exit(0)


async def plot():
    """Plot indefinitely."""
    plt.ion()
    fig = plt.figure()

    # stop program when window is closed
    fig.canvas.mpl_connect('close_event', lambda _: shutdown())

    axes = fig.add_subplot(111)
    plt.show()
    plt.pause(0.1)

    axplt = False

    async with Spectrometer() as spectrometer:
        while 1:  # plot indefinitely
            wvl, data = await spectrometer.get(EXPOSURE)
            if not axplt:
                axplt = axes.plot(wvl, data, 'r-')[0]
            axplt.set_ydata(data)
            plt.draw()
            plt.pause(0.1)


def main():
    """Startup program."""
    # handle ctrl+c
    signal.signal(signal.SIGINT, lambda _signal, _frame: shutdown())

    parser = configargparse.get_argument_parser()
    parser.description = 'Spectrometer live viewer'

    options = parser.parse_args()
    conf.Conf().options = options

    loop = asyncio.get_event_loop()
    loop.run_until_complete(plot())


if __name__ == "__main__":
    main()
