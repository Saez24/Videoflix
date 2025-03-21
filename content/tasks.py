import os
import subprocess
import shutil
from django.conf import settings

from content.models import Video

QUALITIES = {
    '1080p': ('1920x1080', '5000k'),
    '720p': ('1280x720', '2800k'),
    '480p': ('854x480', '1400k')
}

def exportJson():
    cmd = """
    python3 manage.py shell <<EOF
    from core.admin import VideoResource
    dataset = VideoResource().export()
    with open("exportJson.txt", "w") as f:
        f.write(dataset.json)
    EOF
    """
    subprocess.run(cmd, shell=True, text=True)

    

# def convert720p(source):
#     new_file_name = source[:-4] + '_720p.mp4' # Alter name + _720p.mp4
#     cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, new_file_name)
#     subprocess.run(cmd, capture_output=True)

def create_base_directory(source):
    base_name = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', os.path.basename(source).rsplit('.', 1)[0])
    os.makedirs(base_name, exist_ok=True)
    return base_name


def generate_ffmpeg_command(source, base_name, quality, resolution, bitrate):
    print(f'Generating command for {quality}')
    print(f'Base name: {base_name}')
    print(f'Resolution: {resolution}')
    print(f'Bitrate: {bitrate}')
    return [
        'ffmpeg',
        '-i', source,
        '-threads', '2',
        '-preset', 'fast',
        '-g', '48',
        '-sc_threshold', '0',
        '-map', '0:v',
        '-map', '0:a?',
        '-s:v', resolution,
        '-c:v', 'libx264',
        '-b:v', bitrate,
        '-c:a', 'aac',
        '-strict', '-2',
        '-f', 'hls',
        '-hls_time', '5',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', f'{base_name}/{quality}_%03d.ts',
        f'{base_name}/{quality}.m3u8'
    ]


def convert_to_hls(source, video_id):
    """
    Converts source file to HLS with multiple quality levels and saves files in corresponding folder.
    """
    print(f'Converting {source} to HLS')
    base_name = create_base_directory(source)
    
    try:
        for quality, (resolution, bitrate) in QUALITIES.items():
            cmd = generate_ffmpeg_command(source, base_name, quality, resolution, bitrate)
            subprocess.run(cmd, capture_output=True, text=True)

            video = Video.objects.get(id=video_id)
            video.hls_playlist = os.path.join(base_name, 'playlist.m3u8')
            video.save() 

            delete_mp4(source)

    except Exception as e:
        print(f'Error saving HLS playlist: {str(e)}')
        raise

def delete_mp4(source,):
    """
    This function deletes the mp4 file that is created for creating the HLS files.
    """
    if os.path.exists(source):
        os.remove(source)
        print(f'{source} deleted')
   