from multiprocessing import Process
import numpy as np
from PyDAQmx import *
from ctypes import *
import socket
from scipy.ndimage import gaussian_filter1d
from numba import jit
import time
from tifffile import imsave

@jit(nopython=True)
def do_binning(img_channel0, img_channel1, pmt_data_channel0, pmt_data_channel1, x, y, bin_size):

    for i in range(len(x)):
        for j in range(bin_size):
            img_channel0[x[i], y[i]] += pmt_data_channel0[i * bin_size + j] / bin_size
            img_channel1[x[i], y[i]] += pmt_data_channel1[i * bin_size + j] / bin_size

class ScanningModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

        print(socket.gethostname())
        if socket.gethostname() == "DESKTOP-D5NK0MQ":
            self.dev_name_scanning_control = "dev1"
            self.dev_name_pmt_control = "dev3"
        elif socket.gethostname() == "DESKTOP-9BQKQP5":
            self.dev_name_scanning_control = "dev1"
            self.dev_name_pmt_control = f"dev2"
        else:
            return

    def start_scanning(self):

        self.x_pixels = self.shared.galvo_scanning_resolutionx.value
        self.y_pixels = self.shared.galvo_scanning_resolutiony.value
        self.turnaround_pixels = self.shared.galvo_scanning_turnaround_pixels.value

        self.pixel_to_galvo_factor = self.shared.galvo_scanning_pixel_galvo_factor.value

        # the input rate from the pmts, is higher!
        self.output_rate = self.shared.galvo_scanning_AOrate_raster_scanning.value
        self.input_rate = self.shared.galvo_scanning_AIrate.value
        self.bin_size = round(self.shared.galvo_scanning_AIrate.value / self.shared.galvo_scanning_AOrate_raster_scanning.value)

        # Create the waveform
        x_line = np.arange(0, self.x_pixels + self.turnaround_pixels*2, 1.0)

        self.x = []
        self.y = []
        for i in range(self.y_pixels):
            if i % 2 == 0:
                self.x.extend(x_line)
            else:
                self.x.extend(x_line[::-1])
            self.y.extend(np.ones(self.x_pixels + self.turnaround_pixels*2, dtype=np.float) * i)

        # Make all the dynamics slower, to help our poor galvos

        # Concatenate to also take care of the jumps between frames
        dx = np.diff(np.r_[self.x, self.x, self.x])
        dy = np.diff(np.r_[self.y, self.y, self.y])

        # low-pass filter the velocities
        dx = gaussian_filter1d(dx, sigma=5)
        dy = gaussian_filter1d(dy, sigma=5)

        # Undo the concatenation
        self.x = np.cumsum(dx)[len(self.x):len(self.x) * 2]
        self.y = np.cumsum(dy)[len(self.x):len(self.x) * 2]

        # The voltage of the galvos is simply a facotor times the mean-centered pixel location
        self.Vx = (self.x - np.mean(self.x)) * self.pixel_to_galvo_factor
        self.Vy = (self.y - np.mean(self.y)) * self.pixel_to_galvo_factor

        if np.min(self.Vx) < -4.9 or np.min(self.Vz) < -4.9 or np.min(self.Vx) < -4.9 or  np.min(self.Vz) < -4.9:
            print("Voltage range too large")
            self.shared.currently_scanning.value = 0

        # Round the pixel locations to be able to later use it as indices to place in the image
        self.x = np.round(self.x).astype(np.uint16)
        self.y = np.round(self.y).astype(np.uint16)

        # Pmt aquires images bin_size faster than the scan, and there are two channels
        self.pmt_buffer_data = np.zeros(2 * len(self.x) * self.bin_size, dtype=np.float64)

        # Make sure the buffers for the LP filtering are propertly initialized at the first image
        self.image_green_LP = None
        self.image_red_LP = None

        # Before starting, initialize the numba function once (which takes long)
        self.get_images(self.pmt_buffer_data[:len(self.x) * self.bin_size],
                        self.pmt_buffer_data[len(self.x) * self.bin_size:])

        # Turn on the PMTs
        self.set_pmt_gains(self.shared.scanning_configuration_pmt_gain_green.value,
                           self.shared.scanning_configuration_pmt_gain_red.value)

        # Galvo output
        DAQmxCreateTask("AO", byref(self.galvo_output_handle))
        DAQmxCreateAOVoltageChan(self.galvo_output_handle, f"{self.dev_name_scanning_control}/ao0:1", "AO", -5.0, 5.0, DAQmx_Val_Volts, "")
        DAQmxCfgSampClkTiming(self.galvo_output_handle, "", float64(self.output_rate), DAQmx_Val_Rising,
                              DAQmx_Val_ContSamps, int(len(self.x)))
        DAQmxWriteAnalogF64(self.galvo_output_handle, int(len(self.x)), 0, 10.0, DAQmx_Val_GroupByChannel, np.r_[self.Vx, self.Vy],
                            byref(self.written), None)

        # Start Pmt input when the scanner starts
        DAQmxCreateTask("AI", byref(self.pmt_input_handle))
        DAQmxCreateAIVoltageChan(self.pmt_input_handle, f"{self.dev_name_scanning_control}/ai0:1", "AI", DAQmx_Val_Cfg_Default, float64(-self.shared.galvo_scanning_expected_pmt_signal_range.value),
                                 float64(self.shared.galvo_scanning_expected_pmt_signal_range.value), DAQmx_Val_Volts, None)

        DAQmxCfgSampClkTiming(self.pmt_input_handle, "", float64(self.input_rate), DAQmx_Val_Rising, DAQmx_Val_ContSamps,
                              int(len(self.x)*self.bin_size))
        DAQmxSetAIDataXferMech(self.pmt_input_handle, f"{self.dev_name_scanning_control}/ai0:1", DAQmx_Val_DMA)  # imporoves buffering problems
        DAQmxCfgDigEdgeStartTrig(self.pmt_input_handle, "ao/StartTrigger", DAQmx_Val_Rising)

        # Open the shutter when the scanner starts
        data = np.ones(1).astype(np.uint8)
        DAQmxWriteDigitalU8(self.shutter_handle, 1, 0, 10, DAQmx_Val_GroupByChannel, data, byref(self.written), None)
        DAQmxCfgDigEdgeStartTrig(self.shutter_handle, "ao/StartTrigger", DAQmx_Val_Rising)

        # Start everything
        DAQmxStartTask(self.galvo_output_handle)

        self.shared.currently_scanning.value = 1

    def set_pmt_gains(self, pmt_gain_green, pmt_gain_red):

        # Only turn on PMT if it was selected to be on during scanning.
        if not self.shared.green_pmt_turn_on_while_scanning.value:
            pmt_gain_green = 0
        if not self.shared.red_pmt_turn_on_while_scanning.value:
            pmt_gain_red = 0

        data = np.array([pmt_gain_green], dtype=np.float64)
        DAQmxWriteAnalogF64(self.pmt_gain_green_control_handle, 1, 1, 10.0, DAQmx_Val_GroupByChannel,
                            data,
                            byref(self.written), None)

        data = np.array([pmt_gain_red], dtype=np.float64)
        DAQmxWriteAnalogF64(self.pmt_gain_red_control_handle, 1, 1, 10.0, DAQmx_Val_GroupByChannel,
                            data,
                            byref(self.written), None)

    def stop_scanning(self):

        if self.shared.currently_scanning.value == 0:
            return

        # Close the shutter
        data = np.zeros(1, dtype = np.uint8)
        DAQmxWriteDigitalU8(self.shutter_handle, 1, 1, 10, DAQmx_Val_GroupByChannel, data, byref(self.written), None)

        # Stop the pmt input motion and galvos
        DAQmxStopTask(self.pmt_input_handle)
        DAQmxStopTask(self.galvo_output_handle)

        DAQmxClearTask(self.pmt_input_handle)
        DAQmxClearTask(self.galvo_output_handle)

        # Zero the galvos
        data = np.zeros(2, dtype=np.float64)
        DAQmxCreateTask("AO", byref(self.galvo_output_handle))
        DAQmxCreateAOVoltageChan(self.galvo_output_handle, f"{self.dev_name_scanning_control}/ao0:1", "AO", -5.0, 5.0, DAQmx_Val_Volts, "")
        DAQmxWriteAnalogF64(self.galvo_output_handle, 1, 1, 10.0, DAQmx_Val_GroupByChannel, data, byref(self.written), None)

        DAQmxStopTask(self.galvo_output_handle)
        DAQmxClearTask(self.galvo_output_handle)

        # Turn off the pmts
        self.set_pmt_gains(0, 0)

        self.shared.currently_scanning.value = 0

    def get_images(self, raw_green_data, raw_red_data):

        # Get the image from the PMT signals
        image_green = np.zeros((self.x_pixels + self.turnaround_pixels * 2, self.y_pixels), dtype=np.float64)
        image_red = np.zeros((self.x_pixels + self.turnaround_pixels * 2, self.y_pixels), dtype=np.float64)

        raw_green_data = np.roll(raw_green_data, self.shared.pmt_data_rolling_shift.value)
        raw_red_data = np.roll(raw_red_data, self.shared.pmt_data_rolling_shift.value)

        do_binning(image_green, image_red, raw_green_data, raw_red_data,
                   self.x, self.y, self.bin_size)

        # Slice away the turnaround
        image_green = image_green[self.turnaround_pixels:-self.turnaround_pixels]
        image_red = image_red[self.turnaround_pixels:-self.turnaround_pixels]

        image_green = (-self.shared.scale_green_channel.value * image_green +
                       self.shared.min_green_channel.value).clip(0, 65535).astype(np.uint16)
        image_red = (-self.shared.scale_red_channel.value * image_red +
                     self.shared.min_red_channel.value).clip(0, 65535).astype(np.uint16)

        return image_green, image_red

    def run(self):

        self.shared_image_green = np.ctypeslib.as_array(self.shared.image_green)
        self.shared_image_red = np.ctypeslib.as_array(self.shared.image_red)

        self.read = int32(0)
        self.written = int32()

        self.shutter_handle = TaskHandle()
        self.pmt_gain_green_control_handle = TaskHandle()
        self.pmt_gain_red_control_handle = TaskHandle()
        self.galvo_output_handle = TaskHandle()
        self.pmt_input_handle = TaskHandle()

        # Close the uniblitz shutter when we start
        data = np.zeros(1, dtype=np.uint8)



        DAQmxCreateTask("Shutter", byref(self.shutter_handle))
        DAQmxCreateDOChan(self.shutter_handle, f"{self.dev_name_scanning_control}/port0/line0", "", DAQmx_Val_ChanForAllLines)
        DAQmxWriteDigitalU8(self.shutter_handle, 1, 1, 10, DAQmx_Val_GroupByChannel, data, byref(self.written), None)


        DAQmxCreateTask("Pmt gain green", byref(self.pmt_gain_green_control_handle))
        DAQmxCreateTask("Pmt gain red", byref(self.pmt_gain_red_control_handle))

        DAQmxCreateAOVoltageChan(self.pmt_gain_green_control_handle, f"{self.dev_name_pmt_control}/ao0", "AO", 0, 5.0, DAQmx_Val_Volts, "")
        DAQmxCreateAOVoltageChan(self.pmt_gain_red_control_handle, f"{self.dev_name_pmt_control}/ao1", "AO", 0, 5.0, DAQmx_Val_Volts, "")

        # Initially, turn both pmts off
        self.set_pmt_gains(0, 0)

        while self.shared.running.value == 1:

            if self.shared.start_scanning_requested.value == 1:
                self.shared.start_scanning_requested.value = 0

                # Start continuous scanning
                self.start_scanning()

                while True:

                    # Adjust the pmt gain if desired, also during the scanning
                    if self.shared.scanning_configuration_pmt_gain_green_update_requested.value == 1:
                        self.shared.scanning_configuration_pmt_gain_green_update_requested.value = 0
                        self.set_pmt_gains(self.shared.scanning_configuration_pmt_gain_green.value,
                                           self.shared.scanning_configuration_pmt_gain_red.value)

                    if self.shared.scanning_configuration_pmt_gain_red_update_requested.value == 1:
                        self.shared.scanning_configuration_pmt_gain_red_update_requested.value = 0
                        self.set_pmt_gains(self.shared.scanning_configuration_pmt_gain_green.value,
                                           self.shared.scanning_configuration_pmt_gain_red.value)

                    if self.shared.stop_scanning_requested.value == 1:
                        self.shared.stop_scanning_requested.value = 0
                        break

                    if self.shared.running.value == 0:
                        break

                    # Read one full galvo image for both channals
                    DAQmxReadAnalogF64(self.pmt_input_handle, int(len(self.x)*self.bin_size), 30.0, DAQmx_Val_GroupByChannel,
                                       self.pmt_buffer_data, int(2 * len(self.x)*self.bin_size), byref(self.read), None)

                    # Do the binning
                    image_green, image_red = self.get_images(self.pmt_buffer_data[:len(self.x) * self.bin_size],
                                                             self.pmt_buffer_data[:len(self.x) * self.bin_size])

                    # Low-pass filter the images
                    if self.image_green_LP is None or \
                            self.shared.scanning_configuration_display_lowpass_filter_constant.value == 0:
                        self.image_green_LP = image_green
                        self.image_red_LP = image_red
                    else:
                        alpha = 0.1 / (self.shared.scanning_configuration_display_lowpass_filter_constant.value + 0.1)
                        self.image_green_LP = (1 - alpha) * self.image_green_LP + alpha * image_green
                        self.image_red_LP = (1 - alpha) * self.image_red_LP + alpha * image_red

                    # Send the LP images out for display
                    self.shared_image_green[:self.x_pixels * self.y_pixels] = self.image_green_LP.flatten()
                    self.shared_image_red[:self.x_pixels * self.y_pixels] = self.image_red_LP.flatten()

                    self.shared.image_green_LP_min.value = np.min(self.image_green_LP)
                    self.shared.image_green_LP_max.value = np.max(self.image_green_LP)
                    self.shared.image_green_LP_mean.value = np.mean(self.image_green_LP)

                    self.shared.image_red_LP_min.value = np.min(self.image_red_LP)
                    self.shared.image_red_LP_max.value = np.max(self.image_red_LP)
                    self.shared.image_red_LP_mean.value = np.mean(self.image_red_LP)

                    # Shell we also save the imaging data?
                    if self.shared.experimemt_flow_control_start_acquire_imaging_data_requested.value == 1:
                        self.shared.experimemt_flow_control_start_acquire_imaging_data_requested.value = 0

                        data_per_trial = dict({"timestamps": [], "green channel": [], "red channel": []})
                        self.shared.experiment_flow_control_currently_acquire_imaging_data.value = 1

                    if self.shared.experiment_flow_control_currently_acquire_imaging_data.value == 1:

                        if self.shared.experiment_configuration_store_green_channel.value == 1 or \
                                self.shared.experiment_configuration_store_red_channel.value == 1:
                            data_per_trial["timestamps"].append(time.time())

                        if self.shared.experiment_configuration_store_green_channel.value == 1:
                            data_per_trial["green channel"].append(np.flipud(image_green.T))

                        if self.shared.experiment_configuration_store_red_channel.value == 1:
                            data_per_trial["red channel"].append(np.flipud(image_red.T))

                # Stop the scanning
                self.stop_scanning()

            if self.shared.experiment_flow_control_store_imaging_data_requested.value == 1:
                self.shared.experiment_flow_control_store_imaging_data_requested.value = 0

                self.shared.experiment_flow_control_currently_storing_imaging_data.value = 1

                root_path = bytearray(self.shared.experiment_flow_control_root_path[:self.shared.experiment_flow_control_root_path_l.value]).decode()

                if self.shared.experiment_configuration_store_green_channel.value == 1 or \
                        self.shared.experiment_configuration_store_red_channel.value == 1:

                    # Save the timestamps of the imaging
                    np.savetxt(root_path / "timestamps.txt", data_per_trial["timestamps"])

                # Save the tiff stacks
                if self.shared.experiment_configuration_store_green_channel.value == 1:
                    images_green = np.array(data_per_trial["green channel"], dtype=np.uint16)
                    imsave(root_path / "green_channel.tif", images_green)

                if self.shared.experiment_configuration_store_red_channel.value == 1:
                    images_red = np.array(data_per_trial["red channel"], dtype=np.uint16)
                    imsave(root_path / "red_channel.tif", images_red)

                ## Empty the buffers
                data_per_trial = dict({"timestamps": [], "green channel": [], "red channel": []})

                self.shared.experiment_flow_control_currently_storing_imaging_data.value = 0
                self.shared.experiment_flow_control_store_imaging_data_completed.value = 1

            time.sleep(0.01)
