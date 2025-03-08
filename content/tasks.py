import os
import subprocess
from django.conf import settings

QUALITIES = {
    '1080p': ('1920x1080', '5000k'),
    '720p': ('1280x720', '2800k'),
    '480p': ('854x480', '1400k')
}

def exportJson():
    shell = [
        'python', 'manage.py', 'shell'
    ]
    imp = [
        'from', 'core.admin', 'import', 'VideoResource'
    ]
    data = [
        'dataset', '=', 'VideoResource().export()'
    ]
    action = [
        'print(dataset.json)'
        'dataset.json', '>', 'exportJson.txt'
    ]
    subprocess.run(shell)
    subprocess.run(imp)
    subprocess.run(data)
    subprocess.run(action)
    

# def convert720p(source):
#     new_file_name = source[:-4] + '_720p.mp4' # Alter name + _720p.mp4
#     cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, new_file_name)
#     subprocess.run(cmd, capture_output=True)

def create_base_directory(source):
    base_name = os.path.join(settings.MEDIA_ROOT, 'hls', os.path.basename(source).rsplit('.', 1)[0])
    os.makedirs(base_name, exist_ok=True)
    return base_name

def generate_ffmpeg_command(source, base_name, quality, resolution, bitrate):
    print(f'Generating command for {quality}')
    return [
        'ffmpeg',
        '-i', source,
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
        '-hls_time', '10',
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
    
    for quality, (resolution, bitrate) in QUALITIES.items():
        cmd = generate_ffmpeg_command(source, base_name, quality, resolution, bitrate)
        subprocess.run(cmd)    