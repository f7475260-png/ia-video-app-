import axios from 'axios';
import path from 'path';
import fs from 'fs-extra';

export async function synthesizeNarration({ segments, tmpDir, provider, language }) {
  if (provider !== 'elevenlabs') {
    // Pas de TTS: renvoie une piste muette par segment (sera géré au montage)
    return { provider: 'none', items: segments.map(s => ({ index: s.index, path: null })) };
  }
  const key = process.env.ELEVENLABS_API_KEY;
  const voice = process.env.ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM'; // voix par défaut (si autorisée)
  if (!key) return { provider: 'none', items: segments.map(s => ({ index: s.index, path: null })) };

  const baseUrl = 'https://api.elevenlabs.io/v1/text-to-speech/' + voice;
  const items = [];
  for (const s of segments) {
    const payload = {
      text: s.text,
      model_id: 'eleven_monolingual_v1',
      voice_settings: { stability: 0.4, similarity_boost: 0.8 }
    };
    const out = path.join(tmpDir, `seg${s.index}.mp3`);
    const res = await axios.post(baseUrl, payload, {
      headers: { 'xi-api-key': key, 'content-type': 'application/json' },
      responseType: 'arraybuffer'
    });
    await fs.outputFile(out, res.data);
    items.push({ index: s.index, path: out });
  }
  return { provider: 'elevenlabs', items };
}
