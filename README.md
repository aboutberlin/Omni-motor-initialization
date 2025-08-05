Here's a simple draft for your GitHub README in English:

---

# Omni Motor Test with Teensy and GUI

This repository contains a simple example code and GUI for testing an **Omni motor** using a **Teensy** microcontroller.

![GUI Example](image.png)

---

## 📦 Files

* **`test_two_motor.zip`** — Example code for Teensy to test Omni motors.
* **`image.png`** — GUI demonstration image.

---

## ⚙️ Setup Instructions

Every time you set up an Omni motor, you will need to **initialize** the Teensy and configure your motor.
For a detailed initialization tutorial, please refer to:
[**Full Guide**](https://cyberbeast.feishu.cn/docx/N3SMd4QyRobzHkx3wP3cT1qXnpf)

---

### 1. Connect to ODrive

Open **Odrivetool** and connect your motor.

---

### 2. Set Motor ID and Baud Rate

```python
odrv0.axis0.config.can.node_id = 3
odrv0.can.config.baud_rate = 1000000  # Change from default 500000 to 1000000
odrv0.save_configuration()
```

---

### 3. Calibrate the Motor

```python
odrv0.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION
dump_errors(odrv0)

odrv0.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
dump_errors(odrv0)

odrv0.axis0.motor.config.pre_calibrated = 1
odrv0.axis0.encoder.config.pre_calibrated = 1
odrv0.save_configuration()
```

---

### 4. Open Corresponding Port

```python
odrv0.axis0.config.can.encoder_rate_ms = 10
odrv0.axis0.config.can.iq_rate_ms = 10
odrv0.save_configuration()
```

---

### 5. Check Torque Constant

```python
odrv0.axis0.motor.config.torque_constant
```

---

✅ **Done!** You have completed all setup steps.

---

Do you want me to also make a **cleaner, more professional GitHub-style version** with badges and section formatting so it looks polished? That would make it look more official.
