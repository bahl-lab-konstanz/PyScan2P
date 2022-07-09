from multiprocessing import Process
import time
import os
from pathlib import Path

class ExperimentFlowControlModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        while self.shared.running.value == 1:

            if self.shared.experiment_flow_control_start_requested.value == 1:
                self.shared.experiment_flow_control_start_requested.value = 0

                self.shared.experiment_flow_control_currently_running.value = 1

                # Make the folder structure for all fish
                root_path = Path(bytearray(self.shared.experiment_configuration_storage_root_path[:self.shared.experiment_configuration_storage_root_path_l.value]).decode())
                root_path.mkdir(exist_ok=True)

                suffix = "test" # TODO get this from the GUI
                folder_name = time.strftime("%Y-%m-%d_%H-%M-%S")
                folder_name += f"_fish{self.shared.fish_configuration_ID.value:03d}"

                if len(suffix) > 0:
                    folder_name += f"_{suffix}"

                root_path = root_path / folder_name

                try:
                    root_path.mkdir(exist_ok=False)
                except:
                    print("Experiment folder", root_path, "already exists. Stopping....")
                    continue

                self.shared.experiment_flow_control_root_path[:len(root_path)] = root_path.encode()
                self.shared.experiment_flow_control_root_path_l.value = len(root_path)

                ########################
                # Save general experiment information
                infos = dict()
                infos["Date and time"] = time.strftime("%Y-%m-%d_%H-%M-%S")
                infos["fish_configuration_ID"] = self.shared.fish_configuration_ID.value
                infos["fish_configuration_genotype"] = bytearray(self.shared.fish_configuration_genotype[:self.shared.fish_configuration_genotype_l.value]).decode()

                infos["fish_configuration_age"] = bytearray(self.shared.fish_configuration_age[:self.shared.fish_configuration_age_l.value]).decode()
                infos["fish_configuration_comments"] = bytearray(self.shared.fish_configuration_comments[:self.shared.fish_configuration_comments_l.value]).decode()
                infos["current_lambda_half_plate_orientation"] = self.shared.current_lambda_half_plate_orientation.value
                infos["current_mai_tai_info_wavelength"] = self.shared.current_mai_tai_info_wavelength.value
                infos["stimulus_configuration_stimulus_path"] = bytearray(self.shared.stimulus_configuration_stimulus_path[:self.shared.stimulus_configuration_stimulus_path_l.value]).decode()
                infos["stimulus_information_number_of_stimuli"] = self.shared.stimulus_information_number_of_stimuli.value
                infos["stimulus_information_time_per_stimulus"] = self.shared.stimulus_information_time_per_stimulus.value
                infos["galvo_scanning_AIrate"] = self.shared.galvo_scanning_AIrate.value
                infos["galvo_scanning_AOrate"] = self.shared.galvo_scanning_AOrate.value
                infos["galvo_scanning_expected_pmt_signal_range"] = self.shared.galvo_scanning_expected_pmt_signal_range.value
                infos["pmt_data_rolling_shift"] = self.shared.pmt_data_rolling_shift.value
                infos["scanning_configuration_pmt_gain_green"] = self.shared.scanning_configuration_pmt_gain_green.value
                infos["scanning_configuration_pmt_gain_red"] = self.shared.scanning_configuration_pmt_gain_red.value
                infos["scanning_configuration_pmt_green_turned_on"] = self.shared.green_pmt_turn_on_while_scanning.value
                infos["scanning_configuration_pmt_red_turned_on"] = self.shared.red_pmt_turn_on_while_scanning.value
                infos["galvo_scanning_resolutionx"] = self.shared.galvo_scanning_resolutionx.value
                infos["galvo_scanning_resolutiony"] = self.shared.galvo_scanning_resolutiony.value
                infos["galvo_scanning_turnaround_pixels"] = self.shared.galvo_scanning_turnaround_pixels.value
                infos["scale_green_channel"] = self.shared.scale_green_channel.value
                infos["min_green_channel"] = self.shared.min_green_channel.value
                infos["scale_red_channel"] = self.shared.scale_red_channel.value
                infos["min_red_channel"] = self.shared.min_red_channel.value
                infos["experiment_configuration_trial_time"] = self.shared.experiment_configuration_trial_time.value
                infos["store_green_channel"] = self.shared.experiment_configuration_store_green_channel.value
                infos["store_red_channel"] = self.shared.experiment_configuration_store_red_channel.value

                # Also save all the attributes to a text file, for easier readings
                fp = open(os.path.join(root_path, "experiment_information.txt"), "w")
                for key in infos.keys():
                    fp.write(f"{key}:\t" + str(infos[key]) + "\n")

                fp.close()

                ####################
                #### Everyhing prepared now, now go start the experiment
                self.shared.start_scanning_requested.value = 1  # start the scanning, this now runs forever and will only be interupted during saving of stacks

                experiment_start_time = time.time()
                experiment_total_time = self.shared.experiment_configuration_trial_time.value

                # Tell the scanning module to start image acquisition
                self.shared.experimemt_flow_control_start_acquire_imaging_data_requested.value = 1

                # Waiting loop to the end of the trial
                trial_start_time = time.time()

                while time.time() - trial_start_time < self.shared.experiment_configuration_trial_time.value:

                    self.shared.experimemt_flow_control_current_time_in_trial.value = time.time() - trial_start_time

                    time.sleep(0.05)

                    # Calculate the percentage done of the experiment
                    self.shared.experiment_flow_control_percentage_done.value = int(100 * (time.time() - experiment_start_time) / experiment_total_time)

                    if self.shared.experiment_flow_control_stop_requested.value == 1:
                        self.shared.experiment_flow_control_stop_requested.value = 0
                        break

                # Stop all acquisitions
                self.shared.experiment_flow_control_currently_acquire_imaging_data.value = 0

                # Store the data
                if self.shared.experiment_configuration_store_green_channel.value == 1 or \
                        self.shared.experiment_configuration_store_red_channel.value == 1:

                    self.shared.experiment_flow_control_store_imaging_data_completed.value = 0
                    self.shared.experiment_flow_control_store_imaging_data_requested.value = 1
                    while self.shared.experiment_flow_control_store_imaging_data_completed.value == 0:

                        if self.shared.experiment_flow_control_stop_requested.value == 1:
                            self.shared.experiment_flow_control_stop_requested.value = 0
                            break

                        time.sleep(0.05)

                self.shared.stop_scanning_requested.value = 1
                self.shared.experiment_flow_control_currently_running.value = 0

                # Close the laser shutter after the experiment
                #if self.shared.current_mai_tai_info_shutter_open.value == 1:
                #    self.shared.pushButton_MaiTai_Shutter_clicked.value = 1

            time.sleep(0.01)