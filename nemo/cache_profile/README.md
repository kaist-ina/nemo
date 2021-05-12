### How to prepare the SR-integrated codec?
```
$NEMO_CODE_ROOT/nemo/cache_profile/script/setup.sh
```
* This builds the SR-integrated codec.
* The codec sources are available at $NEMO_CODE_ROOT/nemo/third_party/libvpx.

### How to generate the cache profile? 
```
$NEMO_CODE_ROOT/nemo/cache_profile/script/select_anchor_points.sh -g [gpu index] -c [content] -q [dnn quality] -i [input resolution] -o [output resolution] -a [algorithm]
(e.g., $NEMO_CODE_ROOT/nemo/cache_profile/script/select_anchor_frames.sh -g 0 -c product_review -q high -i 240 -o 1080 -a nemo)
```
* We provide three types of algorithm: `nemo` is our method, `uniform` & `random` selects anchor frames uniformly and randomly respectively.
* Currently, the SR-integrated codec only supports online inference at Qualcomm devices. So, the super-resoluted frames are prepared/saved in advance by Tensorflow.
* Cache profiles are saved at `$NEMO_DATA_ROOT/[content]/profile/[video name]/[DNN name]/*.profile`.
* Logs are saved at `$NEMO_DATA_ROOT/[content]/log/[video name]/[DNN name]/*.txt`.
* To understand the logs, please refer the `$NEMO_CODE_ROOT/nemo/cache_profile/anchor_point_selector.py`.

### How to analyze frame dependency & frame type? (Figure 5 in the paper)
```
$NEMO_CODE_ROOT/nemo/cache_profile/script/analyze_video.sh -g [gpu index] -c [content] -q [quality] -i [input  resolution] -o [output resolution] -a [algorithm]
(e.g., $NEMO_CODE_ROOT/nemo/cache_profile/script/analyze_video.sh -g 0 -c product_review -q high -i 240 -o 1080 -a nemo)
```
* Logs are saved at `$NEMO_DATA_ROOT/[content]/log/[video name]/[DNN name]/[algorithm type]*.txt`.
* To understand the logs, please refer the `$NEMO_CODE_ROOT/nemo/cache_profile/video_analyzer.py`.
