#include <Arduino.h>
#include <FlexCAN_T4.h>
#include "Sig_Motor_Control.h"

FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_16> Can3;

Motor_Control_Tmotor sig_m1(0x001, 3);
Motor_Control_Tmotor sig_m2(0x002, 3);

float M1_torque_command = 0.9f;
float M2_torque_command = 0.9f;

CAN_message_t msgR;
float initial_pos_1 = 0; 
float initial_pos_2 = 0;
float tau_t_1 = 0; 
float tau_t_2 = 0;

union FloatBytes { float value; uint8_t bytes[4]; };

void sendAllMotorsFrame(uint8_t *buf, uint8_t &len)
{
  int idx = 0;
  buf[idx++] = 0xA5;
  buf[idx++] = 0x5A;

  FloatBytes fb;
  fb.value = sig_m1.pos;        memcpy(buf+idx, fb.bytes, 4); idx += 4;
  fb.value = sig_m1.spe;        memcpy(buf+idx, fb.bytes, 4); idx += 4;
  fb.value = M1_torque_command; memcpy(buf+idx, fb.bytes, 4); idx += 4;
  fb.value = sig_m1.torque;     memcpy(buf+idx, fb.bytes, 4); idx += 4;

  fb.value = sig_m2.pos;        memcpy(buf+idx, fb.bytes, 4); idx += 4;
  fb.value = sig_m2.spe;        memcpy(buf+idx, fb.bytes, 4); idx += 4;
  fb.value = M2_torque_command; memcpy(buf+idx, fb.bytes, 4); idx += 4;
  fb.value = sig_m2.torque;     memcpy(buf+idx, fb.bytes, 4); idx += 4;

  len = idx;   // =34
}

void sendAllMotorsBLE()
{
  uint8_t buffer[34]; uint8_t len;
  sendAllMotorsFrame(buffer, len);

  /* ---- 发到蓝牙 (Serial5) ---- */
  Serial5.write(buffer, len);

  /* ---- 同时发到 USB (Serial) 供 GUI 调试 ---- */
  Serial.write(buffer, len);
}

void printDebug()
{
  Serial.printf("[DBG] p1=%.3f w1=%.3f τ1=%.2f | p2=%.3f w2=%.3f τ2=%.2f\r\n",
                sig_m1.pos, sig_m1.spe, sig_m1.torque,
                sig_m2.pos, sig_m2.spe, sig_m2.torque);
}

/* ---------- CAN Rx ---------- */
const uint16_t ID_M1_POSVEL = (0x001<<5) | 0x009;  // 0x049
const uint16_t ID_M1_TORQUE = (0x001<<5) | 0x01C;  // 0x05C
const uint16_t ID_M2_POSVEL = (0x002<<5) | 0x009;  // 0x029
const uint16_t ID_M2_TORQUE = (0x002<<5) | 0x01C;  // 0x03C
const uint16_t ID_M1_IQ = (0x001<<5) | 0x014;  // 0x064
const uint16_t ID_M2_IQ = (0x002<<5) | 0x014;  // 0x034


#define KT_1  0.43f   
#define KT_2  0.43f   

void receive_torque_ctl_feedback()
{
    while (Can3.read(msgR)) {
        switch (msgR.id) {
            case ID_M1_POSVEL:
                sig_m1.unpack_pos_vel(msgR, initial_pos_1);
                break;
            case ID_M1_IQ: {
                float iq = *(float *)&msgR.buf[4];      
                sig_m1.torque = iq * KT_1;              
                break;
            }

            case ID_M2_POSVEL:
                sig_m2.unpack_pos_vel(msgR, initial_pos_2);
                break;
            case ID_M2_IQ: {
                float iq = *(float *)&msgR.buf[4];
                sig_m2.torque = iq * KT_2;
                break;
            }
        }
    }
}



void setup()
{
  Serial.begin(115200);// USB -> /dev/ttyACM0
  Serial5.begin(115200);   // 若你真有蓝牙模块仍可保留
  delay(1000);

  /* ---- CAN ---- */
  Can3.begin();
  Can3.setBaudRate(1000000);

  /* ---- 电机 ---- */
  sig_m1.sig_torque_ctl_mode_start(); delay(200);
  sig_m2.sig_torque_ctl_mode_start(); delay(200);
  sig_m1.sig_motor_start();
  delay(500);    

  sig_m2.sig_motor_start();
  delay(500);
}

void loop()
{
  /* 控制命令 */
  sig_m1.sig_torque_cmd(M1_torque_command);
  sig_m2.sig_torque_cmd(M2_torque_command);

  /* 读取反馈 */
  receive_torque_ctl_feedback();
  receive_torque_ctl_feedback();
  receive_torque_ctl_feedback();
  receive_torque_ctl_feedback();
  receive_torque_ctl_feedback();
  receive_torque_ctl_feedback();



  /* 打印到串口，便于在 Arduino Serial Monitor 里确认 */
  printDebug();

  /* 发送 GUI 帧 */
  sendAllMotorsBLE();

  delay(20);   // 50 Hz
}
