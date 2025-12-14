from render import Renderer
from game import GameManager


def main():
    gm = GameManager(1)
    renderer = Renderer(gm)
    renderer.main_loop()

if __name__ == "__main__":
    main()