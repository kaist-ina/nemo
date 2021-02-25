### How to downlaod and encode videos? 

1. Download a video using youtube-dl
```
$  $NEMO_CODE_ROOT/nemo/video/script/downloader.sh -c [content name]
```
* `content name`: It indicates a content catagory used in NEMO (e.g., product review, how to, ...)
* The video's URL is provided at `$NEMO_CODE_ROOT/nemo/video/downloader.py`
* The video is downloaded at `$NEMO_DATA_ROOT/video/`

2. Encode the video using ffmpeg 
```
$  $NEMO_CODE_ROOT/nemovideo/script/encoder.sh -c [content name]
```
* The encoded videos (240-1080p) are stored at `$NEMO_DATA_ROOT/[content name]/video`
