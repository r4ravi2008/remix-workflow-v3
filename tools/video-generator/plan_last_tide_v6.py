"""Frame-bound full-film transition plan; missing coverage stays explicit."""
import hashlib
import json
import math
from pathlib import Path
from prepare_last_tide_v6 import BASE, OUT, EXPECTED, save

# Desired seconds determine relative pacing inside each musical section, not
# forced lyric timings. C sources are paid footage; A sources are coverage gaps.
# Existing ranges are provisional selects to be inspected in motion before use.
SECTIONS = [
 ('Invitation', 0, 30.6, [
  ('C01',7,0,144,'Empty route; no sudden person','cut'),
  ('A01',6,0,144,'Ivory moon-line slowly breaks in lacquer water','graphic_match'),
  ('C02',4,20,116,'Distant Arjun; neutral observation','cut'),
  ('A02',6,0,144,'Oxblood silk seen only as a reflection, no body','reflection_dissolve'),
  ('C03',2,0,36,'A single withheld glance before her smile','cut'),
  ('C04',3,28,87,'Tara crosses; silk closes the image','silk_occlusion')]),
 ('Desire without display',30.6,73.32,[
  ('A03',6,0,144,'Antique brass token turns once in wet sand','trapezoid_reveal'),
  ('C05',4,75,139,'Token rather than smiling face; contextual hands','graphic_match'),
  ('C06',2,0,43,'One step off the jetty','cut'),
  ('C07',2,0,65,'First lateral pursuit burst; open distance','cut'),
  ('A04',6,0,144,'Palm shadow crosses ivory fabric suspended outdoors','shadow_reveal'),
  ('C08',4,0,90,'Tara stops; he stays apart','cut'),
  ('A05',6,0,144,'Two distant light streaks never quite meet','reflection_dissolve'),
  ('C09',3,0,58,'Her hand determines the next route','cut'),
  ('C10',4,0,65,'Mangrove light as an environmental insert','masked_scale_reveal')]),
 ('Traces of memory',73.32,130.94,[
  ('A06',7,0,144,'Long-lens empty backwater, one brass glint, negative space','cut'),
  ('C11',6,0,132,'Reflection plane only; no cropped torsos','graphic_match'),
  ('C12',4,0,92,'Boat is encountered, not a romantic ride','shadow_reveal'),
  ('C13',5,0,126,'Paper boat released; cause before consequence','cut'),
  ('A07',6,0,144,'Paper fold drifts across a black-water frame','graphic_match'),
  ('C14',3,0,72,'Old handprints are a clue, not explanatory text','cut'),
  ('C15',3,0,59,'Recognizing the object; end before broad smiles','cut'),
  ('A08',7,0,144,'Abstract home-film light flickers on an empty outdoor sail','reflection_dissolve'),
  ('C17',4,0,88,'Token recognition; keep both hands contextual','trapezoid_reveal'),
  ('A09',7,0,144,'Two shadows move at different speeds across wet sand','cut')]),
 ('Stop pursuing',130.94,163.16,[
  ('C18',5,0,119,'She walks away; he does not intervene','cut'),
  ('C19',5,0,119,'He waits; deliberate empty space between them','shadow_reveal'),
  ('A10',7,0,144,'Brass reflection slows while water continues','reflection_dissolve'),
  ('C20',5,0,120,'Tara alone; neutral pause and choice','cut'),
  ('A11',7,0,144,'Ivory fabric crosses black water, no figure','silk_occlusion')]),
 ('She chooses the distance',163.16,193.64,[
  ('C21',3,0,63,'Her turn is a decision, not an invitation repeated','cut'),
  ('A12',8,0,144,'Two isolated ivory glints acquire a shared rhythm','reflection_dissolve'),
  ('C22',4,0,96,'She returns and makes the approach','cut'),
  ('C23',3,0,66,'Chosen proximity, no grasp or pull','graphic_match'),
  ('A13',7,0,144,'A paper boat crosses an old handprint reflection','trapezoid_reveal')]),
 ('Pace matched',193.64,227.6,[
  ('C24',5,0,120,'They move side by side, equal pace','cut'),
  ('A14',7,0,144,'Gold and ivory reflections travel together, petrol only in water','masked_scale_reveal'),
  ('C25',5,0,120,'Shared response from the landscape, restrain cyan in grade','cut'),
  ('A15',7,0,144,'Empty sandbar opens toward dawn, static long lens, moving tide','reflection_dissolve'),
  ('C27',7,0,144,'Wide walking departure; no embrace required','graphic_match')])
]


def main():
    beatmap=json.loads((OUT/'measured-beats.json').read_text())
    beats=beatmap['beats']
    total=math.ceil(beatmap['durationSeconds']*24)
    old=json.loads((BASE/'resolve/resolve-edit-map-v4.json').read_text())
    sources={x['scene']:x['path'] for x in old['items'] if x.get('style')=='wide-original'}
    def nearest(seconds):
        return min(beats,key=lambda x:abs(x['seconds']-seconds))
    shots=[]
    events=[]
    for si,(section,start,end,rows) in enumerate(SECTIONS):
        first=0 if si==0 else nearest(start)['frame24']
        last=total if si==len(SECTIONS)-1 else nearest(end)['frame24']
        weights=sum(row[1] for row in rows)
        cursor=first
        cumulative=0
        for j,(source,weight,srcin,srcout,purpose,incoming) in enumerate(rows):
            cumulative+=weight
            stop=last if j==len(rows)-1 else nearest((first+(last-first)*cumulative/weights)/24)['frame24']
            assert stop>cursor
            ident=f'S{len(shots)+1:02}'
            existing=source.startswith('C')
            speed=(srcout-srcin)/(stop-cursor)
            shots.append(dict(id=ident,section=section,sourceId=source,path=sources.get(source),
                sourceInFrame=srcin,sourceOutFrame=srcout,recordInFrame=cursor,recordOutFrame=stop,
                durationSeconds=round((stop-cursor)/24,3),speedCandidate=round(speed,4),
                purpose=purpose,status='existing_candidate' if existing else 'coverage_needed',
                framing='environmental_crop_requires_head_mid_tail_check' if source in ['C10','C11'] else 'contain',
                generationSeconds=6 if not existing else None,
                verification=['full_usable_motion_review','grade_match','focal_framing','no_repeated_window']))
            if shots[:-1]:
                durations={'cut':0,'graphic_match':0,'reflection_dissolve':22,'silk_occlusion':11,
                    'shadow_reveal':11,'trapezoid_reveal':8,'masked_scale_reveal':8}
                dur=durations[incoming]
                anchor=nearest(cursor/24)
                events.append(dict(id=f'T{len(events)+1:02}',outgoing=shots[-2]['id'],incoming=ident,
                    family=incoming,impactFrame=cursor,beatIndex=anchor['index'],beatSeconds=anchor['seconds'],
                    musicalRole='section boundary' if j==0 else 'selected internal accent',
                    startFrame=cursor-dur//2,endFrame=cursor+dur-dur//2,durationFrames=dur,
                    beatAnchorRole='midpoint' if dur else 'cut',outgoingHandleFrames=math.ceil(dur/2),
                    incomingHandleFrames=math.ceil(dur/2),owner='Resolve/Fusion',
                    intent=purpose,fallback='clean motivated cut; record style unavailable, never mislabel',
                    parameters={'direction':'motivated by shot motion; verify before implementation',
                                'easing':'smoothstep','maximumTransientScale':1.04 if incoming=='masked_scale_reveal' else 1,
                                'flash':False,'reverse':False},
                    status='planned_not_implemented'))
            cursor=stop
    assert shots[-1]['recordOutFrame']==total
    assert all(a['recordOutFrame']==b['recordInFrame'] for a,b in zip(shots,shots[1:]))
    assert len({x['sourceId'] for x in shots})==len(shots)
    counts={family:sum(e['family']==family for e in events) for family in sorted({e['family'] for e in events})}
    missing=[x for x in shots if x['status']=='coverage_needed']
    plan={'revision':'v6-full-film-plan-1','audioSha256':EXPECTED,
        'beatMapSha256':hashlib.sha256((OUT/'measured-beats.json').read_bytes()).hexdigest(),
        'timeline':{'fps':24,'width':1920,'height':1080,'activeHeight':804,'matteTopBottom':138,
                    'totalFrames':total,'durationSeconds':total/24,'audioDurationSeconds':227.6,
                    'tailPadSeconds':round(total/24-227.6,6)},
        'status':'planned_provisional_audio_listening_and_motion_review_pending',
        'shots':shots,'transitions':events,'plannedFamilyCounts':counts,
        'coverage':{'existingSourcesSelected':len(shots)-len(missing),'newCoverageSlots':len(missing),
                    'newCoverageTimelineSeconds':round(sum(x['durationSeconds'] for x in missing),3),
                    'newGenerationSeconds':len(missing)*6,'repeatedSourceWindows':0,
                    'stillSubstitutes':0,'fullLengthCoveragePlanned':True,'fullLengthCoverageAvailable':False},
        'preservedButNotSelected':['C16','C26'],
        'notes':['Kissing/near-kissing footage retained on disk but omitted from this deadpan cut.',
                 'No labels in this plan constitute acceptance or proof of rendered effects.',
                 'New coverage is supplementary environmental motion, not regeneration of paid character clips.',
                 'Source trims and retime cadence require full motion inspection; do not force a failed range to fill duration.']}
    save('full-film-plan.json',plan)
    config=json.loads((Path(__file__).resolve().parents[2]/'.agents/skills/music-video-director/assets/effects-config.json').read_text())
    config['framing'].update(allow_source_crop=True,rule='shot-scoped environmental crops only; no repeated zoom treatment')
    config['transitions'].update(palette=['graphic_match','silk_occlusion','shadow_reveal','trapezoid_reveal','reflection_dissolve','masked_scale_reveal'],minimum_distinct_styles=4,minimum_uses_per_style=2,duration_beats=[.75,1,2],flash_max_opacity=0,selection='explicit full-film-plan.json events; not random')
    config['boomerang']['enabled']=False
    config['motion_graphics'].update(enabled=False,owner='Resolve')
    config['lyrics'].update(enabled=True,display='transliteration',owner='Resolve',max_lines=2,word_highlight='disabled until word timing is verified',typography='ivory 38px medium sans, restrained tracking, lower matte, no bounce or scale pulses')
    (BASE/'effects-config.json').write_text(json.dumps(config,indent=2)+'\n')
    lines=['# The Last Tide — full-film transition plan V6','','Plan before implementation. All ranges are half-open, 24 fps, bound to the canonical audio hash `'+EXPECTED+'`. Beat anchors are measured candidates; downbeats and lyric timing still need listening.','',
      '## Direction','',
      'Deadpan desire becomes recognition, then matched pace. The world moves more than the performers. Keep Kerala outdoors; no nightclub, interior cinema rebuild or honeymoon montage. No kissing is needed to resolve the story. The cinema memory survives only as brief abstract home-film light outdoors.','',
      'Black, oxblood, antique gold and ivory dominate. Reduce blue broadly; retain a trace only in wet reflections. Skin stays alive. No crushed silhouettes masquerading as a grade.','',
      '## Transition grammar','',
      '- Most edits are clean cuts or graphic matches. Let imagery and timing do the work.',
      '- Silk/shadow occlusion follows an actual foreground edge; never sweep an arbitrary filter across a face.',
      '- Trapezoid reveals are short, asymmetrical, three-point visual accents, not a template on every join.',
      '- Reflection dissolves overlap environmental planes, not two offset faces.',
      '- Only two masked-scale reveals, no more than 4% transient scaling; never perpetual push-ins.',
      '- No flash frames, invented anamorphic camera motion, source reversal or shot loops.',
      '- Incoming source time must continue through its transition and clean shot, never restart at the cut.','',
      '## Lyrics','',
      'Preserve native canonical words, render the separate Latin transliteration. Phrase starts follow the vocal, not a forcibly snapped grid. A short reveal can land on a nearby measured beat only if it does not mistime the phrase. Ivory type in the lower matte, at most two lines; no lyric bounce, no giant karaoke words, no text over faces. The last line is explicitly flagged by the new alignment and must be repaired before export.','',
      '## Full-song shot and transition schedule','',
      '| Shot | Time | Source | Function | Incoming transition |','|---|---|---|---|---|']
    for i,x in enumerate(shots):
        family='opening' if i==0 else events[i-1]['family']
        lines.append(f'| {x["id"]} | {x["recordInFrame"]/24:.3f}–{x["recordOutFrame"]/24:.3f} | {x["sourceId"]} | {x["purpose"]} | {family} |')
    lines += ['', '## Coverage and implementation gate','',
       f'{len(shots)-len(missing)} existing clips are selected once each. {len(missing)} supplementary environmental slots require {plan["coverage"]["newCoverageTimelineSeconds"]:.3f} seconds of timeline coverage; plan six-second-or-shorter generation, then inspect usable motion and retime cadence. No new generation has been submitted by this planner.',
       '', 'Do not repeat the old sources to conceal these gaps. Preserve C16 and C26, but do not force their romantic gestures into this version. Do not call this full plan a completed assembly.',
       '', 'Implementation order: render the existing retime diagnostic → verify source continuity → inspect/generate only missing environmental coverage → native Resolve full assembly → Fusion masks and grade → repair lyric timing and render text → full motion/audio review → final master and review export.']
    (OUT/'transition-plan.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'shots':len(shots),'frames':total,'coverage':plan['coverage'],'families':counts},indent=2))


if __name__=='__main__':
    main()
