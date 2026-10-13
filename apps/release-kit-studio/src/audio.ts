export const decodedAudioDuration = (
  bytes: ArrayBuffer,
  signal: AbortSignal,
): Promise<number> =>
  new Promise((resolve, reject) => {
    if (signal.aborted) {
      reject(new Error('Audio inspection was interrupted.'))
      return
    }
    const context = new OfflineAudioContext(1, 1, 16000)
    const abort = () => {
      signal.removeEventListener('abort', abort)
      reject(new Error('Audio inspection was interrupted.'))
    }
    signal.addEventListener('abort', abort, { once: true })
    Promise.resolve()
      .then(() => {
        signal.throwIfAborted()
        return context.decodeAudioData(bytes)
      })
      .then(
        audio => {
          signal.removeEventListener('abort', abort)
          if (signal.aborted) return
          const duration = audio.length / audio.sampleRate
          if (!Number.isFinite(duration) || duration <= 0 || duration > 900) {
            reject(new Error('Choose readable audio up to 15 minutes long.'))
            return
          }
          resolve(duration)
        },
        () => {
          signal.removeEventListener('abort', abort)
          reject(
            new Error('This audio could not be decoded. Try WAV, MP3, or M4A.'),
          )
        },
      )
  })
