import axios from 'axios';
import path from 'path';
import fs from 'fs-extra';

const PEXELS_API_KEY = process.env.PEXELS_API_KEY;

export async function fetchAssetsForSegments({ segments, tmpDir }) {
  if (!PEXELS_API_KEY) throw new Error('PEXELS_API_KEY manquant');
  const headers = { Authorization: PEXELS_API_KEY };
  const results = [];

  for (const seg of segments) {
    const q = cleanQuery(seg.title + ' ' + seg.text);
    // 1) Essayer une vidéo Pexels
    let filePath = null;
    try {
      const v = await axios.get('https://api.pexels.com/videos/search', { headers, params: { query: q, per_page: 1 } });
      const video = v.data?.videos?.[0];
      if (video) {
        const file = bestVideoFile(video);
        if (file?.link) {
          filePath = await download(file.link, path.join(tmpDir, `seg${seg.index}.mp4`));
          results.push({ type: 'video', path: filePath, index: seg.index });
          continue;
        }
      }
    } catch {}

    // 2) Sinon, image Pexels
    try {
      const i = await axios.get('https://api.pexels.com/v1/search', { headers, params: { query: q, per_page: 1 } });
      const photo = i.data?.photos?.[0];
      if (photo?.src?.large2x) {
        filePath = await download(photo.src.large2x, path.join(tmpDir, `seg${seg.index}.jpg`));
        results.push({ type: 'image', path: filePath, index: seg.index });
        continue;
      }
    } catch {}

    // 3) Dernier recours: fond neutre
    const fallback = await makeSolidImage(path.join(tmpDir, `seg${seg.index}_fallback.jpg`));
    results.push({ type: 'image', path: fallback, index: seg.index });
  }
  return results;
}

function bestVideoFile(video) {
  // privilégier 1080p mp4
  const files = (video?.video_files || []).filter(f => f.file_type === 'video/mp4');
  files.sort((a,b) => (b.height||0) - (a.height||0));
  return files[0] || video?.video_files?.[0];
}

async function download(url, outPath) {
  const res = await axios.get(url, { responseType: 'arraybuffer' });
  await fs.outputFile(outPath, res.data);
  return outPath;
}

function cleanQuery(s) {
  return String(s).replace(/[:]/g, ' ').slice(0, 100);
}

async function makeSolidImage(outPath) {
  // image grise 1920x1080 en base64 minimaliste
  const { createCanvas } = await import('canvas'); // nécessite node-canvas si non dispo -> alternative: image prépackagée
  const w = 1920, h = 1080;
  const canvas = createCanvas(w, h);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#111827'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#374151'; for (let i=0; i<10; i++){ ctx.fillRect(i*200, 0, 100, h); }
  const buf = canvas.toBuffer('image/jpeg', { quality: 0.9 });
  await fs.outputFile(outPath, buf);
  return outPath;
}
