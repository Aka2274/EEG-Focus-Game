import tkinter as tk
import math
import random

from eeg import EEGProcessor

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_SPEED,
    MIN_TORCH_RADIUS,
    MAX_TORCH_RADIUS
)


# ============================================================
# EEG HAUNTED FOREST
# ============================================================

class HauntedForest:

    def __init__(self, root):

        self.root = root

        self.root.title("EEG Haunted Forest")

        self.root.geometry(
            f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}"
        )

        self.root.resizable(False, False)


        # ====================================================
        # CANVAS
        # ====================================================

        self.canvas = tk.Canvas(
            root,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            bg="#020502",
            highlightthickness=0
        )

        self.canvas.pack()


        # ====================================================
        # EEG
        # ====================================================

        self.eeg = EEGProcessor()

        if not self.eeg.start():

            print("EEG could not start.")

        else:

            print("EEG started successfully.")


        # ====================================================
        # PLAYER
        # ====================================================

        self.player_x = SCREEN_WIDTH / 2
        self.player_y = SCREEN_HEIGHT / 2

        self.player_radius = 14

        self.dx = 0
        self.dy = 0


        # ====================================================
        # HEALTH
        # ====================================================

        self.health = 100


        # ====================================================
        # KEYS
        # ====================================================

        self.keys = []

        self.keys_collected = 0

        self.TOTAL_KEYS = 10

        self.create_keys()


        # ====================================================
        # MONSTERS
        # ====================================================

        self.monsters = []

        self.create_monsters()


        # ====================================================
        # TREES
        # ====================================================

        self.trees = []

        self.create_forest()


        # ====================================================
        # KEYBOARD
        # ====================================================

        self.keys_pressed = set()

        self.root.bind(
            "<KeyPress>",
            self.key_down
        )

        self.root.bind(
            "<KeyRelease>",
            self.key_up
        )


        # ====================================================
        # GAME
        # ====================================================

        self.game_running = True

        self.update()


    # ========================================================
    # CREATE FOREST
    # ========================================================

    def create_forest(self):

        random.seed(20)

        self.trees = []

        for _ in range(85):

            x = random.randint(
                40,
                SCREEN_WIDTH - 40
            )

            y = random.randint(
                100,
                SCREEN_HEIGHT - 40
            )

            distance = self.distance(
                x,
                y,
                self.player_x,
                self.player_y
            )

            if distance < 130:

                continue

            self.trees.append(
                (x, y)
            )


    # ========================================================
    # CREATE 10 KEYS
    # ========================================================

    def create_keys(self):

        self.keys = [

            # Top-left
            [120, 130, False],

            # Upper-left
            [300, 180, False],

            # Upper-middle
            [500, 120, False],

            # Upper-right
            [780, 150, False],

            # Far-right
            [950, 280, False],

            # Bottom-right
            [900, 540, False],

            # Lower-middle-right
            [700, 500, False],

            # Bottom-middle
            [500, 580, False],

            # Bottom-left
            [250, 520, False],

            # Left-middle
            [120, 350, False]

        ]


    # ========================================================
    # CREATE MONSTERS
    # ========================================================

    def create_monsters(self):

        self.monsters = [

            {
                "x": 100,
                "y": 140,
                "visible": False,
                "speed": 0.65,
                "damage": 0.12
            },

            {
                "x": 950,
                "y": 140,
                "visible": False,
                "speed": 0.80,
                "damage": 0.15
            },

            {
                "x": 940,
                "y": 570,
                "visible": False,
                "speed": 0.70,
                "damage": 0.13
            },

            {
                "x": 100,
                "y": 570,
                "visible": False,
                "speed": 0.90,
                "damage": 0.17
            },

            {
                "x": 760,
                "y": 470,
                "visible": False,
                "speed": 0.75,
                "damage": 0.14
            },

            {
                "x": 450,
                "y": 130,
                "visible": False,
                "speed": 0.60,
                "damage": 0.10
            }

        ]


    # ========================================================
    # KEYBOARD
    # ========================================================

    def key_down(self, event):

        self.keys_pressed.add(
            event.keysym.lower()
        )


    def key_up(self, event):

        self.keys_pressed.discard(
            event.keysym.lower()
        )


    # ========================================================
    # DISTANCE
    # ========================================================

    def distance(
        self,
        x1,
        y1,
        x2,
        y2
    ):

        return math.sqrt(
            (x1 - x2) ** 2
            +
            (y1 - y2) ** 2
        )


    # ========================================================
    # PLAYER MOVEMENT
    # ========================================================

    def move_player(self):

        self.dx = 0
        self.dy = 0


        if "w" in self.keys_pressed:

            self.dy -= PLAYER_SPEED


        if "s" in self.keys_pressed:

            self.dy += PLAYER_SPEED


        if "a" in self.keys_pressed:

            self.dx -= PLAYER_SPEED


        if "d" in self.keys_pressed:

            self.dx += PLAYER_SPEED


        # Normalize diagonal movement

        if self.dx != 0 and self.dy != 0:

            self.dx *= 0.707

            self.dy *= 0.707


        self.player_x += self.dx
        self.player_y += self.dy


        # Screen boundaries

        self.player_x = max(
            25,
            min(
                SCREEN_WIDTH - 25,
                self.player_x
            )
        )


        self.player_y = max(
            90,
            min(
                SCREEN_HEIGHT - 25,
                self.player_y
            )
        )


    # ========================================================
    # GET EEG FOCUS
    # ========================================================

    def get_focus(self):

        focus = self.eeg.get_focus()

        return max(
            0,
            min(
                100,
                focus
            )
        )


    # ========================================================
    # TORCH RADIUS
    # ========================================================

    def get_torch_radius(self):

        focus = self.get_focus()

        ratio = focus / 100.0

        radius = (
            MIN_TORCH_RADIUS
            +
            ratio *
            (
                MAX_TORCH_RADIUS
                -
                MIN_TORCH_RADIUS
            )
        )

        return radius


    # ========================================================
    # KEY VISIBILITY
    #
    # 0-5%     = invisible
    # 5-30%    = very faint
    # 30-60%   = medium
    # 60-80%   = bright
    # 80-100%  = glowing
    # ========================================================

    def get_key_visibility(self):

        focus = self.get_focus()


        # ----------------------------------------------
        # BELOW 5%
        # Completely invisible
        # ----------------------------------------------

        if focus < 5:

            return 0.0


        # ----------------------------------------------
        # 5-100%
        # Gradually increase visibility
        # ----------------------------------------------

        visibility = (
            focus - 5
        ) / 95


        return max(
            0.0,
            min(
                1.0,
                visibility
            )
        )


    # ========================================================
    # CAN COLLECT KEY?
    # ========================================================

    def can_collect_keys(self):

        focus = self.get_focus()

        return focus >= 5


    # ========================================================
    # COLLECT KEYS
    # ========================================================

    def collect_keys(self):

        if not self.can_collect_keys():

            return


        for key in self.keys:

            x, y, collected = key


            if collected:

                continue


            d = self.distance(
                self.player_x,
                self.player_y,
                x,
                y
            )


            if d < 35:

                key[2] = True

                self.keys_collected += 1

                print(
                    f"KEY COLLECTED!"
                    f" {self.keys_collected}"
                    f"/{self.TOTAL_KEYS}"
                )


    # ========================================================
    # DRAW KEYS
    # ========================================================

    def draw_keys(self):

        visibility = (
            self.get_key_visibility()
        )


        # ----------------------------------------------------
        # BELOW 5%
        # ----------------------------------------------------

        if visibility <= 0:

            return


        for x, y, collected in self.keys:

            if collected:

                continue


            # =================================================
            # 5-20%
            # VERY FAINT
            # =================================================

            if visibility < 0.20:

                self.canvas.create_oval(
                    x - 7,
                    y - 7,
                    x + 7,
                    y + 7,
                    fill="#3c381d",
                    outline=""
                )

                continue


            # =================================================
            # 20-40%
            # FAINT KEY
            # =================================================

            if visibility < 0.40:

                self.canvas.create_oval(
                    x - 9,
                    y - 9,
                    x + 9,
                    y + 9,
                    fill="#77702b",
                    outline=""
                )

                self.canvas.create_line(
                    x + 7,
                    y,
                    x + 22,
                    y,
                    fill="#77702b",
                    width=3
                )

                continue


            # =================================================
            # 40-60%
            # MEDIUM KEY
            # =================================================

            if visibility < 0.60:

                self.canvas.create_oval(
                    x - 10,
                    y - 10,
                    x + 10,
                    y + 10,
                    fill="#aaa22e",
                    outline=""
                )

                self.canvas.create_line(
                    x + 8,
                    y,
                    x + 28,
                    y,
                    fill="#aaa22e",
                    width=4
                )

                self.canvas.create_line(
                    x + 20,
                    y,
                    x + 20,
                    y + 7,
                    fill="#aaa22e",
                    width=3
                )

                continue


            # =================================================
            # 60-80%
            # BRIGHT KEY
            # =================================================

            if visibility < 0.80:

                self.canvas.create_oval(
                    x - 11,
                    y - 11,
                    x + 11,
                    y + 11,
                    fill="#e0c52e",
                    outline=""
                )

                self.canvas.create_line(
                    x + 9,
                    y,
                    x + 31,
                    y,
                    fill="#e0c52e",
                    width=5
                )

                self.canvas.create_line(
                    x + 20,
                    y,
                    x + 20,
                    y + 8,
                    fill="#e0c52e",
                    width=3
                )

                self.canvas.create_line(
                    x + 27,
                    y,
                    x + 27,
                    y + 6,
                    fill="#e0c52e",
                    width=3
                )

                continue


            # =================================================
            # 80-100%
            # FULL GLOWING KEY
            # =================================================

            # Outer glow

            self.canvas.create_oval(
                x - 22,
                y - 22,
                x + 22,
                y + 22,
                outline="#fff2a6",
                width=2
            )

            self.canvas.create_oval(
                x - 16,
                y - 16,
                x + 16,
                y + 16,
                outline="#ffe866",
                width=2
            )


            # Key ring

            self.canvas.create_oval(
                x - 11,
                y - 11,
                x + 11,
                y + 11,
                fill="#ffd700",
                outline="#fff5b0",
                width=2
            )


            # Key shaft

            self.canvas.create_line(
                x + 9,
                y,
                x + 36,
                y,
                fill="#ffd700",
                width=5
            )


            # Key teeth

            self.canvas.create_line(
                x + 21,
                y,
                x + 21,
                y + 10,
                fill="#ffd700",
                width=3
            )

            self.canvas.create_line(
                x + 29,
                y,
                x + 29,
                y + 7,
                fill="#ffd700",
                width=3
            )


    # ========================================================
    # UPDATE MONSTERS
    # ========================================================

    def update_monsters(
        self,
        torch_radius
    ):

        for monster in self.monsters:

            x = monster["x"]
            y = monster["y"]


            d = self.distance(
                self.player_x,
                self.player_y,
                x,
                y
            )


            # ------------------------------------------------
            # Monster enters torch
            # ------------------------------------------------

            if d <= torch_radius:

                monster["visible"] = True


            # ------------------------------------------------
            # Monster disappears into darkness
            # ------------------------------------------------

            elif d > torch_radius * 1.5:

                monster["visible"] = False


            # ------------------------------------------------
            # Monster follows player
            # ------------------------------------------------

            if monster["visible"]:

                dx = (
                    self.player_x
                    -
                    monster["x"]
                )

                dy = (
                    self.player_y
                    -
                    monster["y"]
                )


                length = math.sqrt(
                    dx * dx
                    +
                    dy * dy
                )


                if length > 45:

                    monster["x"] += (
                        dx / length
                        *
                        monster["speed"]
                    )

                    monster["y"] += (
                        dy / length
                        *
                        monster["speed"]
                    )


            # ------------------------------------------------
            # DAMAGE
            # ------------------------------------------------

            if d < 38:

                self.health -= (
                    monster["damage"]
                )


        self.health = max(
            0,
            self.health
        )


    # ========================================================
    # DRAW FOREST
    # ========================================================

    def draw_forest(self):

        self.canvas.create_rectangle(
            0,
            70,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            fill="#07140b",
            outline=""
        )


        # ----------------------------------------------------
        # GRASS
        # ----------------------------------------------------

        random.seed(10)

        for _ in range(350):

            x = random.randint(
                0,
                SCREEN_WIDTH
            )

            y = random.randint(
                75,
                SCREEN_HEIGHT
            )


            self.canvas.create_line(
                x,
                y,
                x + 2,
                y - 5,
                fill="#174824"
            )


        # ----------------------------------------------------
        # TREES
        # ----------------------------------------------------

        for x, y in self.trees:

            # Trunk

            self.canvas.create_rectangle(
                x - 7,
                y,
                x + 7,
                y + 35,
                fill="#28180f",
                outline=""
            )


            # Lower foliage

            self.canvas.create_polygon(
                x,
                y - 35,
                x - 32,
                y + 10,
                x + 32,
                y + 10,
                fill="#12371f",
                outline=""
            )


            # Upper foliage

            self.canvas.create_polygon(
                x,
                y - 20,
                x - 25,
                y + 25,
                x + 25,
                y + 25,
                fill="#0d2c18",
                outline=""
            )


    # ========================================================
    # DRAW MONSTER
    # ========================================================

    def draw_one_monster(
        self,
        monster
    ):

        if not monster["visible"]:

            return


        x = monster["x"]
        y = monster["y"]


        # Shadow

        self.canvas.create_oval(
            x - 28,
            y - 32,
            x + 28,
            y + 32,
            fill="#160303",
            outline=""
        )


        # Body

        self.canvas.create_oval(
            x - 21,
            y - 26,
            x + 21,
            y + 26,
            fill="#571313",
            outline="#c83232",
            width=2
        )


        # Left horn

        self.canvas.create_polygon(
            x - 14,
            y - 19,
            x - 27,
            y - 38,
            x - 5,
            y - 22,
            fill="#3b0909",
            outline=""
        )


        # Right horn

        self.canvas.create_polygon(
            x + 14,
            y - 19,
            x + 27,
            y - 38,
            x + 5,
            y - 22,
            fill="#3b0909",
            outline=""
        )


        # Left eye

        self.canvas.create_oval(
            x - 12,
            y - 9,
            x - 4,
            y - 1,
            fill="#ff3333",
            outline=""
        )


        # Right eye

        self.canvas.create_oval(
            x + 4,
            y - 9,
            x + 12,
            y - 1,
            fill="#ff3333",
            outline=""
        )


        # Mouth

        self.canvas.create_arc(
            x - 11,
            y,
            x + 11,
            y + 17,
            start=180,
            extent=180,
            style=tk.ARC,
            outline="#ff7777",
            width=2
        )


    # ========================================================
    # DRAW ALL MONSTERS
    # ========================================================

    def draw_monsters(self):

        for monster in self.monsters:

            self.draw_one_monster(
                monster
            )


    # ========================================================
    # DRAW PLAYER
    # ========================================================

    def draw_player(self):

        # Body

        self.canvas.create_oval(
            self.player_x - 15,
            self.player_y - 15,
            self.player_x + 15,
            self.player_y + 15,
            fill="#dddddd",
            outline="#ffffff",
            width=2
        )


        # Torch center

        self.canvas.create_oval(
            self.player_x - 5,
            self.player_y - 5,
            self.player_x + 5,
            self.player_y + 5,
            fill="#fff3a6",
            outline=""
        )


    # ========================================================
    # DRAW TORCH
    # ========================================================

    def draw_torch(
        self,
        radius
    ):

        # ----------------------------------------------------
        # Darkness
        # ----------------------------------------------------

        self.canvas.create_rectangle(
            0,
            70,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            fill="#000000",
            stipple="gray75",
            outline=""
        )


        # ----------------------------------------------------
        # Light rings
        # ----------------------------------------------------

        steps = 18


        for i in range(
            steps,
            0,
            -1
        ):

            r = radius * (
                i / steps
            )


            brightness = int(
                20
                +
                100 *
                (
                    1 -
                    i / steps
                )
            )


            brightness = max(
                15,
                min(
                    120,
                    brightness
                )
            )


            color = (
                f"#{brightness:02x}"
                f"{brightness:02x}"
                f"{int(brightness * 0.55):02x}"
            )


            self.canvas.create_oval(
                self.player_x - r,
                self.player_y - r,
                self.player_x + r,
                self.player_y + r,
                fill=color,
                outline=""
            )


        # ----------------------------------------------------
        # Player
        # ----------------------------------------------------

        self.draw_player()


    # ========================================================
    # HUD
    # ========================================================

    def draw_hud(
        self,
        focus,
        torch_radius
    ):

        # Top bar

        self.canvas.create_rectangle(
            0,
            0,
            SCREEN_WIDTH,
            70,
            fill="#0d0d0d",
            outline=""
        )


        # Title

        self.canvas.create_text(
            20,
            20,
            text="EEG HAUNTED FOREST",
            anchor="w",
            fill="white",
            font=(
                "Arial",
                16,
                "bold"
            )
        )


        # Health

        self.canvas.create_text(
            300,
            20,
            text=f"HP: {int(self.health)}",
            anchor="w",
            fill="#ff5555",
            font=(
                "Arial",
                13,
                "bold"
            )
        )


        # Focus

        self.canvas.create_text(
            410,
            20,
            text=f"FOCUS: {int(focus)}%",
            anchor="w",
            fill="#4aa3ff",
            font=(
                "Arial",
                13,
                "bold"
            )
        )


        # Torch

        self.canvas.create_text(
            550,
            20,
            text=f"TORCH: {int(torch_radius)}",
            anchor="w",
            fill="#ffd966",
            font=(
                "Arial",
                13,
                "bold"
            )
        )


        # Keys

        self.canvas.create_text(
            700,
            20,
            text=(
                f"KEYS: "
                f"{self.keys_collected}"
                f"/"
                f"{self.TOTAL_KEYS}"
            ),
            anchor="w",
            fill="#ffd700",
            font=(
                "Arial",
                13,
                "bold"
            )
        )


        # ----------------------------------------------------
        # Focus status
        # ----------------------------------------------------

        if focus < 5:

            status = "TOO DISTRACTED - KEYS HIDDEN"

            status_color = "#ff4444"

        elif focus < 30:

            status = "WEAK FOCUS - KEYS FAINT"

            status_color = "#cc9933"

        elif focus < 60:

            status = "FOCUSING - SEARCH CAREFULLY"

            status_color = "#dddd55"

        elif focus < 80:

            status = "GOOD FOCUS - KEYS VISIBLE"

            status_color = "#66dd88"

        else:

            status = "HIGH FOCUS - TORCH BRIGHT"

            status_color = "#ffff66"


        self.canvas.create_text(
            SCREEN_WIDTH - 20,
            50,
            text=status,
            anchor="e",
            fill=status_color,
            font=(
                "Arial",
                10,
                "bold"
            )
        )


        # Controls

        self.canvas.create_text(
            20,
            50,
            text=(
                "W A S D = Move"
                "   |   "
                "Focus to strengthen torch"
                "   |   "
                "Find all 10 keys"
            ),
            anchor="w",
            fill="#aaaaaa",
            font=(
                "Arial",
                10
            )
        )


    # ========================================================
    # GAME OVER
    # ========================================================

    def game_over(self):

        self.canvas.create_rectangle(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            fill="#000000",
            stipple="gray50",
            outline=""
        )


        self.canvas.create_text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 50,
            text="YOU WERE LOST IN THE FOREST",
            fill="#ff4444",
            font=(
                "Arial",
                28,
                "bold"
            )
        )


        self.canvas.create_text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 10,
            text=(
                f"Keys found: "
                f"{self.keys_collected}/"
                f"{self.TOTAL_KEYS}"
            ),
            fill="#ffd700",
            font=(
                "Arial",
                16
            )
        )


        self.canvas.create_text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 50,
            text="Press R to restart",
            fill="white",
            font=(
                "Arial",
                14
            )
        )


        self.root.bind(
            "<r>",
            lambda e: self.restart()
        )


    # ========================================================
    # WIN SCREEN
    # ========================================================

    def win_screen(self):

        self.canvas.create_rectangle(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            fill="#000000",
            stipple="gray50",
            outline=""
        )


        self.canvas.create_text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 60,
            text="YOU ESCAPED!",
            fill="#66ff88",
            font=(
                "Arial",
                38,
                "bold"
            )
        )


        self.canvas.create_text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            text="ALL 10 KEYS FOUND",
            fill="#ffd700",
            font=(
                "Arial",
                22,
                "bold"
            )
        )


        self.canvas.create_text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 45,
            text="Press R to play again",
            fill="white",
            font=(
                "Arial",
                14
            )
        )


        self.root.bind(
            "<r>",
            lambda e: self.restart()
        )


    # ========================================================
    # RESTART
    # ========================================================

    def restart(self):

        self.player_x = SCREEN_WIDTH / 2
        self.player_y = SCREEN_HEIGHT / 2

        self.health = 100

        self.keys_collected = 0

        self.keys_pressed.clear()

        self.create_keys()

        self.create_monsters()

        self.create_forest()

        self.root.unbind(
            "<r>"
        )


    # ========================================================
    # MAIN GAME LOOP
    # ========================================================

    def update(self):

        self.canvas.delete(
            "all"
        )


        # ====================================================
        # GAME OVER
        # ====================================================

        if self.health <= 0:

            self.draw_forest()

            self.game_over()

            self.root.after(
                30,
                self.update
            )

            return


        # ====================================================
        # WIN
        # ====================================================

        if self.keys_collected >= self.TOTAL_KEYS:

            self.draw_forest()

            self.win_screen()

            self.root.after(
                30,
                self.update
            )

            return


        # ====================================================
        # MOVE
        # ====================================================

        self.move_player()


        # ====================================================
        # EEG
        # ====================================================

        focus = self.get_focus()

        torch_radius = (
            self.get_torch_radius()
        )


        # ====================================================
        # GAME LOGIC
        # ====================================================

        self.collect_keys()

        self.update_monsters(
            torch_radius
        )


        # ====================================================
        # DRAW
        # ====================================================

        self.draw_forest()

        self.draw_keys()

        self.draw_monsters()

        self.draw_torch(
            torch_radius
        )

        self.draw_hud(
            focus,
            torch_radius
        )


        # ====================================================
        # NEXT FRAME
        # ====================================================

        self.root.after(
            30,
            self.update
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    game = HauntedForest(
        root
    )

    root.mainloop()
