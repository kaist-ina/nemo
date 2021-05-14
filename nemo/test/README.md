### How to setup?
```
$NEMO_CODE_ROOT/nemo/test/script/setup_local.sh 
```
* This builds the SR-integrated codec for mobiles.
```
$NEMO_CODE_ROOT/nemo/test/script/setup_device.sh -c [content name] -q [quality level] -r [input resolution] -a [algorithm] -d [device id]
(e.g., $NEMO_CODE_ROOT/nemo/test/script/setup_device.sh -c product_review -q high -r 240 -a nemo_0.5 -d [device id])
```
* This copies libvpx binary files, videos, DNNs, cache profiles to mobiles.

### How to measure the latency?
```
$NEMO_CODE_ROOT/nemo/test/script//measure_latency.sh -c [content name] -q [quality level] -r [input resolution] -a [algorithm] -d [device id]
(e.g., $NEMO_CODE_ROOT/nemo/test/script//measure_latency.sh -c product_review -q high -r 360 -a nemo_0.5 -d [device id])
```
* This measures the latencies of three methods: 1) decode w/o super-resolution, 2) per-frame super-resolution, 3) nemo
* The logs of 1) are saved at `$NEMO_DATA_ROOT/log/[video name]/[device id]/latency.txt`.
* The logs of 2) are saved at `$NEMO_DATA_ROOT/log/[video name]/[model name]/[device id]/latency.txt`.
* The logs of 3) are saved at `$NEMO_DATA_ROOT/log/[video name]/[algorithm name]/[device id]/latency.txt`.

### How to measure the quality?
```
$NEMO_CODE_ROOT/nemo/test/script/measure_quality.sh -g [gpu index] -c [content name] -q [quality level] -r [input resolution] -a [algorithm] 
(e.g., $NEMO_CODE_ROOT/nemo/test/script//measure_quality.sh -g 0 -c product_review -q high -r 360 -a nemo_0.5 -d [device id])
```
* This measures the qualities of three methods: 1) decode w/o super-resolution, 2) per-frame super-resolution, 3) nemo
* The logs of 1) are saved at `$NEMO_DATA_ROOT/log/[video name]/quality.txt`.
* The logs of 2) are saved at `$NEMO_DATA_ROOT/log/[video name]/[model name]/quality.txt`.
* The logs of 3) are saved at `$NEMO_DATA_ROOT/log/[video name]/[algorithm name]/quality.txt`.
