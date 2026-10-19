import subprocess

for t in [3, 8, 19, 36]:
    cmd = ["ffmpeg", "-y", "-ss", str(t), "-i", "output/The American Revolution.mp4", "-frames:v", "1", f"output/rev_frame_{t}s.jpg"]
    subprocess.run(cmd, capture_output=True)

print("Extracted frames!")
