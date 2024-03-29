from multiprocessing import Value, sharedctypes
import ctypes

from modules.scanning_module import ScanningModule
#from modules.maitai_module import MaiTaiModule
#from modules.lambda_half_plate_module import LambdaHalfPlateModule
from modules.uniblitz_shutter_status_module import UniblitzShutterStatusModule
from modules.experiment_flow_control_module import ExperimentFlowControlModule
import socket

class Shared():
    def __init__(self):

        if socket.gethostname() == "DESKTOP-D5NK0MQ":
            self.dev_shutter_control = "dev1"
            self.dev_name_scanning_control = "dev1"
            self.dev_name_pmt_control = "dev3"
            self.com_port_laser = "COM3"
            self.baudrate_laser = 9600
            self.lambda_half_plate_serial = b"27600313"
        elif socket.gethostname() == "DESKTOP-9BQKQP5":
            self.dev_shutter_control = "dev1"
            self.dev_name_scanning_control = "dev1"
            self.dev_name_pmt_control = f"dev2"
            self.com_port_laser = "COM5"
            self.baudrate_laser = 115200
            self.lambda_half_plate_serial = b"27005044"
        elif socket.gethostname() == "DESKTOP-KATJA":
            self.dev_shutter_control = "dev1"
            self.dev_name_scanning_control = "dev1"
            self.dev_name_pmt_control = f"dev1"
            self.com_port_laser = "COM3"
            self.baudrate_laser = 9600
            self.lambda_half_plate_serial = b"27005044"
        else:
            return

        self.image_green_LP = sharedctypes.RawArray(ctypes.c_uint16, 2048 * 2048)
        self.image_red_LP = sharedctypes.RawArray(ctypes.c_uint16, 2048 * 2048)

        # Gui control
        self.raster_scanning_start_requested = Value('b', 0)
        self.raster_scanning_stop_requested = Value('b', 0)

        # MAI TAI Information
        self.current_mai_tai_info_modelocking = Value('b', 0)
        self.current_mai_tai_info_laser_emmision = Value('b', 0)
        self.current_mai_tai_info_wavelength = Value('i', 0)
        self.current_mai_tai_info_warmup = Value('d', 0)
        self.current_mai_tai_info_power = Value('d', 0)
        self.current_mai_tai_info_shutter_open = Value('b', 0)
        self.current_mai_tai_info = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.current_mai_tai_info_l = Value('i', 0)
        self.pushButton_MaiTai_Shutter_clicked = Value('b', 0)
        self.pushButton_MaiTai_ON_clicked = Value("b", 0)
        self.pushButton_MaiTai_OFF_clicked = Value('b', 0)

        self.target_mai_tai_wavelength = Value('i', 0)
        self.target_mai_tai_wavelength_changed = Value('b', 0)

        self.update_laser_power_calibration_file_requested = Value('b', 0)
        self.prospective_power_at_specimen = Value('d', -1)

        # lamda half plate
        self.initial_lambda_half_plate_orientation = Value('d', 0)
        self.target_lambda_half_plate_orientation = Value('d', 0)
        self.target_lambda_half_plate_orientation_changed = Value("b", 0)
        self.current_lambda_half_plate_orientation = Value('d', 0)
        self.lambda_half_plate_orientation_change_completed = Value("b", 0)
        self.laser_power_self_calibration_currently_running = Value("b", 0)
        self.lambda_half_plate_homing_completed = Value('b', 0)

        self.prechirp_motor_set = Value('d', 70)
        self.prechirp_motor_current = Value('d', 70)
        self.prechirp_motor_changed = Value("b", 0)

        # power meter module
        self.laser_power_self_calibration_requested = Value('b', 0)
        self.laser_power_self_calibration_cancel_requested = Value('b', 0)
        self.current_laser_power_meter_value = Value('d', 0)

        self.stimulus_flow_control_start_requested = Value('b', 0)
        self.stimulus_flow_control_next_stimulus_requested = Value('b', 0)

        self.stimulus_flow_control_index = Value('i', 0)
        self.stimulus_flow_control_start_time = Value('d', 0)
        self.stimulus_flow_control_start_index = Value('i', 0)
        self.stimulus_flow_control_result_info = Value('d', 0)
        self.stimulus_flow_control_current_time = Value('d', 0)
        self.stimulus_flow_control_currently_running = Value('b', 0)

        # Fish information
        self.fish_configuration_ID = Value('i', 0)
        self.fish_configuration_suffix = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.fish_configuration_suffix_l = Value('i', 0)
        self.fish_configuration_genotype = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.fish_configuration_genotype_l = Value('i', 0)
        self.fish_configuration_age = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.fish_configuration_age_l = Value('i', 0)
        self.fish_configuration_comments = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.fish_configuration_comments_l = Value('i', 0)

        # Experiment information
        self.experiment_configuration_storage_root_path = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.experiment_configuration_storage_root_path_l = Value("i", 0)
        self.experiment_configuration_store_green_channel = Value('b', 0)
        self.experiment_configuration_store_red_channel = Value('b', 0)
        self.experiment_configuration_trial_time = Value('i', 600)
        self.experimemt_flow_control_current_time_in_trial = Value('d', 0)

        self.experiment_flow_control_root_path = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.experiment_flow_control_root_path_l = Value('i', 0)

        self.experiment_flow_control_start_requested = Value('b', 0)
        self.experiment_flow_control_stop_requested = Value('b', 0)
        self.experiment_flow_control_currently_running = Value('b', 0)
        self.experiment_flow_control_percentage_done = Value('i', 0)

        self.experimemt_flow_control_start_acquire_imaging_data_requested = Value('b', 0)
        self.experiment_flow_control_currently_acquire_imaging_data = Value('b', 0)
        self.experiment_flow_control_store_imaging_data_requested = Value('b', 0)
        self.experiment_flow_control_currently_storing_imaging_data = Value('b', 0)
        self.experiment_flow_control_store_imaging_data_completed = Value('b', 0)

        ### Scanning module
        self.current_uniblitz_status = Value('b', 0)

        self.start_scanning_requested = Value('b', 0)
        self.stop_scanning_requested = Value('b', 0)
        self.current_time_per_frame = Value('d', 0)
        self.currently_scanning = Value('b', 0)

        self.pmt_data_rolling_shift = Value('i', 34)

        self.scale_green_channel = Value('i', 20000)
        self.min_green_channel = Value('i', 10000)
        self.scale_red_channel = Value('i', 20000)
        self.min_red_channel = Value('i', 10000)

        # NI pci 6115 specific 10 Mhz, pci 6110 has 5mz,  6374 3.571 Mhz, 6363 BNC 1Mhz
        self.galvo_scanning_AIrate = Value('i', 1000000)
        self.galvo_scanning_AOrate = Value('i', 400000)
        self.galvo_scanning_AOrate_raster_scanning = Value('i', 400000)
        self.galvo_scanning_AOrate_regional_scanning = Value('i', 400000)
        self.galvo_scanning_resolutionx = Value('i', 800)
        self.galvo_scanning_resolutiony = Value('i', 800)
        self.galvo_scanning_turnaround_pixels = Value('i', 30)
        self.galvo_scanning_pixel_galvo_factor = Value('d', 0.005)

        # self.scanning_configuration_pmt_gain_green_update_requested =  Value('b', 0)
        # self.scanning_configuration_pmt_gain_green = Value('d', 0)
        # self.scanning_configuration_pmt_gain_red_update_requested = Value('b', 0)
        # self.scanning_configuration_pmt_gain_red = Value('d', 0)
        self.green_pmt_turn_on_while_scanning = Value('b', 0)
        self.red_pmt_turn_on_while_scanning = Value('b', 0)

        #####
        self.scanning_configuration_display_lowpass_filter_constant = Value('d', 0)
        self.green_channel_slider_low = Value('i', 10000)
        self.green_channel_slider_high = Value('i', 14095)
        self.red_channel_slider_low = Value('i', 10000)
        self.red_channel_slider_high = Value('i', 14095)
        self.imaging_display_configuration_fill_missing_pixels = Value('b', 0)
        self.image_green_LP_min = Value('d', 0)
        self.image_green_LP_max = Value('d', 0)
        self.image_green_LP_mean = Value('d', 0)
        self.image_red_LP_min = Value('d', 0)
        self.image_red_LP_max = Value('d', 0)
        self.image_red_LP_mean = Value('d', 0)

        ### general programm flow
        self.running = Value('b', 1)

    def start_threads(self):

        ExperimentFlowControlModule(self).start()
        #MaiTaiModule(self).start()
        #LambdaHalfPlateModule(self).start()
        UniblitzShutterStatusModule(self).start()
        ScanningModule(self).start()
