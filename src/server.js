import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs-extra';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';
import { generateVideo } from './generator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));
app.use(express.static(path.join(__dirname, '..', 'public')));

const OUTPUT_DIR = process.env.OUTPUT_DIR || './outputs';
await fs.ensureDir(OUTPUT_DIR);

const jobs = new Map(); // id -> { status, progress, message, error, files }

function updateJob(id, patch) {
  const prev = jobs.get(id) || {};
  const next = { ...prev, ...patch };
  jobs.set(id, next);
}

app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, durationSec, format, language, ttsProvider, subtitles } = req.body || {};
    if (!prompt || !durationSec || !format || !language) {
      return res.status(400).json({ error: 'Paramètres manquants' });
    }
    const max = Number(process.env.MAX_DURATION_SEC || 300);
    const safeDuration = Math.min(Number(durationSec), max);
    const id = uuidv4();
    updateJob(id, { status: 'queued', progress: 0, message: 'En file', error: null, files: null });

    // Process async
    (async () => {
      try {
        updateJob(id, { status: 'running', message: 'Préparation...' });
        const files = await generateVideo({
          id, prompt, durationSec: safeDuration, format, language,
          ttsProvider: ttsProvider || 'none', subtitles: !!subtitles,
          onProgress: (p, m) => updateJob(id, { progress: p, message: m })
        });
        updateJob(id, { status: 'done', progress: 100, message: 'Terminé', files });
      } catch (err) {
        console.error(err);
        updateJob(id, { status: 'error', error: err?.message || String(err), message: 'Erreur' });
      }
    })();

    res.json({ id });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/status/:id', (req, res) => {
  const job = jobs.get(req.params.id);
  if (!job) return res.status(404).json({ error: 'Job inconnu' });
  res.json(job);
});

app.get('/api/download/:id', async (req, res) => {
  const job = jobs.get(req.params.id);
  if (!job || job.status !== 'done' || !job.files) return res.status(404).end();
  const type = req.query.type === 'srt' ? 'srt' : 'mp4';
  const file = type === 'mp4' ? job.files.video : job.files.srt;
  if (!file || !(await fs.pathExists(file))) return res.status(404).end();
  res.download(file);
});

const port = Number(process.env.PORT || 3000);
app.listen(port, () => {
  console.log(`Server on http://localhost:${port}`);
});
