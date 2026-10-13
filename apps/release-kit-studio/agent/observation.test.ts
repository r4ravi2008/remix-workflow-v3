// @vitest-environment node
import { createHash } from 'node:crypto'
import { describe, expect, it } from 'vitest'

import {
  type ObservationIntent,
  audioQuestions,
  observationKey,
  validateObservationIntent,
  validateObservationReceipt,
} from './observation'

const intent: ObservationIntent = {
  schemaVersion: 1,
  id: 'a'.repeat(64),
  kind: 'audio-window',
  jobId: '8f55a7a3-e2df-4239-ab5f-603ad55d070b',
  releaseId: '92a6e687-e9ec-4325-a767-f44a56c73d84',
  briefSha256: 'b'.repeat(64),
  sourceSha256: 'c'.repeat(64),
  sourceBytes: 46018732,
  sourceDuration: 239.68,
  language: 'Telugu',
  lyrics: 'ప్రతి నిమిషం',
  startSeconds: 60,
  endSeconds: 68,
}
const fixture = () => ({
  schemaVersion: 2,
  status: 'observed',
  request: { ...intent },
  source: { sha256: intent.sourceSha256, bytes: intent.sourceBytes },
  reviewer: {
    model: 'Qwen/Qwen2-Audio-7B-Instruct',
    revision: '0a095220c30b7b31434169c3086508ef3ea5bf0a',
    quantization: 'nf4-text-bf16-audio',
    promptSha256: createHash('sha256')
      .update(JSON.stringify(audioQuestions))
      .digest('hex'),
    runnerSha256: 'd'.repeat(64),
  },
  decodedAudio: { sampleRate: 16000, samples: 128000, sha256: 'e'.repeat(64) },
  modelAudioInput: {
    featureShape: [1, 128, 3000],
    attendedFrames: 800,
    audioTokens: 200,
    featureSha256: 'f'.repeat(64),
  },
  observations: audioQuestions.map(question => ({
    question,
    response: 'Singing over a repeated synth pattern.',
    usable: true,
    issues: Array<string>(),
    semanticVerified: false,
  })),
  observationContractPassed: true,
  modelLoad: {
    thinkerOnly: true,
    missingKeys: 0,
    mismatchedKeys: 0,
    discardedAudioGenerationKeys: 12,
  },
  audioPerceptionComplete: true,
  semanticFindingsVerified: false,
  fullSongHeard: false,
  pilotApproved: false,
  humanAccepted: false,
})
const ctcIntent: ObservationIntent = {
  ...intent,
  kind: 'lyric-alignment',
  lineIndices: [0],
  alignmentDevice: 'cpu',
  alignmentBackend: 'indic-conformer-ctc',
}
const ctcFixture = () => ({
  status: 'aligned-unverified',
  request: { ...ctcIntent, device: 'cpu' },
  source: { sha256: intent.sourceSha256, bytes: intent.sourceBytes },
  model: 'OpenVoiceOS/ai4bharat-indicconformer-te-onnx',
  revision: 'd952dec2a1d256a1569cdfc9a9615cba05a1a2e3',
  runnerSha256: 'a'.repeat(64),
  weights: {
    sha256: 'd615acecbfcffca3fa04ed8bc62284ba30cf48f90f537d4d0040b1b0e75f0b1c',
    bytes: 137677313,
  },
  runtime: {
    device: 'cpu',
    provider: 'CPUExecutionProvider',
    computeType: 'int8',
    cpuThreads: 4,
  },
  preprocessor: {
    package: 'onnx-asr',
    version: '0.12.0',
    sha256: '7ab6b0d1f57832e56f59aa7cab4289de50df7f8d5296cdfd281d9c9b7b8d73e0',
    bytes: 89473,
  },
  vocabulary: {
    sha256: 'dc0b7bbb9eca8d3c8aebf1eb86e3144c90d692b4008cf5a32d46437b942b23ac',
    bytes: 2706,
  },
  canonicalText: 'ప్రతి నిమిషం',
  alignmentComplete: true,
  alignmentContractPassed: true,
  decodedAudio: { sampleRate: 16000, samples: 128000, sha256: 'b'.repeat(64) },
  modelAudioInput: {
    featureShape: [1, 80, 801],
    attendedFrames: 800,
    ctcFrames: 200,
    frameSeconds: 0.04,
    featureSha256: 'c'.repeat(64),
    ctcSha256: 'd'.repeat(64),
  },
  nativeTokenization: 'exact-piece-lattice-without-transliteration',
  words: [
    {
      wordIndex: 0,
      text: 'ప్రతి',
      startFrame: 3,
      endFrame: 25,
      startSeconds: 60.12,
      endSeconds: 61,
      probability: 0.9,
      issues: Array<string>(),
      verified: false,
    },
    {
      wordIndex: 1,
      text: 'నిమిషం',
      startFrame: 25,
      endFrame: 50,
      startSeconds: 61,
      endSeconds: 62,
      probability: 0.9,
      issues: Array<string>(),
      verified: false,
    },
  ],
  lyricTimingVerified: false,
  canonicalLyricsChanged: false,
  fullSongHeard: false,
  pilotApproved: false,
  humanAccepted: false,
})

describe('source-bound model evidence', () => {
  it('accepts only the pinned audio backend selected by the immutable operation', () => {
    const omniIntent: ObservationIntent = {
      ...intent,
      audioBackend: 'qwen2.5-omni',
    }
    const row = fixture()
    row.modelAudioInput.featureShape = [1, 128, 30000]
    row.reviewer = {
      ...row.reviewer,
      model: 'Qwen/Qwen2.5-Omni-7B',
      revision: 'ae9e1690543ffd5c0221dc27f79834d0294cba00',
      quantization: 'nf4-text-bf16-audio-vision-thinker-only',
    }
    expect(validateObservationReceipt(omniIntent, row)).toEqual(row)
    expect(() => validateObservationReceipt(intent, row)).toThrow()
    expect(() => validateObservationReceipt(omniIntent, fixture())).toThrow()
    row.reviewer.revision = 'a'.repeat(40)
    expect(() => validateObservationReceipt(omniIntent, row)).toThrow()
    expect(() =>
      validateObservationIntent({
        ...omniIntent,
        kind: 'speech',
        startSeconds: 0,
        endSeconds: intent.sourceDuration,
      }),
    ).toThrow('fixed audio backend')
    expect(observationKey(omniIntent)).not.toEqual(observationKey(intent))
  })
  it('rejects Omni receipts with truncated features or an extra odd-length audio token', () => {
    const omniIntent: ObservationIntent = {
      ...intent,
      audioBackend: 'qwen2.5-omni',
      endSeconds: 68.01,
    }
    const row = fixture()
    row.request.endSeconds = omniIntent.endSeconds
    row.decodedAudio.samples = 128160
    row.modelAudioInput.featureShape = [1, 128, 30000]
    row.modelAudioInput.attendedFrames = 801
    row.reviewer = {
      ...row.reviewer,
      model: 'Qwen/Qwen2.5-Omni-7B',
      revision: 'ae9e1690543ffd5c0221dc27f79834d0294cba00',
      quantization: 'nf4-text-bf16-audio-vision-thinker-only',
    }
    expect(validateObservationReceipt(omniIntent, row)).toEqual(row)
    row.modelAudioInput.audioTokens = 201
    expect(() => validateObservationReceipt(omniIntent, row)).toThrow()
    row.modelAudioInput.audioTokens = 200
    row.modelAudioInput.featureShape = [1, 128, 801]
    expect(() => validateObservationReceipt(omniIntent, row)).toThrow()
  })
  it('binds CTC evidence to the pinned native model, preprocessing and explicit CPU selection', () => {
    const row = ctcFixture()
    expect(validateObservationReceipt(ctcIntent, row)).toEqual(row)
    for (const change of [
      { alignmentDevice: 'cuda' as const },
      { language: 'Hindi' as const },
    ])
      expect(() =>
        validateObservationIntent({ ...ctcIntent, ...change }),
      ).toThrow()
    const changed = ctcFixture()
    changed.preprocessor.sha256 = 'f'.repeat(64)
    expect(() => validateObservationReceipt(ctcIntent, changed)).toThrow()
    expect(() =>
      validateObservationReceipt(
        { ...ctcIntent, alignmentBackend: undefined },
        row,
      ),
    ).toThrow()
  })
  it('rejects CTC timing outside the actual token-emission grid and incomplete feature coverage', () => {
    const invented = ctcFixture()
    invented.words[0]!.startSeconds = 60.15
    expect(() => validateObservationReceipt(ctcIntent, invented)).toThrow(
      'emitted frame range',
    )
    const truncated = ctcFixture()
    truncated.modelAudioInput.attendedFrames = 700
    expect(() => validateObservationReceipt(ctcIntent, truncated)).toThrow(
      'incomplete attended audio',
    )
    const asserted = ctcFixture()
    asserted.lyricTimingVerified = true
    expect(() => validateObservationReceipt(ctcIntent, asserted)).toThrow()
  })
  it('selects distinct chronological native lines only for forced alignment', () => {
    const alignment: ObservationIntent = {
      ...intent,
      kind: 'lyric-alignment',
      lineIndices: [0, 2],
      lyrics: 'ప్రతి నిమిషం\nనీ రూపమే\nప్రతి నిమిషం',
    }
    const value: ObservationIntent = { ...intent, kind: 'lyric-alignment' }
    expect(() => validateObservationIntent(value)).toThrow()
    expect(validateObservationIntent(alignment).lineIndices).toEqual([0, 2])
    for (const indices of [[2, 0], [0, 0], [3], [0.5], []])
      expect(() =>
        validateObservationIntent({ ...alignment, lineIndices: indices }),
      ).toThrow()
    expect(() =>
      validateObservationIntent({ ...intent, lineIndices: [0] }),
    ).toThrow()
  })

  it('requires canonical word spellings, exact range and explicit uncertainty in alignment receipts', () => {
    const alignmentIntent: ObservationIntent = {
      ...intent,
      kind: 'lyric-alignment',
      lineIndices: [0],
    }
    const raw = {
      status: 'aligned-unverified',
      request: { ...alignmentIntent, device: 'cuda' },
      runtime: { device: 'cuda', computeType: 'int8_float16', cpuThreads: 4 },
      source: { sha256: intent.sourceSha256, bytes: intent.sourceBytes },
      model: 'Systran/faster-whisper-large-v3',
      revision: 'edaa852ec7e145841d8ffdb056a99866b5f0a478',
      runnerSha256: 'a'.repeat(64),
      weights: {
        sha256:
          '69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1',
        bytes: 3087284237,
      },
      canonicalText: 'ప్రతి నిమిషం',
      alignmentComplete: true,
      alignmentContractPassed: true,
      decodedAudio: {
        sampleRate: 16000,
        samples: 128000,
        sha256: 'b'.repeat(64),
      },
      modelAudioInput: {
        featureShape: [128, 3000],
        attendedFrames: 800,
        textTokens: 12,
        featureSha256: 'c'.repeat(64),
      },
      words: [
        {
          wordIndex: 0,
          text: 'ప్రతి',
          startSeconds: 60.1,
          endSeconds: 61,
          probability: 0.9,
          issues: Array<string>(),
          verified: false,
        },
        {
          wordIndex: 1,
          text: 'నిమిషం',
          startSeconds: 61,
          endSeconds: 62,
          probability: 0.9,
          issues: Array<string>(),
          verified: false,
        },
      ],
      lyricTimingVerified: false,
      canonicalLyricsChanged: false,
      fullSongHeard: false,
      pilotApproved: false,
      humanAccepted: false,
    }
    expect(validateObservationReceipt(alignmentIntent, raw)).toEqual(raw)
    const cropEdge = structuredClone(raw)
    cropEdge.words[0]!.startSeconds = 60
    expect(() =>
      validateObservationReceipt(alignmentIntent, cropEdge),
    ).toThrow()
    cropEdge.words[0]!.issues = ['crop-boundary-onset-unresolved']
    cropEdge.alignmentContractPassed = false
    expect(validateObservationReceipt(alignmentIntent, cropEdge)).toEqual(
      cropEdge,
    )
    const changed = structuredClone(raw)
    changed.words[0]!.text = 'ప్రతీ'
    expect(() => validateObservationReceipt(alignmentIntent, changed)).toThrow()
    const outside = structuredClone(raw)
    outside.words[1]!.endSeconds = 70
    expect(() => validateObservationReceipt(alignmentIntent, outside)).toThrow()
    const uncertain = structuredClone(raw)
    uncertain.words[0]!.probability = 0.1
    expect(() =>
      validateObservationReceipt(alignmentIntent, uncertain),
    ).toThrow()
    uncertain.words[0]!.issues = ['uncertain-canonical-word']
    uncertain.alignmentContractPassed = false
    expect(validateObservationReceipt(alignmentIntent, uncertain)).toEqual(
      uncertain,
    )
  })
  it('keeps exact native lyrics and distinct brief/range identities', () => {
    expect(validateObservationIntent(intent).lyrics).toBe('ప్రతి నిమిషం')
    expect(observationKey(intent)).not.toBe(
      observationKey({ ...intent, briefSha256: 'd'.repeat(64) }),
    )
    expect(observationKey(intent)).not.toBe(
      observationKey({ ...intent, startSeconds: 61 }),
    )
    for (const invalid of [
      { endSeconds: 100 },
      { sourceDuration: Infinity },
      { sourceBytes: 1.5 },
      { jobId: 'foreign' },
    ])
      expect(() =>
        validateObservationIntent({ ...intent, ...invalid }),
      ).toThrow()
    expect(() =>
      validateObservationIntent({ ...intent, kind: 'speech' }),
    ).toThrow()
  })

  it('rejects foreign source, incomplete attended audio and false review claims', () => {
    expect(validateObservationReceipt(intent, fixture())).toEqual(fixture())
    const foreign = fixture()
    foreign.request.releaseId = crypto.randomUUID()
    const truncated = fixture()
    truncated.modelAudioInput.attendedFrames = 400
    const textOnly = fixture()
    textOnly.modelAudioInput.audioTokens = 1
    const altered = fixture()
    altered.decodedAudio.samples = 64000
    const asserted = fixture()
    asserted.fullSongHeard = true
    for (const invalid of [foreign, truncated, textOnly, altered, asserted])
      expect(() => validateObservationReceipt(intent, invalid)).toThrow()
  })

  it('preserves invalid observations without accepting their timing claims', () => {
    const row = fixture()
    row.status = 'observed-with-issues'
    row.observationContractPassed = false
    row.observations[0] = {
      question: audioQuestions[0] ?? '',
      response: 'A transition happens at 3:20.',
      usable: false,
      issues: ['Unmeasured timing'],
      semanticVerified: false,
    }
    expect(validateObservationReceipt(intent, row)).toEqual(row)
    row.observations[0].usable = true
    row.observations[0].issues = []
    row.observationContractPassed = true
    row.status = 'observed'
    expect(() => validateObservationReceipt(intent, row)).toThrow()
  })

  it('preserves terminal failure without converting it into coverage or approval', () => {
    const failed = {
      ...fixture(),
      status: 'failed',
      audioPerceptionComplete: false,
    }
    expect(() => validateObservationReceipt(intent, failed)).toThrow(
      'qualification failed',
    )
  })
})
