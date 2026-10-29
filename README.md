# EEG-Focus-Game
EEG-integrated survival game using the Upside Down Labs single-channel EEG kit

# EEG Focus Game 🌲🎮

An EEG-integrated survival game that combines real-time brainwave signal processing with interactive gameplay using the **Upside Down Labs Neuroscience Kit**.

## About the Project

EEG Focus Game is a brain-computer interaction project in which EEG signals are processed to estimate a focus score. This score influences the player's torch visibility while navigating a haunted forest, collecting keys, and avoiding monsters.

The project explores the integration of EEG signal processing with gaming to create an interactive experience controlled by brain-derived signals.

## Features

- Real-time EEG signal acquisition
- Serial communication with EEG hardware
- EEG frequency analysis using Fast Fourier Transform (FFT)
- Theta, alpha, and beta frequency-band analysis
- Experimental focus score estimation
- Dynamic torch visibility based on the estimated focus score
- Haunted forest survival gameplay

## Technologies Used

- **Python** — core programming language
- **Tkinter** — graphical user interface
- **NumPy** — numerical computation and signal processing
- **PySerial** — serial communication with EEG hardware
- **Upside Down Labs Neuroscience Kit** — EEG data acquisition

## Project Structure

```text
EEG-Focus-Game/
├── main.py
├── eeg.py
├── config.py
└── README.md
```

- `main.py` — main game logic and graphical interface
- `eeg.py` — EEG data acquisition and signal processing
- `config.py` — EEG hardware settings and game configuration

## Requirements

- Python 3.x
- Upside Down Labs Neuroscience Kit
- USB connection to the EEG device
- Compatible device firmware and serial data format

## Installation

Install the required Python libraries:

```bash
pip install numpy pyserial
```

Tkinter is generally included with Python installations; some Linux distributions may require installing it separately.

## How to Run

1. Connect the EEG device to your computer.
2. Identify the serial/COM port assigned to the device.
3. Open `config.py` and update the `PORT` value to match your device.
4. Verify that the baud rate matches the device firmware.
5. Run the game:

   ```bash
   python main.py
   ```

## EEG Signal Processing

The EEG module reads incoming serial data and processes the first EEG channel. Fast Fourier Transform (FFT) is used to estimate activity in the following frequency bands:

- Theta: 4–8 Hz
- Alpha: 8–13 Hz
- Beta: 13–30 Hz

These frequency-band estimates are used to calculate an experimental focus score. The score is smoothed over time and used by the game to influence torch visibility.

The focus score is an experimental signal-derived estimate and is not a clinically validated measurement of attention or concentration.

## Gameplay

The player explores a haunted forest environment while managing visibility and avoiding monsters. The torch radius changes according to the EEG-derived focus score, connecting EEG signal processing with game mechanics.

## Limitations

- EEG recordings can be affected by movement, electrode contact, and electrical interference.
- Focus estimates may vary with recording conditions and individual differences.
- Performance depends on correct hardware configuration and serial communication.
- The focus estimation algorithm requires further testing and validation.

## Project Status

Prototype — exploring real-time EEG signal processing and brain-computer interaction in gaming.

## Future Improvements

- Improve EEG artifact handling and signal quality.
- Validate focus estimation against suitable reference measurements.
- Add new game levels and interactive features.
- Evaluate the relationship between EEG features and gameplay performance.

---

EEG Focus Game — Connecting brain signals with interactive gameplay.🧠🎮
