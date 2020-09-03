import signal
import sys
import asyncio
import configargparse
import matplotlib.pyplot as plt
from ...conf import Conf
from .spectrometer import Spectrometer

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
    Conf().options = options

    loop = asyncio.get_event_loop()
    loop.run_until_complete(plot())


if __name__ == "__main__":
    main()
