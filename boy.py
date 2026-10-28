from pathlib import Path

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a, load_image,
)

from settings import CANVAS_WIDTH, SPRITE_BOTTOM, SPRITE_SIZE
from states import AutoRun, Idle, Run, Sleep


class Boy:
    def __init__(self, image=None, canvas_width=CANVAS_WIDTH):
        self.x = canvas_width / 2
        self.frame = 0.0
        self.face_dir = 1
        self.move_dir = 0
        self.keys_down = set()
        self.canvas_width = canvas_width
        image_path = Path(__file__).resolve().parent / 'assets' / 'animation_sheet.png'
        self.image = image if image is not None else load_image(str(image_path))
        self.change_state(Idle)

    @property
    def state_name(self):
        return type(self.state).__name__

    @property
    def draw_size(self):
        return SPRITE_SIZE * self.state.scale

    @property
    def draw_y(self):
        return SPRITE_BOTTOM + self.draw_size / 2

    def change_state(self, state_class):
        self.state = state_class()
        self.state.enter(self)

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        if event.type == SDL_KEYDOWN:
            if event.key in self.keys_down:
                return
            self.keys_down.add(event.key)
        else:
            self.keys_down.discard(event.key)

        if isinstance(self.state, AutoRun):
            if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
                self.move_dir = 1 if event.key == SDLK_RIGHT else -1
                self.face_dir = self.move_dir
                self.change_state(Run)
            return

        if (isinstance(self.state, Idle) and event.type == SDL_KEYDOWN
                and event.key == SDLK_a):
            self.change_state(AutoRun)
            return

        if isinstance(self.state, Sleep):
            if event.type != SDL_KEYDOWN:
                return
            if event.key == SDLK_SPACE:
                self.change_state(Idle)
                return

        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return
        self.move_dir = (int(SDLK_RIGHT in self.keys_down)
                         - int(SDLK_LEFT in self.keys_down))
        if self.move_dir:
            self.face_dir = self.move_dir
            if not isinstance(self.state, Run):
                self.change_state(Run)
        elif isinstance(self.state, Run):
            self.change_state(Idle)

    def update(self, dt):
        self.state.update(self, max(0.0, dt))

    def animate(self, dt, fps):
        self.frame = (self.frame + fps * dt) % 8

    def clamp_to_screen(self):
        half = self.draw_size / 2
        self.x = max(half, min(self.canvas_width - half, self.x))

    def draw(self):
        self.state.draw(self)
