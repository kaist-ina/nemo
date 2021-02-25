# NEMO: Enabling Neural-enhanced Video Streaming on Commodity Mobile Devices

This is an official Github repository for the MobiCom paper "NEMO: Enabling Neural-enhanced Video Streaming on Commodity Mobile Devices". This project is built upon Google libvpx, Android Exoplayer, and Qualcomm SNPE and consists of C/C++/Java/Python.   
[[Project homepage]](http://ina.kaist.ac.kr/~nemo/) [[Paper]](https://dl.acm.org/doi/10.1145/3372224.3419185) [[Video]](https://www.youtube.com/watch?v=GPHlAUYCk18&ab_channel=ACMSIGMOBILEONLINE)

## Prerequisites

* OS: Ubuntu 16.04 or higher versions
* HW: NVIDIA GPU
* Docker: https://docs.docker.com/install/
* NVIDIA docker: https://github.com/NVIDIA/nvidia-docker

## Guide
We provide a step-by-step guide with a single video (which content is product review).  
All the folloiwing commands must be executed inside the docker. 

## 1. Setup

* Build a docker image (based on the Tensorflow Docker)
```
mkdir ${HOME}/nemo-docker && cd ${HOME}/docker
wget https://gist.githubusercontent.com/chaos5958/81267beccd06a38c83e661db6f1c3f34/raw/000baf071e418d0c7ddd9edbd137fa4fa9503279/Dockerfile
sudo docker build -t nemo .
```
* Run a docker image 
```
wget https://gist.githubusercontent.com/chaos5958/1be24ddcd3c15a5fc2015d15e8c44ad4/raw/141ecaa1d54eff0e3bdc04206aa3304cae2c604c/run_nemo_docker.sh
sudo ./run_nemo_docker.sh
```

## 2. Download/Encode a video

* Download a Youtube video
```
$NEMO_CODE_ROOT/nemo/video/script/downloader.sh -c product_review
```

* Encode the video 
```
$NEMO_CODE_ROOT/nemo/video/script/encoder.sh -c product_review
```

[Details are described in this file.](nemo/video/README.md)




### `Mobile devices`: Currently, we only support Android devices with Qualcomm processors   
* Samsung Galaxy S10+: Snapdragon 855   
* Samsung Galaxy S6 Task: Snapdragon 855   
* Samsung Galaxy Note8: Snapdragon 835   
* Samsung A70: Snapdragon 675   
* Xiaomi Mi9: Snapdragon 855   
* Xiaomi Redmi Note7: Snapdragon 660   
* LG GPad5: Snapdragon 821   

## Directory Structures

### `nemo`

This contains the source code of NEMO.

### `paper`

This contains additional material of the paper.

### `dataset`

This contains a dataset used in the paper including network traces and Youtube videos.

### `demo`

This contains several figures that clearly show the benefit of NEMO.

## Step 1: Set up environment (TBU:10.25 Sun)

## Step 2: Prepare video dataset (TBU:10.25 Sun)
 
## Step 3: Train/Validate a super-resolution DNN (TBU:10.25 Sun)

## Step 4: Generate a cache profile (TBU:10.11.01 Sun)

## Step 5: Execute on Android (TBU: 11.08, Sun)

## Limitations (TBU: 11.15, Sun)

## Tips: Extend libvpx (TBU: 11.15, Sun)

## Tips: Extend Exoplayer (TBU: 11.22, Sun)

## Tips: Support Other Platforms (TBU: 11.22, Sun)

## License

* `BY-NC-SA` – [Attribution-NonCommercial-ShareAlike](https://github.com/idleberg/Creative-Commons-Markdown/blob/master/4.0/by-nc-sa.markdown)

NEMO is currently protected under the patent and is retricted to be used for the commercial usage.
