from math import pi

from settings import (
    ANIMATION_FPS, AUTO_RUN_ANIMATION_FPS, AUTO_RUN_DURATION, AUTO_RUN_SCALE,
    AUTO_RUN_SPEED, IDLE_TIMEOUT, RUN_SPEED,
)


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


class AutoRun(State):
    scale = AUTO_RUN_SCALE
    running = True

    def enter(self, boy):
        super().enter(boy)
        boy.move_dir = boy.face_dir

    def update(self, boy, dt):
        # 긴 프레임에서도 AutoRun의 실제 이동 시간은 5초를 넘지 않는다.
        active_dt = min(dt, max(0.0, AUTO_RUN_DURATION - self.elapsed))
        self.elapsed += active_dt
        boy.animate(active_dt, AUTO_RUN_ANIMATION_FPS)
        boy.x += boy.face_dir * AUTO_RUN_SPEED * active_dt

        left = boy.draw_size / 2
        right = boy.canvas_width - left
        # 초과 이동량을 반사하므로 한 프레임에 여러 벽을 지나도 위치가 보존된다.
        while boy.x < left or boy.x > right:
            if boy.x > right:
                boy.x = 2 * right - boy.x
                boy.face_dir = -1
            elif boy.x < left:
                boy.x = 2 * left - boy.x
                boy.face_dir = 1
        if boy.x <= left:
            boy.face_dir = 1
        elif boy.x >= right:
            boy.face_dir = -1
        boy.move_dir = boy.face_dir

        if self.elapsed >= AUTO_RUN_DURATION:
            boy.change_state(Idle)
