if __name__ == "__main__":

    from shared import Shared
    from pathlib import Path
    import sys
    from appdirs import user_data_dir

    shared = Shared()
    shared.start_threads()

    from PyQt6 import QtCore, uic, QtWidgets

    import os
    import numpy as np
    import pyqtgraph as pg
    import pickle

    class GUI_Dialog(QtWidgets.QDialog):
        def __init__(self, parent=None):
            QtWidgets.QWidget.__init__(self, parent)

            self.shared = shared
            path = os.path.dirname(__file__)

            pg.setConfigOption('background', pg.mkColor(20 / 255.))
            pg.setConfigOption('foreground', 'w')

            uic.loadUi(os.path.join(path, "PyScan2P_dialog.ui"), self)

            # scale all the widgets (4k, windows scaling problem)
            fontscale = 1#1  # 2.2
            sizescale = 1.1#2.2

            # Scale the application window
            size = self.size()
            self.resize(int(size.width()*sizescale), int(size.height()*sizescale))

            for widget in self.findChildren(QtWidgets.QWidget):

                size = widget.size()

                widget.resize(int(size.width()*sizescale), int(size.height()*sizescale))
                widget.move(int(widget.x()*sizescale), int(widget.y()*sizescale))

                font = widget.font()

                font.setPointSize(font.pointSize() * fontscale)
                widget.setFont(font)

            self.pushButton_startstop_continuous_scanning.clicked.connect(self.pushButton_startstop_continuous_scanning_clicked)

            ##########
            ### Laser tab

            self.spinBox_setMaiTai_wavelength.valueChanged.connect(self.spinBox_setMaiTai_wavelength_valueChanged)
            self.doubleSpinBox_prechirp_motor.valueChanged.connect(self.doubleSpinBox_prechirp_motor_valueChanged)
            self.pushButton_MaiTai_Shutter.clicked.connect(self.pushButton_MaiTai_Shutter_clicked)
            self.pushButton_MaiTai_ON.clicked.connect(self.pushButton_MaiTai_ON_clicked)
            self.pushButton_MaiTai_OFF.clicked.connect(self.pushButton_MaiTai_OFF_clicked)

            self.doubleSpinBox_target_lambda_half_plate_orientation.valueChanged.connect(self.doubleSpinBox_target_lambda_half_plate_orientation_valueChanged)

            self.laser_calibration_interpolation_function = None

            ##########
            ### Scanning tab

            # Fill the dwelltime combobox
            binsizes = np.arange(2, 400)
            AIrate = self.shared.galvo_scanning_AIrate.value

            self.combo_infos = []
            for binsize in binsizes:
                if AIrate % binsize == 0:
                    AOrate = AIrate/float(binsize)
                    dwelltime = 1e6/AOrate

                    text = u"%.1f μs ( = %s kHz)"%(dwelltime, AOrate/1000.)

                    self.combo_infos.append(int(AOrate))
                    self.comboBox_dwelltime_raster_scanning.addItem(text)

            self.comboBox_dwelltime_raster_scanning.setCurrentIndex(3)

            self.doubleSpinBox_scanning_configuration_pmt_gain_green.valueChanged.connect(self.doubleSpinBox_scanning_configuration_pmt_gain_green_valueChanged)
            self.doubleSpinBox_scanning_configuration_pmt_gain_red.valueChanged.connect(self.doubleSpinBox_scanning_configuration_pmt_gain_red_valueChanged)

            self.checkBox_green_pmt_turn_on_while_scanning.clicked.connect(self.checkBox_green_pmt_turn_on_while_scanning_clicked)
            self.checkBox_red_pmt_turn_on_while_scanning.clicked.connect(self.checkBox_red_pmt_turn_on_while_scanning_clicked)

            ##########
            # Image
            self.spinBox_pmt_data_rolling_shift.valueChanged.connect(self.spinBox_pmt_data_rolling_shift_valueChanged)

            self.spinBox_galvo_scanning_resolutionx.valueChanged.connect(self.spinBox_galvo_scanning_resolutionx_valueChanged)
            self.spinBox_galvo_scanning_resolutiony.valueChanged.connect(self.spinBox_galvo_scanning_resolutiony_valueChanged)
            self.spinBox_raster_scanning_turn_around_pixels.valueChanged.connect(self.spinBox_raster_scanning_turn_around_pixels_valueChanged)
            self.doubleSpinBox_scanning_configuration_pixel_to_galvo_factor.valueChanged.connect(self.doubleSpinBox_scanning_configuration_pixel_to_galvo_factor_valueChanged)

            # Fish configuration
            self.spinBox_fish_configuration_ID.valueChanged.connect(self.spinBox_fish_configuration_ID_valueChanged)
            self.lineEdit_fish_configuration_suffix.textChanged.connect(self.lineEdit_fish_configuration_suffix_textChanged)
            self.lineEdit_fish_configuration_genotype.textChanged.connect(self.lineEdit_fish_configuration_genotype_textChanged)
            self.lineEdit_fish_configuration_age.textChanged.connect(self.lineEdit_fish_configuration_age_textChanged)
            self.lineEdit_fish_configuration_comments.textChanged.connect(self.lineEdit_fish_configuration_comments_textChanged)

            # Experiment
            self.checkBox_experiment_store_green_channel.clicked.connect(self.checkBox_experiment_store_green_channel_clicked)
            self.checkBox_experiment_store_red_channel.clicked.connect(self.checkBox_experiment_store_red_channel_clicked)

            self.pushButton_start_experiment.clicked.connect(self.pushButton_start_experiment_clicked)

            self.spinBox_experiment_configuration_trial_time.valueChanged.connect(self.spinBox_experiment_configuration_trial_time_valueChanged)

            self.pushButton_volume_scanning_load_filepath.clicked.connect(self.pushButton_volume_scanning_load_filepath_clicked)
            self.lineEdit_volume_scanning_filepath.textChanged.connect(self.lineEdit_volume_scanning_filepath_textChanged)

            self.doubleSpinBox_scanning_configuration_display_lowpass_filter_constant.valueChanged.connect(self.doubleSpinBox_scanning_configuration_display_lowpass_filter_constant_valueChanged)
            self.green_channel_slider_low.valueChanged.connect(self.green_channel_slider_low_valueChanged)
            self.green_channel_slider_high.valueChanged.connect(self.green_channel_slider_high_valueChanged)
            self.red_channel_slider_low.valueChanged.connect(self.red_channel_slider_low_valueChanged)
            self.red_channel_slider_high.valueChanged.connect(self.red_channel_slider_high_valueChanged)
            self.spinBox_scale_green_channel.valueChanged.connect(self.spinBox_scale_green_channel_valueChanged)
            self.spinBox_min_green_channel.valueChanged.connect(self.spinBox_min_green_channel_valueChanged)

            self.spinBox_scale_red_channel.valueChanged.connect(self.spinBox_scale_red_channel_valueChanged)
            self.spinBox_min_red_channel.valueChanged.connect(self.spinBox_min_red_channel_valueChanged)

            self.comboBox_dwelltime_raster_scanning.activated.connect(self.comboBox_dwelltime_raster_scanning_activated)

            ########################################
            # load the configuration file
            self.load_configuration()

            self.update_gui_timer = QtCore.QTimer()
            self.update_gui_timer.timeout.connect(self.update_gui)
            self.update_gui_timer.start(20)

            self.delayed_initialization_timer = QtCore.QTimer()
            self.delayed_initialization_timer.timeout.connect(self.delayed_initialization)
            self.delayed_initialization_timer.start(2000)

            ############################################
            # green pmt tab

            # the histogram plot
            labelStyle = {'color': '#FFF', 'font-size': '{}pt'.format(10)}
            self.pyqtgraph_histogram_green_channel.setLabel('left', 'Density (%)', **labelStyle)
            self.pyqtgraph_histogram_green_channel.setLabel('bottom', 'Brightness value', **labelStyle)
            self.pyqtgraph_histogram_green_channel.setXRange(10000, 14096)

            curvePen = pg.mkPen(color=(0, 255, 0), width=2.5)
            self.green_image_histogram_curve = pg.PlotCurveItem(pen=curvePen)
            self.pyqtgraph_histogram_green_channel.addItem(self.green_image_histogram_curve)

            curvePen = pg.mkPen(color=(200, 200, 200), width=1.5)
            self.green_image_slider_low_curve = pg.PlotCurveItem(pen=curvePen)
            self.pyqtgraph_histogram_green_channel.addItem(self.green_image_slider_low_curve)

            curvePen = pg.mkPen(color=(200, 200, 200), width=1.5)
            self.green_image_slider_high_curve = pg.PlotCurveItem(pen=curvePen)
            self.pyqtgraph_histogram_green_channel.addItem(self.green_image_slider_high_curve)

            # the pmt data plot
            self.pyqtgraph_green_pmt_image_item = pg.ImageItem()
            self.pyqtgraph_green_pmt_image.hideAxis('left')
            self.pyqtgraph_green_pmt_image.hideAxis('bottom')
            self.pyqtgraph_green_pmt_image.addItem(self.pyqtgraph_green_pmt_image_item)
            self.pyqtgraph_green_pmt_image.setAspectLocked()

            ############################################
            # red pmt tab

            # the histogram plot
            labelStyle = {'color': '#FFF', 'font-size': '{}pt'.format(10)}
            self.pyqtgraph_histogram_red_channel.setLabel('left', 'Density (%)', **labelStyle)
            self.pyqtgraph_histogram_red_channel.setLabel('bottom', 'Brightness value', **labelStyle)
            self.pyqtgraph_histogram_red_channel.setXRange(10000, 14096)

            curvePen = pg.mkPen(color=(255, 0, 0), width=2.5)
            self.red_image_histogram_curve = pg.PlotCurveItem(pen=curvePen)
            self.pyqtgraph_histogram_red_channel.addItem(self.red_image_histogram_curve)

            curvePen = pg.mkPen(color=(200, 200, 200), width=1.5)
            self.red_image_slider_low_curve = pg.PlotCurveItem(pen=curvePen)
            self.pyqtgraph_histogram_red_channel.addItem(self.red_image_slider_low_curve)

            curvePen = pg.mkPen(color=(200, 200, 200), width=1.5)
            self.red_image_slider_high_curve = pg.PlotCurveItem(pen=curvePen)
            self.pyqtgraph_histogram_red_channel.addItem(self.red_image_slider_high_curve)

            # the pmt data plot
            self.pyqtgraph_red_pmt_image_item = pg.ImageItem()
            self.pyqtgraph_red_pmt_image.hideAxis('left')
            self.pyqtgraph_red_pmt_image.hideAxis('bottom')
            self.pyqtgraph_red_pmt_image.addItem(self.pyqtgraph_red_pmt_image_item)
            self.pyqtgraph_red_pmt_image.setAspectLocked()

            # dual red/green tab

            # the pmt data plot
            self.pyqtgraph_dual_pmt_image_item = pg.ImageItem()
            self.pyqtgraph_dual_pmt_image.hideAxis('left')
            self.pyqtgraph_dual_pmt_image.hideAxis('bottom')
            self.pyqtgraph_dual_pmt_image.addItem(self.pyqtgraph_dual_pmt_image_item)
            self.pyqtgraph_dual_pmt_image.setAspectLocked()

        def load_configuration(self):

            user_data_folder = Path(user_data_dir("PyScan2P", "arminbahl"))

            try:
                [self.shared.experiment_configuration_store_green_channel.value,
                 self.shared.experiment_configuration_store_red_channel.value,
                 self.shared.experiment_configuration_trial_time.value,
                 self.shared.galvo_scanning_AOrate_raster_scanning.value,
                 self.shared.galvo_scanning_AOrate_regional_scanning.value,
                 self.shared.galvo_scanning_resolutionx.value,
                 self.shared.galvo_scanning_resolutiony.value,
                 self.shared.galvo_scanning_turnaround_pixels.value,
                 self.shared.galvo_scanning_pixel_galvo_factor.value,
                 self.shared.pmt_data_rolling_shift.value,
                 self.shared.scanning_configuration_pmt_gain_green.value,
                 self.shared.scanning_configuration_pmt_gain_red.value,
                 self.shared.scanning_configuration_display_lowpass_filter_constant.value,
                 self.shared.green_channel_slider_low.value,
                 self.shared.green_channel_slider_high.value,
                 self.shared.red_channel_slider_low.value,
                 self.shared.red_channel_slider_high.value,
                 self.shared.scale_green_channel.value,
                 self.shared.min_green_channel.value,
                 self.shared.scale_red_channel.value,
                 self.shared.min_red_channel.value,
                 volume_scanning_filepath] = pickle.load(open(user_data_folder / "configuration.pickle", "rb"))

                filepath = volume_scanning_filepath.encode()
                self.shared.experiment_configuration_storage_root_path[:len(filepath)] = filepath
                self.shared.experiment_configuration_storage_root_path_l.value = len(filepath)

            except Exception as e:
                print(e)

        def save_configuration(self):

            user_data_folder = Path(user_data_dir("PyScan2P", "arminbahl"))

            if not user_data_folder.exists():
                user_data_folder.mkdir(parents=True)

            try:
                volume_scanning_filepath = bytearray(self.shared.experiment_configuration_storage_root_path[:self.shared.experiment_configuration_storage_root_path_l.value]).decode()

                pickle.dump([self.shared.experiment_configuration_store_green_channel.value,
                 self.shared.experiment_configuration_store_red_channel.value,
                 self.shared.experiment_configuration_trial_time.value,
                 self.shared.galvo_scanning_AOrate_raster_scanning.value,
                 self.shared.galvo_scanning_AOrate_regional_scanning.value,
                 self.shared.galvo_scanning_resolutionx.value,
                 self.shared.galvo_scanning_resolutiony.value,
                 self.shared.galvo_scanning_turnaround_pixels.value,
                 self.shared.galvo_scanning_pixel_galvo_factor.value,
                 self.shared.pmt_data_rolling_shift.value,
                 self.shared.scanning_configuration_pmt_gain_green.value,
                 self.shared.scanning_configuration_pmt_gain_red.value,
                 self.shared.scanning_configuration_display_lowpass_filter_constant.value,
                 self.shared.green_channel_slider_low.value,
                 self.shared.green_channel_slider_high.value,
                 self.shared.red_channel_slider_low.value,
                 self.shared.red_channel_slider_high.value,
                 self.shared.scale_green_channel.value,
                 self.shared.min_green_channel.value,
                 self.shared.scale_red_channel.value,
                 self.shared.min_red_channel.value,
                 volume_scanning_filepath
            ], open(user_data_folder / "configuration.pickle", "wb"))
            except Exception as e:
                print(e)

        def spinBox_fish_configuration_ID_valueChanged(self):
            self.shared.fish_configuration_ID.value = self.spinBox_fish_configuration_ID.value()

        def lineEdit_fish_configuration_suffix_textChanged(self):
            fish_configuration_suffix = self.lineEdit_fish_configuration_suffix.text().encode()

            self.shared.fish_configuration_suffix[:len(fish_configuration_suffix)] = fish_configuration_suffix
            self.shared.fish_configuration_suffix_l.value = len(fish_configuration_suffix)

        def lineEdit_fish_configuration_genotype_textChanged(self):
            fish_configuration_genotype = self.lineEdit_fish_configuration_genotype.text().encode()

            self.shared.fish_configuration_genotype[:len(fish_configuration_genotype)] = fish_configuration_genotype
            self.shared.fish_configuration_genotype_l.value = len(fish_configuration_genotype)

        def lineEdit_fish_configuration_age_textChanged(self):
            fish_configuration_age = self.lineEdit_fish_configuration_age.text().encode()

            self.shared.fish_configuration_age[:len(fish_configuration_age)] = fish_configuration_age
            self.shared.fish_configuration_age_l.value = len(fish_configuration_age)

        def lineEdit_fish_configuration_comments_textChanged(self):
            fish_configuration_comments = self.lineEdit_fish_configuration_comments.text().encode()

            self.shared.fish_configuration_comments[:len(fish_configuration_comments)] = fish_configuration_comments
            self.shared.fish_configuration_comments_l.value = len(fish_configuration_comments)

        def checkBox_experiment_store_green_channel_clicked(self):
            self.shared.experiment_configuration_store_green_channel.value = 1 if self.checkBox_experiment_store_green_channel.isChecked() else 0

        def checkBox_experiment_store_red_channel_clicked(self):
            self.shared.experiment_configuration_store_red_channel.value = 1 if self.checkBox_experiment_store_red_channel.isChecked() else 0

        def doubleSpinBox_scanning_configuration_display_lowpass_filter_constant_valueChanged(self):
            self.shared.scanning_configuration_display_lowpass_filter_constant.value = self.doubleSpinBox_scanning_configuration_display_lowpass_filter_constant.value()

        def green_channel_slider_low_valueChanged(self):
            self.shared.green_channel_slider_low.value = self.green_channel_slider_low.value()

        def green_channel_slider_high_valueChanged(self):
            self.shared.green_channel_slider_high.value = self.green_channel_slider_high.value()

        def red_channel_slider_low_valueChanged(self):
            self.shared.red_channel_slider_low.value = self.red_channel_slider_low.value()

        def red_channel_slider_high_valueChanged(self):
            self.shared.red_channel_slider_high.value = self.red_channel_slider_high.value()

        def spinBox_scale_red_channel_valueChanged(self):
            self.shared.scale_red_channel.value = self.spinBox_scale_red_channel.value()

        def spinBox_min_red_channel_valueChanged(self):
            self.shared.min_red_channel.value = self.spinBox_min_red_channel.value()

        def spinBox_min_green_channel_valueChanged(self):
            self.shared.min_green_channel.value = self.spinBox_min_green_channel.value()

        def spinBox_scale_green_channel_valueChanged(self):
            self.shared.scale_green_channel.value = self.spinBox_scale_green_channel.value()

        def spinBox_galvo_scanning_resolutionx_valueChanged(self):
            self.shared.galvo_scanning_resolutionx.value = self.spinBox_galvo_scanning_resolutionx.value()

        def spinBox_galvo_scanning_resolutiony_valueChanged(self):
            self.shared.galvo_scanning_resolutiony.value = self.spinBox_galvo_scanning_resolutiony.value()

        def spinBox_raster_scanning_turn_around_pixels_valueChanged(self):
            self.shared.galvo_scanning_turnaround_pixels.value = self.spinBox_raster_scanning_turn_around_pixels.value()

        def doubleSpinBox_scanning_configuration_pixel_to_galvo_factor_valueChanged(self):
            self.shared.galvo_scanning_pixel_galvo_factor.value = self.doubleSpinBox_scanning_configuration_pixel_to_galvo_factor.value()

        def lineEdit_volume_scanning_filepath_textChanged(self):
            filepath = self.lineEdit_volume_scanning_filepath.text().encode()

            self.shared.experiment_configuration_storage_root_path[:len(filepath)] = filepath
            self.shared.experiment_configuration_storage_root_path_l.value = len(filepath)

        def pushButton_volume_scanning_load_filepath_clicked(self):
            filepath = os.path.abspath(QtWidgets.QFileDialog.getExistingDirectory())
            self.lineEdit_volume_scanning_filepath.setText(filepath)

        def pushButton_start_experiment_clicked(self):

            if self.shared.currently_scanning.value == 1 and self.shared.experiment_flow_control_currently_running.value == 0: # if in freerunning mode
                self.shared.stop_scanning_requested.value = 1
                return

            if self.shared.experiment_flow_control_currently_running.value == 1:
                self.shared.experiment_flow_control_stop_requested.value = 1
            else:
                self.shared.experiment_flow_control_start_requested.value = 1

        def spinBox_experiment_configuration_trial_time_valueChanged(self):
            self.shared.experiment_configuration_trial_time.value = self.spinBox_experiment_configuration_trial_time.value()

        def doubleSpinBox_target_lambda_half_plate_orientation_valueChanged(self):
            self.shared.target_lambda_half_plate_orientation.value = self.doubleSpinBox_target_lambda_half_plate_orientation.value()
            self.shared.target_lambda_half_plate_orientation_changed.value = 1

        def pushButton_laser_configuration_open_shutter_briefly_clicked(self):
            self.shared.laser_configuration_open_shutter_briefly_requested.value = 1

        def doubleSpinBox_prechirp_motor_valueChanged(self):
            self.shared.prechirp_motor_set.value = self.doubleSpinBox_prechirp_motor.value()
            self.shared.prechirp_motor_changed.value = 1

        def keyPressEvent(self, e):
            if e.key() == QtCore.Qt.Key.Key_Escape:
                self.close()

        def delayed_initialization(self):

            # image
            self.doubleSpinBox_scanning_configuration_display_lowpass_filter_constant.setValue(self.shared.scanning_configuration_display_lowpass_filter_constant.value)
            self.green_channel_slider_low.setValue(self.shared.green_channel_slider_low.value)
            self.green_channel_slider_high.setValue(self.shared.green_channel_slider_high.value)
            self.red_channel_slider_low.setValue(self.shared.red_channel_slider_low.value)
            self.red_channel_slider_high.setValue(self.shared.red_channel_slider_high.value)
            self.spinBox_scale_green_channel.setValue(self.shared.scale_green_channel.value)
            self.spinBox_min_green_channel.setValue(self.shared.min_green_channel.value)
            self.spinBox_scale_red_channel.setValue(self.shared.scale_red_channel.value)
            self.spinBox_min_red_channel.setValue(self.shared.min_red_channel.value)

            ## scanning tab

            try:
                self.comboBox_dwelltime_raster_scanning.setCurrentIndex(self.combo_infos.index(self.shared.galvo_scanning_AOrate_raster_scanning.value))
            except:
                pass

            self.doubleSpinBox_scanning_configuration_pmt_gain_green.setValue(self.shared.scanning_configuration_pmt_gain_green.value)
            self.doubleSpinBox_scanning_configuration_pmt_gain_red.setValue(self.shared.scanning_configuration_pmt_gain_red.value)

            self.checkBox_green_pmt_turn_on_while_scanning.setChecked(self.shared.green_pmt_turn_on_while_scanning.value == 1)
            self.checkBox_red_pmt_turn_on_while_scanning.setChecked(self.shared.red_pmt_turn_on_while_scanning.value == 1)

            self.spinBox_galvo_scanning_resolutionx.setValue(self.shared.galvo_scanning_resolutionx.value)
            self.spinBox_galvo_scanning_resolutiony.setValue(self.shared.galvo_scanning_resolutiony.value)

            self.spinBox_raster_scanning_turn_around_pixels.setValue(self.shared.galvo_scanning_turnaround_pixels.value)

            self.doubleSpinBox_scanning_configuration_pixel_to_galvo_factor.setValue(self.shared.galvo_scanning_pixel_galvo_factor.value)

            self.spinBox_pmt_data_rolling_shift.setValue(self.shared.pmt_data_rolling_shift.value)

            self.spinBox_experiment_configuration_trial_time.setValue(self.shared.experiment_configuration_trial_time.value)

            self.checkBox_experiment_store_green_channel.setChecked(self.shared.experiment_configuration_store_green_channel.value == 1)
            self.checkBox_experiment_store_red_channel.setChecked(self.shared.experiment_configuration_store_red_channel.value == 1)

            path = bytearray(self.shared.experiment_configuration_storage_root_path[:self.shared.experiment_configuration_storage_root_path_l.value]).decode()
            self.lineEdit_volume_scanning_filepath.setText(path)

            # laser
            self.spinBox_setMaiTai_wavelength.setValue(self.shared.current_mai_tai_info_wavelength.value)
            self.doubleSpinBox_prechirp_motor.setValue(self.shared.prechirp_motor_current.value)

            self.doubleSpinBox_target_lambda_half_plate_orientation.setValue(self.shared.initial_lambda_half_plate_orientation.value)

            self.delayed_initialization_timer.stop()

        def spinBox_setMaiTai_wavelength_valueChanged(self):
            self.shared.target_mai_tai_wavelength.value = self.spinBox_setMaiTai_wavelength.value()
            self.shared.target_mai_tai_wavelength_changed.value = 1

        def pushButton_MaiTai_Shutter_clicked(self):
            self.shared.pushButton_MaiTai_Shutter_clicked.value = 1

        def pushButton_MaiTai_ON_clicked(self):
            self.shared.pushButton_MaiTai_ON_clicked.value = 1

        def pushButton_MaiTai_OFF_clicked(self):
            self.shared.pushButton_MaiTai_OFF_clicked.value = 1

        def spinBox_pmt_data_rolling_shift_valueChanged(self):
            self.shared.pmt_data_rolling_shift.value = self.spinBox_pmt_data_rolling_shift.value()

        def comboBox_dwelltime_raster_scanning_activated(self):
            self.shared.galvo_scanning_AOrate_raster_scanning.value = self.combo_infos[self.comboBox_dwelltime_raster_scanning.currentIndex()]

        def pushButton_startstop_continuous_scanning_clicked(self):

            if self.shared.experiment_flow_control_currently_running.value == 1:
                self.shared.experiment_flow_control_stop_requested.value = 1
                return

            if self.shared.currently_scanning.value == 1:
                self.shared.stop_scanning_requested.value = 1
                return

            self.shared.start_scanning_requested.value = 1

        def doubleSpinBox_scanning_configuration_pmt_gain_green_valueChanged(self):
            self.shared.scanning_configuration_pmt_gain_green.value = self.doubleSpinBox_scanning_configuration_pmt_gain_green.value()
            self.shared.scanning_configuration_pmt_gain_green_update_requested.value = 1

        def doubleSpinBox_scanning_configuration_pmt_gain_red_valueChanged(self):
            self.shared.scanning_configuration_pmt_gain_red.value = self.doubleSpinBox_scanning_configuration_pmt_gain_red.value()
            self.shared.scanning_configuration_pmt_gain_red_update_requested.value = 1

        def checkBox_green_pmt_turn_on_while_scanning_clicked(self):
            self.shared.green_pmt_turn_on_while_scanning.value = 1 if self.checkBox_green_pmt_turn_on_while_scanning.isChecked() else 0
            self.shared.scanning_configuration_pmt_gain_green_update_requested.value = 1

        def checkBox_red_pmt_turn_on_while_scanning_clicked(self):
            self.shared.red_pmt_turn_on_while_scanning.value = 1 if self.checkBox_red_pmt_turn_on_while_scanning.isChecked() else 0
            self.shared.scanning_configuration_pmt_gain_red_update_requested.value = 1

        def update_gui(self):

            # Update the voltage range display for the scan pattern
            width = self.shared.galvo_scanning_resolutionx.value + self.shared.galvo_scanning_turnaround_pixels.value * 2
            height = self.shared.galvo_scanning_resolutionx.value
            min_max_Vx = width / 2 * self.shared.galvo_scanning_pixel_galvo_factor.value
            min_max_Vy = height / 2 * self.shared.galvo_scanning_pixel_galvo_factor.value
            self.label_voltage_range.setText(f"Galvo range:\n X:  ±{min_max_Vx:.2f} V\n Y:  ±{min_max_Vy:.2f} V")

            # allow some gui control from other processes (running protocol)
            if self.shared.raster_scanning_start_requested.value == 1:
                self.shared.raster_scanning_start_requested.value = 0

                if self.shared.currently_scanning.value == 0:
                    self.pushButton_startstop_continuous_scanning_clicked()

            if self.shared.raster_scanning_stop_requested.value == 1:
                self.shared.raster_scanning_stop_requested.value = 0

                if self.shared.currently_scanning.value == 1:
                    self.pushButton_startstop_continuous_scanning_clicked()

            current_display_tab = self.tabWidget_display_data.currentIndex()
            current_configuration_tab = self.tabWidget_configuration.currentIndex()

            #########

            if self.shared.scanning_configuration_pmt_gain_green.value > 0 and self.shared.green_pmt_turn_on_while_scanning.value == 1 and self.shared.currently_scanning.value == 1:
                green_label_text = f"Green PMT: ON"
                green_label_color = "yellow"
                green_label_border = "orange"
            else:
                green_label_text = f"Green PMT: off"
                green_label_color = "rgb(100, 100, 100)"
                green_label_border = "rgb(50, 50, 50)"
                
            if self.shared.scanning_configuration_pmt_gain_red.value > 0 and self.shared.red_pmt_turn_on_while_scanning.value == 1 and self.shared.currently_scanning.value == 1:
                red_label_text = f"red PMT: ON"
                red_label_color = "yellow"
                red_label_border = "orange"
            else:
                red_label_text = f"red PMT: off"
                red_label_color = "rgb(100, 100, 100)"
                red_label_border = "rgb(50, 50, 50)"
                
            self.label_green_pmt_state.setText(green_label_text)
            self.label_green_pmt_state.setStyleSheet(f"QLabel {{ color:black; background: {green_label_color}; border: 1px solid  {green_label_border}}}")

            self.label_red_pmt_state.setText(red_label_text)
            self.label_red_pmt_state.setStyleSheet(f"QLabel {{ color:black; background: {red_label_color}; border: 1px solid  {red_label_border}}}")

            ####################
            ### MAI Thai Info Update
            if self.shared.current_mai_tai_info_laser_emmision.value == 1:

                self.label_laser_emmision.setText("Laser is ON")
                self.label_laser_emmision.setStyleSheet("QLabel {color: red; font-size: 18pt;font-weight: bold;}")

            else:
                self.label_laser_emmision.setText("Laser is OFF")
                self.label_laser_emmision.setStyleSheet("QLabel {color: white; font-size: 10pt;font-weight: normal;}")

            self.label_MaiTai_wavelength.setText("%d nm" % self.shared.current_mai_tai_info_wavelength.value)
            self.label_MaiTai_warmup.setText("%.1f%%" % self.shared.current_mai_tai_info_warmup.value)
            self.label_MaiTai_laserpower.setText("%.2f W" % self.shared.current_mai_tai_info_power.value)
            self.label_MaiTai_prechirp.setText("%.2f %%" % self.shared.prechirp_motor_current.value)

            if self.shared.current_mai_tai_info_modelocking.value == 1:
                self.label_MaiTai_modelocking.setStyleSheet(
                    "QLabel { color:black; background: yellow; border: 1px solid  orange}")
                self.label_MaiTai_modelocking.setText("ML")
            else:
                self.label_MaiTai_modelocking.setStyleSheet(
                    "QLabel { color:black; background: rgb(50, 50, 50); border: 1px solid  rgb(20, 20, 20)}")
                self.label_MaiTai_modelocking.setText("")

            if self.shared.current_mai_tai_info_shutter_open.value == 1:
                self.pushButton_MaiTai_Shutter.setStyleSheet(""".QPushButton {
                            background-color: yellow; color:black; border-style: outset;
                            border-width: 2px;
                            border-color: orange;
                            }
                            """)
                self.pushButton_MaiTai_Shutter.setText("Close shutter")
            else:
                self.pushButton_MaiTai_Shutter.setStyleSheet(""".QPushButton {
                            background-color: rgb(150, 150, 150); color:black; border-style: outset;
                            border-width: 2px;
                            border-color: rgb(100, 100, 100);
                            }
                            """)

                self.pushButton_MaiTai_Shutter.setText("Open shutter")

            self.plainTextEdit_mai_tai_current_info.setPlainText(
                bytearray(self.shared.current_mai_tai_info[:self.shared.current_mai_tai_info_l.value]).decode())

            ###################################
            ### update lambda half plate infortmation
            self.label_current_lambda_half_plate_orientation.setText(
                "%.1f" % self.shared.current_lambda_half_plate_orientation.value)


            if self.shared.current_uniblitz_status.value == 0:
                self.label_current_uniblitz_status.setStyleSheet(
                    "QLabel { color:black; background: rgb(100, 100, 100); border: 1px solid  rgb(50, 50, 50)}")

                self.label_current_uniblitz_status.setText("Closed")
            else:
                self.label_current_uniblitz_status.setStyleSheet(
                    "QLabel { color:black; background: yellow; border: 1px solid orange}")

                self.label_current_uniblitz_status.setText("Open")

            if self.shared.current_mai_tai_info_shutter_open.value == 0:
                self.label_current_laser_shutter_status.setStyleSheet(
                    "QLabel { color:black; background: rgb(100, 100, 100); border: 1px solid  rgb(50, 50, 50)}")

                self.label_current_laser_shutter_status.setText("Closed")
            else:
                self.label_current_laser_shutter_status.setStyleSheet(
                    "QLabel { color:black; background: yellow; border: 1px solid orange}")

                self.label_current_laser_shutter_status.setText("Open")

            ####################
            ### Update scanning buttons
            if self.shared.currently_scanning.value == 1:

                stylesheet = """
                                                .QPushButton {
                                                    background-color: red; color:black; border-style: outset;
                                                    border-width: 2px;
                                                    border-color: darkred;
                                                    }
                                                    """

                self.pushButton_startstop_continuous_scanning.setStyleSheet(stylesheet)
                self.pushButton_startstop_continuous_scanning.setText("Stop scanning")

                self.pushButton_start_experiment.setStyleSheet(stylesheet)
                self.pushButton_start_experiment.setText("Stop scanning")

                # also gray out the configuration elemments
                self.comboBox_dwelltime_raster_scanning.setEnabled(False)

                self.spinBox_galvo_scanning_resolutionx.setEnabled(False)
                self.spinBox_galvo_scanning_resolutiony.setEnabled(False)
                self.spinBox_raster_scanning_turn_around_pixels.setEnabled(False)

                self.checkBox_experiment_store_green_channel.setEnabled(True)
                self.checkBox_experiment_store_red_channel.setEnabled(True)
                self.lineEdit_volume_scanning_filepath.setEnabled(True)
                self.pushButton_volume_scanning_load_filepath.setEnabled(True)

            if self.shared.experiment_flow_control_currently_running.value == 1:
                stylesheet = """
                    .QPushButton {
                        background-color: red; color:black; border-style: outset;
                        border-width: 2px;
                        border-color: darkred;
                        }
                        """

                self.pushButton_startstop_continuous_scanning.setStyleSheet(stylesheet)
                self.pushButton_startstop_continuous_scanning.setText("Stop scanning")

                self.pushButton_start_experiment.setStyleSheet(stylesheet)
                self.pushButton_start_experiment.setText("Stop experiment")

                # disable the all confiugartion elements
                # also gray out the configuration elemments

                self.comboBox_dwelltime_raster_scanning.setEnabled(False)
                self.spinBox_galvo_scanning_resolutionx.setEnabled(False)
                self.spinBox_galvo_scanning_resolutiony.setEnabled(False)
                self.spinBox_raster_scanning_turn_around_pixels.setEnabled(False)

                self.checkBox_experiment_store_green_channel.setEnabled(False)
                self.checkBox_experiment_store_red_channel.setEnabled(False)
                self.lineEdit_volume_scanning_filepath.setEnabled(False)
                self.pushButton_volume_scanning_load_filepath.setEnabled(False)


            if self.shared.currently_scanning.value == 0 and self.shared.experiment_flow_control_currently_running.value == 0:

                stylesheet = """
                                    .QPushButton {
                                        background-color: green; color:black; border-style: outset;
                                        border-width: 2px;
                                        border-color: darkgreen;
                                        }
                                        """

                self.pushButton_startstop_continuous_scanning.setStyleSheet(stylesheet)
                self.pushButton_startstop_continuous_scanning.setText("Start continuous scanning")

                self.pushButton_start_experiment.setStyleSheet(stylesheet)
                self.pushButton_start_experiment.setText("Start experiment")

                # enable all configuration elements
                self.comboBox_dwelltime_raster_scanning.setEnabled(True)
                self.spinBox_galvo_scanning_resolutionx.setEnabled(True)
                self.spinBox_galvo_scanning_resolutiony.setEnabled(True)
                self.spinBox_raster_scanning_turn_around_pixels.setEnabled(True)

                # but allow the experiment elements still to be modified
                self.checkBox_experiment_store_green_channel.setEnabled(True)
                self.checkBox_experiment_store_red_channel.setEnabled(True)
                self.lineEdit_volume_scanning_filepath.setEnabled(True)
                self.pushButton_volume_scanning_load_filepath.setEnabled(True)

            fulltime = 1 * self.shared.experiment_configuration_trial_time.value
            info = "\nTotal time:\t\t≈ {:.1f} s ({:.1f} min) ".format(fulltime, fulltime / 60)

            info += "\nCurrent time in trial:\t{:.02f} s".format(self.shared.experimemt_flow_control_current_time_in_trial.value)

            info += "\n\nCurrently storing data:\t{}".format(self.shared.experiment_flow_control_currently_storing_imaging_data.value == 1)

            self.label_volume_scanning_info.setText(info)
            self.progressBar_experiment_percentage_done.setValue(self.shared.experiment_flow_control_percentage_done.value)

            if current_display_tab == 0 and self.shared.currently_scanning.value == 1:
                x_pixels = self.shared.galvo_scanning_resolutionx.value
                y_pixels = self.shared.galvo_scanning_resolutiony.value

                image_green_LP = np.ctypeslib.as_array(self.shared.image_green_LP)[:x_pixels * y_pixels]
                image_green_LP.shape = (x_pixels, y_pixels)

                # display
                self.pyqtgraph_green_pmt_image_item.setImage(image_green_LP, autoLevels=False, levels=(self.shared.green_channel_slider_low.value, self.shared.green_channel_slider_high.value))

                # Update the histogram
                hist, bin_edges = np.histogram(image_green_LP.flatten(), bins=1000, range=(10000, 14096), density=True)
                if not np.isnan(hist).any():
                    self.green_image_histogram_curve.setData(bin_edges[1:], hist * 100)
                    self.green_image_slider_low_curve.setData([self.shared.green_channel_slider_low.value, self.shared.green_channel_slider_low.value],
                                                              [0, np.nanmax(hist) * 100])
                    self.green_image_slider_high_curve.setData([self.shared.green_channel_slider_high.value, self.shared.green_channel_slider_high.value],
                                                               [0, np.nanmax(hist) * 100])

                image_min = self.shared.image_green_LP_min.value
                image_max = self.shared.image_green_LP_max.value
                image_mean = self.shared.image_green_LP_mean.value
                time_per_frame = self.shared.current_time_per_frame.value

                info = f"Time per frame: {time_per_frame:.1f} s;\tMinimum: {image_min:.1f}, Maximum: {image_max:.1f}, Mean: {image_mean:.1f}"
                self.label_info_raw_signal_range_green_channel.setText(info)

            ####################
            ### Update red PMT
            if current_display_tab == 1 and self.shared.currently_scanning.value == 1:
                x_pixels = self.shared.galvo_scanning_resolutionx.value
                y_pixels = self.shared.galvo_scanning_resolutiony.value
                image_red_LP = np.ctypeslib.as_array(self.shared.image_red_LP)[:x_pixels * y_pixels]
                image_red_LP.shape = (x_pixels, y_pixels)

                # display
                self.pyqtgraph_red_pmt_image_item.setImage(image_red_LP, autoLevels=False, levels=(self.shared.red_channel_slider_low.value, self.shared.red_channel_slider_high.value))

                # Update the histogram
                hist, bin_edges = np.histogram(image_red_LP.flatten(), bins=1000, range=(10000, 14096), density=True)
                if not np.isnan(hist).any():
                    self.red_image_histogram_curve.setData(bin_edges[1:], hist * 100)
                    self.red_image_slider_low_curve.setData([self.shared.red_channel_slider_low.value, self.shared.red_channel_slider_low.value],
                                                              [0, np.nanmax(hist) * 100])
                    self.red_image_slider_high_curve.setData([self.shared.red_channel_slider_high.value, self.shared.red_channel_slider_high.value],
                                                               [0, np.nanmax(hist) * 100])

                image_min = self.shared.image_red_LP_min.value
                image_max = self.shared.image_red_LP_max.value
                image_mean = self.shared.image_red_LP_mean.value
                time_per_frame = self.shared.current_time_per_frame.value

                info = f"Time per frame: {time_per_frame:.1f} s;\tMinimum: {image_min:.1f}, Maximum: {image_max:.1f}, Mean: {image_mean:.1f}"
                self.label_info_raw_signal_range_red_channel.setText(info)

            ### Update dual image
            if current_display_tab == 2 and self.shared.currently_scanning.value == 1:
                x_pixels = self.shared.galvo_scanning_resolutionx.value
                y_pixels = self.shared.galvo_scanning_resolutiony.value
                image_green_LP = np.ctypeslib.as_array(self.shared.image_green_LP)[:x_pixels * y_pixels]

                image_red_LP = np.ctypeslib.as_array(self.shared.image_red_LP)[
                                      :x_pixels * y_pixels]

                image_dual_LP = np.zeros((x_pixels, y_pixels, 3))
                image_dual_LP[:, :, 0] = image_red_LP.reshape(x_pixels, y_pixels)
                image_dual_LP[:, :, 1] = image_green_LP.reshape(x_pixels, y_pixels) # / 4095 * 255
                image_dual_LP[:, :, 2] = image_red_LP.reshape(x_pixels, y_pixels)

                # Scaling according to Brightness values in green and red tabs.
                image_dual_LP[:, :, 0] = (image_dual_LP[:, :, 0] - self.shared.red_channel_slider_low.value) / (self.shared.red_channel_slider_high.value - self.shared.red_channel_slider_low.value) * 4096
                image_dual_LP[:, :, 1] = (image_dual_LP[:, :, 1] - self.shared.green_channel_slider_low.value) / (self.shared.green_channel_slider_high.value - self.shared.green_channel_slider_low.value) * 4096
                image_dual_LP[:, :, 2] = (image_dual_LP[:, :, 2] - self.shared.red_channel_slider_low.value) / (
                                                            self.shared.red_channel_slider_high.value - self.shared.red_channel_slider_low.value) * 4096
                # display
                self.pyqtgraph_dual_pmt_image_item.setImage(image_dual_LP, autoLevels=False, levels=(0, 4096))

        def closeEvent(self, event):

            if self.shared.current_mai_tai_info_laser_emmision.value == 1:
                message = QtWidgets.QMessageBox(self)
                message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                message.setText("The laser is still emmiting light, do you really want to close the software without switching it off?", )
                message.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes |
                                           QtWidgets.QMessageBox.StandardButton.No)

                reply = message.exec()

                if reply == QtWidgets.QMessageBox.StandardButton.No:
                    event.ignore()
                    return

            if self.shared.current_mai_tai_info_shutter_open.value == 1:
                message = QtWidgets.QMessageBox(self)
                message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                message.setText("The laser shutter is still open. Do you really want to close the software without closing it?", )
                message.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes |
                                           QtWidgets.QMessageBox.StandardButton.No)

                reply = message.exec()

                if reply == QtWidgets.QMessageBox.StandardButton.No:
                    event.ignore()
                    return

            if self.shared.currently_scanning.value == 1:
                message = QtWidgets.QMessageBox(self)
                message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                message.setText("The galvo mirrors are still scanning and the UNIBLITZ shutter is still open. Do you really want to close the software without stopping the task and closing the shutter?", )
                message.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes |
                                           QtWidgets.QMessageBox.StandardButton.No)

                reply = message.exec()

                if reply == QtWidgets.QMessageBox.StandardButton.No:
                    event.ignore()
                    return

            self.save_configuration()
            self.shared.running.value = 0
            self.close()

    app = QtWidgets.QApplication(sys.argv)

    main = GUI_Dialog()

    main.show()
    result = app.exec()

    shared.running.value = 0
    sys.exit(result)
