import requests
import os
import cv2
import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from CameraManager import CameraManager  # ✅ CameraManager for accessing the camera

# ✅ Firebase Configuration
FIREBASE_DATABASE_URL = "https://project-mavii1-default-rtdb.firebaseio.com"

class SignUpPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None  # ✅ Camera initialization
        self.is_scanning = False  # ✅ Track face scanning state
        self.full_name = ""

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # ✅ App Logo
        self.layout.add_widget(Image(source='logs.png', size_hint=(None, None), size=(120, 120), pos_hint={"center_x": 0.5}))

        # ✅ Signup Fields
        self.full_name_input = TextInput(hint_text="Full Name", multiline=False, size_hint=(1, 0.1))
        self.layout.add_widget(self.full_name_input)

        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(1, 0.1))
        self.layout.add_widget(self.password_input)

        self.confirm_password_input = TextInput(hint_text="Confirm Password", password=True, multiline=False, size_hint=(1, 0.1))
        self.layout.add_widget(self.confirm_password_input)

        # ✅ Category Selection
        self.category_spinner = Spinner(
            text="Select Category",
            values=["Teacher", "Student"],
            size_hint=(1, 0.1)
        )
        self.layout.add_widget(self.category_spinner)

        # ✅ Signup Error Label
        self.signup_error_label = Label(text="", color=(1, 0, 0, 1), size_hint=(1, 0.05))
        self.layout.add_widget(self.signup_error_label)

        # ✅ Signup Button
        self.signup_button = Button(text="Sign Up", size_hint=(1, 0.15), font_size=18, bold=True)
        self.signup_button.bind(on_press=self.start_signup)
        self.layout.add_widget(self.signup_button)

        # ✅ Navigation Buttons
        self.login_button = Button(text="Log In", size_hint=(1, 0.15), font_size=18, bold=True)
        self.login_button.bind(on_release=lambda x: setattr(self.manager, "current", "login_page"))
        self.layout.add_widget(self.login_button)

        self.add_widget(self.layout)

    def start_signup(self, instance):
        """Step 1: Validate user details before scanning face."""
        self.full_name = self.full_name_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        category = self.category_spinner.text.strip()

        if not self.full_name or not password or not confirm_password or category == "Select Category":
            self.signup_error_label.text = "Fill all fields!"
            return

        if password != confirm_password:
            self.signup_error_label.text = "Passwords do not match!"
            return

        # ✅ Store user data in Firebase
        db_url = f"{FIREBASE_DATABASE_URL}/users.json"
        user_info = {
            "full_name": self.full_name,
            "password": password,  # ⚠ Store hashed password in production
            "category": category
        }
        db_response = requests.post(db_url, json=user_info)

        if db_response.status_code == 200:
            # ✅ Proceed to Face Scan
            self.signup_error_label.text = "User registered! Scanning face..."
            self.capture_face()  # ✅ Capture face without displaying camera feed
        else:
            self.signup_error_label.text = "Error saving user data!"

    def capture_face(self):
        """Capture user's face and save the image (No Camera Feed)."""
        self.camera = CameraManager()
        ret, frame = self.camera.get_frame()

        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # ✅ Create `images` folder if it doesn't exist
            if not os.path.exists("images"):
                os.makedirs("images")

            # ✅ Save Image with Username
            image_path = os.path.join("images", f"{self.full_name}.jpg")
            cv2.imwrite(image_path, gray)
            print(f"✅ Face image saved: {image_path}")

            # ✅ Redirect to Login Page
            self.manager.current = "login_page"
