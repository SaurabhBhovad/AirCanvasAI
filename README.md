# 🎨 AirCanvasAI

A computer vision web application that transforms your hand into a virtual paintbrush. AirCanvasAI combines hand gesture recognition with real-time drawing capabilities, enabling intuitive interaction for digital annotation, online teaching, and collaborative presentations.

## ✨ Features

### Core Features
- **Gesture-Based Drawing**: Use your hand to draw on a virtual canvas in real-time
- **Multi-Color Support**: Choose from 7 different colors (Blue, Green, Red, Yellow, Cyan, Purple) plus eraser
- **Laser Pointer Mode**: Point at content without drawing when both index and middle fingers are raised
- **Screen Share Integration**: Toggle between webcam and desktop screen capture modes
- **PDF Annotation**: Annotate PDFs and documents with hand gestures
- **Picture-in-Picture**: View your camera feed while sharing your screen

### Advanced Capabilities
- **Real-Time Hand Tracking**: Powered by MediaPipe for accurate finger detection
- **Firebase Integration**: Track user sessions and save notes to Firestore database
- **User Management**: Support for multiple roles (Teacher, Student) with session tracking
- **Save & Clear**: Save your annotations as images or clear the canvas instantly
- **Responsive Web Interface**: Works on any system with a webcam

## 🛠 Tech Stack

- **Backend**: Python, Flask
- **Computer Vision**: OpenCV, MediaPipe
- **Web Frontend**: HTML5, JavaScript
- **Database**: Firebase Firestore
- **Screen Capture**: MSS (Multi-Screen Screenshot)
- **Video Streaming**: MJPEG over HTTP

## 📋 Project Structure

```
AirCanvasAI/
├── app.py              # Main Flask application & video streaming logic
├── board.html          # Drawing board interface
├── index.html          # Login/setup page
├── debug.py            # Debugging utilities
├── templates/          # HTML template directory
└── .gitignore          # Git ignore configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Webcam or camera device
- Flask
- OpenCV (cv2)
- MediaPipe
- Firebase Admin SDK
- MSS (Multi-Screen Screenshot)
- NumPy

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SaurabhBhovad/AirCanvasAI.git
   cd AirCanvasAI
   ```

2. **Install required dependencies**
   ```bash
   pip install flask opencv-python mediapipe firebase-admin numpy mss
   ```

3. **Setup Firebase (Optional)**
   - Create a Firebase project at https://firebase.google.com
   - Download your service account key as `serviceAccountKey.json`
   - Place it in the project root directory
   - If no Firebase key is found, the app will work in offline mode

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   - Open your browser and navigate to `http://localhost:5000`
   - Enter your name and role (Teacher/Student)
   - Click "Start Session" to begin

## 🎖️ How to Use

### Drawing Modes

#### Mode 1: Drawing (Index Finger Only)
- Raise only your **index finger** to activate drawing mode
- Move your finger to draw on the canvas
- Select colors from the color palette at the top (in webcam mode)
- The canvas automatically tracks your finger movements

#### Mode 2: Laser Pointer (Index + Middle Fingers)
- Raise both **index** and **middle fingers** to activate laser pointer mode
- A red glowing circle appears at your fingertip
- Use this to point at content without drawing
- Perfect for highlighting areas during presentations

### Canvas Actions

- **💾 Save Note**: Saves current drawing as an image file to `static/captures/`
- **🧟 Clear Board**: Clears all drawings from the canvas
- **📺 Toggle Screen Share**: Switch between webcam mode and desktop screen capture
- **Logout**: Return to the login page

## 🔇 How It Works

### Hand Detection Pipeline

1. **Frame Capture**: Real-time video captured from your webcam at 1280x720 resolution
2. **Hand Detection**: MediaPipe identifies hand landmarks (finger positions)
3. **Gesture Recognition**: Analyzes which fingers are raised to determine mode
4. **Drawing Logic**: 
   - Index finger position determines brush location
   - Line smoothing for smoother strokes
   - Color selection based on finger position in palette
5. **Canvas Composition**: Overlays drawings on live camera feed or screen
6. **Watermark**: Adds mentor name in bottom-right corner
7. **Stream Output**: Sends MJPEG stream to web browser

### Key Algorithms

- **Finger Detection**: Uses MediaPipe's pre-trained hand pose model
- **Smoothing**: Exponential smoothing (factor of 5) for fluid brush strokes
- **Color Selection**: Divides screen into 7 sections for color palette
- **Canvas Blending**: Uses bitwise operations for transparent drawing overlay

## 📁 File Descriptions

### app.py
Main Flask application containing:
- Firebase database initialization
- Hand detection and gesture recognition logic
- Video frame generation and MJPEG streaming
- Drawing canvas manipulation
- Route handlers for web interface
- Screen capture functionality

**Key Functions:**
- `generate_frames()`: Real-time video stream processing
- `index()`: User login/setup endpoint
- `board()`: Main drawing interface endpoint
- `toggle_mode()`: Switch between webcam and screen share
- `save_board()`: Save drawings as image
- `clear_board()`: Clear canvas

### board.html
Drawing interface with:
- Live video stream display
- Control buttons (Save, Clear, Toggle Screen Share)
- User information display
- Responsive button styling
- JavaScript handlers for board actions

### index.html
Login/setup page featuring:
- User name input field
- Role selection dropdown (Teacher/Student)
- Start session button
- Clean, centered UI design
- Form submission to Flask backend

### debug.py
Debugging utilities for development and testing.

## 🔗 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/` | GET/POST | Login page and user setup |
| `/board` | GET | Main drawing interface |
| `/video_feed` | GET | MJPEG video stream |
| `/toggle_mode` | POST | Switch webcam/screen mode |
| `/save_board` | POST | Save current drawing |
| `/clear_board` | POST | Clear canvas |

## 🔩 Configuration

### Adjustable Parameters (in app.py)

```python
brushThickness = 15        # Drawing brush thickness
eraserThickness = 50       # Eraser thickness
smoothening = 5            # Line smoothing factor (lower = smoother)
resolution = (1280, 720)   # Video resolution
min_detection_confidence = 0.85  # Hand detection confidence threshold
```

### Color Palette

```python
colors = [
    (0, 0, 0),      # Eraser
    (255, 0, 0),    # Blue
    (0, 255, 0),    # Green
    (0, 0, 255),    # Red
    (0, 255, 255),  # Yellow
    (255, 255, 0),  # Cyan
    (255, 0, 255)   # Purple
]
```

## 🛩️ Troubleshooting

### Issue: Webcam not detected
- **Solution**: Check if your webcam is properly connected and recognized by your OS
- Verify camera permissions in your operating system
- Try adjusting `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` if using a secondary camera

### Issue: Hand not being detected
- Ensure proper lighting conditions
- Keep your hand clearly visible in the frame
- Try adjusting `min_detection_confidence` to a lower value (e.g., 0.7) in app.py

### Issue: Drawing is shaky
- Increase the `smoothening` value (e.g., 10-15) for smoother strokes
- Improve lighting and camera focus
- Ensure your hand is moving smoothly

### Issue: Firebase connection error
- Download your service account key from Firebase console
- Place it in the project root directory as `serviceAccountKey.json`
- Or simply remove the JSON file to use offline mode

## 📚 Future Enhancements

- [ ] Support for multi-hand detection and drawing
- [ ] Hand gesture recognition for special tools (pan, zoom, etc.)
- [ ] Real-time collaboration with multiple users
- [ ] Drawing tools library (shapes, lines, arrows)
- [ ] PDF support for direct annotation
- [ ] Voice command integration
- [ ] Mobile app version
- [ ] Cloud storage integration
- [ ] Undo/Redo functionality
- [ ] Advanced gesture controls

## 🚀 Use Cases

### Educational Settings
- **Online Teaching**: Teachers can annotate slides and documents in real-time
- **Virtual Classroom**: Interactive whiteboard for student engagement
- **Exam Proctoring**: Screen share with annotation capabilities

### Professional Presentations
- **Live Demos**: Highlight areas of interest using laser pointer mode
- **Design Reviews**: Annotate designs and prototypes on-the-fly
- **Conference Talks**: Gesture-based drawing for interactive presentations

### Creative Applications
- **Digital Art**: Create freehand drawings and sketches
- **Animation**: Frame-by-frame drawing with canvas saves
- **Content Creation**: Annotate video tutorials and educational content

## 📝 Notes for Developers

### Running in Debug Mode
```bash
python app.py
```
The Flask app will run on `http://localhost:5000` with debug mode enabled.

### Customization Tips

1. **Change Canvas Size**: Modify `imgCanvas = np.zeros((720, 1280, 3), np.uint8)` in app.py
2. **Adjust Hand Detection**: Modify `min_detection_confidence` parameter
3. **Modify Colors**: Edit the `colors` list in the global settings section
4. **Add New Routes**: Follow the Flask `@app.route()` decorator pattern
5. **Styling**: Edit CSS in HTML files for UI customization

### Performance Optimization
- Reduce video resolution for slower systems
- Increase smoothening value to reduce processing overhead
- Use screen mode instead of webcam for better performance
- Monitor CPU usage with tools like Task Manager or Activity Monitor

## 🔍 Security Considerations

- Firebase credentials should be kept private (already in .gitignore)
- Run on localhost or trusted networks for local use
- For production deployment, implement proper authentication
- Sanitize user inputs for role and name fields
- Consider adding HTTPS for remote access

## 📚 Documentation & Resources

- [MediaPipe Hand Detection](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Firebase Documentation](https://firebase.google.com/docs)

## 🚑 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👥 Acknowledgments

- **MediaPipe**: For providing the excellent hand detection model
- **OpenCV**: For computer vision capabilities
- **Flask**: For the lightweight web framework
- **Firebase**: For database and real-time features

## 📋 Contact & Support

For questions, bug reports, or feature requests, please:
- Open an issue on GitHub
- Contact the developer
- Check existing documentation and issues first

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Status**: Active Development
