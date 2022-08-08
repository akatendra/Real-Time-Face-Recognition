from collections import deque
from threading import Thread
from time import time

import cv2 as cv
import face_recognition as fr
import numpy as np
import win32con
import win32gui
import win32ui


# Class WindowCapture from https://www.youtube.com/watch?v=WymCpVUPWQ4
class WindowCapture:
    # properties
    width = 0
    height = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name):
        # find the handle for the window we want to capture
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.width = window_rect[2] - window_rect[0]
        self.height = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        border_pixels = 8
        titlebar_pixels = 30
        self.width = self.width - (border_pixels * 2)
        self.height = self.height - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.width, self.height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.width, self.height), dcObj,
                   (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.height, self.width, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type()
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[..., :3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hwnd, '|', hex(hwnd), '|', win32gui.GetClassName(hwnd),
                      '|',
                      win32gui.GetWindowText(hwnd))

        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)


# Class CountsPerSec from https://nrsyed.com/2018/07/05/multithreading-with-opencv-python-to-improve-video-processing-performance/
class CountsPerSec:
    """
    Class that tracks the number of occurrences ("counts") of an
    arbitrary event and returns the frequency in occurrences
    (counts) per second. The caller must increment the count.
    """

    def __init__(self):
        self._start_time = None
        self._num_occurrences = 0

    def start(self):
        self._start_time = time()
        return self

    def increment(self):
        self._num_occurrences += 1

    def counts_per_sec(self):
        elapsed_time = time() - self._start_time
        return self._num_occurrences / elapsed_time if elapsed_time > 0 else 0


class VideoGet:
    """
    Class that continuously gets screenshots from named window
    with a dedicated thread.
    """

    def __init__(self, src):
        self.stream = WindowCapture(src)
        self.screenshot = self.stream.get_screenshot()
        self.stopped = False

    def start(self):
        Thread(target=self.get, name='VideoGet', args=(), daemon=True).start()
        return self

    def get(self):
        while not self.stopped:
            self.screenshot = self.stream.get_screenshot()


    def stop(self):
        self.stopped = True


class VideoShow:
    """
    Class that continuously shows a screenshots using a dedicated thread.
    """

    def __init__(self, screenshot=None):
        self.screenshot = screenshot
        self.stopped = False

    def start(self):
        Thread(target=self.show, name='VideoShow', args=(), daemon=True).start()
        return self

    def show(self):
        while not self.stopped:
            # press 'q' with the output window focused to exit.
            # waits 1 ms every loop to process key presses
            cv.imshow('ZOOM Class Attendance', self.screenshot)
            if cv.waitKey(1) == ord('q'):
                self.stopped = True


    def stop(self):
        self.stopped = True


class VideoQueue:

    def __init__(self, screenshot=None):
        self.video_queue = deque()
        self.screenshot = screenshot
        self.screenshot_out = None
        self.stopped = False

    def start(self):
        Thread(target=self.add, name='VideoQueueAdd', args=(), daemon=True).start()
        # Thread(target=self.pop, name='VideoQueuePop', args=()).start()
        return self

    def start_pop(self):
        Thread(target=self.pop, name='VideoQueuePop', args=(), daemon=True).start()
        return self

    def add(self):
        while not self.stopped:
            self.video_queue.append(self.screenshot)


    def pop(self):
        while not self.stopped:
            self.screenshot_out = self.video_queue.popleft()


    def size(self):
        return len(self.video_queue)

    def stop(self):
        self.stopped = True


# class ScreenshotFaceRecognition:
#     def __init__(self, screenshot):
#         self.screenshot = screenshot
#
#     def start(self):
#         thread = Thread(target=self.face_processing, args=())
#         thread.start()
#         thread.join()
#         return self
#
#     def face_processing(self):
#         # Find all the faces and face encodings in the screenshot
#         global face_locations, face_encodings
#         face_locations = fr.face_locations(self.screenshot)
#         face_encodings = fr.face_encodings(self.screenshot, face_locations)
#
#
# class ScrFaceRecThread(Thread):
#     # constructor
#     def __init__(self, screenshot):
#         self.screenshot = screenshot
#         # execute the base constructor
#         Thread.__init__(self)
#         # set a default value
#         self.face_locations = None
#         self.face_encodings = None
#
#     # function executed in a new thread
#     def run(self):
#         self.face_locations = fr.face_locations(self.screenshot)
#         self.face_encodings = fr.face_encodings(self.screenshot,
#                                                 self.face_locations)
