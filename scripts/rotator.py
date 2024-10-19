from colorsys import hsv_to_rgb

import requests

HOST = "http://localhost"
MODE = "direct-switch"

hue = 0
while 1:
  colour = list(map(lambda x: int(x * 255), hsv_to_rgb(hue, 1, 1)))
  print(colour)
  hue = (hue + 0.01) % 1
  requests.post(
      f"{HOST}/desk/light", json={"colour": colour, "mode": MODE}
  )
