# PyScan2P
CSHL Imaging Course: A minimal version of PyZebra2P  

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

**Any suggestions on how to improve the framework?**:
Visit us at our [lab website](www.neurobiology-konstanz.com/bahl).
