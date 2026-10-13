"""Prepare feathered garbage mattes for native Fusion compositing.

This does not render the film. All picture assembly and rendering remain in Resolve.
The matte shapes follow the source motion and share each shot's native time map.
"""
from pathlib import Path
import json
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

P = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
A = P / 'analysis/r14-native'

shapes = {
    'S01': {
        'file': 'S01-reach-a01.mp4', 'frames': 124,
        'head': [(287, 161, 351, 224), (291, 186, 353, 247)],
        'polygons': [
            ([(305,207),(352,199),(369,237),(372,286),(324,293),(298,253)],
             [(309,237),(356,229),(370,267),(372,318),(319,325),(299,274)]),
            ([(314,222),(287,264),(237,291),(215,302),(205,321),(236,325),(285,288),(328,247)],
             [(313,248),(276,276),(232,287),(201,280),(188,286),(209,309),(244,309),(294,287),(331,268)]),
            ([(348,202),(380,177),(394,144),(401,121),(423,116),(441,138),(416,149),(405,186),(382,218),(354,232)],
             [(348,230),(390,225),(415,204),(416,179),(432,169),(448,190),(435,214),(405,242),(359,262)]),
            ([(324,276),(366,271),(414,346),(411,374),(394,409),(404,447),(341,449),(338,416),(326,418),(329,448),(275,448),(272,431),(288,411),(263,365),(261,336)],
             [(320,309),(367,305),(429,354),(427,379),(390,418),(406,449),(343,450),(337,423),(326,424),(328,449),(273,449),(272,433),(289,417),(255,375),(250,356)])
        ]
    },
    'S03': {
        'file': 'S03-ankle-accent-a01.mp4', 'frames': 70,
        'polygons': [
            ([(165,0),(313,0),(320,65),(413,204),(416,258),(371,355),(376,385),(401,425),(250,427),(240,389),(219,361),(211,397),(205,427),(77,427),(90,381),(99,351),(60,262),(48,202),(78,140)],
             [(165,0),(313,0),(320,65),(413,204),(416,258),(371,355),(376,385),(401,425),(250,427),(240,389),(219,361),(211,397),(205,427),(77,427),(90,381),(99,351),(60,262),(48,202),(78,140)])
        ]
    },
    'S04': {
        'file': 'S04-catch-point-a01.mp4', 'frames': 84,
        'polygons': [
            ([(0,421),(81,418),(216,312),(254,278),(263,238),(281,205),(292,179),(296,150),(315,147),(320,182),(345,171),(385,145),(405,143),(405,171),(374,192),(393,210),(389,232),(368,241),(347,269),(323,300),(285,321),(263,348),(186,453),(129,506),(48,530),(0,576)],
             [(0,443),(72,440),(158,351),(187,322),(181,295),(160,261),(154,242),(170,203),(162,169),(181,156),(196,184),(205,166),(212,140),(230,139),(239,160),(220,184),(247,180),(261,193),(251,211),(246,259),(246,299),(235,333),(208,359),(161,423),(121,484),(116,530),(40,556),(0,576)])
        ]
    }
}

def source_time(shot, frame):
    if shot == 'S01': return frame
    if shot == 'S04': return frame * 123 / 83
    if frame <= 27: return frame * 55 / 27
    if frame <= 61: return 55 + (frame - 27) * 55 / 34
    return 110 + (frame - 61) * 13 / 8

def normalized_outline(points):
    points = np.array(points, dtype=float)
    closed = np.vstack([points, points[0]])
    distances = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(closed, axis=0), axis=1))])
    positions = np.linspace(0, distances[-1], 128, endpoint=False)
    return np.stack([np.interp(positions, distances, closed[:,axis]) for axis in [0,1]], axis=1)

for spec in shapes.values():
    spec['polygons'] = [(normalized_outline(a),normalized_outline(b)) for a,b in spec['polygons']]

records = []
for shot, spec in shapes.items():
    out = A / f'{shot}-matte-sequence-a03'
    out.mkdir(exist_ok=True)
    sheet = Image.new('RGB', (1536, 864))
    inspected = np.linspace(0, spec['frames']-1, 8, dtype=int).tolist()
    for frame in range(spec['frames']):
        source_frame = source_time(shot, frame)
        fraction = source_frame / 123
        matte = Image.new('L', (1024,576), 0)
        draw = ImageDraw.Draw(matte)
        if 'head' in spec:
            head = np.array(spec['head'][0])*(1-fraction)+np.array(spec['head'][1])*fraction
            draw.ellipse(tuple(head), fill=255)
        for start,end in spec['polygons']:
            points = np.array(start)*(1-fraction)+np.array(end)*fraction
            draw.polygon([tuple(p) for p in points], fill=255)
        matte = matte.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(3))
        matte.resize((1920,1080),Image.Resampling.LANCZOS).save(out/f'{shot}-matte-{frame:04}.png')
        if frame in inspected:
            raw = subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(P/'originals'/spec['file']),'-vf',f'select=eq(n\\,{round(source_frame)})','-frames:v','1','-f','image2pipe','-vcodec','png','-'],check=True,capture_output=True).stdout
            import io
            image = Image.open(io.BytesIO(raw)).convert('RGB')
            preview = Image.fromarray((np.array(image).astype(np.float64)*np.array(matte)[:,:,None]/255).astype(np.uint8))
            preview.thumbnail((512,288))
            k=inspected.index(frame)
            sheet.paste(preview,((k%3)*512,(k//3)*288))
            ImageDraw.Draw(sheet).text(((k%3)*512+8,(k//3)*288+8),f'output {frame} / source {source_frame:.1f}',fill='white')
    sheet.save(A/f'{shot}-masked-motion-a03-sheet.png')
    records.append({'shot':shot,'frames':spec['frames'],'first_matte':str(out/f'{shot}-matte-0000.png'),'source_time_anchors':[[f,source_time(shot,f)] for f in inspected],'feather_source_pixels':3,'dilate_source_pixels':12})
(A/'motion-mattes-a03.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records))
