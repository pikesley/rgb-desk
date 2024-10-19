# from colorsys import hsv_to_rgb
from random import random
# from time import sleep

import requests

HOST = "http://localhost"
MODE = "spot-fill"
# INTERVAL = 20

# while True:
# colour = list(map(lambda x: int(x * 255), hsv_to_rgb(random(), 1, 1)))
# print(colour)
requests.post(
  f"{HOST}/desk/light", json={"hue": random(), "mode": MODE}
)
  # sleep(INTERVAL)
