"""Converts a TGA screenshot to a PNG at most 1600 px wide (run with Blender: blender --background --python tools/tga2png.py -- in.tga out.png). Prints the source size."""
import bpy, sys
src, dst = sys.argv[-2], sys.argv[-1]
img = bpy.data.images.load(src)
w, h = img.size
print("SIZE", w, h)
if w > 1600:
    s = 1600.0 / w
    img.scale(int(w * s), int(h * s))
img.file_format = 'PNG'
img.filepath_raw = dst
img.save()
