from math import pi

from settings import ANIMATION_FPS, IDLE_TIMEOUT, RUN_SPEED


class State:
    scale = 1.0
    running = False

    def enter(self, boy):
        self.elapsed = 0.0
        boy.frame = 0.0
        boy.clamp_to_screen()

    def update(self, boy, dt):
        pass

    def draw(self, boy):
        row = (100 if boy.face_dir == 1 else 0) if self.running else (
            300 if boy.face_dir == 1 else 200
        )
        boy.image.clip_draw(
            int(boy.frame) * 100, row, 100, 100,
            boy.x, boy.draw_y, boy.draw_size, boy.draw_size,
        )


class Idle(State):
    def enter(self, boy):
        super().enter(boy)
        boy.move_dir = 0

    def update(self, boy, dt):
        self.elapsed += dt
        boy.animate(dt, ANIMATION_FPS)
        if self.elapsed >= IDLE_TIMEOUT:
            boy.change_state(Sleep)


class Run(State):
    running = True

    def update(self, boy, dt):
        boy.animate(dt, ANIMATION_FPS)
        boy.x += boy.move_dir * RUN_SPEED * dt
        boy.clamp_to_screen()


class Sleep(State):
    def enter(self, boy):
        super().enter(boy)
        boy.move_dir = 0

    def draw(self, boy):
        row = 300 if boy.face_dir == 1 else 200
        boy.image.clip_composite_draw(
            0, row, 100, 100, boy.face_dir * pi / 2, '',
            boy.x, boy.draw_y - 25, boy.draw_size, boy.draw_size,
        )
