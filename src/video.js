import ffmpegPath from 'ffmpeg-static';
import ffmpeg from 'fluent-ffmpeg';
import path from 'path';
import fs from 'fs-extra';

ffmpeg.setFfmpegPath(ffmpegPath);

// Stratégie:
// 1) Pour chaque segment: générer un clip segment_i.mp4
//    - Si vidéo source: découpe, recadrage, scale, pad
//    - Si image: zoompan (Ken Burns) pendant seg.duration
//    - Si narration dispo: on garde l'audio du TTS pour ce clip, sinon silence
// 2) Concaténer tous les clips
// 3) Ajouter sous-titres (burn-in) à la fin pour éviter désync
export async function composeVideo({ id, segments, media, narration, srtPath, outPath, resolution, tmpDir, burnSubtitles }, onp) {
  const { w, h } = resolution;
  const segOutputs = [];

  for (const seg of segments) {
    onp?.(progressRatio(segments.length, seg.index, 0.1), `Préparation segment ${seg.index}/${segments.length}`);
    const m = media.find(x => x.index === seg.index);
    const n = narration?.items?.find(x => x.index === seg.index);
    const out = path.join(tmpDir, `clip_${seg.index}.mp4`);
    if (m?.type === 'video') {
      await makeVideoClip({ src: m.path, out, duration: seg.duration, w, h, audio: n?.path || null });
    } else {
      await makeImageClip({ src: m?.path, out, duration: seg.duration, w, h, audio: n?.path || null });
    }
    segOutputs.push(out);
  }

  const concatPath = path.join(tmpDir, `concat_${id}.mp4`);
  await concatClips(segOutputs, concatPath);

  if (burnSubtitles && await fs.pathExists(srtPath)) {
    await burnInSubtitles(concatPath, srtPath, outPath);
  } else {
    await fs.copy(concatPath, outPath);
  }
}

function progressRatio(total, idx, base) {
  return base + (idx / total) * (1 - base);
}

async function makeVideoClip({ src, out, duration, w, h, audio }) {
  return new Promise((resolve, reject) => {
    let cmd = ffmpeg(src)
      .videoFilters([
        `scale=w=${w}:h=${h}:force_original_aspect_ratio=cover`,
        `crop=${w}:${h}`,
      ])
      .setDuration(duration)
      .outputOptions(['-r 30', '-pix_fmt yuv420p', '-preset veryfast'])
      .on('end', resolve)
      .on('error', reject);

    if (audio) {
      cmd = cmd.input(audio).audioCodec('aac').outputOptions(['-shortest']);
    } else {
      cmd = cmd.outputOptions(['-an']);
    }
    cmd.save(out);
  });
}

async function makeImageClip({ src, out, duration, w, h, audio }) {
  // Effet Ken Burns simple: zoom 1.0→1.1 et pan horizontal
  const fps = 30;
  const zoomStart = 1.0, zoomEnd = 1.1;
  const filter = [
    `scale=${w}:${h}:force_original_aspect_ratio=cover`,
    `crop=${w}:${h}`,
    `zoompan=z='zoom+(${zoomEnd - zoomStart})/${duration}/${fps}':x='iw*(on/${duration}/${fps})':y=0:d=${duration*fps}:s=${w}x${h}`
  ];

  return new Promise((resolve, reject) => {
    let cmd = ffmpeg(src)
      .loop(duration)
      .videoFilters(filter)
      .inputOptions(['-framerate 1'])
      .outputOptions(['-t ' + duration, '-r 30', '-pix_fmt yuv420p', '-preset veryfast'])
      .on('end', resolve)
      .on('error', reject);

    if (audio) {
      cmd = cmd.input(audio).audioCodec('aac').outputOptions(['-shortest']);
    } else {
      cmd = cmd.outputOptions(['-an']);
    }
    cmd.save(out);
  });
}

async function concatClips(files, out) {
  const listPath = out + '.txt';
  const list = files.map(f => `file '${f.replace(/'/g, "'\\''")}'`).join('\n');
  await fs.outputFile(listPath, list);
  return new Promise((resolve, reject) => {
    ffmpeg()
      .input(listPath)
      .inputOptions(['-f concat', '-safe 0'])
      .outputOptions(['-c copy'])
      .on('end', resolve)
      .on('error', reject)
      .save(out);
  });
}

async function burnInSubtitles(input, srt, out) {
  return new Promise((resolve, reject) => {
    ffmpeg(input)
      .videoFilters(`subtitles='${srt.replace(/:/g, '\\:')}'`)
      .outputOptions(['-c:a copy', '-pix_fmt yuv420p', '-preset veryfast'])
      .on('end', resolve)
      .on('error', reject)
      .save(out);
  });
}
