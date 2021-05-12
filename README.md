# NEMO (MobiCom'20)

This is an official Github repository for the MobiCom paper "NEMO: Enabling Neural-enhanced Video Streaming on Commodity Mobile Devices". This project is built upon Google libvpx, Android Exoplayer, and Qualcomm SNPE and consists of C/C++/Java/Python.   
[[Project homepage]](http://ina.kaist.ac.kr/~nemo/) [[Paper]](https://dl.acm.org/doi/10.1145/3372224.3419185) [[Video]](https://www.youtube.com/watch?v=GPHlAUYCk18&ab_channel=ACMSIGMOBILEONLINE)

If you use our work for research, please cite it.
```
@inproceedings{yeo2020nemo,
  title={NEMO: enabling neural-enhanced video streaming on commodity mobile devices},
  author={Yeo, Hyunho and Chong, Chan Ju and Jung, Youngmok and Ye, Juncheol and Han, Dongsu},
  booktitle={Proceedings of the 26th Annual International Conference on Mobile Computing and Networking},
  pages={1--14},
  year={2020}
}
```
Lastly, NEMO is currently protected under the patent and is retricted to be used for the commercial usage.  
* `BY-NC-SA` – [Attribution-NonCommercial-ShareAlike](https://github.com/idleberg/Creative-Commons-Markdown/blob/master/4.0/by-nc-sa.markdown)

## Project structure
```
./nemo
├── video                  # Python: Video downloader/encoder
├── dnn                    # Python: DNN trainer/converter
├── cache_profile          # Python: Anchor point selector
├── player                 # Java, C/C++: Android video player built upon Exoplayer and the SR-integrated codec
./third_party
├── libvpx                 # C/C++: SR-integrated codec
```

## Prerequisites

* OS: Ubuntu 16.04 or higher versions
* HW: NVIDIA GPU
* Docker: https://docs.docker.com/install/
* NVIDIA docker: https://github.com/NVIDIA/nvidia-docker

## Guide
We provide a step-by-step guide with a single video (which content is product review).  
All the folloiwing commands must be executed inside the docker. 

### 1. Setup
* Clone the NEMO docker repository
```
git clone https://github.com/chaos5958/nemo-docker.git
```
* Build the docker image 
```
cd ${HOME}/nemo-docker
./build.sh
```
* Run & Attach to the docker
```
cd ${HOME}/nemo-docker
./run.sh
```
* Clone the NEMO main repository
```
git clone --recurse-submodules https://github.com/kaist-ina/nemo-main.git ${NEMO_CODE_ROOT}
```

### 2. Prepare videos

* Download a Youtube video
```
$NEMO_CODE_ROOT/nemo/tool/script/download_video.sh -c product_review
```

* Encode the video 
```
$NEMO_CODE_ROOT/nemo/tool/script/encode_video.sh -c product_review
```
[Details are described in this file.](nemo/tool/README.md)

### 3. Prepare DNNs

* Train a DNN
```
$NEMO_CODE_ROOT/nemo/dnn/script/train_video.sh -g 0 -c product_review -q high -i 240 -o 1080
```

* Convert the TF model to the Qualcomm SNPE dlc
```
$NEMO_CODE_ROOT/nemo/dnn/script/convert_tf_to_snpe.sh -g 0 -c product_review -q high -i 240 -o 1080
```
[Details are described in this file.](nemo/dnn/README.md)

### 4. Generate a cache profile 

* Build the SR-integrated codec
```
$NEMO_CODE_ROOT/nemo/cache_profile/script/setup.sh
```

* Generate the cache profile using the codec
```
$NEMO_CODE_ROOT/nemo/cache_profile/script/select_anchor_points.sh -g 0 -c product_review -q high -i 240 -o 1080 -a nemo
```

* (Optional) Analyze frame dependencies & frame types
```
$NEMO_CODE_ROOT/nemo/cache_profile/script/analyze_video.sh -g 0 -c product_review -q high -i 240 -o 1080 -a nemo
```
[Details are described in this file.](nemo/cache_profile/README.md)

### 5. Benchmark NEMO vs. baselines (TBU)

### 6. Play NEMO in Android smartphones (TBU)

## FAQ (TBU)
