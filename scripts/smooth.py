from colorsys import hsv_to_rgb

import requests

HOST = "http://localhost"
MODE = "direct-switch"
INCREMENT = 0.001

while True:
    hue = 0.0
    while hue < 1.0:
        rgb = hsv_to_rgb(hue, 1, 1)
        colour = list(map(lambda x: int(x * 255), rgb))
        print(colour)
        requests.post(
          f"{HOST}/desk/light", json={"colour": colour, "mode": MODE}
        )
        hue += INCREMENT

#for _ in range(COUNT):
#  colour = list(map(lambda x: int(x * 255), hsv_to_rgb(random(), 1, 1)))
#  print(colour)
#  requests.post(
#      f"{HOST}/desk/light", json={"colour": colour, "mode": MODE}
#  )
