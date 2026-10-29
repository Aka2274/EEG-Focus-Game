import serial
import threading
import time
import numpy as np

from config import (
    PORT,
    BAUD_RATE,
    SAMPLE_RATE,
    WINDOW_SIZE,
    SMOOTHING
)


class EEGProcessor:

    def __init__(self):

        self.port = PORT
        self.baud = BAUD_RATE

        self.ser = None
        self.running = False

        self.samples = []

        self.lock = threading.Lock()

        # Start from neutral value
        self.focus = 50.0

        self.theta_power = 0.0
        self.alpha_power = 0.0
        self.beta_power = 0.0

        self.thread = None

        # Calibration
        self.calibration_values = []

        self.baseline_low = None
        self.baseline_high = None

        self.packet_count = 0


    # =========================================================
    # CONNECT
    # =========================================================

    def connect(self):

        try:

            self.ser = serial.Serial(
                self.port,
                self.baud,
                timeout=1
            )

            time.sleep(2)

            self.ser.reset_input_buffer()

            # Start streaming
            self.ser.write(b"START\n")
            self.ser.flush()

            print()
            print("================================")
            print("EEG CONNECTED")
            print("PORT:", self.port)
            print("BAUD:", self.baud)
            print("================================")
            print()

            return True

        except Exception as e:

            print("EEG CONNECTION ERROR:")
            print(e)

            return False


    # =========================================================
    # START
    # =========================================================

    def start(self):

        if self.ser is None:

            if not self.connect():

                return False

        self.running = True

        self.thread = threading.Thread(
            target=self.read_loop,
            daemon=True
        )

        self.thread.start()

        return True


    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        self.running = False

        if self.ser:

            try:
                self.ser.close()
            except:
                pass


    # =========================================================
    # READ SERIAL DATA
    # =========================================================

    def read_loop(self):

        buffer = bytearray()

        while self.running:

            try:

                # Read available bytes
                data = self.ser.read(
                    self.ser.in_waiting or 1
                )

                if not data:
                    continue

                buffer.extend(data)

                # -----------------------------------------
                # Search for packets
                # -----------------------------------------

                while len(buffer) >= 16:

                    # Find synchronization bytes
                    if buffer[0] != 0xC7:

                        buffer.pop(0)
                        continue

                    if buffer[1] != 0x7C:

                        buffer.pop(0)
                        continue

                    # We have possible packet
                    packet = buffer[:16]

                    # Check ending byte
                    if packet[15] != 0x01:

                        buffer.pop(0)
                        continue

                    # Decode packet
                    channels = self.decode_packet(
                        packet
                    )

                    if channels is not None:

                        # Channel 1 = first EEG channel
                        eeg_value = channels[0]

                        self.add_sample(
                            eeg_value
                        )

                        self.packet_count += 1

                    # Remove processed packet
                    del buffer[:16]


            except Exception as e:

                print("Serial read error:", e)

                time.sleep(0.1)


    # =========================================================
    # DECODE 16-BYTE PACKET
    # =========================================================

    def decode_packet(self, packet):

        try:

            if len(packet) != 16:
                return None

            # Synchronization
            if packet[0] != 0xC7:
                return None

            if packet[1] != 0x7C:
                return None

            # End byte
            if packet[15] != 0x01:
                return None


            channels = []

            # -------------------------------------------------
            # Packet format:
            #
            # Byte 0  = C7
            # Byte 1  = 7C
            # Byte 2  = header/counter
            #
            # Bytes 3-14 = six 16-bit channels
            #
            # Byte 15 = 01
            #
            # BIG-ENDIAN
            # -------------------------------------------------

            for i in range(6):

                high = packet[
                    3 + i * 2
                ]

                low = packet[
                    4 + i * 2
                ]

                value = (
                    high << 8
                ) | low

                channels.append(value)


            return channels


        except Exception:

            return None


    # =========================================================
    # ADD EEG SAMPLE
    # =========================================================

    def add_sample(self, value):

        with self.lock:

            self.samples.append(
                float(value)
            )

            if len(self.samples) > WINDOW_SIZE:

                self.samples.pop(0)

            current_length = len(
                self.samples
            )

        # Calculate only when enough samples exist

        if current_length >= WINDOW_SIZE:

            self.calculate_focus()


    # =========================================================
    # CALCULATE FOCUS
    # =========================================================

    def calculate_focus(self):

        with self.lock:

            data = np.array(
                self.samples,
                dtype=float
            )

        if len(data) < WINDOW_SIZE:

            return


        # Remove DC component

        data = data - np.mean(data)


        # -----------------------------------------------------
        # FFT
        # -----------------------------------------------------

        window = np.hanning(
            len(data)
        )

        windowed = data * window

        fft = np.fft.rfft(
            windowed
        )

        frequencies = np.fft.rfftfreq(
            len(data),
            1 / SAMPLE_RATE
        )

        power = np.abs(fft) ** 2


        # -----------------------------------------------------
        # Frequency bands
        # -----------------------------------------------------

        theta = self.band_power(
            frequencies,
            power,
            4,
            8
        )

        alpha = self.band_power(
            frequencies,
            power,
            8,
            13
        )

        beta = self.band_power(
            frequencies,
            power,
            13,
            30
        )


        self.theta_power = theta
        self.alpha_power = alpha
        self.beta_power = beta


        # -----------------------------------------------------
        # Focus ratio
        # -----------------------------------------------------

        denominator = (
            alpha
            +
            theta
            +
            1e-12
        )

        raw_ratio = (
            beta / denominator
        )


        # Convert to 0-100

        focus = 100 * (
            raw_ratio /
            (1 + raw_ratio)
        )


        focus = np.clip(
            focus,
            0,
            100
        )


        # -----------------------------------------------------
        # Smooth focus
        # -----------------------------------------------------

        self.focus = (
            (1 - SMOOTHING)
            * self.focus
            +
            SMOOTHING
            * focus
        )


    # =========================================================
    # BAND POWER
    # =========================================================

    def band_power(
        self,
        frequencies,
        power,
        low,
        high
    ):

        mask = (
            (frequencies >= low)
            &
            (frequencies < high)
        )

        if not np.any(mask):

            return 0.0

        return float(
            np.mean(
                power[mask]
            )
        )


    # =========================================================
    # GET FOCUS
    # =========================================================

    def get_focus(self):

        return float(
            self.focus
        )


    # =========================================================
    # GET SAMPLES
    # =========================================================

    def get_samples(self):

        with self.lock:

            return list(
                self.samples
            )


    # =========================================================
    # GET EEG BANDS
    # =========================================================

    def get_bands(self):

        return (
            self.theta_power,
            self.alpha_power,
            self.beta_power
        )


    # =========================================================
    # DEBUG INFORMATION
    # =========================================================

    def get_status(self):

        with self.lock:

            sample_count = len(
                self.samples
            )

        return {
            "packets": self.packet_count,
            "samples": sample_count,
            "focus": self.focus,
            "theta": self.theta_power,
            "alpha": self.alpha_power,
            "beta": self.beta_power
        }
