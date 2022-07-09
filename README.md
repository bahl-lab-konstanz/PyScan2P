# PyScan2P: A minimalist version of PyZebra2P  
The PyScan2P software package is a minimalist version of the Python-based microscopy framework PyZebra2P that is beeing developed in the Bahl lab at the University of Konstanz. PyScan2P is open to the attendees of the [CSHL Imaging Course](https://meetings.cshl.edu/courses.aspx?course=C-IMAG&year=22) and the neurobiology students at the University of Konstanz and should teach students how to set up a simple two-photon imaging system. The package is organized in a modular way, such that students can later extend it to their specific needs, such as adding visual stimulation, behavioral tracking, stage control, electrophysiology, etc.  

Please let us know if you have any suggestions or ideas on how to improve our software. Visit us at our [lab website](https://www.neurobiology-konstanz.com/bahl).  
Armin & Katja. 

## Setting up the right Python environment
Install the latest anaconda version for your operating system (https://www.anaconda.com/products/individual).  
Open the anaconda command prompt. 

We try to have everything in one conda channel and avoid pip as much as possible. This should help building a healthy dependency tree.  

conda create --name PyScan2P --channel conda-forge python=3.9  
conda activate PyScan2P  

conda update -n base -c defaults conda  
conda config --add channels conda-forge  
conda config --set channel_priority strict  

conda install --yes -c conda-forge -v appdirs cython matplotlib numpy numpydoc pyqtgraph scikit-image scikit-learn scipy tifffile imageio-ffmpeg numba ftd2xx pyserial pyvisa  
pip install PyDAQmx pyqt6 pyqt6-tools
