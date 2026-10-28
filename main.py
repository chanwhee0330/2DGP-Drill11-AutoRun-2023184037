from pathlib import Path
from time import perf_counter

from pico2d import (
    SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, clear_canvas, close_canvas, delay,
    get_events, load_image, open_canvas, update_canvas,
)

from boy import Boy
from settings import CANVAS_HEIGHT, CANVAS_WIDTH


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        assets = Path(__file__).resolve().parent / 'assets'
        grass = load_image(str(assets / 'grass.png'))
        boy = Boy()
        previous_time = perf_counter()
        running = True

        while running:
            now = perf_counter()
            dt = now - previous_time
            previous_time = now

            for event in get_events():
                if event.type == SDL_QUIT or (
                    event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE
                ):
                    running = False
                    break
                boy.handle_event(event)

            if not running:
                break
            boy.update(dt)
            clear_canvas()
            grass.draw(CANVAS_WIDTH / 2, 30)
            boy.draw()
            update_canvas()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
