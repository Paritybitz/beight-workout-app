import cv2
import mediapipe as mp
import numpy as np

# Angle Calculation
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360.0 - angle

    return angle

def current_stage(angle):
    if angle >= 130:
        return 'Up'
    elif angle <= 90:
        return 'Down'
    else: 
        return "Mid"

def posture_check(shoulder, hip, knee, ankle):
    hip_angle = calculate_angle(shoulder, hip, knee)
    knee_angle = calculate_angle(hip, knee, ankle)

    if 160 <= hip_angle <= 200 and 160 <= knee_angle <= 200:
        return "Straight", hip_angle, knee_angle
    else:
        return "Bent", hip_angle, knee_angle

#### Main Capturing Function ####

def pushup_tracker():
    # Initialize Mediapipe Pose Detection
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    pushup_counter = 0
    check_posture = True

    # Init. vid capturing
    cap = cv2.VideoCapture(0)

    # Change vid res
    width = 1280 
    height = 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Image recoloring
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # Get landmark coordinates
            shoulder = [int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * width), 
                        int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * height)]
            elbow = [int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * width), 
                        int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * height)]
            wrist = [int(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * width), 
                        int(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * height)]
            hip = [int(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * width), 
                        int(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * height)]
            knee = [int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * width), 
                        int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * height)]
            ankle = [int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * width), 
                        int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * height)]
            
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            stage = current_stage(elbow_angle)
            posture, hip_angle, knee_angle = posture_check(shoulder, hip, knee, ankle)

            # Display text
            cv2.putText(image, 'Stage: {}'.format(stage), 
                        (50, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(image, 'Posture: {}'.format(posture), 
                        (50, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Elbow Angle: {:.2f}'.format(elbow_angle), 
                        (50, 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Hip Angle: {:.2f}'.format(hip_angle), 
                        (50, 250), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Knee Angle: {:.2f}'.format(knee_angle), 
                        (50, 300), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))

        except Exception as e:
            print(f"Exception: {e}")
        
        # Display the output using OpenCV
        cv2.imshow('Push-Up Tracker', image)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # End video capturing
    cap.release()
    cv2.destroyAllWindows()
