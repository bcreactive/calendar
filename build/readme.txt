use at your own risk!

apk compiled using buildozer
i used the google colab notebook to compile the apk from my main.py and save_file.json files:


when !buildozer init is executed, you need to edit the generated buildozer.spec file (or use the spec in build folder):

include json and mp3 files and fix screen orientation:


[app]

source.include_exts = py,png,jpg,kv,atlas,json,mp3

orientation = portrait, landscape



This are the commands I used to set up the colab notebook to compile the apk successfully:
------------------------------------------------------------------------------------------

!pip install buildozer

!pip install cython==0.29.19

!sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev

!sudo apt-get install -y \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good

!sudo apt-get install build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev zlib1g-dev libssl-dev openssl libgdbm-dev libgdbm-compat-dev liblzma-dev libreadline-dev libncursesw5-dev libffi-dev uuid-dev libffi6

!sudo apt-get install libffi-dev

!buildozer init

!cd /content/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius && /content/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/hostpython3/desktop/hostpython3/native-build/python3 setup.py build_ext -v

!pip install -U cython 

!apt update
!apt install openjdk-17-jdk

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"

!sudo apt-get update
!sudo apt-get install libtool

!buildozer -v android debug

!buildozer android clean