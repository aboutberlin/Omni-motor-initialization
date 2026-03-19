import time

while True:
    try:
        print(
            f"state={odrv0.axis0.current_state} "
            f"axis_err=0x{int(odrv0.axis0.error):X} "
            f"motor_err=0x{int(odrv0.axis0.motor.error):X} "
            f"enc_err=0x{int(odrv0.axis0.encoder.error):X} "
            f"ctrl_err=0x{int(odrv0.axis0.controller.error):X} "
            f"sys_err=0x{int(odrv0.error):X} "
            f"vbus={odrv0.vbus_voltage:.2f} "
            f"ibus={odrv0.ibus:.2f} "
            f"vel={odrv0.axis0.encoder.vel_estimate:.3f} "
            f"iq={odrv0.axis0.motor.current_control.Iq_measured:.3f}"
        )
    except Exception as e:
        print("read_err:", e)
    time.sleep(0.02)  # 50Hz



# 在 odrivetool 里执行
# odrv0 = odrive.find_any()

def get_attr_path(root, path):
    obj = root
    for part in path.split("."):
        obj = getattr(obj, part)
    return obj

params = [
    # ===== 你的原始参数 =====
    ("gear_ratio", "axis0.motor.config.gear_ratio"),
    ("torque_constant", "axis0.motor.config.torque_constant"),
    ("current_lim", "axis0.motor.config.current_lim"),

    ("vel_limit", "axis0.controller.config.vel_limit"),
    ("enable_vel_limit", "axis0.controller.config.enable_vel_limit"),
    ("enable_torque_mode_vel_limit", "axis0.controller.config.enable_torque_mode_vel_limit"),
    ("torque_ramp_rate", "axis0.controller.config.torque_ramp_rate"),

    ("dc_max_positive_current", "config.dc_max_positive_current"),
    ("dc_max_negative_current", "config.dc_max_negative_current"),
    ("dc_bus_overvoltage_trip_level", "config.dc_bus_overvoltage_trip_level"),
    ("dc_bus_undervoltage_trip_level", "config.dc_bus_undervoltage_trip_level"),

    ("enable_brake_resistor", "config.enable_brake_resistor"),
    ("brake_resistance", "config.brake_resistance"),

    ("fet_therm_enabled", "axis0.motor.fet_thermistor.config.enabled"),
    ("fet_therm_limit", "axis0.motor.fet_thermistor.config.temp_limit_upper"),
    ("motor_therm_enabled", "axis0.motor.motor_thermistor.config.enabled"),
    ("motor_therm_limit", "axis0.motor.motor_thermistor.config.temp_limit_upper"),

    # ===== CAN 链路配置 =====
    ("can_node_id", "axis0.config.can.node_id"),
    ("can_baud_rate", "can.config.baud_rate"),
    ("can_protocol", "can.config.protocol"),
    ("can_enable_r120", "can.config.enable_r120"),
    ("comm_intf_mux", "config.comm_intf_mux"),

    # ===== CAN 周期上报配置 =====
    ("can_heartbeat_rate_ms", "axis0.config.can.heartbeat_rate_ms"),
    ("can_encoder_rate_ms", "axis0.config.can.encoder_rate_ms"),
    ("can_motor_error_rate_ms", "axis0.config.can.motor_error_rate_ms"),
    ("can_encoder_error_rate_ms", "axis0.config.can.encoder_error_rate_ms"),
    ("can_controller_error_rate_ms", "axis0.config.can.controller_error_rate_ms"),
    ("can_iq_rate_ms", "axis0.config.can.iq_rate_ms"),
    ("can_bus_vi_rate_ms", "axis0.config.can.bus_vi_rate_ms"),

    # ===== 回灌/刹车相关 =====
    ("max_regen_current", "config.max_regen_current"),
    ("enable_dc_bus_overvoltage_ramp", "config.enable_dc_bus_overvoltage_ramp"),
    ("dc_bus_overvoltage_ramp_start", "config.dc_bus_overvoltage_ramp_start"),
    ("dc_bus_overvoltage_ramp_end", "config.dc_bus_overvoltage_ramp_end"),

    # ===== 看门狗配置 =====
    ("enable_watchdog", "axis0.config.enable_watchdog"),
    ("watchdog_timeout", "axis0.config.watchdog_timeout"),

    # ===== 控制器保存参数 =====
    ("control_mode", "axis0.controller.config.control_mode"),
    ("input_mode", "axis0.controller.config.input_mode"),
    ("inertia", "axis0.controller.config.inertia"),
    ("pos_gain", "axis0.controller.config.pos_gain"),
    ("vel_gain", "axis0.controller.config.vel_gain"),
    ("vel_integrator_gain", "axis0.controller.config.vel_integrator_gain"),
]

for name, path in params:
    try:
        val = get_attr_path(odrv0, path)
        print(f"{name}: {val}")
    except Exception as e:
        print(f"{name}: ERROR ({e})")
