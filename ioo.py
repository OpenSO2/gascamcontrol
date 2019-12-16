import cv2
from concurrent.futures import ThreadPoolExecutor


class Io():
    async def save_png(self, filename, img, loop):
        img *= 16
        await loop.run_in_executor(ThreadPoolExecutor(), cv2.imwrite, filename, img)
