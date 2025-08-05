import sys, struct, time, threading, serial
from serial.tools import list_ports
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

WIN = 200          # 滚动窗口长度
BAUD = 115200

def list_serial_ports():
    return [p.device for p in list_ports.comports()]

class Reader(threading.Thread):
    """后台线程：按 34 字节帧读取 8 个 float"""
    def __init__(self, ser, gui):
        super().__init__(daemon=True)
        self.ser, self.gui = ser, gui
        self.run_flag = True
    def stop(self): self.run_flag = False
    def run(self):
        while self.run_flag:
            if self.ser.read(1) != b'\xA5': continue
            if self.ser.read(1) != b'\x5A': continue
            payload = self.ser.read(32)
            if len(payload) != 32: continue
            vals = struct.unpack('<8f', payload)
            t = time.time()
            self.gui.push_data(t, *vals)

class Main(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("双电机实时显示 (简版)")
        self.resize(1000, 600)

        # ---- 数据缓存 ----
        self.t_buf = [0]*WIN
        self.Lθ, self.Lω, self.Lcmd, self.Lτ = ([0]*WIN for _ in range(4))
        self.Rθ, self.Rω, self.Rcmd, self.Rτ = ([0]*WIN for _ in range(4))

        # ---- UI ----
        vbox = QtWidgets.QVBoxLayout(self)
        hbox = QtWidgets.QHBoxLayout(); vbox.addLayout(hbox)

        self.cmb = QtWidgets.QComboBox(); self.cmb.addItems(list_serial_ports())
        self.btn = QtWidgets.QPushButton("连接")
        self.lbl = QtWidgets.QLabel("未连接")
        hbox.addWidget(QtWidgets.QLabel("端口:")); hbox.addWidget(self.cmb)
        hbox.addWidget(self.btn); hbox.addWidget(self.lbl)

        self.btn.clicked.connect(self.toggle_conn)

        grid = QtWidgets.QGridLayout(); vbox.addLayout(grid)
        font = self.font(); font.setPointSize(12)
        def lab(txt): l = QtWidgets.QLabel(txt); l.setFont(font); return l
        self.l_L = lab("Lθ=0  ω=0  τ=0 / 0")
        self.l_R = lab("Rθ=0  ω=0  τ=0 / 0")
        grid.addWidget(self.l_L,0,0); grid.addWidget(self.l_R,0,1)

        # ---- 绘图 ----
        self.plt_L = pg.PlotWidget(title="m1电机")
        self.plt_R = pg.PlotWidget(title="m2电机")
        vbox.addWidget(self.plt_L); vbox.addWidget(self.plt_R)

        penG, penB, penR = pg.mkPen('g'), pg.mkPen('b'), pg.mkPen('r')
        self.cur_Lθ   = self.plt_L.plot(pen=penG, name="θ")
        self.cur_Lcmd = self.plt_L.plot(pen=penB, name="τ_cmd")
        self.cur_Lτ   = self.plt_L.plot(pen=penR, name="τ")

        self.cur_Rθ   = self.plt_R.plot(pen=penG)
        self.cur_Rcmd = self.plt_R.plot(pen=penB)
        self.cur_Rτ   = self.plt_R.plot(pen=penR)

        # ---- 刷新计时器 ----
        self.timer = QtCore.QTimer(self); self.timer.timeout.connect(self.refresh)
        self.timer.start(40)   # 25 Hz GUI 刷新

        self.ser = None; self.reader = None

    # ------------------- 串口连接 / 断开 -------------------
    def toggle_conn(self):
        if self.ser:           # 断开
            self.reader.stop(); self.ser.close()
            self.ser = None; self.lbl.setText("断开")
            self.btn.setText("连接"); return

        port = self.cmb.currentText()
        if not port: return
        try:
            self.ser = serial.Serial(port, BAUD, timeout=0.02)
            self.reader = Reader(self.ser, self); self.reader.start()
            self.lbl.setText("已连接"); self.btn.setText("断开")
        except serial.SerialException as e:
            self.lbl.setText(f"失败:{e}")

    # ------------------- 数据推进 -------------------
    def push_data(self, t, La, Ls, Lc, Lt, Ra, Rs, Rc, Rt):
        self.t_buf = self.t_buf[1:]+[t]
        for buf,val in zip(
            (self.Lθ,self.Lω,self.Lcmd,self.Lτ,
             self.Rθ,self.Rω,self.Rcmd,self.Rτ),
            (La, Ls, Lc, Lt, Ra, Rs, Rc, Rt)):
            buf.pop(0); buf.append(val)

    # ---------------- GUI 刷新 ----------------
    def refresh(self):
        if self.t_buf[0]==0: return
        t0 = self.t_buf[0]
        x  = [t-t0 for t in self.t_buf]

        self.cur_Lθ.setData(x, self.Lθ)
        self.cur_Lcmd.setData(x, self.Lcmd)
        self.cur_Lτ.setData(x, self.Lτ)

        self.cur_Rθ.setData(x, self.Rθ)
        self.cur_Rcmd.setData(x, self.Rcmd)
        self.cur_Rτ.setData(x, self.Rτ)

        self.l_L.setText(f"Lθ={self.Lθ[-1]:.2f}  ω={self.Lω[-1]:.2f}  "
                         f"τ={self.Lτ[-1]:.2f}/{self.Lcmd[-1]:.2f}")
        self.l_R.setText(f"Rθ={self.Rθ[-1]:.2f}  ω={self.Rω[-1]:.2f}  "
                         f"τ={self.Rτ[-1]:.2f}/{self.Rcmd[-1]:.2f}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pg.setConfigOptions(antialias=True)
    w = Main(); w.show()
    sys.exit(app.exec_())
