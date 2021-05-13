### How to train a DNN? 
```
$NEMO_CODE_ROOT/nemo/dnn/script/train_video.sh -g [gup index] -c [content name] -q [quality level] -i [input resolution] -o [output resolution]
(e.g., $NEMO_CODE_ROOT/nemo/dnn/script/train_video.sh -g 0 -c product_review -q high -i 240 -o 1080)
```
* `content name`: It indicates a content catagory used in NEMO. (e.g., product review, how to, ...)
* A DNN is saved at `$NEMO_DATA_ROOT/[content name]/checkpoint/[video name]/[dnn name]`. (e.g., `$NEMO_DATA_ROOT/product_review/checkpoint/240p_512kbps_s0_d300.webm/NEMO_S_B8_F32_S4_deconv/`)

### How to test a DNN?
```
$NEMO_CODE_ROOT/nemo/dnn/script/test_video.sh -g [gup index] -c [content name] -q [quality level] -i [input resolution] -o [output resolution]
(e.g., $NEMO_CODE_ROOT/nemo/dnn/script/test_video.sh -g 0 -c product_review -q high -i 240 -o 1080)
```
* This measures PSNR of frames that are recovered by bilinear interpolation and super-reoslution.
* Logs are saved at `$NEMO_DATA_ROOT/[content name]/result/[video name]/[dnn name]`. (e.g., `$NEMO_DATA_ROOT/product_review/result/240p_512kbps_s0_d300.webm/NEMO_S_B8_F32_S4_deconv/`) 

### How to convert a TF model to a SNPE version?
```
$NEMO_CODE_ROOT/nemo/dnn/script/convert_tf_to_snpe.sh -g [gup index] -c [content name] -q [quality level] -i [input resolution] -o [output resolution] 
(e.g., $NEMO_CODE_ROOT/nemo/dnn/script/convert_tf_to_snpe.sh -g 0 -c product_review -q high -i 240 -o 1080)
```
* This converts a TF checkpoint to a dlc format.
* A dlc is saved at `$NEMO_DATA_ROOT/[content name]/checkpoint/[video name]/[dnn name]`. (e.g., `$NEMO_DATA_ROOT/product_review/checkpoint/240p_512kbps_s0_d300.webm/NEMO_S_B8_F32_S4_deconv/`)

### How to test a SNPE model on Qualcomm devices?
```
$NEMO_CODE_ROOT/nemo/dnn/script/test_snpe.sh -g [gpu index] -c [content name] -q [quality level] -r [input resolution] -s [scale] -d [device id]
(e.g., $NEMO_CODE_ROOT/nemo/dnn/script/test_snpe.sh -g 0 -c product_review -q high -r 240 -s 4 -d [device id])
```
* `device id`: It indicates adb device ID, and you can get this by `adb devices`.
* Logs are saved at `$NEMO_DATA_ROOT/[content name]/log/[video name]/[dnn name]/snpe_random_benchmark/*`.
* To understand the logs, please refer [[Qualcomm SNPE documents]](https://developer.qualcomm.com/docs/snpe/usergroup10.html).
