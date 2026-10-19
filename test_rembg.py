import sys
try:
    from rembg import remove
    from PIL import Image
    print("rembg is installed!")
except Exception as e:
    print("Failed:", e)
