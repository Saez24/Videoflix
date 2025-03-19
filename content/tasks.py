import os
import subprocess
from django.conf import settings

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
    subprocess.run(cmd, shell=True, text=True, check=True)

def create_base_directory(source):
    base_name = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', os.path.basename(source).rsplit('.', 1)[0])
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
        '-b:a', '128k',  # Falls Audio vorhanden ist
        '-f', 'hls',
        '-hls_time', '10',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', os.path.join(base_name, f'{quality}_%03d.ts'),
        os.path.join(base_name, f'{quality}.m3u8')
    ]

def convert_to_hls(source, video_id):
    """
    Converts source file to HLS with multiple quality levels and saves files in corresponding folder.
    """
    print(f'Converting {source} to HLS')
    base_name = create_base_directory(source)
    
    for quality, (resolution, bitrate) in QUALITIES.items():
        cmd = generate_ffmpeg_command(source, base_name, quality, resolution, bitrate)
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ Conversion for {quality} completed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error converting {quality}: {e.stderr.decode()}")
