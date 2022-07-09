from multiprocessing import Process
import numpy as np
from PyDAQmx import *
from ctypes import byref
import time

class UniblitzShutterStatusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        # Start a general handle which always monitors the status of the uniblitz shutter
        self.shutter_status_handle = TaskHandle()

        DAQmxCreateTask("Shutter status", byref(self.shutter_status_handle))

        DAQmxCreateDIChan(self.shutter_status_handle, "Dev1/port0/line1", "", DAQmx_Val_ChanForAllLines)

        DAQmxStartTask(self.shutter_status_handle)

        read = int32()

        shutter_status_data = np.zeros((1), dtype=np.uint8)

        while self.shared.running.value == 1:

            DAQmxReadDigitalU8(self.shutter_status_handle, int(1), 10.0, DAQmx_Val_GroupByChannel, shutter_status_data,
                               int(1), byref(read), None)

            if shutter_status_data[0] & 2 == 2:  # if it is high, the shutter is open
                self.shared.current_uniblitz_status.value = 1
            else:
                self.shared.current_uniblitz_status.value = 0

            time.sleep(0.1)

        ## Stop the shutter status task
        DAQmxStopTask(self.shutter_status_handle)
        DAQmxClearTask(self.shutter_status_handle)