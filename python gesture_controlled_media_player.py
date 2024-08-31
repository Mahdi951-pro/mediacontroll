import cv2
import mediapipe as mp
import pyautogui
import subprocess

# Initialize MediaPipe and OpenCV
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize media control variables
is_playing = False
previous_gesture = None

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw landmarks on the hand
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get coordinates for thumb (4) and index finger (8) tips
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

            # Calculate distance between thumb and index finger tips
            distance = ((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2) ** 0.5

            # Gesture: Pinch (Play/Pause)
            if distance < 50:
                if previous_gesture != "pinch":
                    pyautogui.press('playpause')
                    is_playing = not is_playing
                    previous_gesture = "pinch"

            # Gesture: Swipe Right (Next Track)
            elif thumb_x < 100 and previous_gesture != "swipe_right":
                pyautogui.press('nexttrack')
                previous_gesture = "swipe_right"

            # Gesture: Swipe Left (Previous Track)
            elif thumb_x > w - 100 and previous_gesture != "swipe_left":
                pyautogui.press('prevtrack')
                previous_gesture = "swipe_left"

            # Gesture: Move Up/Down (Volume Control)
            elif index_y < h // 4 and previous_gesture != "move_up":
                pyautogui.press('volumeup')
                previous_gesture = "move_up"
            elif index_y > 3 * h // 4 and previous_gesture != "move_down":
                pyautogui.press('volumedown')
                previous_gesture = "move_down"
            else:
                previous_gesture = None

    # Display the frame
    cv2.imshow("Gesture-Controlled Media Player by MAHDI", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
