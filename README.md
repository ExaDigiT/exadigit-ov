# ExaDigiT for NVIDIA Omniverse
This repo is made from the kit-app-template, more info found here: https://github.com/NVIDIA-Omniverse/kit-app-template
## Installation
Clone this repo
```bash
git clone https://code.ornl.gov/exadigit/exadigit-ov.git
```
Build then launch exadigit.dc_digital_twin_base.kit in developer mode
```bash
cd exadigit-ov
repo build
repo launch -d
```

## Simulation Server Setup
1. Follow instructions to install ExaDigiT Simulation Server here (make sure to clone with submodules): https://code.ornl.gov/exadigit/simulationserver
2. Run the server locally, it will be hosted on http:localhost:8080


## Usage
1. From the app, open the file `test.usd` or `stress-test.usd` in the `test-files` directory.

   *_(Note: `stress-test.usd` may take a while to load.)_*
2. Using the ExaDigiT extension window under the Run Simulation tab, fill in the required fields then press the **"Run"** button to trigger a new simulation via the RAPS simulation server.
3. Using the ExaDigiT extension window under the Simulation List tab, you'll see previously run simulations with info including
the Simulation ID, the System it was ran on, and the Start time of the run. Press the **"Select"** button next to the simulation of
your choice to set the current simulation you'd like to see data for.
4. Using the ExaDigiT extension window under the Propagation tab, press the **"Generate Lookup Map"** button to dynamically assign `xnames` and create a lookup map for your data center scene.
5. Also in the ExaDigiT extension window under the Propagation tab, press the **"Propagate Data"** button to send some test data to each data center component in the scene. You can then click on a prim in-scene, and an editor utility widget will pop up detailing its attributes.

   *_(Depending on whether you're using `test.usd` or `stress-test.usd`, you can comment or uncomment lines 116/119 in
   `exadigit-ov\source\extensions\exadigit.data_loader\exadigit\data_loader\extension.py` to generate the appropriate test data.)_*

## Citation

If you use ExaDigiT or exadigit-ov in your research, please cite our work:

    @inproceedings{inproceedings,
      title={A Digital Twin Framework for Liquid-cooled Supercomputers as Demonstrated at Exascale}, 
      author={Brewer, Wesley and Maiterth, Matthias and Kumar, Vineet and Wojda, Rafal and Bouknight, Sedrick and Hines, Jesse and Shin, Woong and Greenwood, Scott and Grant, David and Williams, Wesley and Wang, Feiyi},
      booktitle={SC24: International Conference for High Performance Computing, Networking, Storage and Analysis},
      pages={1--18},
      year={2024},
      organization={IEEE}
    }

    @misc{doecode_127899,
      title = {ExaDigiT/RAPS},
      author = {Brewer, Wesley and Maiterth, Matthias and Bouknight, Sedrick and Hines, Jesse and Webb, Tyler J.},
      doi = {10.11578/dc.20240627.4},
      url = {https://doi.org/10.11578/dc.20240627.4},
      howpublished = {[Computer Software] \url{https://doi.org/10.11578/dc.20240627.4}},
      year = {2024},
      month = {jun}
    }

Thank you for your support!
