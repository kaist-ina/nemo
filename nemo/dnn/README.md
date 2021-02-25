### How to train a DNN? 
`$  $NEMO_CODE_ROOT/nemo/dnn/script/train_video.sh -g [gup index] -c [content name] -q [quality level] -i [input resolution] -o [output resolution]`  
e.g., `$ $NEMO_CODE_ROOT/nemo/dnn/script/train_video.sh -g 0 -c product_review -q high -i 240 -o 1080`
* `content name`: It indicates a content catagory used in NEMO. (e.g., product review, how to, ...)
* The DNN is saved at `$NEMO_DATA_ROOT/[content name]/checkpoint/[video name]/[dnn name]`. (e.g., `$NEMO_DATA_ROOT/product_review/checkpoint/240p_512kbps_s0_d300.webm/NEMO_S_B8_F32_S4_deconv/`)

### How to test a DNN?
`$  $NEMO_CODE_ROOT/nemo/dnn/script/test_video.sh -g [gup index] -c [content name] -q [quality level] -i [input resolution] -o [output resolution]`  
e.g., `$ $NEMO_CODE_ROOT/nemo/dnn/script/test_video.sh -g 0 -c product_review -q high -i 240 -o 1080`
* This measures PSNR of frames that are recovered by bilinear interpolation and super-reoslution.
* The result is saved at `$NEMO_DATA_ROOT/[content name]/result/[video name]/[dnn name]`. (e.g., `$NEMO_DATA_ROOT/product_review/result/240p_512kbps_s0_d300.webm/NEMO_S_B8_F32_S4_deconv/`) 

### How to convert a TF model to a SNPE version?
`$  $NEMO_CODE_ROOT/nemo/dnn/script/convert_tf_to_snpe.sh -g [gup index] -c [content name] -q [quality level] -i [input resolution] -o [output resolution]`  
e.g., `$ $NEMO_CODE_ROOT/nemo/dnn/script/convert_tf_to_snpe.sh -g 0 -c product_review -q high -i 240 -o 1080`
* This converts a TF checkpoint to a dlc format.
* The dlc is saved at `$NEMO_DATA_ROOT/[content name]/checkpoint/[video name]/[dnn name]`. (e.g., `$NEMO_DATA_ROOT/product_review/checkpoint/240p_512kbps_s0_d300.webm/NEMO_S_B8_F32_S4_deconv/`)
