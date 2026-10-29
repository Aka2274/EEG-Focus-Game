# ==========================================
# EEG HAUNTED FOREST - CONFIGURATION
# ==========================================

# -------------------------------
# SERIAL SETTINGS
# -------------------------------

PORT = "COM10"
BAUD_RATE = 230400

# Arduino EEG sample rate
SAMPLE_RATE = 500


# -------------------------------
# EEG PROCESSING
# -------------------------------

# Number of samples used for analysis
WINDOW_SIZE = 500

# Smoothing
SMOOTHING = 0.15


# -------------------------------
# GAME SETTINGS
# -------------------------------

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700

PLAYER_SPEED = 5

# Torch
MIN_TORCH_RADIUS = 90
MAX_TORCH_RADIUS = 350

# Focus
MIN_FOCUS = 0
MAX_FOCUS = 100


# -------------------------------
# GAME COLORS
# -------------------------------

BACKGROUND = "#07100b"
FOREST = "#102819"
TREE = "#183d24"
TREE_DARK = "#0b1d12"

PLAYER = "#dddddd"
TORCH_COLOR = "#ffd966"

MONSTER = "#8b1e1e"

TEXT = "#ffffff"

HEALTH_COLOR = "#e74c3c"
FOCUS_COLOR = "#4aa3ff"
TORCH_UI_COLOR = "#ffd966"
