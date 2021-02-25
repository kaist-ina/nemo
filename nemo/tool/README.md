### How to downlaod a video? 
```
$NEMO_CODE_ROOT/nemo/tool/script/download_video.sh -c [content name]
(e.g.,  $NEMO_CODE_ROOT/nemo/tool/script/download_video.sh -c product_review)
```
* `content name`: It indicates a content catagory used in NEMO. (e.g., product review, how to, ...)
* The video's URL is provided at `$NEMO_CODE_ROOT/nemo/video/downloader.py`.
* The video is downloaded at `$NEMO_DATA_ROOT/video/`.

### How to encode a video?
```
$  $NEMO_CODE_ROOT/nemo/tool/script/encode_video.sh -c [content name]
(e.g.,  $NEMO_CODE_ROOT/nemo/tool/script/encode_video.sh -c product_review)
```
* The encoded videos (240-1080p) are stored at `$NEMO_DATA_ROOT/[content name]/video`. (e.g., `$NEMO_DATA_ROOT/product_review/video`)
