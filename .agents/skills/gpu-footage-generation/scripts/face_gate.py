"""Face gate for restyled anchors (tools venv: insightface buffalo_l, opencv, numpy).

usage: face_gate.py '[["B1","anchor.png","source_frame.png"], ...]' '{"hero":["indep_ref.png"]}' sheet.jpg
For each pair, faces are matched by position; the sheet shows source | anchor crops. "structure" = ArcFace cosine of the anchor
face vs the same source frame's face; "identity" = vs independent reference close-ups. Calibrate with a real-vs-real pair of the
same actor first (Nuvvantene hero: 0.39 with sunglasses). ArcFace under-reads cel-shaded faces, so the side-by-side sheet is the
deciding check and the numbers are supporting evidence. Re-run on mid/end frames of motion to catch drift."""
import sys, json, cv2, numpy as np
from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"]); app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.25)
pairs = json.loads(sys.argv[1]); refs = json.loads(sys.argv[2]); out = sys.argv[3]
def emb(img):
    return sorted(app.get(img), key=lambda f: -(f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
ref_e = {k: [emb(cv2.imread(p))[0].normed_embedding for p in v if emb(cv2.imread(p))] for k, v in refs.items()}
tiles, report = [], []
for name, anchor, source in pairs:
    A = cv2.imread(anchor); S = cv2.resize(cv2.imread(source), (A.shape[1], A.shape[0]))
    fa, fs = emb(A), emb(S)
    for f in fa[:2]:
        cx = (f.bbox[0]+f.bbox[2])/2; cy = (f.bbox[1]+f.bbox[3])/2
        g = min(fs, key=lambda q: abs((q.bbox[0]+q.bbox[2])/2-cx)+abs((q.bbox[1]+q.bbox[3])/2-cy)) if fs else None
        x0, y0, x1, y1 = [int(v) for v in f.bbox]; pad = int(0.35*(x1-x0))
        box = (max(0,x0-pad), max(0,y0-pad), min(A.shape[1],x1+pad), min(A.shape[0],y1+pad))
        ca = cv2.resize(A[box[1]:box[3], box[0]:box[2]], (256, 256)); cs = cv2.resize(S[box[1]:box[3], box[0]:box[2]], (256, 256))
        struct = float(np.dot(f.normed_embedding, g.normed_embedding)) if g is not None else None
        ident = {k: round(max(float(np.dot(f.normed_embedding, e)) for e in v), 3) for k, v in ref_e.items() if v}
        report.append({"anchor": name, "face_box": box, "structure_vs_source_frame": None if struct is None else round(struct, 3), "identity_vs_refs": ident})
        t = np.hstack([cs, ca]); cv2.putText(t, f"{name} struct {struct:.2f}" if struct is not None else name, (6, 20), 0, 0.55, (0,255,255), 2); tiles.append(t)
rows = [np.hstack(tiles[i:i+3] + [np.zeros_like(tiles[0])]*(3-len(tiles[i:i+3]))) for i in range(0, len(tiles), 3)]
cv2.imwrite(out, np.vstack(rows)); print(json.dumps(report, indent=1))
