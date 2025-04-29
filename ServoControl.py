from SingleServoJoint import SingleServoJoint
import time

shoulderYaw = SingleServoJoint(2, -90, 90, 90)

shoulderYaw.zero()
time.sleep(1)
shoulderYaw.move_to_angle(90)
time.sleep(1)
shoulderYaw.move_to_angle(-90)
time.sleep(1)
shoulderYaw.stop()