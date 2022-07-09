from multiprocessing import Process
import serial
import time
import socket

class MaiTaiModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        ser = serial.Serial(baudrate=self.shared.baudrate_laser, port=self.shared.com_port_laser, bytesize=8, stopbits=1, rtscts=0, timeout=1, xonxoff=1, parity='N')  # open serial port

        queries = [#["CONTrol:PHAse?", "Phase"],
                   #["CONTrol:MLENable?", "Modelock enable"],
                   #["MODE?", "Mode"],
                   [b"PLASer:ERRCode?", b"Errcode"],
                   [b"READ:PLASer:POWer?", b"PPower"],
                   [b"READ:PLASer:PCURrent?", b"PCur"],
                   [b"READ:PLASer:SHGS?", b"SHGS"],
                   [b"CONTrol:MLENable?", b"MLENable"],
                   [b"CONTrol:PHAse?", b"PHAse"],
                   [b"READ:PLASer:DIODe1:CURRent?", b"Diode1_Cur"],
                   [b"READ:PLASer:DIODe2:CURRent?", b"Diode2_Cur"],
                   [b"READ:PLASer:DIODe1:TEMPerature?", b"Diode1_Temp"],
                   [b"READ:PLASer:DIODe2:TEMPerature?", b"Diode2_Temp"],
                   [b"READ:TEMP:BODY?", b"Temp_Body"],
                   [b"read:temp:tow?", b"Temp_Tower"],
                   [b"READ:HUMIDITY?", b"Humidity"],
                   [b"READ:PULSING?", b"Pulsing Diode"],
                   [b"tim:watc?", b"Watchdog timer"],
                   [b"tim:stan?", b"Standby timer"],
                   [b"READ:HEAD:HOUR?", b"Laser head hours"]]

        ser.write(b"TIMEr:WATChdog 600\r\n")  # watchdog timer, if laser doesnt get signal for 600seconds, (programm crashed or shut down, shuts off laser, disable with = 0!

        while self.shared.running.value == 1:

            # query the most important information

            try:
                ser.write(b"READ:PCTWarmedup?\r\n")
                self.shared.current_mai_tai_info_warmup.value = float(ser.readline()[:-2])

                ser.write(b"READ:WAVelength?\r\n")
                self.shared.current_mai_tai_info_wavelength.value = int(ser.readline()[:-3])

                ser.write(b"READ:POWer?\r\n")
                self.shared.current_mai_tai_info_power.value = float(ser.readline()[:-2])

                ser.write(b"SHUTter?\r\n")
                self.shared.current_mai_tai_info_shutter_open.value = int(ser.readline()[:-1])

                ser.write(b"CONTrol:DSMPOS?\r\n")
                self.shared.prechirp_motor_current.value = float(ser.readline()[:-1].decode().split(" percent")[0])

                # status bits
                ser.write(b"*STB?\r\n")
                status = int(ser.readline()[:-1])
                if status & 1 == 1:
                    self.shared.current_mai_tai_info_laser_emmision.value = 1
                else:
                    self.shared.current_mai_tai_info_laser_emmision.value = 0

                if status & 2 == 2:
                    self.shared.current_mai_tai_info_modelocking.value = 1
                else:
                    self.shared.current_mai_tai_info_modelocking.value = 0

                ####
                # query more detailed information
                current_mai_tai_info = b""

                for query in queries:

                    ser.write(query[0] + b'\r\n')

                    current_mai_tai_info += query[1] + b": " + ser.readline()[:-1] + b"; "

                ser.write(b"SYSTem:ERR?\r\n")
                while True:
                    response = ser.readline()[:-1]

                    if response == b"":
                        break

                    current_mai_tai_info += response + b"; "

                self.shared.current_mai_tai_info[:len(current_mai_tai_info)] = current_mai_tai_info
                self.shared.current_mai_tai_info_l.value = len(current_mai_tai_info)

                ####################### Set variables
                if self.shared.pushButton_MaiTai_Shutter_clicked.value == 1:
                    if self.shared.current_mai_tai_info_shutter_open.value == 1:
                        ser.write(b"SHUTter 0\r\n")  # if currently open, close it
                    else:
                        ser.write(b"SHUTter 1\r\n")  # if currently closed, close it

                    self.shared.pushButton_MaiTai_Shutter_clicked.value = 0

                if self.shared.pushButton_MaiTai_ON_clicked.value == 1:
                    self.shared.pushButton_MaiTai_ON_clicked.value = 0

                    ser.write(b"ON\r\n")

                if self.shared.pushButton_MaiTai_OFF_clicked.value == 1:
                    ser.write(b"OFF\r\n")
                    self.shared.pushButton_MaiTai_OFF_clicked.value = 0

                if self.shared.target_mai_tai_wavelength_changed.value == 1:
                    ser.write(b"WAVelength %0d"%self.shared.target_mai_tai_wavelength.value)
                    self.shared.target_mai_tai_wavelength_changed.value = 0

                if self.shared.prechirp_motor_changed.value == 1:
                    ser.write(b"CONTrol:MTRMOV %f"%self.shared.prechirp_motor_set.value)
                    self.shared.prechirp_motor_changed.value = 0

            except Exception as e:
                pass  # while the laser changes wavlength no querries possible

            time.sleep(0.05)

        ser.close()
