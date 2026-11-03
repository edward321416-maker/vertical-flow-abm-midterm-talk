/**
 * point_cloud_engine.js
 * Stochastic stippling, 1D simplex noise, monotone cubic Hermite interpolation and 2.5D isometric ridge projection.
 * Deterministic: every random draw comes from a seeded Mulberry32 stream, so identical input data and seeds always
 * produce an identical point cloud. Node values are exact: noise is multiplied by an envelope that is zero at every
 * floor-boundary node, so the data points themselves are never altered.
 */
(function (root) {
  'use strict';

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function makeSimplex1D(rng) {
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      const t = p[i]; p[i] = p[j]; p[j] = t;
    }
    const perm = new Uint8Array(512);
    for (let i = 0; i < 512; i++) perm[i] = p[i & 255];
    const grad = (h, x) => { h &= 15; let g = 1 + (h & 7); if (h & 8) g = -g; return g * x; };
    return function noise(x) {
      const i0 = Math.floor(x), i1 = i0 + 1, x0 = x - i0, x1 = x0 - 1;
      let t0 = 1 - x0 * x0; t0 *= t0;
      const n0 = t0 * t0 * grad(perm[i0 & 255], x0);
      let t1 = 1 - x1 * x1; t1 *= t1;
      const n1 = t1 * t1 * grad(perm[i1 & 255], x1);
      return 0.395 * (n0 + n1);
    };
  }

  function fbm(noise, x, octaves) {
    let sum = 0, amp = 1, freq = 1, norm = 0;
    for (let o = 0; o < octaves; o++) {
      sum += amp * noise(x * freq);
      norm += amp; amp *= 0.5; freq *= 2.03;
    }
    return sum / norm;
  }

  // Fritsch-Carlson monotone cubic Hermite through (0,ys[0]) ... (n-1,ys[n-1]); no overshoot between nodes.
  function monotoneCubic(ys) {
    const n = ys.length, d = new Array(n - 1), m = new Array(n);
    for (let i = 0; i < n - 1; i++) d[i] = ys[i + 1] - ys[i];
    m[0] = d[0]; m[n - 1] = d[n - 2];
    for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
    for (let i = 0; i < n - 1; i++) {
      if (d[i] === 0) { m[i] = 0; m[i + 1] = 0; continue; }
      const a = m[i] / d[i], b = m[i + 1] / d[i], s = a * a + b * b;
      if (s > 9) { const t = 3 / Math.sqrt(s); m[i] = t * a * d[i]; m[i + 1] = t * b * d[i]; }
    }
    return function (t) {
      if (t <= 0) return ys[0];
      if (t >= n - 1) return ys[n - 1];
      const i = Math.floor(t), u = t - i;
      const h00 = (1 + 2 * u) * (1 - u) * (1 - u), h10 = u * (1 - u) * (1 - u), h01 = u * u * (3 - 2 * u), h11 = u * u * (u - 1);
      return h00 * ys[i] + h10 * m[i] + h01 * ys[i + 1] + h11 * m[i + 1];
    };
  }

  /**
   * Height profile (in data units) of one simulation run along the 8 boundary nodes.
   * ys: the run's real values at the nodes. sds: per-node standard deviation over runs.
   * Between nodes a noise term (scaled by the local deviation and an envelope that vanishes at the nodes) adds texture.
   */
  function ridgeProfile(ys, sds, nSamp, noise, ampFrac, phase) {
    const n = ys.length, f = monotoneCubic(ys), out = new Float32Array(nSamp);
    for (let k = 0; k < nSamp; k++) {
      const t = (k / (nSamp - 1)) * (n - 1);
      const i = Math.min(Math.floor(t), n - 2), u = t - i;
      const sd = sds[i] * (1 - u) + sds[i + 1] * u;
      const env = Math.sin(Math.PI * u);
      out[k] = Math.max(0, f(t) + env * ampFrac * sd * fbm(noise, t * 2.2 + phase, 4));
    }
    return out;
  }

  /**
   * Draw a stack of ridge slices (far to near). Every slice is an occluding silhouette plus two stipple layers:
   *  - strip: shallow stipple that stays visible between a slice crest and the crest of the next nearer slice (the ridge top surface)
   *  - face:  deep stipple with exponential decay P(y) = exp(-k (y_crest - y)) drawn only for the nearest slice (the lit front face)
   * cfg: runs[][8], sds[8], kh (px per data unit), x0, dx, baseY, zx, zy, z0, rng, noise, occluder, clip:{x,y,w,h},
   *      contourEvery, contourAlpha, ampFrac, samples,
   *      strip:{count, tau, maxD, alpha:[min,max], size}, face:{samples, count, tau, maxD, alpha:[min,max], size}
   * Returns {particles, slices}.
   */
  function drawRidgeStack(ctx, cfg) {
    const NB = 24, buckets = Array.from({ length: NB }, () => []);
    const nS = cfg.runs.length, nSamp = cfg.samples || 420;
    let total = 0;
    const flush = (size) => {
      for (let b = 0; b < NB; b++) {
        const arr = buckets[b];
        if (!arr.length) continue;
        ctx.fillStyle = 'rgba(255,255,255,' + ((b + 0.5) / NB).toFixed(3) + ')';
        for (let i = 0; i < arr.length; i += 2) ctx.fillRect(arr[i], arr[i + 1], size, size);
        arr.length = 0;
      }
    };
    const spawn = (px, py, k, count, tau, maxD, alpha) => {
      const n = count + (cfg.rng() < (count % 1) ? 1 : 0), whole = Math.floor(count) + (cfg.rng() < (count % 1) ? 1 : 0);
      void n;
      for (let q = 0; q < whole; q++) {
        const d = -Math.log(1 - cfg.rng()) * tau;             // P(y) = exp(-k (y_crest - y))
        if (d > maxD) continue;
        const a = alpha[0] + (alpha[1] - alpha[0]) * Math.exp(-d / (tau * 0.8));
        buckets[Math.min(NB - 1, Math.floor(a * NB))].push(px + (cfg.rng() - 0.5) * 1.6, py + d);
        total++;
      }
    };
    ctx.save();
    ctx.beginPath(); ctx.rect(cfg.clip.x, cfg.clip.y, cfg.clip.w, cfg.clip.h); ctx.clip();
    for (let s = nS - 1; s >= 0; s--) {
      const z = cfg.z0 + s;
      const build = (ns) => {
        const prof = ridgeProfile(cfg.runs[s], cfg.sds, ns, cfg.noise, cfg.ampFrac, s * 0.37);
        const px = new Float32Array(ns), py = new Float32Array(ns);
        for (let k = 0; k < ns; k++) {
          const tt = (k / (ns - 1)) * (cfg.runs[s].length - 1);
          px[k] = cfg.x0 + tt * cfg.dx + z * cfg.zx;
          py[k] = cfg.baseY - z * cfg.zy - prof[k] * cfg.kh;
        }
        return [px, py];
      };
      const [px, py] = build(nSamp);
      ctx.beginPath();
      ctx.moveTo(px[0], cfg.clip.y + cfg.clip.h);
      for (let k = 0; k < nSamp; k++) ctx.lineTo(px[k], py[k]);
      ctx.lineTo(px[nSamp - 1], cfg.clip.y + cfg.clip.h);
      ctx.closePath();
      ctx.fillStyle = 'rgba(5,5,5,' + cfg.occluder + ')';
      ctx.fill();
      for (let k = 0; k < nSamp; k++) {
        spawn(px[k], py[k], k, cfg.strip.count, cfg.strip.tau, cfg.strip.maxD, cfg.strip.alpha);
        buckets[NB - 1].push(px[k] + (cfg.rng() - 0.5) * 1.2, py[k] + cfg.rng() * 1.6);   // crest edge glow
        total++;
      }
      flush(cfg.strip.size);
      if (s === 0 && cfg.face) {                                 // lit front face of the nearest slice
        const [fx, fy] = build(cfg.face.samples);
        for (let k = 0; k < cfg.face.samples; k++) spawn(fx[k], fy[k], k, cfg.face.count, cfg.face.tau, cfg.face.maxD, cfg.face.alpha);
        flush(cfg.face.size);
      }
      if (cfg.contourEvery && s % cfg.contourEvery === 0) {
        ctx.beginPath();
        for (let k = 0; k < nSamp; k++) { if (k) ctx.lineTo(px[k], py[k]); else ctx.moveTo(px[k], py[k]); }
        ctx.strokeStyle = 'rgba(255,255,255,' + cfg.contourAlpha + ')';
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
    ctx.restore();
    return { particles: total, slices: nS };
  }

  // 32-bit FNV-1a over a string, used to verify that two renders are identical.
  function fnv1a(str) {
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    return ('00000000' + h.toString(16)).slice(-8);
  }

  const api = { mulberry32, makeSimplex1D, fbm, monotoneCubic, ridgeProfile, drawRidgeStack, fnv1a };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.PointCloudEngine = api;
})(typeof window !== 'undefined' ? window : globalThis);
