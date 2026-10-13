# Root comparison of the Rec.709 integration designs

Root read both complete candidates before scoring.
Candidate A is native-color-integration-candidate-a.md, SHA a7d34b392c992605476f77d3316c5f65872b29da41266d01cea93adbfb4e3cde.
Candidate B is mastering-rec709-integration-candidate-b.md, SHA eac2e2c30c3751bc9110d96d9eafce239d4d2c3a8beb2b672ee848479f2ff8ac.

Scores are design judgments from 1, weak, to 5, strong.

| Dimension | A | B | Reason |
| --- | ---: | ---: | --- |
| Caller clarity | 5 | 5 | Both add one closed profile and keep existing operations. |
| Historical compatibility | 5 | 5 | Both preserve V1 writer behavior and absent optional evidence. |
| Evidence clarity | 5 | 3 | A records the actual tuple. B duplicates counts and hashes an already fixed tuple. |
| Ownership and module depth | 5 | 4 | A puts append policy in the session that owns the format. B also names movie.rs as policy owner. |
| Scope and reader load | 3 | 2 | Both add a recursive container parser. B adds a separate tuple digest protocol. |
| Feasibility grounding | 5 | 5 | Both use the complete tested native tuple and retained probe. |
| Verification value | 4 | 4 | Both preserve fixed pixels, PCM and historical receipts. Lifecycle retesting needs bounded scope. |
| Total | 32 | 28 | A provides the clearer evidence model. |

Root prefers A as the base, subject to independent judgment.
The synthesis should remove the production recursive MOV color parser.
The product can require the complete encoded Core Media tuple on every compressed video sample.
It can require the matching Core Video tuple on every decoded output buffer.
Those measured tuples express the codec contract directly.
The existing ftyp reader remains unchanged.
The independent proof still reads the actual bounded sample-entry colr bytes.
It requires the observed nclc 1/1/1 representation before accepting this output unit.

This removes a new binary parser and avoids duplicating native format-description observations.
The production claim will be the complete Rec.709 tuple, not a universal atom representation guarantee.
The exact nclc representation remains an observed property of the accepted bounded artifact.
No ICC, gamma, gamut, source metadata conversion or natural-color claim is added.

The final evidence field should contain encoded_samples and decoded_buffers tuples.
Counts remain video_track.sample_buffers and video_frames.
The field is absent for V1 and H264.
Receipt4 requires it for V2.
The writer session attaches and reads back every input tuple before append.
Each native verification loop checks each tuple before recording the final evidence.

Publication and worker ownership do not change.
Existing lifecycle regression tests, Receipt4 validation, fresh ordinary exports and bounded active cancellation remain required.
The full film, WATCHED, HEARD and creative acceptance remain outside this engineering unit.
