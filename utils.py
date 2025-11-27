import math

# --- CONFIGURATION ---
# Known width of objects in centimeters (Real World)
KNOWN_WIDTHS = {
    "person": 50.0,      # Average shoulder width
    "cell phone": 7.5,   # Average width
    "bottle": 6.5,       # Average diameter
    "cup": 8.0,
    "chair": 50.0,
    "potted plant": 20.0,
    "laptop": 35.0,
    "mouse": 6.0,
    "keyboard": 45.0,
    "book": 15.0
}

# Default Focal Length (Pixel units) - Needs Calibration!
DEFAULT_FOCAL_LENGTH = 600.0 

def calculate_distance(pixel_width, real_width, focal_length):
    """
    Calculate distance from the camera to the object.
    Formula: D = (W * F) / P
    """
    if pixel_width == 0: 
        return 0
    return (real_width * focal_length) / pixel_width
