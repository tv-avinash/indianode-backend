#!/bin/bash

ffmpeg -y \
-f lavfi -i color=c=black:s=1920x1080:d=30 \
-f lavfi -i "sine=frequency=70:duration=30" \
-filter_complex "\
[0:v]\
drawtext=text='INDIANODE':fontcolor=white:fontsize=140:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,4)',\
drawtext=text='Type anything and get music instantly':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,4,8)',\
drawtext=text='Add image and auto soundtrack':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,8,12)',\
drawtext=text='Upload voice or vlog get bgm':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,12,16)',\
drawtext=text='Any genre Classical EDM Fusion':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,16,22)',\
drawtext=text='indianode.com':fontcolor=magenta:fontsize=100:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,22,30)'\
[v]" \
-map "[v]" -map 1:a \
-c:v libx264 -preset medium -pix_fmt yuv420p -c:a aac \
-shortest indianode_promo_30s.mp4

