export type SSEDataHandler = (data: string) => void

export async function readSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onData: SSEDataHandler
) {
  const decoder = new TextDecoder()
  let buffer = ''
  let finished = false

  const processEvent = (event: string) => {
    const data = event
      .split(/\r?\n/)
      .filter(line => line.startsWith('data:'))
      .map(line => line.slice(5).replace(/^ /, ''))
      .join('\n')

    if (!data) return
    if (data === '[DONE]') {
      finished = true
      return
    }
    onData(data)
  }

  const processBuffer = (flush = false) => {
    while (!finished) {
      const boundary = buffer.match(/\r?\n\r?\n/)
      if (!boundary || boundary.index === undefined) break

      const event = buffer.slice(0, boundary.index)
      buffer = buffer.slice(boundary.index + boundary[0].length)
      processEvent(event)
    }

    if (flush && buffer.trim() && !finished) {
      processEvent(buffer)
      buffer = ''
    }
  }

  try {
    while (!finished) {
      const { done, value } = await reader.read()
      if (done) {
        buffer += decoder.decode()
        processBuffer(true)
        break
      }

      buffer += decoder.decode(value, { stream: true })
      processBuffer()
    }
  } finally {
    reader.releaseLock()
  }
}
