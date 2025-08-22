// Simple SRT builder à partir des segments (start/end en secondes)
function fmtTime(t) {
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  const s = Math.floor(t % 60);
  const ms = Math.floor((t - Math.floor(t)) * 1000);
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')},${String(ms).padStart(3,'0')}`;
}

export function buildSRT(segments) {
  return segments.map((seg, i) => {
    const idx = i + 1;
    const start = fmtTime(seg.start);
    const end = fmtTime(seg.end);
    const text = seg.text.replace(/\s+/g, ' ').trim();
    return `${idx}\n${start} --> ${end}\n${text}\n`;
  }).join('\n');
}
