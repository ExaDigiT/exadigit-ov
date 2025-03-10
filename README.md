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