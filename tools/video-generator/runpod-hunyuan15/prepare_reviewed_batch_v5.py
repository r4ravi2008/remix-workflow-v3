"""Stage only the individually inspected first post-pilot group of anchors."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from prepare_motion_v5 import build, OUT, sha

reviews = {'01': {
    'C005': 'Full-size reviewed: sharp male profile foreground left and woman distant right at gate; separated geography and matching office palette; badges/clothing consistent with next gate shot. No embedded messages or anatomy defect observed.',
    'C006': 'Full-size reviewed beside C005 and approved C007: same faces and lobby, coherent gate/card interaction; visible card hand and bag hand plausible, no contact or coercion. Preserve card and restrained expressions.',
    'C008': 'Full-size reviewed beside approved walking C007: correct distant desk revision with three empty chairs separating adults; faces and wardrobe recognizable, visible hand plausible, no added messages. Do not move them together.',
}, '02': {
    'C002': 'Full-size reviewed: same adult woman, charcoal suit, cream top and black bag as following cafe and office anchors. Face, bag grip and free hand clear. Quiet arrival at cafe with ample reflective background; preserve independent gaze.',
    'C003': 'Full-size reviewed beside cafe arrival: matching face/clothing/bag and environment; coffee-cup and phone grips plausible, phone back has no message lettering. Solitary routine advances arrival to holding coffee. Dawn light differs but fits the opening morning montage.',
    'C004': 'Full-size reviewed beside cafe and distant-admiration anchors: sharp recognizable adult female face, matched hair/wardrobe, red architectural field and negative space. Portrait is a deliberate editorial insert rather than a new location/action claim; keep mouth closed.'
}, '03': {
    'C009': 'Full-size reviewed: recognizable woman walking alone in glass corridor, matching charcoal office wardrobe, cream top and bag. Visible anatomy coherent and room for restrained walking. City landmark is an editorial backdrop, not documentary location evidence.',
    'C010': 'Full-size reviewed beside corridor and invitation: same adults, woman ahead/right, man behind/left, visible separation outside T-Hub. Brief backward glance is plausible but must not become prolonged mutual staring while walking. No touching.',
    'C011': 'Full-size reviewed: same man left and woman right beside nighttime coffee vendor. His open palm conveys invitation; visible hands and faces coherent. Red/teal lighting and wardrobe continue after-work sequence. Invitation must remain nonverbal.',
    'C011b': 'Full-size reviewed beside invitation: woman turning away in a reserved response, man watching with hands lowered. Same wardrobe, props and city-night palette. Preserve distance and restrained response, not sudden intimacy.'
}, '04': {
    'C013': 'Full-size reviewed: city-and-cafe atmospheric insert with steaming cup, road traffic and warm sky; no focal faces. Stylized skyline is an editorial location cue. Preserve warm low light without claiming a literal overnight time jump within the shot.',
    'C014': 'Full-size reviewed: sharp recognizable woman at cafe, plausible phone grip and hand supporting cheek, matching charcoal wardrobe. Phone back faces camera and no text is baked in. Left red negative space supports later message graphics.',
    'C015': 'Full-size reviewed beside message shot: same woman and wardrobe, phone lowered at waist with its back visible, coherent fingers and contemplative outward gaze. Rooftop is an editorial reaction insert, not a continuous cafe-camera move. No legible screen text.',
    'C016': 'Full-size reviewed: woman foreground left reaching for takeaway cup at office desk; man background right with respectful separation. Faces and wardrobe match office anchors, visible hand and cup geometry plausible. This is a later office coffee gesture rather than a cafe arrival.'
}, '05': {
    'C017': 'Full-size reviewed beside office coffee gesture: same adults now sharing the desk, her hand resting on closed folio and his on ceramic mug. Clear faces and coherent hands; changed cup is a later reciprocal coffee moment, not a continuous transfer of the previous takeaway cup.',
    'C018': 'Full-size reviewed: same adults remain separated by glass mullion, matched badges and office clothing, hands in pockets/crossed arms plausible. City bridge behind glass gives layered composition. Do not create duplicate reflected faces.',
    'C019': 'Full-size reviewed: bridge and lake landscape with coherent cables and rippled reflections, no focal people. Works as temporal/location interlude between office exchanges. Maintain twilight rather than attempt sunset-to-dawn morphing.',
    'C020': 'Full-size reviewed: woman foreground left with plausible phone grip, same man turning back behind cubicle on right. Clear male face and consistent female profile/hair/wardrobe. Phone back visible, no message lettering. Preserve office separation.'
}, '06': {
    'C021': 'Full-size reviewed: foreground woman at laptop with recognizable clear face, man softly focused behind glass. Office wardrobe and red accent match neighboring shots; physical separation remains. Background softness is deliberate depth of field, not a focal-face detail claim.',
    'C022': 'Full-size reviewed beside desk distance: man stands left by printer, woman seated right looks away. Clear faces and consistent badges/wardrobe; no contact or cornering. Keep man where he is rather than approaching her chair.',
    'C023': 'Full-size reviewed: recognizable man alone in architectural corridor with coherent visible hand, forward walking room and stable glass lines. Fits one controlled lateral burst; maintain independent eyeline rather than staring sideways throughout.',
    'C024': 'Full-size reviewed beside corridor: same adults at widely separated elevator bays, plausible hands and bag, matched dark office clothing. Woman looks away, man remains distant. Preserve separate departure paths with no convergence or prolonged mutual stare.'
}, '07': {
    'C025': 'Full-size reviewed: same office-clothed adults walking at lakeside with visible space, clear faces, coherent bag hand and badges. Woman looks out to lake rather than at man. Night bridge matches following inserts; maintain independent walking eyelines.',
    'C026': 'Full-size reviewed: sharp same adults standing beside lake rail with hands relaxed and no contact. Camera position is a new frontal setup after walking, not continuous screen-position matching. Bridge and warm reflected lights match reaction singles.',
    'C026b': 'Full-size reviewed beside pair and male single: same sharp female face, hair, charcoal lapel, cream top and badge lanyard; gaze toward lake left of camera. Consistent blue/gold background. This is a restrained response, not reciprocal eyeline match.',
    'C026c': 'Full-size reviewed beside pair and female single: recognizable sharp male face with matched hair, dark jacket/shirt and bridge lighting. Gaze left toward her is consistent with pair setup. No visible anatomy or baked text defect.'
}, '08': {
    'C027': 'Full-size reviewed: same woman alone in red-lit apartment kitchen, clear face and plausible phone grip. Screen faces her, no embedded message. Negative space left supports later boyfriend-message graphic. This is received-message reaction, not generated boyfriend footage.',
    'C028': 'Full-size reviewed beside phone shot: consistent woman, kitchen fixtures and red lighting, phone lowered and gaze out window. Natural restrained disappointment and coherent hand/phone geometry. No additional person or message lettering.',
    'C029': 'Full-size reviewed: elevated metro and city towers at twilight, coherent rails/train silhouette and traffic. No visible character: prompt must not invent a familiar glance or person. Temporal interlude to next portrait.',
    'C030': 'Full-size reviewed: sharp same female face in charcoal jacket and cream top against crimson wall; clear profile and eyes, no unwanted text. Quiet portrait insert links apartment reaction to later decision, without invented champagne prop.'
}, '09': {
    'C031': 'Full-size reviewed: recognizable woman seated with phone, clear face/hand and left negative space. Charcoal outfit and cream top remain coherent; no baked text. Narrative message complexity belongs to editor overlays, not model-generated interface.',
    'C031b': 'Full-size reviewed beside preceding phone shot: same woman, plausible two-handed phone grip, reserved glance away before reply. Background and wardrobe consistent with red office/cafe editorial treatment. Screen is turned away and contains no legible text.',
    'C032': 'Full-size reviewed: woman at open rear cab door foreground left, man several metres behind by office entrance. Clear identities and visible hand grips; no touching. Preserve separation through departure and do not force both to enter simultaneously.',
    'C033': 'Full-size reviewed: same adults seated with gap in rear cab, coherent faces and matching dark wardrobe. Window reflections are intentional stylized layers and must remain stable, not become additional people. This later shared ride is an editorial ellipsis after separate departure.'
}, '10': {
    'C034': 'Full-size reviewed: twilight city, curved traffic trails and bridge/lake, stable architectural lines and no focal faces. Visual connective insert after cab ride; maintain urban geometry rather than abstract morphing.',
    'C035': 'Full-size reviewed: woman at closed hotel door, man waiting several metres behind. Clear faces and plausible raised hand/bag grip; matched office wardrobe. Anchor is already at door, so animate hesitation instead of replaying corridor approach.',
    'C035b': 'Full-size reviewed beside corridor pair: sharp same male face and jacket, same warm/red corridor fixtures. Hands remain in pockets and gaze toward offscreen woman; deliberate reverse/reaction insert preserving respectful wait.',
    'C036': 'Full-size reviewed beside preceding corridor views: same woman lowers hand near door handle, clear profile, coherent fingers, man soft behind. Subtle advance from raised-hand hesitation rather than new approach. Keep door closed for her decision.'
}, '11': {
    'C037': 'Full-size reviewed: sharp same woman at threshold looking toward soft-focus male foreground; coherent face/hair/lanyard and warm red door setting. This is an eyeline reaction insert, not evidence he moved or pressured her.',
    'C038': 'Full-size reviewed: two plausible adult hands beside two badges already on counter, laptop and black bag; intentional prop insert without voyeuristic body framing. Badges carry portraits and graphic rules, not meaningful generated messaging. Animate hands withdrawing, not duplicate badge placement.',
    'C040': 'Full-size reviewed: same fully clothed adults stand close by hotel window with joined hands, recognizable faces and coherent fingers. Badges and bag absent after set-down; dark jacket and cream scoop-neck top preserved. Restrained non-explicit ending choice with stable reflection.'
}, '12': {
    'C040b': 'Full-size reviewed beside C040: same fully clothed adults at same window with joined hands, woman resting head on his shoulder. Recognizable faces, coherent contact and fingers, matching cream scoop-neck top/dark jacket and absent badges/bag. Stable reflective city background; ending resolves to non-explicit chosen closeness.'
}, '13': {
    'C001': 'Revised full-size city anchor reviewed: plausible road bus with visible rubber tires, stable city architecture and warm low light. Original tram-like artifact removed. No focal faces. Preserve skyline and traffic lanes; independent opening plate.',
    'C039': 'Revised normalized full frame and C038/C040/C040b neighbors reviewed: matching cream scoop-neck top and charcoal jacket, no returned bag after set-down, same faces, coherent hand on panel and separated blocking. Preserve room and restraint; no touch or intimate action.',
    'C041': 'Same reviewed revised city anchor returns as bookend; generate independent continuing traffic with a separate seed rather than replay the opening footage. Preserve road bus geometry, skyline and light.'
}}
prompt_overrides = {
    'C011': ('He gently asks about coffee or a walk.', 'He offers a small open-palm gesture toward the coffee stall, then waits quietly. Both keep their lips gently closed; the invitation is entirely nonverbal.'),
    'C011b': ('Reciprocal glance within the same invitation, not a second invitation..', 'She gives one reserved glance and gently turns her attention away. He respects her space with hands lowered. Lips stay gently closed; no repeated invitation or sudden intimacy.'),
    'C013': ('Night passes; desire remains unresolved.', 'Quiet city interlude: distant traffic glides naturally and steam curls gently above the foreground cup. Preserve the warm low sky and architecture; no abrupt day-to-night transformation.'),
    'C014': ('His gentle follow-up message appears in frame space.', 'She quietly studies her phone, then pauses thoughtfully. Keep the phone back facing the camera. The empty left side remains free of graphics; message lettering will be added later by the editor.'),
    'C015': ('She locks the phone without replying.', 'She lowers the phone slightly and looks away, choosing not to reply. Keep its back toward camera and lips gently closed; do not invent a visible interface or text.'),
    'C016': ('She appears for coffee anyway.', 'At the office desk she rests her fingertips beside the takeaway coffee cup, then briefly notices the man in the background. He remains at a respectful distance. Preserve cup, hand anatomy and desk layout.'),
    'C017': ('Returned coffee becomes a quiet romantic gesture.', 'They share one quiet glance across the desk. His hand remains on the ceramic mug and her hand rests on the closed folio; no transfer or new objects. Lips remain gently closed.'),
    'C019': ('Durgam Cheruvu time passage.', 'Twilight lake interlude: gentle water ripples and distant bridge traffic beneath a stable blue-orange sky. Preserve bridge geometry and lighting; no day-to-night transformation.'),
    'C020': ('A quiet message and a look across the office.', 'She lowers her phone slightly and gives one brief glance toward him across the office. He returns the glance without moving closer. Phone back stays toward camera, with no screen lettering or floating message graphics. Both keep lips gently closed.'),
    'C022': ('He waits; she maintains the boundary.', 'He remains beside the printer with hands relaxed, without approaching her chair. She turns her gaze back to her work. Lips remain gently closed and their physical separation remains unchanged.'),
    'C023': ('his-architectural-walk.', 'He walks forward alone, returning his eyes naturally to his path after one fleeting side glance.'),
    'C024': ('separate-exits.', 'They turn toward their own separate elevator bays, maintaining the large distance between them. No approach toward one another and no walking while staring at each other.'),
    'C025': ('bridge-walk.', 'They walk forward independently along the lakeside, keeping the visible gap. She briefly looks toward the water then returns her gaze to her path; he looks ahead. No prolonged mutual stare.'),
    'C026': ('still-pair-restless-city.', 'They pause beside the lake rail, quietly breathing as city reflections ripple behind them. Keep their spacing and hands relaxed, with gently closed lips; no approach or touching.'),
    'C027': ('Boyfriend says he will be away.', 'Alone in the kitchen she studies her phone and pauses with subdued disappointment. Phone back faces camera, screen content remains unseen. Keep the left negative space empty; the received message is added later by the editor.'),
    'C029': ('Friday city motion and a familiar glance.', 'The metro train glides smoothly left along the existing elevated rails while distant road traffic moves below. Preserve train shape, track geometry and twilight; no added characters.'),
    'C031': ('OYO invitation, boyfriend-thread reread, deliberate acceptance.', 'She quietly rereads her phone with a thoughtful pause, lips gently closed. Keep the phone back facing camera and the left negative space empty. All invitation and reply text will be added later by the editor.'),
    'C031b': ('She considers the invitation, then chooses to reply; messages remain editor overlays..', 'She looks down at the phone held in both hands and makes one small deliberate thumb tap, then pauses. Phone back remains toward camera; no generated text or interface. Lips stay gently closed.'),
    'C033': ('Very slow lateral anamorphic tracking; preserve deliberate negative space.', 'Camera is fixed relative to the back seat; city lights slide across the windows and existing reflections while the two adults share one brief quiet glance. Preserve the space between them and do not create additional reflected people.'),
    'C034': ('Hyderabad night abstracts into desire.', 'Night traffic flows smoothly along the curved road beside the lake. City lights shimmer subtly on water; buildings and bridge remain stable and photographic, without morphing.'),
    'C035': ('Hotel corridor; she leads but slows.', 'Already standing at the closed hotel door, she pauses with her raised hand hovering. He waits several metres behind without approaching. Quiet breathing, gently closed lips; do not open the door or restart walking.'),
    'C036': ('She pauses at the threshold; he waits.', 'She lowers her hovering hand a little toward the handle, then pauses to choose. Door remains closed and man stays back, without pressure or contact. Lips remain gently closed.'),
    'C038': ('Work identities and badges are set down.', 'Both badges are already resting on the counter. The two hands slowly withdraw without touching each other. Keep badges, bag, laptop and keycard stationary; do not add or duplicate objects.'),
    'C040': ('Standing together at the window, they choose closeness and hold hands..', 'Already standing close with hands joined, the fully clothed adults quietly look out over the city. Gentle breathing and a subtle shared lean, stable interlaced fingers. Keep clothes on and their joined hands low; no further intimate action.'),
    'C040b': ('She rests her head on his shoulder; held hands and city reflections resolve the closeness..', 'Her head already rests gently on his shoulder and their hands are already joined. Hold this quiet fully clothed closeness with natural breathing and subtle city reflections; no repeated lean, no new intimate action, stable hands and gently closed lips.')
}
parser = argparse.ArgumentParser()
parser.add_argument('--batch', choices=sorted(reviews), default='01')
args = parser.parse_args()
notes = reviews[args.batch]
plan = build()
jobs = []
stage = OUT / ('batch-' + args.batch)
stage.mkdir(exist_ok=True)
assert not (stage / 'plan.json').exists(), 'Existing batch plan is immutable; inspect it instead of overwriting'
for index, (key, note) in enumerate(notes.items()):
    source = next(j for j in plan['jobs'] if j['jobId'] == key)
    group = next(g for g in plan['generationGroups'] if g['generationId'] == key)
    assert not source['issues']
    target = stage / (key + '.png')
    shutil.copy2(source['anchorPath'], target)
    assert sha(target) == source['anchorSha256']
    prompt = source['prompt']
    if key in prompt_overrides:
        old, new = prompt_overrides[key]
        assert old in prompt
        prompt = prompt.replace(old, new)
    seed = 2026092200 + int(key[1:]) if key[1:].isdigit() else int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)
    jobs.append({**source, 'prompt': prompt, 'nativeFrames': group['nativeFrames'], 'placements': group['placements'],
                 'status': 'ANCHOR_REVIEWED_FOR_GENERATION', 'submissionAllowed': True,
                 'reviewedForGeneration': True, 'review': note, 'seed': seed})
result = {'provider': 'RunPod', 'topUpAllowed': False, 'jobs': jobs,
          'pilotUserApproval': 'Yes, continue with this quality',
          'observedBalanceUSD': 6.67, 'scope': 'Small generation batch only; outputs require motion review before final assembly',
          'contractSha256': plan['contractSha256']}
(stage / 'plan.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'stage': str(stage), 'jobs': [{ 'id':j['jobId'], 'frames':j['nativeFrames']} for j in jobs]}))
