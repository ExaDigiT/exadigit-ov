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
1. Follow instructions to install ExaDigiT Simulation Server here: https://code.ornl.gov/exadigit/simulationserver
2. Run the server locally, it will be hosted on http:localhost:8080


## Usage
1. From the app, open the file `test.usd` or `stress-test.usd` in the `test-files` directory.

   *_(Note: `stress-test.usd` may take a while to load.)_*
2. Using the Data Loader extension window, press the **"Refresh Scene"** button to dynamically assign `xnames` and
   create a lookup map for your data center scene.
3. Also in the Data Loader extension window, press the **"Propagate Data"** button to send some test data to each data center
   component in the scene. You can then click on a prim in-scene, and an editor utility widget will pop up detailing its attributes.

   *_(Depending on whether you're using `test.usd` or `stress-test.usd`, you can comment or uncomment lines 116/119 in
   `exadigit-ov\source\extensions\exadigit.data_loader\exadigit\data_loader\extension.py` to generate the appropriate test data.)_*

## Citation

If you use ExaDigiT or exadigit-ov in your research, please cite our work:

    @inproceedings{exadigitUE5,
        author={Maiterth, Matthias and Brewer, Wes and De Wet, Dane and Greenwood, Scott and Kumar, Vineet and Hines, Jesse and Bouknight, Sedrick and Wang, Zhe and Dykes, Tim and Wang, Feiyi},
        booktitle={2024 IEEE Visualization and Visual Analytics (VIS)},
        title={Visualizing an Exascale Data Center Digital Twin: Considerations, Challenges and Opportunities},
        year={2024},
        pages={21-25},
        addreess={St. Pete Beach, FL},
        publisher={IEEE},
        doi={10.1109/VIS55277.2024.00012}
    }

    @inproceedings{exadigit,
      title={ExaDigiT: A Framework for Digital Twins of Liquid-cooled Supercomputers Demonstrating Comprehensive Modeling of Workloads, Power, and Cooling},
      author={Brewer, W. and Dash, S. and Maiterth, S. and Greenwood, S. and Shin, W. and Grant, D. and others},
      booktitle={SC24: International Conference for High Performance Computing, Networking, Storage and Analysis},
      pages={1--18},
      year={2024},
      publisher={IEEE}
    }

Thank you for your support!
