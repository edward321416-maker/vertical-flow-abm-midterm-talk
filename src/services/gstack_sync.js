'use strict';
/**
 * gstack_sync.js
 * Google Sheets API v4 data loader, Google Drive API v3 PNG/SVG archiver and execution logger.
 *
 * Offline-first: nothing here is required to render the poster. When credentials are missing, the network fails or the
 * quota is exhausted, loadBoundaryData() falls back to src/data/aik_boundary_rep.json and the poster still renders.
 *
 * Environment:
 *   GOOGLE_APPLICATION_CREDENTIALS  path to a Service Account JSON key
 *   GSTACK_SHEET_ID                 spreadsheet id (live boundary data + 'CLAUDECODE Execution Log' tab)
 *   GSTACK_SHEET_RANGE              optional, default 'alk_boundary_rep!A1:I17' (the tab name is the user's own sheet tab)
 *   GSTACK_DRIVE_FOLDER_ID          Drive folder for the exported PNG / SVG (optional upload)
 *
 * Expected sheet layout (header row + 16 data rows, columns matched by header name, case-insensitive):
 *   scenario (A|B), boundary (1..8 or "1->2F"), flow_avg, flow_sd, anchor, esc_share, elev_share, dominant_mode, retention_pct
 *
 * CLI:
 *   node src/services/gstack_sync.js status
 *   node src/services/gstack_sync.js load
 *   node src/services/gstack_sync.js log --source local-json --resolution 2400x4200 --duration 1300 --status OK [--run-id ID]
 *   node src/services/gstack_sync.js upload <png> <svg>
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const LOCAL_JSON = path.join(ROOT, 'src', 'data', 'aik_boundary_rep.json');
const LOCAL_LOG = path.join(ROOT, '.gstack_execution_log.jsonl');
const LOG_TAB = 'CLAUDECODE Execution Log';
const DEFAULT_RANGE = 'alk_boundary_rep!A1:I17';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** Exponential backoff for HTTP 429 (RATE_LIMIT_EXCEEDED) and 5xx. base 1000 ms, 3 retries, jitter on. */
async function withBackoff(fn, opts) {
  const o = Object.assign({ baseMs: 1000, maxRetries: 3, jitter: true, sleepFn: sleep, rng: Math.random }, opts);
  for (let attempt = 0; ; attempt++) {
    try {
      return await fn(attempt);
    } catch (err) {
      const status = Number((err && (err.code || err.status || (err.response && err.response.status))) || 0);
      const reason = JSON.stringify((err && err.errors) || (err && err.response && err.response.data) || '');
      const retryable = status === 429 || (status >= 500 && status <= 599) || /RATE_LIMIT_EXCEEDED|rateLimitExceeded/.test(reason);
      if (!retryable || attempt >= o.maxRetries) throw err;
      const delay = o.baseMs * Math.pow(2, attempt) + (o.jitter ? Math.floor(o.rng() * o.baseMs) : 0);
      await o.sleepFn(delay);
    }
  }
}

function credentialStatus() {
  const keyPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
  return {
    credentials: !!(keyPath && fs.existsSync(keyPath)),
    sheetId: !!process.env.GSTACK_SHEET_ID,
    driveFolderId: !!process.env.GSTACK_DRIVE_FOLDER_ID,
  };
}

function loadGoogle() {
  try { return require('googleapis').google; } catch (e) { return null; }       // optional dependency
}

async function getClients(scopes) {
  const st = credentialStatus();
  if (!st.credentials) return { error: 'GOOGLE_APPLICATION_CREDENTIALS missing or file not found' };
  const google = loadGoogle();
  if (!google) return { error: "npm package 'googleapis' is not installed" };
  const auth = new google.auth.GoogleAuth({ keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS, scopes });
  return { google, auth };
}

function readLocal() {
  if (!fs.existsSync(LOCAL_JSON)) throw new Error('src/data/aik_boundary_rep.json not found; run python src/data/build_poster_dataset.py');
  return JSON.parse(fs.readFileSync(LOCAL_JSON, 'utf8'));
}

/** Merge live sheet rows into the local dataset (the sheet carries means only; per-run arrays stay local). */
function mergeSheetRows(local, values) {
  const head = values[0].map((h) => String(h).trim().toLowerCase());
  const col = (n) => head.indexOf(n);
  const need = ['scenario', 'boundary', 'flow_avg', 'anchor', 'dominant_mode'];
  need.forEach((n) => { if (col(n) < 0) throw new Error('sheet header missing column: ' + n); });
  const out = JSON.parse(JSON.stringify(local));
  let merged = 0;
  values.slice(1).forEach((r) => {
    const sc = String(r[col('scenario')]).trim().toUpperCase().slice(0, 1);
    const b = parseInt(String(r[col('boundary')]).replace(/[^0-9].*$/, ''), 10);
    const tgt = out.scenarios[sc] && out.scenarios[sc].boundaries[b - 1];
    if (!tgt) return;
    tgt.flow = Math.round(Number(String(r[col('flow_avg')]).replace(/,/g, '')));
    tgt.anchor = Number(r[col('anchor')]);
    tgt.dominant_mode = String(r[col('dominant_mode')]).trim().toUpperCase().slice(0, 3);
    merged++;
  });
  if (merged !== 16) throw new Error('expected 16 boundary rows, merged ' + merged);
  return out;
}

/** Live Sheets ingestion with graceful local fallback. Never throws because of the network or credentials. */
async function loadBoundaryData(opts) {
  const o = Object.assign({ range: process.env.GSTACK_SHEET_RANGE || DEFAULT_RANGE, backoff: {} }, opts);
  const local = readLocal();
  const st = credentialStatus();
  if (!st.sheetId) return { source: 'local-json', data: local, reason: 'GSTACK_SHEET_ID not set' };
  try {
    const c = await getClients(['https://www.googleapis.com/auth/spreadsheets.readonly']);
    if (c.error) return { source: 'local-json', data: local, reason: c.error };
    const sheets = c.google.sheets({ version: 'v4', auth: c.auth });
    const res = await withBackoff(() => sheets.spreadsheets.values.get({ spreadsheetId: process.env.GSTACK_SHEET_ID, range: o.range }), o.backoff);
    return { source: 'google-sheets', data: mergeSheetRows(local, res.data.values || []), reason: 'ok' };
  } catch (err) {
    return { source: 'local-json', data: local, reason: 'sheets failed: ' + (err && err.message ? err.message : String(err)) };
  }
}

/** Append one structured row to the 'CLAUDECODE Execution Log' tab. A local JSONL copy is always written. */
async function appendExecutionLog(info, opts) {
  const o = Object.assign({ backoff: {} }, opts);
  const row = [info.timestamp || new Date().toISOString(), info.runId || process.env.GITHUB_SHA || 'local-' + Date.now(), info.source || 'local-json',
    info.resolution || '2400x4200', info.durationMs == null ? '' : info.durationMs, info.status || 'OK'];
  try { fs.appendFileSync(LOCAL_LOG, JSON.stringify({ row }) + '\n'); } catch (e) { /* read-only checkout: ignore */ }
  const st = credentialStatus();
  if (!st.sheetId) return { appended: false, skipped: true, reason: 'GSTACK_SHEET_ID not set', row };
  try {
    const c = await getClients(['https://www.googleapis.com/auth/spreadsheets']);
    if (c.error) return { appended: false, skipped: true, reason: c.error, row };
    const sheets = c.google.sheets({ version: 'v4', auth: c.auth });
    await withBackoff(() => sheets.spreadsheets.values.append({
      spreadsheetId: process.env.GSTACK_SHEET_ID, range: "'" + LOG_TAB + "'!A:F", valueInputOption: 'RAW', insertDataOption: 'INSERT_ROWS', requestBody: { values: [row] },
    }), o.backoff);
    return { appended: true, skipped: false, row };
  } catch (err) {
    return { appended: false, skipped: false, reason: 'append failed: ' + (err && err.message ? err.message : String(err)), row };
  }
}

const MIME = { '.png': 'image/png', '.svg': 'image/svg+xml' };

/** Upload the exported PNG and SVG HUD to the Drive folder; an existing file with the same name gets a new revision. */
async function uploadToDrive(files, opts) {
  const o = Object.assign({ backoff: {} }, opts);
  const folder = process.env.GSTACK_DRIVE_FOLDER_ID;
  if (!folder) return { uploaded: [], skipped: true, reason: 'GSTACK_DRIVE_FOLDER_ID not set' };
  const c = await getClients(['https://www.googleapis.com/auth/drive.file']);
  if (c.error) return { uploaded: [], skipped: true, reason: c.error };
  const drive = c.google.drive({ version: 'v3', auth: c.auth });
  const uploaded = [];
  for (const f of files) {
    if (!fs.existsSync(f)) { uploaded.push({ file: f, error: 'file not found' }); continue; }
    const name = path.basename(f), mimeType = MIME[path.extname(f).toLowerCase()] || 'application/octet-stream';
    const q = "name = '" + name.replace(/'/g, "\\'") + "' and '" + folder + "' in parents and trashed = false";
    const found = await withBackoff(() => drive.files.list({ q, fields: 'files(id,name)', spaces: 'drive' }), o.backoff);
    const media = { mimeType, body: fs.createReadStream(f) };
    const existing = found.data.files && found.data.files[0];
    const res = existing
      ? await withBackoff(() => drive.files.update({ fileId: existing.id, media, fields: 'id,name,version' }), o.backoff)
      : await withBackoff(() => drive.files.create({ requestBody: { name, parents: [folder] }, media, fields: 'id,name,version' }), o.backoff);
    uploaded.push({ file: f, id: res.data.id, versioned: !!existing });
  }
  return { uploaded, skipped: false };
}

function status() {
  const st = credentialStatus();
  return { credentials: st.credentials, sheetId: st.sheetId, driveFolderId: st.driveFolderId, googleapisInstalled: !!loadGoogle(), localDatasetPresent: fs.existsSync(LOCAL_JSON),
    mode: st.credentials && st.sheetId ? 'live-capable' : 'offline-fallback' };
}

async function main(argv) {
  const cmd = argv[0] || 'status';
  const flag = (n, d) => { const i = argv.indexOf('--' + n); return i >= 0 ? argv[i + 1] : d; };
  if (cmd === 'status') { console.log(JSON.stringify(status(), null, 2)); return; }
  if (cmd === 'load') { const r = await loadBoundaryData(); console.log(JSON.stringify({ source: r.source, reason: r.reason, rows: r.data.scenarios.A.boundaries.length + r.data.scenarios.B.boundaries.length }, null, 2)); return; }
  if (cmd === 'log') {
    const r = await appendExecutionLog({ source: flag('source'), resolution: flag('resolution'), durationMs: flag('duration'), status: flag('status'), runId: flag('run-id') });
    console.log(JSON.stringify(r, null, 2)); return;
  }
  if (cmd === 'upload') { const r = await uploadToDrive(argv.slice(1)); console.log(JSON.stringify(r, null, 2)); return; }
  console.error('usage: gstack_sync.js status|load|log|upload'); process.exitCode = 2;
}

module.exports = { withBackoff, loadBoundaryData, appendExecutionLog, uploadToDrive, mergeSheetRows, status, credentialStatus };
if (require.main === module) main(process.argv.slice(2)).catch((e) => { console.error(e.message); process.exitCode = 1; });
