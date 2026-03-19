import time, math

odrv0 = odrive.find_any()
axis = odrv0.axis0

# 配置为力矩模式
axis.requested_state = AXIS_STATE_IDLE
axis.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
axis.controller.config.input_mode = INPUT_MODE_PASSTHROUGH
axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

# 参数：输出侧 ±20Nm，0.5Hz
A_out = 20.0
f = 0.5
dt = 0.005      # 200Hz
T = 30.0        # 跑30秒
gear = float(axis.motor.config.gear_ratio)

t0 = time.time()
try:
    while time.time() - t0 < T:
        t = time.time() - t0
        tau_out = A_out * math.sin(2 * math.pi * f * t)
        tau_rotor = tau_out / gear   # 输出侧 -> 转子侧
        axis.controller.input_torque = tau_rotor
        time.sleep(dt)
finally:
    axis.controller.input_torque = 0.0
    axis.requested_state = AXIS_STATE_IDLE
    print("done")
