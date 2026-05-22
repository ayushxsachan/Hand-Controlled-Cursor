import time

import cv2
import numpy as np
import pyautogui

from HandTrackingModule import HandDetector


# ----------------------------- User settings ----------------------------- #
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FRAME_REDUCTION = 100

# Cursor smoothing. Higher values are steadier; lower values are faster.
SMOOTHING = 6.0
FAST_SMOOTHING = 3.0
FAST_MOVE_DISTANCE = 250

# Left click: raise index + middle fingers once.
LEFT_CLICK_COOLDOWN = 0.55

# Right click: raise only the middle finger once.
RIGHT_CLICK_COOLDOWN = 0.8

# Scroll: raise index + middle + ring and move them up/down.
SCROLL_SENSITIVITY = 0.55
SCROLL_DEAD_ZONE = 6
SCROLL_MAX_STEP = 8


class VirtualMouse:
    """Controls the mouse by converting hand landmarks into mouse actions."""

    def __init__(self):
        self.detector = HandDetector(
            max_hands=1,
            model_complexity=0,
            detection_confidence=0.75,
            tracking_confidence=0.75,
        )

        self.screen_width, self.screen_height = pyautogui.size()
        self.current_x = self.screen_width / 2
        self.current_y = self.screen_height / 2

        self.left_click_ready = True
        self.last_left_click_time = 0

        self.right_click_ready = True
        self.last_right_click_time = 0

        self.previous_scroll_y = None
        self.mode_text = "Idle"

    def move_cursor(self, index_x, index_y, frame_width, frame_height):
        """Map index fingertip position from camera space to screen space."""
        target_x = np.interp(
            index_x,
            (FRAME_REDUCTION, frame_width - FRAME_REDUCTION),
            (0, self.screen_width),
        )
        target_y = np.interp(
            index_y,
            (FRAME_REDUCTION, frame_height - FRAME_REDUCTION),
            (0, self.screen_height),
        )

        target_x = np.clip(target_x, 0, self.screen_width - 1)
        target_y = np.clip(target_y, 0, self.screen_height - 1)

        distance = np.hypot(target_x - self.current_x, target_y - self.current_y)
        smoothing = FAST_SMOOTHING if distance > FAST_MOVE_DISTANCE else SMOOTHING

        self.current_x += (target_x - self.current_x) / smoothing
        self.current_y += (target_y - self.current_y) / smoothing

        pyautogui.moveTo(self.current_x, self.current_y, duration=0)

    def handle_left_click(self, is_left_click_mode):
        """Left click once when the user enters the two-finger gesture."""
        now = time.time()

        if is_left_click_mode:
            if self.left_click_ready and now - self.last_left_click_time > LEFT_CLICK_COOLDOWN:
                pyautogui.click(button="left")
                self.last_left_click_time = now
                self.left_click_ready = False
                return True
        else:
            self.left_click_ready = True

        return False

    def handle_right_click(self, is_right_click_mode):
        """Right click once when the user enters the middle-finger gesture."""
        now = time.time()

        if is_right_click_mode:
            if self.right_click_ready and now - self.last_right_click_time > RIGHT_CLICK_COOLDOWN:
                pyautogui.click(button="right")
                self.last_right_click_time = now
                self.right_click_ready = False
                return True
        else:
            self.right_click_ready = True

        return False

    def handle_scroll(self, landmark_list, is_scroll_mode):
        """Scroll by moving the index + middle + ring finger midpoint up or down."""
        if not is_scroll_mode:
            self.previous_scroll_y = None
            return 0

        index_y = landmark_list[8][2]
        middle_y = landmark_list[12][2]
        ring_y = landmark_list[16][2]
        scroll_y = (index_y + middle_y + ring_y) // 3

        if self.previous_scroll_y is None:
            self.previous_scroll_y = scroll_y
            return 0

        delta_y = scroll_y - self.previous_scroll_y
        self.previous_scroll_y = scroll_y

        if abs(delta_y) < SCROLL_DEAD_ZONE:
            return 0

        scroll_amount = int(np.clip(-delta_y * SCROLL_SENSITIVITY, -SCROLL_MAX_STEP, SCROLL_MAX_STEP))

        if scroll_amount != 0:
            pyautogui.scroll(scroll_amount)

        return scroll_amount

    @staticmethod
    def draw_debug_info(image, fps, mode_text, fingers):
        """Show helpful feedback while tuning gestures."""
        cv2.rectangle(
            image,
            (FRAME_REDUCTION, FRAME_REDUCTION),
            (image.shape[1] - FRAME_REDUCTION, image.shape[0] - FRAME_REDUCTION),
            (255, 255, 0),
            2,
        )

        cv2.rectangle(image, (0, 0), (420, 120), (20, 20, 20), cv2.FILLED)
        cv2.putText(image, f"FPS: {int(fps)}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(image, f"Mode: {mode_text}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(image, f"Fingers: {fingers}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)


def open_camera():
    """Open the webcam and request a low-latency capture setup."""
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        cap = cv2.VideoCapture(CAMERA_INDEX)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def main():
    pyautogui.PAUSE = 0
    pyautogui.MINIMUM_DURATION = 0
    pyautogui.FAILSAFE = True

    cap = open_camera()
    if not cap.isOpened():
        print("Could not open webcam. Check the camera index or permissions.")
        return

    mouse = VirtualMouse()
    previous_time = time.time()

    print("AI Virtual Mouse started. Press 'q' in the OpenCV window to quit.")

    try:
        while True:
            success, image = cap.read()
            if not success:
                print("Could not read frame from webcam.")
                break

            image = cv2.flip(image, 1)
            image = mouse.detector.find_hands(image, draw=True)
            landmark_list, _ = mouse.detector.find_position(image, draw=False)

            fingers = [0, 0, 0, 0, 0]
            mode_text = "Idle"

            if landmark_list:
                fingers = mouse.detector.fingers_up(landmark_list)
                index_x, index_y = landmark_list[8][1], landmark_list[8][2]
                frame_height, frame_width, _ = image.shape

                index_up = fingers[1] == 1
                middle_up = fingers[2] == 1
                ring_up = fingers[3] == 1
                pinky_up = fingers[4] == 1

                pointer_mode = index_up and not middle_up and not ring_up and not pinky_up
                left_click_mode = index_up and middle_up and not ring_up and not pinky_up
                scroll_mode = index_up and middle_up and ring_up and not pinky_up
                right_click_mode = (not index_up) and middle_up and not ring_up and not pinky_up

                if pointer_mode:
                    mouse.move_cursor(index_x, index_y, frame_width, frame_height)
                    mode_text = "Move"

                if left_click_mode:
                    mode_text = "Left click"
                    if mouse.handle_left_click(left_click_mode):
                        cv2.circle(image, (index_x, index_y), 22, (0, 255, 0), cv2.FILLED)
                else:
                    mouse.handle_left_click(False)

                if right_click_mode:
                    mode_text = "Right click"
                    mouse.handle_right_click(right_click_mode)
                else:
                    mouse.handle_right_click(False)

                if scroll_mode:
                    scroll_amount = mouse.handle_scroll(landmark_list, scroll_mode)
                    mode_text = f"Scroll {scroll_amount}"
                    cv2.circle(image, (index_x, index_y), 15, (255, 255, 0), cv2.FILLED)
                else:
                    mouse.handle_scroll(landmark_list, False)
            else:
                mouse.handle_left_click(False)
                mouse.handle_scroll([], False)
                mouse.handle_right_click(False)

            current_time = time.time()
            fps = 1 / max(current_time - previous_time, 0.001)
            previous_time = current_time

            mouse.draw_debug_info(image, fps, mode_text, fingers)
            cv2.imshow("AI Virtual Mouse", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except pyautogui.FailSafeException:
        print("PyAutoGUI fail-safe triggered. Move the mouse away from the top-left corner and restart.")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
