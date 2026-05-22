import math

import cv2
import mediapipe as mp


class HandDetector:
    """Small wrapper around MediaPipe Hands for easier beginner use."""

    def __init__(
        self,
        mode=False,
        max_hands=1,
        model_complexity=0,
        detection_confidence=0.7,
        tracking_confidence=0.7,
    ):
        self.mode = mode
        self.max_hands = max_hands
        self.model_complexity = model_complexity
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

        self.results = None
        self.hand_label = None
        self.tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, image, draw=True):
        """Detect hands in a BGR OpenCV image and optionally draw landmarks."""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)

        if self.results.multi_handedness:
            self.hand_label = self.results.multi_handedness[0].classification[0].label
        else:
            self.hand_label = None

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw_styles.get_default_hand_landmarks_style(),
                    self.mp_draw_styles.get_default_hand_connections_style(),
                )

        return image

    def find_position(self, image, hand_no=0, draw=True):
        """
        Return a list of landmarks for one hand.

        Each item looks like: [landmark_id, x_pixel, y_pixel, z_depth]
        """
        landmark_list = []
        bbox = None

        if not self.results or not self.results.multi_hand_landmarks:
            return landmark_list, bbox

        if hand_no >= len(self.results.multi_hand_landmarks):
            return landmark_list, bbox

        hand = self.results.multi_hand_landmarks[hand_no]
        height, width, _ = image.shape
        x_values = []
        y_values = []

        for landmark_id, landmark in enumerate(hand.landmark):
            cx = int(landmark.x * width)
            cy = int(landmark.y * height)
            landmark_list.append([landmark_id, cx, cy, landmark.z])
            x_values.append(cx)
            y_values.append(cy)

            if draw:
                cv2.circle(image, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        bbox = (min(x_values), min(y_values), max(x_values), max(y_values))

        if draw:
            x_min, y_min, x_max, y_max = bbox
            cv2.rectangle(image, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20), (0, 255, 0), 2)

        return landmark_list, bbox

    def fingers_up(self, landmark_list):
        """
        Return which fingers are up as a list: [thumb, index, middle, ring, pinky].

        This app mainly uses index/middle/ring/pinky. Thumb detection is included
        for completeness, but it can vary more with camera angle and hand rotation.
        """
        if len(landmark_list) < 21:
            return [0, 0, 0, 0, 0]

        fingers = []

        # Thumb: compare tip with the previous joint along the x-axis.
        if self.hand_label == "Left":
            fingers.append(1 if landmark_list[self.tip_ids[0]][1] < landmark_list[self.tip_ids[0] - 1][1] else 0)
        else:
            fingers.append(1 if landmark_list[self.tip_ids[0]][1] > landmark_list[self.tip_ids[0] - 1][1] else 0)

        # Other fingers: a fingertip is "up" when it is above its PIP joint.
        for finger_index in range(1, 5):
            tip_id = self.tip_ids[finger_index]
            fingers.append(1 if landmark_list[tip_id][2] < landmark_list[tip_id - 2][2] else 0)

        return fingers

    @staticmethod
    def find_distance(point1_id, point2_id, landmark_list, image=None, draw=True):
        """Return distance between two landmarks and optionally draw the measurement."""
        x1, y1 = landmark_list[point1_id][1], landmark_list[point1_id][2]
        x2, y2 = landmark_list[point2_id][1], landmark_list[point2_id][2]
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        distance = math.hypot(x2 - x1, y2 - y1)

        if image is not None and draw:
            cv2.circle(image, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(image, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(image, (center_x, center_y), 8, (0, 255, 0), cv2.FILLED)

        return distance, (x1, y1, x2, y2, center_x, center_y)
