import ftd2xx
from ftd2xx.defines import *
import struct as st
import time
from multiprocessing import Process

# see https://github.com/freespace/pyAPT/blob/master/pyAPT/controller.py
# http://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol_Rev_18.pdf

class LambdaHalfPlateModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.ftdi = None
        devices = ftd2xx.createDeviceInfoList()

        for i in range(devices):
            device = ftd2xx.getDeviceInfoDetail(i)

            # On either of the computers
            if device["serial"] == b"27005044" or device["serial"] == b"27600313":
                self.ftdi = ftd2xx.open(dev=device["index"])


        if self.ftdi == None:
            print("No Motion controller for lambda half plate...")
            return

        self.position_scaling = 1919.64  # see manuel of apt controller

        self.ftdi.setBaudRate(115200)
        self.ftdi.setDataCharacteristics(BITS_8, STOP_BITS_1, PARITY_NONE)
        self.ftdi.setTimeouts(1, 1)
        time.sleep(0.05)

        self.ftdi.purge(PURGE_RX | PURGE_TX)
        time.sleep(0.05)

        self.ftdi.resetDevice()

        self.ftdi.setFlowControl(FLOW_RTS_CTS, 0, 0)
        self.ftdi.setRts()

        # flash the lights
        str = st.pack('<HBBBB', 0x0223, 0x00, 0x00, 0x50, 0x01)

        self.ftdi.write(str)
        time.sleep(0.05)

        # get essential information
        # request the data string
        str = st.pack('<HBBBB', 0x0005, 0x00, 0x00, 0x50, 0x01)
        self.ftdi.write(str)
        time.sleep(0.05)

        # get the data string
        str = self.ftdi.read(90)
        time.sleep(0.05)

        # get info
        sn, model, hwtype, fwver, notes, _, hwver, modstate, numchan = st.unpack("<l8sH4s48s12sHHH", str[6:])

        # request the old target position
        # request the postion
        str = st.pack("<HBBBB", 0x0411, 0x01, 0x00, 0x50, 0x01)
        self.ftdi.write(str)
        time.sleep(0.05)

        # read position
        str = self.ftdi.read(12)
        time.sleep(0.05)
        chan, pos = st.unpack("<Hl", str[6:])
        self.shared.initial_lambda_half_plate_orientation.value = pos / self.position_scaling

        # home the stage
        # move to home position
        # TODO, move all this into the general stage controler module
        str = st.pack("<HBBBB", 0x0443, 0x01, 0x00, 0x50, 0x01)
        self.ftdi.write(str)
        time.sleep(0.1)
        print("Lambda/2 plate stage homing....")
        self.shared.lambda_half_plate_homing_completed.value = 0

        while self.shared.running.value == 1:

            # check for status information
            str = self.ftdi.read(6)

            if len(str) == 6:

                message_id, param1, param2, dest, source = st.unpack("<HBBBB", str)

                if message_id == 0x0464: # stage movement completed?
                    # read some data bytes
                    self.ftdi.read(14)
                    #time.sleep(0.1)

                    self.shared.lambda_half_plate_orientation_change_completed.value = 1

                elif message_id == 0x0466:
                    self.ftdi.read(14)
                    #time.sleep(0.1)
                    self.shared.lambda_half_plate_orientation_change_completed.value = 1
                    print("Lambda/2 plate stage movement stopped.")

                elif message_id == 0x0412:
                    str = self.ftdi.read(6)
                    #time.sleep(0.1)

                    chan, pos = st.unpack("<Hl", str)
                    self.shared.current_lambda_half_plate_orientation.value = pos / self.position_scaling

                elif message_id == 0x0444:
                    self.shared.lambda_half_plate_homing_completed.value = 1
                    print("Lambda/2 plate stage homing completed.")

                else:
                    print("####### Unknown lambda/2 plate stage message......... ", hex(message_id))

            if self.shared.target_lambda_half_plate_orientation_changed.value == 1 and self.shared.lambda_half_plate_homing_completed.value == 1:

                self.shared.target_lambda_half_plate_orientation_changed.value = 0

                str = st.pack("<HBBBBHl", 0x0453, 0x06, 0x00, 0x50 | 0x80, 0x01, 1, int(self.shared.target_lambda_half_plate_orientation.value * self.position_scaling))
                self.ftdi.write(str)
                time.sleep(0.1)

            else:

                str = st.pack("<HBBBB", 0x0411, 0x01, 0x00, 0x50, 0x01) # request the postion
                self.ftdi.write(str)
                time.sleep(0.1)

            time.sleep(0.05)

        self.ftdi.resetDevice()
        self.ftdi.close()
