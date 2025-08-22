import path from 'path';
import fs from 'fs-extra';
import ffmpegPath from 'ffmpeg-static';
import ffmpeg from 'fluent-ffmpeg';
import { expandPromptToSegments } from './llm.js';
import { fetchAssetsForSegments } from './stock.js';
import { synthesizeNarration } from './tts.js';
import { buildSRT } from './subtitles.js';
import { composeVideo } from './video.js';

ffmpeg.setFfmpegPath(ffmpegPath);

export async function generateVideo(opts) {
  const {
    id, prompt, durationSec, format, language,
    ttsProvider, subtitles, onProgress
  } = opts;

  const OUTPUT_DIR = process.env.OUTPUT_DIR || './outputs';
  const jobDir = path.join(OUTPUT_DIR, id);
  const tmpDir = path.join(jobDir, 'tmp');
  await fs.ensureDir(tmpDir);

  onProgress?.(3, 'Génération du plan...');
  const segments = expandPromptToSegments({ prompt, language, totalDurationSec: durationSec });

  onProgress?.(15, 'Récupération des médias libres...');
  const media = await fetchAssetsForSegments({ segments, tmpDir });

  onProgress?.(35, ttsProvider === 'none' ? 'Ignorer la narration' : 'Synthèse vocale...');
  const narration = await synthesizeNarration({ segments, tmpDir, provider: ttsProvider, language });

  onProgress?.(55, 'Création des sous-titres...');
  const srtPath = path.join(jobDir, `${id}.srt`);
  await fs.outputFile(srtPath, buildSRT(segments));

  onProgress?.(60, 'Montage vidéo...');
  const resolution = format === 'short' ? { w: 1080, h: 1920 } : { w: 1920, h: 1080 };
  const outPath = path.join(jobDir, `${id}.mp4`);
  await composeVideo({
    id, segments, media, narration, srtPath,
    outPath, resolution, tmpDir, burnSubtitles: true
  }, (p, m) => onProgress?.(60 + Math.round(p * 0.38), m));

  onProgress?.(100, 'Nettoyage...');
  return { video: outPath, srt: srtPath };
}
