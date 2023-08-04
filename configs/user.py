# proxy to connect outside
# NOTE refactoring vgmdb with requests has not been completed
# for now, you can only use http proxy, i.e. no socks5
PROXY : str = ''
# PROXY : str = 'http://127.0.0.1:7890'

# you can add necessary paths here so making AC able to locate executables
USER_PATHS : list[str] = [
    # add you paths below
    '%USERPROFILE%/scoop/shims',
    'C:/Program Files/WinRAR',
    'C:/Program Files (x86)/WinRAR',
    'C:/Program Files/7-Zip',
]

FFMPEG_PATH : str = ''
RAR_PATH : str = ''

# whether to generate an audio digest for each input m2ts in VNA
# this improves the accuracy of file matching in VND
ENABLE_VNA_AUDIO_SAMPLES : bool = True

# whether to use VGMDB/MB/FREEDB in MusicRechecker
ENABLE_VGMDB : bool = True
ENABLE_MUSICBREAINZ : bool = False
ENABLE_FREEDB : bool = False

# you can optionally turn off VNA's file checking
# this will make VNA much faster to generate the naming proposal (VND.csv)
ENABLE_FILE_CHECKING_IN_VNA : bool = True

# the temporary directory name for ScansRechecker's hardlink functionality
# it is better a dirname, don't use an absolute path
TEMP_DIRNAME_HARDLINK : str = '@AC-Temp'

# this is the default temp decompress dir to check the fonts archive
# it can be a relative path or absolute path
# if will be placed
TEMP_DIRPATH_DECOMPRESS : str = '$TEMP'

# if multiprocessing is validated, then use this number of workers for IO-intensive jobs e.g. CRC32
# the default value of 8 should be able to max out PCIe 4.0 x4 SSDs
# it will be automatically lower to not exceed the number of CPU threads
MAX_NUM_IO_WORKERS : int = 8

# this is used to determine the number of multiprocessing-workers for CPU/RAM-intensive tasks
# the number is calculated based on your available RAM, not the total RAM
MIN_RAM_PER_WORKER : int = 10 # this unit is GiB

# whether to still enable multi-processing when ssd checker failed
# such case happens when you're using some RAMDISK on Windows e.g. ImDisk
# ssd checker cannot lookup the disk type of such SCSI devices
ENABLED_MULTI_PROC_IF_NOT_SURE : bool = False



#* advanced user config ------------------------------------------------------------------------------------------------

# if the video has a simple crop from 1080p like to 1072p, now we still mark it as 1080p
# here, if the actual height >= this value, we mark it as 1080p
MIN_VID_HEIGHT_TO_STILL_LABEL_AS_1080 : int = 900



# videos differ within this threshold is considered as the same
# commonly the minimal fps is 23.976 (~42ms per frame)
# so we allow 50ms, allowing truncating the last frame
SAME_DURATION_THRESHOLD_MS :int  = 50

# the max allowed duration difference between tracks, e.g. video vs audio
# this value should be more loose than `SAME_DURATION_THRESHOLD_MS`
MAX_TRACK_DURATION_DIFF_MS : int = 200

# the duration between the last chapter and end of *video* must exceed this time
MAX_DISTANCE_FROM_LAST_CHAPTER_VIDEO_END : int = 3000


# if the number audio exceeds this number within a disc dir, we consider the audio is of track-split disc
# it's very rare that we have many track-joint discs for a single ALBUM
# such case is only practically seen in the complete soundtrack album of some game series with decades of history
# setting this value too low will increase instability
NUM_AUD_TO_CONSIDER_AS_SPLIT_TRACK_DISC : int = 5

# warn the user of image files smaller than this size (unit: Bytes)
SMALL_IMAGE_FILE_SIZE = 1024

# normally, we consider A3 (297x420mm) is the largest size that a regular home scanner can do
# so the max possible length under 600dpi is 420/25.4*600=9921px
# so if any side exceeds 10000px, tell the user to consider downsampling from the 'useless' 1200dpi
LARGE_SCANS_THRESHOLD = 10000

# warn that user if the cover art is unnecessarily large
# NOTE digital cover art rarely exceeds ~3000px
NORMAL_COVER_ART_LENGTH = 4000 # 4000px
NORMAL_COVER_ART_FILESIZE = 10 * 1024 * 1024 # 10MiB

ASS_LANG_THRESHOLD : int = 5




USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

LANGUAGE = 'en-GB'

VNA_DEFAULT_CONFIG = {
    'csv': True,
    'yaml': False,
    'json': False,
}


# this is the start point and length (both in second) used to detect the offset between two audio tracks
# *change them accordingly if you want to detect the offset from other interval
CHK_OFFSET_STA : int = 0
CHK_OFFSET_LEN : int = 30
assert CHK_OFFSET_LEN > 0
# we know (a²+b²)/ab>=2 and ==2 only if a==b, but if <=`XCORR_RATIO` we still think a==b
XCORR_RATIO : int = 4
# if the average difference on samples is below this value, then we think 2 audio are the same
# note the difference is defined in integer value of 16-bit PCM, i.e. the max/min value of audio is 32767/-32768
# 1 for 16-bit integer PCM == 1.5e-6 for floating PCM (2**16*1.5e-5=0.98)
MAX_DIFF_MEAN : int = 1



# this is the show name that will be applied when the program didn't correctly catch your mistake of forgetting filling any showname for VND. This should never appear on your hard disk - but if you see it, please fill a bug report.
FALLBACK_SHOWNAME = '1145141919810'


#* don't touch below --------------------------------------------------------------------------------------------------

if MIN_VID_HEIGHT_TO_STILL_LABEL_AS_1080 > 1080:
    MIN_VID_HEIGHT_TO_STILL_LABEL_AS_1080 = 1080


import psutil
cpu, ram = psutil.cpu_count(logical=False), psutil.virtual_memory().total // (1024**3)
NUM_IO_JOBS = min(cpu, MAX_NUM_IO_WORKERS)
NUM_CPU_JOBS = min(cpu, max(ram // (MIN_RAM_PER_WORKER), 1))
del psutil, cpu, ram


if TEMP_DIRNAME_HARDLINK:
    from pathlib import Path
    TEMP_DIR_PATH = Path(TEMP_DIRNAME_HARDLINK)
    del Path
else:
    TEMP_DIR_PATH = None


import os, pathlib
if TEMP_DIRNAME_HARDLINK:
    TEMP_DIR_HARDLINK = pathlib.Path(os.path.expandvars(TEMP_DIRNAME_HARDLINK))
else:
    TEMP_DIR_HARDLINK = pathlib.Path('@AC-TEMP')
del os, pathlib, TEMP_DIRNAME_HARDLINK


import os, pathlib
if TEMP_DIRPATH_DECOMPRESS:
    TEMP_DIR_DECOMPRESS = pathlib.Path(os.path.expandvars(TEMP_DIRPATH_DECOMPRESS))
else:
    TEMP_DIR_DECOMPRESS = pathlib.Path(os.path.expandvars('$TEMP'))
del os, pathlib, TEMP_DIRPATH_DECOMPRESS


if not LANGUAGE:
    import locale
    LANGUAGE = locale.getdefaultlocale()[LANGUAGE]
    del locale


if PROXY:
    import os
    os.environ['HTTP_PROXY'] = PROXY
    os.environ['HTTPS_PROXY'] = PROXY
    os.environ['SOCKS_PROXY'] = PROXY
    del os
