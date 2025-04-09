import os
import subprocess
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

def create_base_directory(source):
    base_name = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', os.path.basename(source).rsplit('.', 1)[0])
    os.makedirs(base_name, exist_ok=True)
    return base_name

def create_master_playlist(base_name, qualities):
    """
    Erstellt eine Master-Playlist-Datei, die alle Qualitäten enthält.
    """
    master_playlist_path = os.path.join('playlist.m3u8')
    with open(master_playlist_path, 'w') as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")

        for quality, (resolution, bitrate) in qualities.items():
            bandwidth = int(bitrate[:-1]) * 1000  # Konvertiere z. B. '5000k' zu 5000000
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution}\n")
            f.write(f"{quality}.m3u8\n")

    print(f'Master playlist created at {master_playlist_path}')
    return master_playlist_path

def generate_ffmpeg_command(source, base_name, quality, resolution, bitrate):
    # Vollständiger Pfad zu ffmpeg (falls erforderlich)
    ffmpeg_path = '/usr/bin/ffmpeg'  # Ändern Sie dies, falls ffmpeg an einem anderen Ort installiert ist

    cmd = [
        ffmpeg_path,
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
        '-hls_time', '5',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', f'{base_name}/{quality}_%03d.ts',
        f'{base_name}/{quality}.m3u8'
    ]
    return cmd

def convert_to_hls(source, video_id):
    """
    Converts source file to HLS with multiple quality levels and saves files in corresponding folder.
    """
    print(f'Converting {source} to HLS')
    base_name = create_base_directory(source)
    
    try:
        for quality, (resolution, bitrate) in QUALITIES.items():
            cmd = generate_ffmpeg_command(source, base_name, quality, resolution, bitrate)
            print(f'Running command: {" ".join(cmd)}')  # Zur Debugging-Zwecken den Befehl als String anzeigen

            # Führen Sie den Befehl aus und erfassen Sie die Ausgabe
            result = subprocess.run(cmd, shell=False, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Ausgabe und Fehlermeldungen anzeigen
            print(f'STDOUT: {result.stdout}')
            print(f'STDERR: {result.stderr}')

            print(f'Finished converting {source} to {quality} HLS')

            master_playlist_path = create_master_playlist(base_name, QUALITIES)

            # Speichern Sie die HLS-Playlist in der Datenbank
            video = Video.objects.get(id=video_id)
            video.hls_playlist = os.path.join('media', 'videos', 'hls', os.path.basename(master_playlist_path))  # Beispiel: 'media/videos/hls/playlist.m3u8'
            video.save()

        # Lösche die ursprüngliche MP4-Datei
        delete_mp4(source)

    except subprocess.CalledProcessError as e:
        print(f'Error during conversion: {e.stderr}')
        raise
    except Exception as e:
        print(f'Error saving HLS playlist: {str(e)}')
        raise

def delete_mp4(source):
    """
    This function deletes the mp4 file that is created for creating the HLS files.
    """
    if os.path.exists(source):
        os.remove(source)
        print(f'{source} deleted')