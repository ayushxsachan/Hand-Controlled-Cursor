# Hand Gesture Controlled Virtual Mouse

A real-time **AI-powered virtual mouse** that allows users to control their computer cursor using **hand gestures** through a webcam.  
The project uses **Computer Vision** and **Hand Tracking** to create a touchless human-computer interaction system.

---

## 🚀 Features

- 🎯 Real-time hand tracking using webcam
- 🖱️ Control mouse cursor with hand movements
- 👆 Perform left click using finger gestures
- ✌️ Scroll functionality using gesture combinations
- 🧠 Smooth cursor movement with interpolation & filtering
- ⚡ Fast and lightweight implementation
- 📷 No external hardware required

---

## 🛠️ Tech Stack

- **Python**
- **OpenCV** – Video capture and image processing
- **MediaPipe** – Hand landmark detection
- **PyAutoGUI** – Mouse automation
- **NumPy** – Mathematical operations

---

## 📂 Project Structure

```bash
Hand-Controlled-Cursor/
│
├── main.py
├── hand_tracking.py
├── requirements.txt
├── README.md
└── assets/
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/hand-controlled-cursor.git
cd hand-controlled-cursor
```

### 2️⃣ Create Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate environment:

#### Windows
```bash
venv\Scripts\activate
```

#### macOS/Linux
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install opencv-python mediapipe pyautogui numpy
```

---

## ▶️ Usage

Run the project using:

```bash
python main.py
```

Ensure:
- Webcam is enabled
- Good lighting conditions are available
- Hand is visible within the camera frame

---

## ✋ Gesture Controls

| Gesture | Action |
|----------|---------|
| Index Finger Up | Move Cursor |
| Index + Thumb Pinch | Left Click |
| Two Fingers Up | Scroll |
| Closed Fist | Pause Tracking |

---

## 🧠 How It Works

1. Webcam captures live video feed.
2. MediaPipe detects hand landmarks.
3. Finger tip coordinates are extracted.
4. Coordinates are mapped to screen dimensions.
5. PyAutoGUI performs mouse actions based on gestures.
6. Smoothing algorithms reduce cursor jitter for better usability.

---

## 🔥 Challenges Faced

- Reducing cursor jitter
- Improving click accuracy
- Mapping camera coordinates to screen resolution
- Maintaining real-time performance with low latency

---

## 📈 Future Improvements

- Right-click support
- Drag-and-drop gestures
- Multi-hand recognition
- Custom gesture training using ML models
- Voice + gesture hybrid control system

---

## 🎯 Applications

- Touchless computer interaction
- Accessibility solutions
- Smart classrooms
- Gaming interfaces
- Gesture-based UI systems

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Ayush Sachan**

- AI & Software Engineering Enthusiast
- Interested in Computer Vision, Automation, and AI Systems

---

## ⭐ Show Your Support

If you like this project, give it a ⭐ on GitHub!
