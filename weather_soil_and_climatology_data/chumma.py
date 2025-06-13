import random
import pyautogui as pg
import time
animal=('sibin', 'rex','jay')
time.sleep(8)

for i in range(20):
    a=random.choice(animal)
    pg.write(a)
    pg.press('enter')