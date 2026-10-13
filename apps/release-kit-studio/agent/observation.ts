import { Schema } from 'effect'
import { createHash } from 'node:crypto'

export const audioQuestions = [
  'Describe the audible sounds in this short excerpt. Is there singing or spoken speech? Do not guess lyrics, language, timestamps, tempo, recording quality, or artist identity.',
  'Describe changes you can hear within this short excerpt, if any. Qualify uncertain changes. Do not provide timestamps, durations, tempo, section names, or events outside the excerpt.',
]
export const AudioBackend = Schema.Literals(['qwen2-audio', 'qwen2.5-omni'])
const questionnaireSha256 = createHash('sha256')
  .update(JSON.stringify(audioQuestions))
  .digest('hex')

export const ObservationIntent = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  id: Schema.String,
  kind: Schema.Literals(['audio-window', 'speech', 'lyric-alignment']),
  jobId: Schema.String,
  releaseId: Schema.String,
  briefSha256: Schema.String,
  sourceSha256: Schema.String,
  sourceBytes: Schema.Number,
  sourceDuration: Schema.Number,
  language: Schema.Literals(['Telugu', 'Hindi', 'Tamil', 'English']),
  lyrics: Schema.String,
  startSeconds: Schema.Number,
  endSeconds: Schema.Number,
  audioBackend: Schema.optional(AudioBackend),
  lineIndices: Schema.optional(Schema.Array(Schema.Number)),
  alignmentDevice: Schema.optional(Schema.Literals(['cuda', 'cpu'])),
  alignmentBackend: Schema.optional(
    Schema.Literals(['whisper', 'indic-conformer-ctc']),
  ),
})
export type ObservationIntent = typeof ObservationIntent.Type
export interface GPUObservation {
  intent: ObservationIntent
  localSource: string
  localReceipt: string
}
export const ObservationManifest = Schema.Struct({
  intent: ObservationIntent,
  receipt: Schema.Struct({
    path: Schema.String,
    sha256: Schema.String,
    bytes: Schema.Number,
  }),
  inferenceSubmitted: Schema.Boolean,
})
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/u
const sha = /^[a-f0-9]{64}$/u
export const observationKey = (intent: ObservationIntent) =>
  createHash('sha256')
    .update(JSON.stringify(Schema.decodeUnknownSync(ObservationIntent)(intent)))
    .digest('hex')

export const validateObservationIntent = (intent: ObservationIntent) => {
  if (
    !sha.test(intent.id) ||
    !uuid.test(intent.jobId) ||
    !uuid.test(intent.releaseId) ||
    !sha.test(intent.briefSha256) ||
    !sha.test(intent.sourceSha256) ||
    !Number.isSafeInteger(intent.sourceBytes) ||
    intent.sourceBytes <= 0 ||
    intent.sourceBytes > 512 * 1024 * 1024 ||
    !Number.isFinite(intent.sourceDuration) ||
    intent.sourceDuration <= 0 ||
    intent.sourceDuration > 900 ||
    !Number.isFinite(intent.startSeconds) ||
    !Number.isFinite(intent.endSeconds) ||
    intent.startSeconds < 0 ||
    intent.endSeconds <= intent.startSeconds ||
    intent.endSeconds > intent.sourceDuration ||
    intent.lyrics.length < 1 ||
    intent.lyrics.length > 30000 ||
    (['audio-window', 'lyric-alignment'].includes(intent.kind) &&
      intent.endSeconds - intent.startSeconds > 30) ||
    (intent.kind === 'speech' &&
      (intent.startSeconds !== 0 ||
        intent.endSeconds !== intent.sourceDuration))
  )
    throw new Error('Observation must bind a frozen source and bounded range.')
  if (
    intent.audioBackend !== undefined &&
    (intent.kind !== 'audio-window' ||
      !['qwen2-audio', 'qwen2.5-omni'].includes(intent.audioBackend))
  )
    throw new Error('Choose a fixed audio backend only for an audio window.')
  const lines = intent.lyrics.split(/\r?\n/u)
  if (intent.kind === 'lyric-alignment') {
    if (
      intent.alignmentBackend === 'indic-conformer-ctc' &&
      (intent.alignmentDevice !== 'cpu' || intent.language !== 'Telugu')
    )
      throw new Error(
        'The pinned CTC backend requires explicitly selected Telugu CPU execution.',
      )
    const indices = intent.lineIndices
    if (
      !indices ||
      indices.length < 1 ||
      indices.length > 8 ||
      indices.some(
        (index, position) =>
          !Number.isSafeInteger(index) ||
          index < 0 ||
          !lines[index]?.trim() ||
          (position > 0 && index <= (indices[position - 1] ?? -1)),
      )
    )
      throw new Error(
        'Alignment requires distinct chronological canonical line indices.',
      )
  } else if (
    intent.lineIndices !== undefined ||
    intent.alignmentDevice !== undefined ||
    intent.alignmentBackend !== undefined
  )
    throw new Error(
      'Canonical line selection applies only to forced alignment.',
    )
  return intent
}

const ReceiptBinding = Schema.Struct({
  status: Schema.String,
  request: Schema.Struct({
    jobId: Schema.String,
    releaseId: Schema.String,
    sourceSha256: Schema.String,
    sourceBytes: Schema.Number,
    sourceDuration: Schema.Number,
  }),
  source: Schema.Struct({ sha256: Schema.String, bytes: Schema.Number }),
  fullSongHeard: Schema.Literal(false),
  pilotApproved: Schema.Literal(false),
  humanAccepted: Schema.Literal(false),
})
const AudioBinding = Schema.Struct({
  schemaVersion: Schema.Literal(2),
  request: Schema.Struct({
    startSeconds: Schema.Number,
    endSeconds: Schema.Number,
  }),
  audioPerceptionComplete: Schema.Literal(true),
  semanticFindingsVerified: Schema.Literal(false),
  observationContractPassed: Schema.Boolean,
  reviewer: Schema.Union([
    Schema.Struct({
      model: Schema.Literal('Qwen/Qwen2-Audio-7B-Instruct'),
      revision: Schema.Literal('0a095220c30b7b31434169c3086508ef3ea5bf0a'),
      quantization: Schema.Literal('nf4-text-bf16-audio'),
      promptSha256: Schema.String,
      runnerSha256: Schema.String,
    }),
    Schema.Struct({
      model: Schema.Literal('Qwen/Qwen2.5-Omni-7B'),
      revision: Schema.Literal('ae9e1690543ffd5c0221dc27f79834d0294cba00'),
      quantization: Schema.Literal('nf4-text-bf16-audio-vision-thinker-only'),
      promptSha256: Schema.String,
      runnerSha256: Schema.String,
    }),
  ]),
  decodedAudio: Schema.Struct({
    sampleRate: Schema.Literal(16000),
    samples: Schema.Number,
    sha256: Schema.String,
  }),
  modelAudioInput: Schema.Struct({
    featureShape: Schema.Array(Schema.Number),
    attendedFrames: Schema.Number,
    audioTokens: Schema.Number,
    featureSha256: Schema.String,
  }),
  observations: Schema.Array(
    Schema.Struct({
      question: Schema.String,
      response: Schema.String,
      usable: Schema.Boolean,
      issues: Schema.Array(Schema.String),
      semanticVerified: Schema.Literal(false),
    }),
  ),
})
const SpeechBinding = Schema.Struct({
  model: Schema.Literal('Systran/faster-whisper-large-v3'),
  revision: Schema.Literal('edaa852ec7e145841d8ffdb056a99866b5f0a478'),
  runnerSha256: Schema.String,
  weights: Schema.Struct({
    sha256: Schema.Literal(
      '69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1',
    ),
    bytes: Schema.Literal(3087284237),
  }),
  decodedAudio: Schema.Struct({
    sampleRate: Schema.Literal(16000),
    samples: Schema.Number,
    sha256: Schema.String,
  }),
  request: Schema.Struct({
    briefSha256: Schema.String,
    lyrics: Schema.String,
    language: Schema.String,
  }),
  recognitionComplete: Schema.Literal(true),
  lyricTimingVerified: Schema.Literal(false),
  canonicalLyricsChanged: Schema.Literal(false),
  durationProcessed: Schema.Number,
})
const alignmentFields = {
  runnerSha256: Schema.String,
  request: Schema.Struct({
    briefSha256: Schema.String,
    language: Schema.String,
    lyrics: Schema.String,
    startSeconds: Schema.Number,
    endSeconds: Schema.Number,
    lineIndices: Schema.Array(Schema.Number),
    device: Schema.Literals(['cuda', 'cpu']),
  }),
  canonicalText: Schema.String,
  alignmentComplete: Schema.Literal(true),
  alignmentContractPassed: Schema.Boolean,
  lyricTimingVerified: Schema.Literal(false),
  canonicalLyricsChanged: Schema.Literal(false),
  decodedAudio: Schema.Struct({
    sampleRate: Schema.Literal(16000),
    samples: Schema.Number,
    sha256: Schema.String,
  }),
  words: Schema.Array(
    Schema.Struct({
      wordIndex: Schema.Number,
      text: Schema.String,
      startSeconds: Schema.Number,
      endSeconds: Schema.Number,
      probability: Schema.Number,
      issues: Schema.Array(Schema.String),
      verified: Schema.Literal(false),
    }),
  ),
}
const WhisperAlignment = Schema.Struct({
  ...alignmentFields,
  model: Schema.Literal('Systran/faster-whisper-large-v3'),
  revision: Schema.Literal('edaa852ec7e145841d8ffdb056a99866b5f0a478'),
  weights: Schema.Struct({
    sha256: Schema.Literal(
      '69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1',
    ),
    bytes: Schema.Literal(3087284237),
  }),
  runtime: Schema.Struct({
    device: Schema.Literals(['cuda', 'cpu']),
    computeType: Schema.String,
    cpuThreads: Schema.Number,
  }),
  modelAudioInput: Schema.Struct({
    featureShape: Schema.Array(Schema.Number),
    attendedFrames: Schema.Number,
    textTokens: Schema.Number,
    featureSha256: Schema.String,
  }),
})
const CTCAlignment = Schema.Struct({
  ...alignmentFields,
  model: Schema.Literal('OpenVoiceOS/ai4bharat-indicconformer-te-onnx'),
  revision: Schema.Literal('d952dec2a1d256a1569cdfc9a9615cba05a1a2e3'),
  weights: Schema.Struct({
    sha256: Schema.Literal(
      'd615acecbfcffca3fa04ed8bc62284ba30cf48f90f537d4d0040b1b0e75f0b1c',
    ),
    bytes: Schema.Literal(137677313),
  }),
  runtime: Schema.Struct({
    device: Schema.Literal('cpu'),
    provider: Schema.Literal('CPUExecutionProvider'),
    computeType: Schema.Literal('int8'),
    cpuThreads: Schema.Literal(4),
  }),
  preprocessor: Schema.Struct({
    package: Schema.Literal('onnx-asr'),
    version: Schema.Literal('0.12.0'),
    sha256: Schema.Literal(
      '7ab6b0d1f57832e56f59aa7cab4289de50df7f8d5296cdfd281d9c9b7b8d73e0',
    ),
    bytes: Schema.Literal(89473),
  }),
  vocabulary: Schema.Struct({
    sha256: Schema.Literal(
      'dc0b7bbb9eca8d3c8aebf1eb86e3144c90d692b4008cf5a32d46437b942b23ac',
    ),
    bytes: Schema.Literal(2706),
  }),
  modelAudioInput: Schema.Struct({
    featureShape: Schema.Array(Schema.Number),
    attendedFrames: Schema.Number,
    featureSha256: Schema.String,
    ctcFrames: Schema.Number,
    frameSeconds: Schema.Literal(0.04),
    ctcSha256: Schema.String,
  }),
  nativeTokenization: Schema.Literal(
    'exact-piece-lattice-without-transliteration',
  ),
  words: Schema.Array(
    Schema.Struct({
      wordIndex: Schema.Number,
      text: Schema.String,
      startFrame: Schema.Number,
      endFrame: Schema.Number,
      startSeconds: Schema.Number,
      endSeconds: Schema.Number,
      probability: Schema.Number,
      issues: Schema.Array(Schema.String),
      verified: Schema.Literal(false),
    }),
  ),
})
const AlignmentBinding = Schema.Union([WhisperAlignment, CTCAlignment])

export const validateObservationReceipt = (
  intent: ObservationIntent,
  raw: unknown,
) => {
  validateObservationIntent(intent)
  const receipt = Schema.decodeUnknownSync(ReceiptBinding)(raw)
  if (
    receipt.request.jobId !== intent.jobId ||
    receipt.request.releaseId !== intent.releaseId ||
    receipt.request.sourceSha256 !== intent.sourceSha256 ||
    receipt.request.sourceBytes !== intent.sourceBytes ||
    receipt.request.sourceDuration !== intent.sourceDuration ||
    receipt.source.sha256 !== intent.sourceSha256 ||
    receipt.source.bytes !== intent.sourceBytes
  )
    throw new Error('Observation receipt belongs to a different frozen source.')
  if (receipt.status === 'failed')
    throw new Error(
      'Model qualification failed; its exact receipt is preserved.',
    )
  if (intent.kind === 'audio-window') {
    const audio = Schema.decodeUnknownSync(AudioBinding)(raw)
    if (intent.audioBackend === 'qwen2.5-omni')
      Schema.decodeUnknownSync(
        Schema.Struct({
          modelLoad: Schema.Struct({
            thinkerOnly: Schema.Literal(true),
            missingKeys: Schema.Literal(0),
            mismatchedKeys: Schema.Literal(0),
            discardedAudioGenerationKeys: Schema.Number.check(
              Schema.isInt(),
              Schema.isGreaterThanOrEqualTo(0),
            ),
          }),
        }),
      )(raw)
    const samples = Math.round(
      (intent.endSeconds - intent.startSeconds) * 16000,
    )
    const frames = Math.ceil(samples / 160)
    const tokens =
      Math.floor(
        (Math.floor((audio.modelAudioInput.attendedFrames - 1) / 2) + 1 - 2) /
          2,
      ) + 1
    if (
      !['observed', 'observed-with-issues'].includes(receipt.status) ||
      (audio.reviewer.model === 'Qwen/Qwen2.5-Omni-7B') !==
        ((intent.audioBackend ?? 'qwen2-audio') === 'qwen2.5-omni') ||
      audio.request.startSeconds !== intent.startSeconds ||
      audio.request.endSeconds !== intent.endSeconds ||
      Math.abs(audio.decodedAudio.samples - samples) > 1 ||
      !sha.test(audio.decodedAudio.sha256) ||
      audio.reviewer.promptSha256 !== questionnaireSha256 ||
      !sha.test(audio.reviewer.runnerSha256) ||
      JSON.stringify(audio.modelAudioInput.featureShape) !==
        (intent.audioBackend === 'qwen2.5-omni'
          ? '[1,128,30000]'
          : '[1,128,3000]') ||
      Math.abs(audio.modelAudioInput.attendedFrames - frames) > 1 ||
      audio.modelAudioInput.audioTokens !== tokens ||
      tokens <= 1 ||
      !sha.test(audio.modelAudioInput.featureSha256) ||
      audio.observations.length !== audioQuestions.length ||
      audio.observations.some(
        (row, index) =>
          row.question !== audioQuestions[index] ||
          row.response.length > 6000 ||
          (row.usable &&
            (row.response.trim().length === 0 ||
              row.issues.length !== 0 ||
              /\d/u.test(row.response))) ||
          (!row.usable && row.issues.length === 0),
      ) ||
      audio.observationContractPassed !==
        audio.observations.every(row => row.usable) ||
      (receipt.status === 'observed') !== audio.observationContractPassed
    )
      throw new Error(
        'Audio observations lack the exact attended source range.',
      )
  } else if (intent.kind === 'speech') {
    const speech = Schema.decodeUnknownSync(SpeechBinding)(raw)
    if (
      receipt.status !== 'recognized-unverified' ||
      speech.request.briefSha256 !== intent.briefSha256 ||
      speech.request.lyrics !== intent.lyrics ||
      speech.request.language !== intent.language ||
      Math.abs(speech.durationProcessed - intent.sourceDuration) > 0.001 ||
      Math.abs(
        speech.decodedAudio.samples - Math.round(intent.sourceDuration * 16000),
      ) > 1 ||
      !sha.test(speech.decodedAudio.sha256) ||
      !sha.test(speech.runnerSha256)
    )
      throw new Error(
        'Speech observations differ from the frozen native lyrics.',
      )
  } else {
    const alignment = Schema.decodeUnknownSync(AlignmentBinding)(raw)
    const lines = intent.lyrics.split(/\r?\n/u)
    const selected = (intent.lineIndices ?? [])
      .map(index => lines[index])
      .join(' ')
    const spellings = selected.trim().split(/\s+/u)
    const samples = Math.round(
      (intent.endSeconds - intent.startSeconds) * 16000,
    )
    if (
      receipt.status !== 'aligned-unverified' ||
      alignment.request.briefSha256 !== intent.briefSha256 ||
      alignment.request.language !== intent.language ||
      alignment.request.lyrics !== intent.lyrics ||
      alignment.request.startSeconds !== intent.startSeconds ||
      alignment.request.endSeconds !== intent.endSeconds ||
      JSON.stringify(alignment.request.lineIndices) !==
        JSON.stringify(intent.lineIndices) ||
      alignment.request.device !== (intent.alignmentDevice ?? 'cuda') ||
      alignment.runtime.device !== (intent.alignmentDevice ?? 'cuda') ||
      alignment.runtime.cpuThreads !== 4 ||
      alignment.canonicalText !== selected ||
      Math.abs(alignment.decodedAudio.samples - samples) > 1 ||
      !sha.test(alignment.decodedAudio.sha256) ||
      !sha.test(alignment.runnerSha256) ||
      !sha.test(alignment.modelAudioInput.featureSha256) ||
      alignment.words.length !== spellings.length
    )
      throw new Error(
        'Forced alignment differs from its selected canonical words or audio range.',
      )
    if (alignment.model === 'Systran/faster-whisper-large-v3') {
      if (
        (intent.alignmentBackend ?? 'whisper') !== 'whisper' ||
        alignment.runtime.computeType !==
          (intent.alignmentDevice === 'cpu'
            ? 'int8_float32'
            : 'int8_float16') ||
        JSON.stringify(alignment.modelAudioInput.featureShape) !==
          '[128,3000]' ||
        alignment.modelAudioInput.attendedFrames !==
          Math.ceil(alignment.decodedAudio.samples / 160) ||
        !Number.isSafeInteger(alignment.modelAudioInput.textTokens) ||
        alignment.modelAudioInput.textTokens < 1 ||
        alignment.modelAudioInput.textTokens > 444
      )
        throw new Error(
          'Whisper alignment has a different backend or incomplete attended audio.',
        )
    } else {
      const input = alignment.modelAudioInput
      const frames = Math.floor(alignment.decodedAudio.samples / 160)
      if (
        intent.alignmentBackend !== 'indic-conformer-ctc' ||
        !Number.isSafeInteger(input.attendedFrames) ||
        input.attendedFrames < frames ||
        input.attendedFrames > frames + 1 ||
        input.featureShape.length !== 3 ||
        input.featureShape[0] !== 1 ||
        input.featureShape[1] !== 80 ||
        !Number.isSafeInteger(input.featureShape[2]) ||
        (input.featureShape[2] ?? 0) < input.attendedFrames ||
        (input.featureShape[2] ?? 0) > frames + 16 ||
        input.ctcFrames !== Math.floor((input.attendedFrames - 1) / 4) + 1 ||
        !sha.test(input.ctcSha256)
      )
        throw new Error(
          'CTC alignment has a different backend or incomplete attended audio.',
        )
      for (const word of alignment.words) {
        const start = intent.startSeconds + word.startFrame * input.frameSeconds
        const end = Math.min(
          intent.endSeconds,
          intent.startSeconds + word.endFrame * input.frameSeconds,
        )
        if (
          !Number.isSafeInteger(word.startFrame) ||
          !Number.isSafeInteger(word.endFrame) ||
          word.startFrame < 0 ||
          word.endFrame <= word.startFrame ||
          word.endFrame > input.ctcFrames ||
          Math.abs(word.startSeconds - start) > 0.000001 ||
          Math.abs(word.endSeconds - end) > 0.000001
        )
          throw new Error(
            'CTC word evidence differs from its actual emitted frame range.',
          )
      }
    }
    const state = { end: intent.startSeconds, passed: true }
    for (const [index, word] of alignment.words.entries()) {
      if (
        word.wordIndex !== index ||
        word.text !== spellings[index] ||
        !Number.isFinite(word.startSeconds) ||
        !Number.isFinite(word.endSeconds) ||
        !Number.isFinite(word.probability) ||
        word.startSeconds < state.end - 0.02 ||
        word.startSeconds < intent.startSeconds ||
        word.endSeconds < word.startSeconds ||
        word.endSeconds > intent.endSeconds + 0.04 ||
        word.probability < 0 ||
        word.probability > 1 ||
        (((index === 0 && word.startSeconds - intent.startSeconds <= 0.02) ||
          word.startSeconds === word.endSeconds ||
          word.probability < 0.6) &&
          word.issues.length === 0)
      )
        throw new Error(
          'Canonical word alignment has invalid or unreported uncertain timing.',
        )
      state.end = word.endSeconds
      state.passed = state.passed && word.issues.length === 0
    }
    if (state.passed !== alignment.alignmentContractPassed)
      throw new Error('Alignment qualification contradicts its word evidence.')
  }
  return raw
}
