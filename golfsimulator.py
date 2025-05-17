import tkinter as tk
import math

# Constantes
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
CLUB_WEIGHTS = [1, 2, 3]
CLUB_COLORS = ["#FFD700", "#A9A9A9", "#8B0000"]
FRICTION = 0.98
SPEED_THRESHOLD = 0.5
MAX_ATTEMPTS = 3
HOLE_RADIUS = BALL_RADIUS + 5
ATTRACTION_RADIUS = 50 
ATTRACTION_FORCE = 0.1


class Ball:
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.moving = False
        self.visible = True

    def update(self, obstacles, hole_center):
        if self.moving and self.visible:
            distance_to_hole = math.hypot(
                self.x - hole_center[0], self.y - hole_center[1])
            if distance_to_hole < ATTRACTION_RADIUS:
                angle_to_hole = math.atan2(
                    hole_center[1] - self.y, hole_center[0] - self.x)
                self.vx += ATTRACTION_FORCE * math.cos(angle_to_hole)
                self.vy += ATTRACTION_FORCE * math.sin(angle_to_hole)

            self.x += self.vx
            self.y += self.vy
            self.vx *= FRICTION
            self.vy *= FRICTION

            for obstacle in obstacles:
                ox1, oy1, ox2, oy2 = obstacle
                if ox1 <= self.x <= ox2 and oy1 <= self.y <= oy2:
                    self.vx *= -1
                    self.vy *= -1

            if self.x - BALL_RADIUS < 0 or self.x + BALL_RADIUS > WIDTH:
                self.vx *= -1
                self.x = max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, self.x))
            if self.y - BALL_RADIUS < 0 or self.y + BALL_RADIUS > HEIGHT:
                self.vy *= -1
                self.y = max(BALL_RADIUS, min(HEIGHT - BALL_RADIUS, self.y))

            if abs(self.vx) < SPEED_THRESHOLD and abs(self.vy) < SPEED_THRESHOLD and distance_to_hole > HOLE_RADIUS:
                self.vx = 0
                self.vy = 0
                self.moving = False
            elif distance_to_hole <= HOLE_RADIUS:
                self.visible = False
                return True
        return False

    def hit(self, angle_deg, power, club_weight):
        angle_rad = math.radians(angle_deg)
        self.vx = power * math.cos(angle_rad) / club_weight
        self.vy = -power * math.sin(angle_rad) / club_weight
        self.moving = True


class Level:
    def __init__(self, canvas, number):
        self.canvas = canvas
        self.number = number
        self.setup_level()

    def setup_level(self):
        if self.number == 1:
            self.ball_start = (100, 300)
            self.hole = (700, 300)
            self.obstacles = [(300, 200, 320, 400)]
        elif self.number == 2:
            self.ball_start = (100, 100)
            self.hole = (700, 500)
            self.obstacles = [(400, 100, 420, 500), (200, 400, 600, 420)]
        elif self.number == 3:
            self.ball_start = (150, 550)
            self.hole = (650, 50)
            self.obstacles = [(300, 300, 500, 320), (500, 100, 520, 400)]

    def draw(self):
        self.canvas.delete("all")
        for obs in self.obstacles:
            self.canvas.create_rectangle(obs, fill="gray")
        self.canvas.create_oval(self.hole[0] - HOLE_RADIUS, self.hole[1] - HOLE_RADIUS,
                                self.hole[0] +
                                HOLE_RADIUS, self.hole[1] + HOLE_RADIUS,
                                fill="black")


class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="green")
        self.canvas.pack()
        self.level_number = 1
        self.attempts = MAX_ATTEMPTS
        self.game_over = False
        self.game_won = False
        self.angle = 0
        self.power = 0
        self.club_weight_index = 0
        self.setup_ui()
        self.load_level()
        self.update()

    def setup_ui(self):
        self.angle_slider = tk.Scale(self.root, from_=0, to=360, orient="horizontal", label="Angle",
                                     command=lambda v: self.set_angle(float(v)))
        self.angle_slider.pack()
        self.power_slider = tk.Scale(self.root, from_=0, to=100, orient="horizontal", label="Power",
                                     command=lambda v: self.set_power(float(v)))
        self.power_slider.pack()
        self.club_slider = tk.Scale(self.root, from_=0, to=2, orient="horizontal", label="Club Weight",
                                    command=lambda v: self.set_club(int(v)))
        self.club_slider.pack()
        self.hit_button = tk.Button(self.root, text="Hit", command=self.hit)
        self.hit_button.pack()
        self.attempts_label = tk.Label(
            self.root, text=f"Attempts: {self.attempts}/{MAX_ATTEMPTS}")
        self.attempts_label.pack()

    def load_level(self):
        self.level = Level(self.canvas, self.level_number)
        self.ball = Ball(*self.level.ball_start)
        self.level.draw()
        self.update_attempts_label()
        self.game_over = False
        self.game_won = False

    def set_angle(self, v):
        self.angle = v

    def set_power(self, v):
        self.power = v

    def set_club(self, i):
        self.club_weight_index = i

    def hit(self):
        if not self.ball.moving and self.attempts > 0 and not self.game_over and not self.game_won:
            self.ball.hit(self.angle, self.power,
                          CLUB_WEIGHTS[self.club_weight_index])
            self.attempts -= 1
            self.update_attempts_label()

    def update(self):
        if not self.game_over and not self.game_won:
            hole_center = self.level.hole
            if self.ball.visible:
                ball_in_hole = self.ball.update(
                    self.level.obstacles, hole_center)
                if ball_in_hole:
                    self.game_won = True
                    self.show_end_screen("YOU WIN!")
            self.redraw()
            self.check_game_over_condition()
        self.root.after(16, self.update)

    def redraw(self):
        self.level.draw()
        if self.ball.visible:
            self.canvas.create_oval(self.ball.x - BALL_RADIUS, self.ball.y - BALL_RADIUS,
                                    self.ball.x + BALL_RADIUS, self.ball.y + BALL_RADIUS,
                                    fill="white")

        if not self.ball.moving and self.ball.visible:
            club_length = 30 + self.power * 0.5
            tx = self.ball.x + club_length * math.cos(math.radians(self.angle))
            ty = self.ball.y - club_length * math.sin(math.radians(self.angle))
            club_color = CLUB_COLORS[self.club_weight_index]
            self.canvas.create_line(
                self.ball.x, self.ball.y, tx, ty, width=6, fill=club_color)

    def check_game_over_condition(self):
        if self.attempts == 0 and not self.ball.moving and not self.game_won and not self.game_over:
            self.game_over = True
            self.show_end_screen("GAME OVER")

    def show_end_screen(self, message):
        end_screen = tk.Toplevel(self.root)
        end_screen.title("Game Over")

        label = tk.Label(end_screen, text=message, font=("Arial", 32))
        label.pack(pady=20)

        retry_button = tk.Button(
            end_screen, text="Retry", command=self.restart_level)
        retry_button.pack(pady=10)

        quit_button = tk.Button(end_screen, text="Quit",
                                command=self.root.destroy)
        quit_button.pack(pady=10)

        if message == "YOU WIN!":
            next_level_button = tk.Button(
                end_screen, text="Next Level", command=self.next_level)
            next_level_button.pack(pady=10)

    def restart_level(self):
        self.attempts = MAX_ATTEMPTS
        self.load_level()

    def next_level(self):
        self.level_number += 1
        if self.level_number > 3:
            self.level_number = 1
        self.restart_level()

    def update_attempts_label(self):
        self.attempts_label.config(
            text=f"Attempts: {self.attempts}/{MAX_ATTEMPTS}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Mini Golf Game")
    game = Game(root)
    root.mainloop()
