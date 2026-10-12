"""Confine generated pigment and produce round 29 outputs; one-time finalizer.

Requires record-28 wall.png and image-tool draft wall-v10.png. Re-running on
finished outputs fails the source hash assertion. No image dependency installed.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import zlib

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('thumbnail', root / 'gathering/make_thumbnail.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
old_path = root / 'artifacts/line-3/wall.png'
new_path = root / 'artifacts/line-3/wall-v10.png'
old = old_path.read_bytes()
previous = json.loads((root / 'dist/line-3/28.json').read_text())
old_hash = hashlib.sha256(old).hexdigest()
assert old_hash == previous['image'].rsplit('/', 1)[1]
w, h, ancestors = helper.png_rgb(old)
w2, h2, generated = helper.png_rgb(new_path.read_bytes())
assert (w, h) == (w2, h2) == (1254, 1254)
# Vacant rock to the right of the sieve and above the scroll. Keep only dark
# substantially new pigment. No generated background or ancestor is copied.
box = (965, 520, 1045, 661)
rows = [bytearray(row) for row in ancestors]
changed = 0
for y in range(box[1], box[3]):
    for x in range(box[0], box[2]):
        at = x*3
        before = ancestors[y][at:at+3]
        pigment = generated[y][at:at+3]
        r, g, b = pigment
        if r < 95 and g < 65 and b < 45 and sum(before)-sum(pigment) > 90:
            rows[y][at:at+3] = bytes(min(a,b) for a,b in zip(before,pigment))
            changed += 1
assert changed > 500, changed
outside = sum(rows[y][x*3:x*3+3] != ancestors[y][x*3:x*3+3]
              for y in range(h) for x in range(w)
              if not (box[0] <= x < box[2] and box[1] <= y < box[3]))
assert outside == 0

def chunk(tag, body):
    return struct.pack('>I', len(body))+tag+body+struct.pack('>I',zlib.crc32(tag+body))

png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w,h,8,2,0,0,0))
       + chunk(b'IDAT',zlib.compress(b''.join(b'\0'+bytes(row) for row in rows),9))
       + chunk(b'IEND',b''))
assert helper.png_rgb(png)[2] == [bytes(row) for row in rows]
new_path.write_bytes(png)
old_path.write_bytes(png)
jpg = helper.jpeg(helper.resize(w,h,rows))
assert len(jpg) < 100000
(root / 'dist/line-3/29.jpg').write_bytes(jpg)
sha = hashlib.sha256(png).hexdigest()
meaning = 'Two trails of charcoal seeds remind Pepe to count repeated provisions.'
record = {'name': 'The Repeated Seeds', 'image': 'https://api.imd.fun/artifacts/'+sha,
          'attributes': [{'trait_type': k, 'value': v} for k,v in [
              ('Cave','Base'),('Wall','Line 3'),('Number',29),
              ('Left behind','access-list-audit'),('Meaning',meaning),
              ('One thing','Offline EIP-1559 transaction decoding')]]}
(root / 'dist/line-3/29.json').write_text(json.dumps(record,indent=2)+'\n')
review = {
    'wall': {'paths':['artifacts/line-3/wall-v10.png','artifacts/line-3/wall.png'],
             'width':w,'height':h,'format':'PNG','mode':'RGB','bytes':len(png),'sha256':sha},
    'thumbnail': {'path':'dist/line-3/29.jpg','width':512,'height':512,
                  'format':'JPEG','bytes':len(jpg)},
    'preservation': {'inheritedSha256':old_hash,'editRectangleXYXY':list(box),
                     'changedPixels':changed,'changedPixelsOutsideRectangle':outside},
    'tests': {'newPassed':14,'inheritedPassed':64,'seededCostPartitions':100,
              'demoExitCode':0,'demoIsSynthetic':True,'demoDestination':'ZTO'},
    'visualReview': {'reviewed':False}, 'unmetVisualRequirements':['Visual review pending']}
(root / 'line-3/round-29-review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(review,indent=2))
