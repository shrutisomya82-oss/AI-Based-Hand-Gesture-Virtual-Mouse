import cv2
import time
import numpy as np

import config  # Import our shared settings
from hand_tracker import HandTracker
from gesture_controller import GestureController


def run_virtual_mouse():
    """Runs the main virtual mouse loop (called by the GUI thread)"""
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandTracker()
    controller = GestureController()
    
    p_time = 0
    c_time = 0
    click_time = 0.0
    
    # Coordinates for smoothening
    smooth_x, smooth_y = 0.0, 0.0

    frame_reduction = 150  
    box_color = (255, 0, 255)

    # Main loop runs as long as the GUI keeps config.running True
    while config.running:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame = detector.find_hands(frame)
        landmark_list = detector.find_position(frame)

        # Draw boundary box
        cv2.rectangle(
            frame, 
            (frame_reduction, frame_reduction), 
            (1280 - frame_reduction, 720 - frame_reduction), 
            box_color, 
            2
        )

        if len(landmark_list) != 0:
            fingers = detector.fingers_up(landmark_list)
            x = landmark_list[8][1]
            y = landmark_list[8][2]

            # Boundary box logic
            if frame_reduction < x < (1280 - frame_reduction) and frame_reduction < y < (720 - frame_reduction):
                box_color = (0, 255, 0)
            else:
                box_color = (0, 0, 255)

            # LERP smoothening using dynamic config value
            smooth_x = smooth_x + (x - smooth_x) / config.smoothening
            smooth_y = smooth_y + (y - smooth_y) / config.smoothening

            # Screen mapping
            mapped_x = np.interp(smooth_x, (frame_reduction, 1280 - frame_reduction), (0, 1280))
            mapped_y = np.interp(smooth_y, (frame_reduction, 720 - frame_reduction), (0, 720))

            cv2.circle(frame, (int(smooth_x), int(smooth_y)), 12, (255, 0, 255), cv2.FILLED)

            # Display finger counts
            cv2.putText(
                frame,
                f"Fingers: {fingers}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            thumb_index = detector.find_distance(4, 8, frame)
            thumb_middle = detector.find_distance(4, 12, frame)

            gesture = "Idle"

            # -----------------------------
            # Gestures
            # -----------------------------
            if fingers == [0, 1, 0, 0, 0]:
                controller.move_mouse(mapped_x, mapped_y, 1280, 720)
                gesture = "Move"

            elif fingers == [0, 1, 1, 0, 0]:
                controller.move_mouse(mapped_x, mapped_y, 1280, 720)
                if time.time() - click_time > config.click_delay:
                    controller.left_click()
                    click_time = time.time()
                gesture = "Left Click"

            elif thumb_index < 35:
                x1, y1 = landmark_list[4][1], landmark_list[4][2]
                x2, y2 = landmark_list[8][1], landmark_list[8][2]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.circle(frame, ((x1+x2)//2, (y1+y2)//2), 8, (0, 255, 0), cv2.FILLED)

                if time.time() - click_time > config.click_delay:
                    controller.right_click()
                    click_time = time.time()
                gesture = "Right Click"

            elif thumb_middle < 35:
                x1, y1 = landmark_list[4][1], landmark_list[4][2]
                x2, y2 = landmark_list[12][1], landmark_list[12][2]
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                cv2.circle(frame, ((x1+x2)//2, (y1+y2)//2), 8, (255, 0, 0), cv2.FILLED)

                if time.time() - click_time > config.click_delay:
                    controller.double_click()
                    click_time = time.time()
                gesture = "Double Click"

            elif fingers == [0, 0, 0, 0, 0]:
                controller.move_mouse(mapped_x, mapped_y, 1280, 720)
                controller.mouse_down()
                gesture = "Drag"

            elif fingers == [0, 1, 1, 1, 0]:
                controller.scroll_up()
                gesture = "Scroll Up"

            elif fingers == [0, 0, 1, 1, 1]:
                controller.scroll_down()
                gesture = "Scroll Down"

            elif fingers == [1, 1, 1, 1, 1]:
                gesture = "Stop"

            elif fingers == [0, 1, 1, 0, 1]:
                if time.time() - click_time > config.click_delay:
                    controller.take_screenshot()
                    click_time = time.time()
                gesture = "Screenshot"

            else:
                controller.mouse_up()
                gesture = "Idle"

            cv2.putText(
                frame,
                f"Gesture : {gesture}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
            )
        else:
            box_color = (255, 0, 255)

        # FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) != 0 else 0
        p_time = c_time
        cv2.putText(
            frame,
            f"FPS : {int(fps)}",
            (1000, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2,
        )

        cv2.imshow("AI Hand Gesture Virtual Mouse", frame)

        # Non-blocking key check 
        if cv2.waitKey(1) & 0xFF == ord("q"):
            config.running = False
            break

    # Clean cleanup when loop stops
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Fallback to run directly if needed
    config.running = True
    run_virtual_mouse()