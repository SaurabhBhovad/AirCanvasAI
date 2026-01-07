from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import cv2
import numpy as np
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, firestore
import os
import time
import math
import mss

app = Flask(__name__)

# --- 1. FIREBASE DATABASE SETUP ---
if not firebase_admin._apps:
    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    else:
        db = None

# --- 2. GLOBAL SETTINGS ---
current_user = {"name": "Teacher", "role": "Mentor"}
imgCanvas = np.zeros((720, 1280, 3), np.uint8)
mode = 'webcam'  # Start with Webcam. Toggle to 'screen' later.

# Drawing Settings
brushThickness = 15
eraserThickness = 50
smoothening = 5
plocX, plocY = 0, 0 

# Colors (B, G, R)
colors = [
    (0,0,0),       # Eraser
    (255, 0, 0),   # Blue
    (0, 255, 0),   # Green
    (0, 0, 255),   # Red
    (0, 255, 255), # Yellow
    (255, 255, 0), # Cyan
    (255, 0, 255)  # Purple
]
current_color = (0, 0, 255) # Default to Red

# --- 3. AI & SCREEN CAPTURE SETUP ---
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.85, min_tracking_confidence=0.8)
sct = mss.mss()
monitor = sct.monitors[1] # Monitor 1 (Change to 2 if you have dual monitors)

def draw_header(img):
    # Only draw the color palette if we are NOT in screen mode (to save screen space)
    # OR draw it semi-transparently. For now, we keep it simple.
    if mode == 'webcam':
        w = 1280 // len(colors)
        for i, color in enumerate(colors):
            cv2.rectangle(img, (i * w, 0), ((i + 1) * w, 80), color, cv2.FILLED)
            cv2.rectangle(img, (i * w, 0), ((i + 1) * w, 80), (255, 255, 255), 2)
            if i == 0:
                cv2.putText(img, "ERASER", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def generate_frames():
    global imgCanvas, plocX, plocY, current_color, mode
    
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    xp, yp = 0, 0

    while True:
        # A. Capture Camera (for Hand Detection)
        success, camera_img = cap.read()
        if not success: break
        camera_img = cv2.flip(camera_img, 1) # Mirror the camera

        # B. Determine Background (Webcam vs PDF/Screen)
        if mode == 'screen':
            try:
                # Capture Desktop
                screen_shot = np.array(sct.grab(monitor))
                img = cv2.cvtColor(screen_shot, cv2.COLOR_BGRA2BGR)
                img = cv2.resize(img, (1280, 720))
                
                # Add "Picture-in-Picture" (Small camera view in bottom left)
                pip_h, pip_w = 180, 320
                small_cam = cv2.resize(camera_img, (pip_w, pip_h))
                # Border for PiP
                cv2.rectangle(img, (0, 720-pip_h), (pip_w, 720), (255,255,255), 3)
                img[720-pip_h:720, 0:pip_w] = small_cam
                
            except Exception as e:
                print(f"Screen Error: {e}")
                img = camera_img
        else:
            img = camera_img

        # C. Hand Processing
        imgRGB = cv2.cvtColor(camera_img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                
                if len(lmList) != 0:
                    x1, y1 = lmList[8][1], lmList[8][2]   # Index Tip
                    x2, y2 = lmList[12][1], lmList[12][2] # Middle Tip

                    # Check which fingers are up
                    fingers = []
                    for id in [8, 12, 16, 20]:
                        if lmList[id][2] < lmList[id - 2][2]: fingers.append(1)
                        else: fingers.append(0)

                    # --- MODE 1: LASER POINTER (Index + Middle Up) ---
                    # Use this to point at the PDF without drawing
                    if fingers[0] and fingers[1]:
                        xp, yp = 0, 0
                        
                        # Draw a Glowing Laser Pointer
                        cv2.circle(img, (x1, y1), 20, (0, 0, 255), cv2.FILLED) # Red Dot
                        cv2.circle(img, (x1, y1), 25, (0, 0, 255), 2)          # Ring
                        
                        # If in Webcam mode, allow color selection
                        if mode == 'webcam' and y1 < 80:
                            section_width = 1280 // len(colors)
                            index = x1 // section_width
                            if index < len(colors):
                                current_color = colors[index]

                    # --- MODE 2: DRAWING (Index Up Only) ---
                    # Use this to write notes
                    if fingers[0] and not fingers[1]:
                        # Smoothing
                        clocX = plocX + (x1 - plocX) / smoothening
                        clocY = plocY + (y1 - plocY) / smoothening
                        
                        cv2.circle(img, (int(clocX), int(clocY)), 15, current_color, cv2.FILLED)
                        
                        if xp == 0 and yp == 0: xp, yp = int(clocX), int(clocY)
                        
                        thickness = eraserThickness if current_color == (0,0,0) else brushThickness
                        
                        cv2.line(imgCanvas, (xp, yp), (int(clocX), int(clocY)), current_color, thickness)
                        
                        xp, yp = int(clocX), int(clocY)
                        plocX, plocY = clocX, clocY

        # D. Combine Layers
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        
        if img.shape != imgCanvas.shape:
             img = cv2.resize(img, (1280, 720))

        try:
            img = cv2.bitwise_and(img, imgInv)
            img = cv2.bitwise_or(img, imgCanvas)
        except: pass

        if mode == 'webcam':
            draw_header(img)
        
        # --- E. WATERMARK (Bottom Right) ---
        # "Mentor: [Name]"
        text = f"MENTOR: {current_user['name'].upper()}"
        
        # 1. Background Box (Black) - Makes it readable on White PDFs
        cv2.rectangle(img, (900, 660), (1280, 720), (0,0,0), cv2.FILLED)
        
        # 2. Text (White)
        # Position slightly adjusted
        cv2.putText(img, text, (920, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # F. Stream Frame
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        global current_user
        current_user = {"name": name, "role": role}
        if db:
            db.collection("users").add({"name": name, "role": role, "timestamp": firestore.SERVER_TIMESTAMP})
        return redirect(url_for('board'))
    return render_template('index.html')

@app.route('/board')
def board():
    return render_template('board.html', user=current_user)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    global mode
    if mode == 'webcam': mode = 'screen'
    else: mode = 'webcam'
    return jsonify({"status": mode})

@app.route('/save_board', methods=['POST'])
def save_board():
    if not os.path.exists("static/captures"): os.makedirs("static/captures")
    filename = f"static/captures/{current_user['name']}_{int(time.time())}.jpg"
    cv2.imwrite(filename, imgCanvas)
    return jsonify({"status": "saved", "file": filename})

@app.route('/clear_board', methods=['POST'])
def clear_board():
    global imgCanvas
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)