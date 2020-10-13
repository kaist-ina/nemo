# NEMO: Enabling Neural-enhanced Video Streaming on Commodity Mobile Devices

This is an official Github repository for the MobiCom paper "NEMO: Enabling Neural-enhanced Video Streaming on Commodity Mobile Devices". This project is built upon Google libvpx, Android Exoplayer, and Qualcomm SNPE and consists of C/C++/Java/Python.
[[Project homepage]](http://ina.kaist.ac.kr/~nemo/) [[Paper]](https://dl.acm.org/doi/10.1145/3372224.3419185) [[Video]](https://www.youtube.com/watch?v=GPHlAUYCk18&ab_channel=ACMSIGMOBILEONLINE)

### Notice (10.13): We’re refactoring our code for public usage, refer to the timeline below.

## Prerequisites

Since Qualcomm SNPE v1.4.0 supports only legacy Tensorflow (<=1.14) and Python (3.5.0), two different environments must be set up for NEMO. We recommend using Anaconda to build separate virtual Python environments.

### `Environment 1`   
Python 3.5    
Tensorflow 1.14 (CPU) - Just for converting Tensorflow models to SNPE ones   
imageio   

### `Environment 2`   
Python 3.6   
Tensorflow 1.15    
imageio   

## Tested Environment

We’ve implemented/tested NEMO using the following server and mobile devices.

### `Server`   
OS: Ubuntu 16.04   
CPU: Intel Xeon E5-2620 v4   
RAM: 32G   
GPU: 2080Ti    

### `Mobile devices`: Currently, we only support Android devices with Qualcomm processors   
Samsung Galaxy S10+: Snapdragon 855   
Samsung Galaxy S6 Task: Snapdragon 855   
Samsung Galaxy Note8: Snapdragon 835   
Samsung A70: Snapdragon 675   
Xiaomi Mi9: Snapdragon 855   
Xiaomi Redmi Note7: Snapdragon 660   
LG GPad5: Snapdragon 821   

## Setup (TBU:10.18 Sun)

## Directory Structures

### `nemo`

This contains the source code of NEMO.

### `paper`

This contains additional material of the paper.

### `dataset`

This contains a dataset used in the paper including network traces and Youtube videos.

### `demo`

This contains several figures that clearly show the benefit of NEMO.

## Step 1: Set up environment (TBU:10.18 Sun)

## Step 2: Prepare video dataset (TBU:10.18 Sun)
 
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
