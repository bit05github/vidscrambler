import os
import subprocess
import ffmpeg
import pydub
import math
import random
from pydub import AudioSegment
from pathlib import Path

user_input = Path(input("Enter the path of your file: "))

if not user_input.exists():
    raise ValueError(f"file not at {user_input}")
with open(user_input, "r+") as iof:
    print("file found")
file_path = user_input
file_name = os.path.basename(file_path)
num_frames = int(subprocess.run(f'ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format default=nokey=1:noprint_wrappers=1 "{file_name}"', shell=True, capture_output=True, text=True).stdout.strip("\n"))

print(file_name)
subprocess.run('cd img & del * /S /Q & cd..', shell=True)
subprocess.run('cd m4a & del * /S /Q & cd..', shell=True)
os.makedirs("m4a", exist_ok=True)
subprocess.Popen('cd temp', shell=True)
os.makedirs("img", exist_ok=True)
subprocess.run(f'ffmpeg -i "{file_name}" -vn -acodec copy m4a/out.m4a', shell=True)
subprocess.run(f'ffmpeg -i "{file_name}" img/img%d.png', shell=True)
fps = subprocess.run(f'ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate "{file_name}"', shell=True, capture_output=True, text=True).stdout.strip("\n")
a,b = fps.split('/', 1)
a = float(a)
b = float(b)
fps = a/b
sound = AudioSegment.from_file("m4a\out.m4a")

segment_length = 1000/fps
total_length = (num_frames/fps) * 1000

num_segments = math.ceil(total_length / segment_length)

orderlist = []

for i in range(num_segments):
    start_time = i * segment_length
    end_time = min((i + 1) * segment_length, total_length)  # Ensure the last segment does not exceed total length
    segment = sound[start_time:end_time]

    # Generate the output file name
    output_file = f'm4a/{i}.wav'
    
    # Export the segment as an MP3 file
    segment.export(output_file, format="wav")
    print(f"Exported: {output_file}")

    orderlist.append(i)

shuffledorder = random.sample(orderlist, len(orderlist))
print(shuffledorder)
finalaudio = AudioSegment.from_file(f'm4a/{shuffledorder[0]}.wav', format="wav")
for i in range(1, num_segments):
    finalaudio = finalaudio + AudioSegment.from_file(f'm4a/{shuffledorder[i]}.wav', format="wav")
finalaudio.export("shuffled.mp3", format="mp3")

for i in range(num_frames):
    old = os.path.join("img", f'img{i+1}')
    new = os.path.join("img", f'shuffle{shuffledorder[i]}')
    os.rename(f'{os.path.dirname(os.path.realpath(__file__))}\\img\\img{i+1}.png', f'{os.path.dirname(os.path.realpath(__file__))}\\img\\shuffle{shuffledorder[i]}.png')
os.remove("shuffled_video.mp4")
subprocess.run(f'ffmpeg -framerate {fps} -i img/shuffle%01d.png -i shuffled.mp3 -c:v libx264 -pix_fmt yuv420p -r {fps} -shortest shuffled_video.mp4', shell=True)
os.remove("shuffled.mp3")