import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Audio setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get coordinates of thumb tip (4) and index finger tip (8)
            x1 = int(hand_landmarks.landmark[4].x * w)
            y1 = int(hand_landmarks.landmark[4].y * h)
            x2 = int(hand_landmarks.landmark[8].x * w)
            y2 = int(hand_landmarks.landmark[8].y * h)

            # Draw circles and line
            cv2.circle(frame, (x1, y1), 10, (255, 0, 0), -1)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 0), -1)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Calculate distance
            distance = math.hypot(x2 - x1, y2 - y1)

            # Map distance to volume range
            vol = np.interp(distance, [30, 300], [min_vol, max_vol])
            volume.SetMasterVolumeLevel(vol, None)

            # Display volume level
            cv2.putText(frame, f'Volume: {int(np.interp(distance, [30, 300], [0, 100]))}%', 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Gesture Volume Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()