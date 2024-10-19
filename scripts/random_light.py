from colorsys import hsv_to_rgb
from random import random

import requests

HOST = "http://localhost"
MODE = "sector-diverge"
MODE = "spot-fill"
#MODE = "direct-switch"
#MODE = "sweep"
COUNT = 10

for i in range(COUNT):
  colour = list(map(lambda x: int(x * 255), hsv_to_rgb(random(), 1, 1)))
  direction = "forwards"
  if i % 2 == 0:
      direction = "backwards"

  print(colour)
  requests.post(
          f"{HOST}/desk/light", json={"colour": colour, "mode": MODE, "direction": direction}
  )
