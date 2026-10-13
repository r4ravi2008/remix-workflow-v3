# Streaming audio behavior unit

The previous movie unit buffered the complete PCM selection and refused more than240video frames.
The new unit replaces whole-selection PCM buffering with bounded native chunks.

Keep the current scope of one48kHz stereo PCM clip, unity gain and zero pan.
Keep movie/image picture semantics unchanged. Audio mixing and resampling remain separate work.
The decoder validates consecutive source sample timestamps, channel layout and finite float samples.
Each callback owns an interleaved float chunk of at most4096frames with its exact source and output sample positions.
A capacity-two channel feeds the encoder. Audio and picture decoders check the same fenced export cancellation.
The native writer receives sequential PCM chunks without loading the complete selection.
The output verifier compares source and reopened AAC samples incrementally at zero offset.
Source and output sample extents, EOF status and waveform similarity are explicit receipt fields.

The native frame bound is now100000, matching the existing project limit. Native operations have1800-second deadlines.
The12-second low-resolution fixture exercises the previous ten-second boundary and a nonzero source offset.
The independent verifier checked all288frames, MP4 clocks and576000stereo samples. The minimum picture PSNR is41.847dB.
Audio similarities exceed0.999989 at zero offset. Source selection is `[8191, 584191)`.
Output readers reached EOF; the selected source read reports its range endpoint without claiming whole-source EOF.
The54tests, formatting and Clippy pass. Maximum-bound throughput and peak process/native-framework memory remain unmeasured.
A synthetic duration fixture cannot satisfy the Panja film or director acceptance gates.
The qualified song map, complete musical pilot and audiovisual review still control production scaling.

Cancellation during track loading calls `cancelLoading` and prevents a later callback from starting retired work.
Blocked chunk producers observe local stop or the shared export signal. Drop closes the channel before joining the worker.
Owned recovery verification retains fencing and cancellation. Completed-export readback remains a read-only operation.
Native framework calls can be stopped cooperatively between calls. A stalled native call cannot be forcibly interrupted by this library.

The first long attempt used the prior240-frame executable after Clippy stopped the new build.
That rejection and inaccurate expected-build label are retained with an observation correction.
The successful fresh intent binds the rebuilt A03 executable and the exact long movie.
The independent observer uses separate code and binary but shares AVFoundation with the producer.
