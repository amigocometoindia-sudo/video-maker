import urllib.request
from rembg import remove
from PIL import Image
urllib.request.urlretrieve("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/1200px-React-icon.svg.png", "test_img.png")
img = Image.open("test_img.png")
out_img = remove(img)
out_img.save("test_out.png", "PNG")
print("Done!")
