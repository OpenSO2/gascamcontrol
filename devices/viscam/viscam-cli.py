"""Command line viscam program for testing and demonstration."""
import asyncio
from argparse import ArgumentParser
import cv2
from viscam import Viscam


async def capture(driver, filename):
    """Capture image from viscam and save to png or raw."""
    async with Viscam(driver=driver) as viscam:
        img = await viscam.get()
        cv2.imwrite(filename, img)


def main():
    """Run main event loop."""
    parser = ArgumentParser()
    parser.add_argument("filename", default="out.png", help="file to save to")
    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")
    options = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(capture(options.driver, options.filename))


if __name__ == "__main__":
    main()
