import cv2
import mediapipe as mp


class HandTracker:

    def __init__(self):
        # Initialize MediaPipe Hands
        self.mpHands = mp.solutions.hands

        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Drawing utility
        self.mpDraw = mp.solutions.drawing_utils

        # Store hand detection results
        self.results = None

        # Fingertip landmark IDs
        self.tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, frame, draw=True):
        """
        Detect hand and draw landmarks.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        frame,
                        hand,
                        self.mpHands.HAND_CONNECTIONS
                    )
        return frame

    def find_position(self, frame, hand_no=0):
        """
        Return all hand landmark positions.
        """
        landmark_list = []

        if self.results and self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_no]
            h, w, c = frame.shape

            for id, landmark in enumerate(hand.landmark):
                cx = int(landmark.x * w)
                cy = int(landmark.y * h)
                landmark_list.append([id, cx, cy])

        return landmark_list

    def fingers_up(self, landmark_list):
        """
        Returns a list indicating which fingers are up.
        Example: [0, 1, 0, 0, 0] -> Only index finger up
        """
        fingers = []

        if len(landmark_list) == 0:
            return fingers

        # Thumb (Simple check: is the thumb tip to the right/left of the joint?)
        if landmark_list[self.tip_ids[0]][1] > landmark_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Index, Middle, Ring, Little (Is the tip above the knuckle joint?)
        for i in range(1, 5):
            if landmark_list[self.tip_ids[i]][2] < landmark_list[self.tip_ids[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
    
    def find_distance(self, p1, p2, frame, draw=True):
        """
        Finds the pixel distance between two landmarks.
        """
        landmark_list = self.find_position(frame)

        if len(landmark_list) == 0:
            return 0

        # Extract coordinates for points p1 and p2
        x1, y1 = landmark_list[p1][1], landmark_list[p1][2]
        x2, y2 = landmark_list[p2][1], landmark_list[p2][2]

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        if draw:
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(frame, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), cv2.FILLED)

        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        return length


# -------------------------------------------------
# Testing Hand Tracker
# -------------------------------------------------

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = HandTracker()

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Mirror the frame for a more natural interaction
        frame = cv2.flip(frame, 1)
        frame = detector.find_hands(frame)
        landmark_list = detector.find_position(frame)

        if len(landmark_list) != 0:
            # Print index finger tip (ID 8) coordinates
            print("Index Finger:", landmark_list[8])

            # Print fingers up/down status
            print("Fingers:", detector.fingers_up(landmark_list))
            
            # Example: Find and print distance between thumb (4) and index finger (8)
            dist = detector.find_distance(4, 8, frame, draw=True)
            print(f"Pinch Distance: {dist:.1f} px")

        cv2.imshow("Hand Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()