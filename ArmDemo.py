from FullArmControl import FullArmControl
import time


arm = FullArmControl(2, 3, 4, 14, 15, 18)
arm.zero()
time.sleep(2)
arm.demo()