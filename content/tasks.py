import subprocess

def convert720p(source):
    new_file_name = source[:-4] + '_720p.mp4' # Alter name + _720p.mp4
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, new_file_name)
    subprocess.run(cmd, capture_output=True)