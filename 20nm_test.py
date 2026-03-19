import time, math

odrv0 = odrive.find_any()
axis = odrv0.axis0

# 力矩模式
axis.requested_state = AXIS_STATE_IDLE
axis.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
axis.controller.config.input_mode = INPUT_MODE_PASSTHROUGH
axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

# 测试参数
A_out = 20.0     # 输出侧幅值 Nm
f = 0.5          # Hz
dt = 0.02        # 50Hz（与你监测频率一致）
T = 30.0         # 秒
gear = float(axis.motor.config.gear_ratio)

t0 = time.time()
try:
    while True:
        t = time.time() - t0
        if t >= T:
            break

        # 输出侧 -> 转子侧
        tau_out = A_out * math.sin(2 * math.pi * f * t)
        tau_rotor = tau_out / gear
        axis.controller.input_torque = tau_rotor

        # 实时监测输出
        print(
            f"t={t:6.2f} "
            f"cmd_out={tau_out:7.3f} "
            f"cmd_rotor={tau_rotor:7.3f} "
            f"state={axis.current_state} "
            f"axis_err=0x{int(axis.error):X} "
            f"motor_err=0x{int(axis.motor.error):X} "
            f"enc_err=0x{int(axis.encoder.error):X} "
            f"ctrl_err=0x{int(axis.controller.error):X} "
            f"sys_err=0x{int(odrv0.error):X} "
            f"vbus={odrv0.vbus_voltage:.2f} "
            f"ibus={odrv0.ibus:.2f} "
            f"vel={axis.encoder.vel_estimate:.3f} "
            f"iq={axis.motor.current_control.Iq_measured:.3f}"
        )

        time.sleep(dt)

finally:
    axis.controller.input_torque = 0.0
    axis.requested_state = AXIS_STATE_IDLE
    print("done")
