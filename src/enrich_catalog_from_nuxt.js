/**
 * enrich_catalog_from_nuxt.js
 * 
 * Concurrent extractor for CellphoneS Nuxt state.
 * Extracts full 9-group technical specifications, genuine warranty information,
 * manufacturer SKU, and real-time prices directly from window.__NUXT__.
 * 
 * Complies with DECISIONS.md D10, D12, D14: Zero fabrication, Strict NULL.
 * Uses 100% static AST/literal parser and structured error logging.
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const RAW_DIR = path.join(ROOT, 'data', 'raw');
const OUT_FILE = path.join(RAW_DIR, 'cellphones_enriched_raw.json');
const FAILED_FILE = path.join(RAW_DIR, 'cellphones_failed_urls.json');

// Blacklisted slugs and keywords
const CATEGORY_SLUGS = new Set([
  'cps_macbook-neo',
  'cps_macbook-air',
  'cps_macbook-pro',
  'macbook-neo',
  'macbook-air',
  'macbook-pro'
]);

const UNRELEASED_PATTERNS = [
  /\bm5\b/i,
  /-m5-/i,
  /\ba18\b/i,
  /-a18-/i
];

const ACCESSORY_OR_USED_PATTERNS = [
  /-cu-/i,
  /cu-xuoc/i,
  /cu-dep/i,
  /ch-cu/i,
  /da-kich-hoat/i,
  /dkh/i,
  /phu-kien/i,
  /ban-phim/i,
  /chuot/i,
  /balo/i,
  /tui-chong-soc/i,
  /man-hinh/i,
  /ram-/i,
  /o-cung-/i,
  /sac-/i
];

function isUnreleasedOrBlacklisted(url, pid) {
  const target = (url + ' ' + (pid || '')).toLowerCase();
  if (CATEGORY_SLUGS.has(pid) || target.includes('/laptop/')) {
    return true;
  }
  for (const pat of UNRELEASED_PATTERNS) {
    if (pat.test(target)) return true;
  }
  for (const pat of ACCESSORY_OR_USED_PATTERNS) {
    if (pat.test(target)) return true;
  }
  return false;
}

/**
 * Safely parses Nuxt payload using a pure static tokenizer and recursive-descent parser.
 * Parses only string literals, numbers, booleans, null, undefined, arrays, and objects.
 */
function tokenizeArgs(argsStr) {
  const tokens = [];
  let i = 0;
  const n = argsStr.length;
  while (i < n) {
    while (i < n && (argsStr[i] === ' ' || argsStr[i] === '\t' || argsStr[i] === '\n' || argsStr[i] === '\r')) i++;
    if (i >= n) break;

    if (argsStr[i] === '"') {
      let s = '"';
      i++;
      while (i < n) {
        if (argsStr[i] === '\\' && i + 1 < n) {
          s += argsStr[i] + argsStr[i + 1];
          i += 2;
        } else if (argsStr[i] === '"') {
          s += '"';
          i++;
          break;
        } else {
          s += argsStr[i];
          i++;
        }
      }
      tokens.push(JSON.parse(s));
    } else {
      let end = i;
      while (end < n && argsStr[end] !== ',') end++;
      const raw = argsStr.substring(i, end).trim();
      if (raw === 'true') tokens.push(true);
      else if (raw === 'false') tokens.push(false);
      else if (raw === 'null' || raw === 'void 0' || raw === 'undefined') tokens.push(null);
      else if (/^Array\(\d+\)$/.test(raw)) tokens.push([]);
      else if (/^-?\d+(\.\d+)?$/.test(raw)) tokens.push(Number(raw));
      else tokens.push(raw);
      i = end;
    }
    while (i < n && argsStr[i] !== ',') i++;
    if (i < n && argsStr[i] === ',') i++;
  }
  return tokens;
}

function parseNuxtPayloadSafely(code) {
  try {
    // Precise IIFE boundaries: starts with window.__NUXT__=(function( or (function(
    const funcMatch = code.match(/window\.__NUXT__\s*=\s*\(function\(([^)]*)\)\s*\{/);
    if (!funcMatch) return null;
    const params = funcMatch[1].split(',').map(s => s.trim());

    // Arguments are passed in closing invocation: }(arg1, arg2, ...)) or }(arg1, arg2, ...));
    const callMatch = code.match(/\}\(([\s\S]*)\)\s*;?\s*$/);
    if (!callMatch) return null;
    const argsStr = callMatch[1];

    const args = tokenizeArgs(argsStr);
    if (args.length !== params.length) return null;

    const varMap = new Map();
    for (let i = 0; i < params.length; i++) {
      varMap.set(params[i], args[i]);
    }

    const pdMatch = code.match(/productData\s*:\s*([a-zA-Z0-9_\$]+|\{)/);
    if (!pdMatch) return null;

    let pdCode = null;
    if (pdMatch[1] !== '{') {
      const varName = pdMatch[1];
      const val = varMap.get(varName);
      if (!val || typeof val !== 'object' || Object.keys(val).length === 0) {
        // Empty product data object (e.g. nF = {})
        return { general: {}, filterable: {}, specification: {} };
      }
      return val;
    }

    const pIdx = pdMatch.index + pdMatch[0].length - 1;
    let brace = 0;
    let started = false;
    let endIdx = -1;
    for (let i = pIdx; i < code.length; i++) {
      if (code[i] === '{') {
        brace++;
        started = true;
      } else if (code[i] === '}') {
        brace--;
        if (started && brace === 0) {
          endIdx = i + 1;
          break;
        }
      }
    }
    if (endIdx === -1) return null;
    pdCode = code.substring(pIdx, endIdx);

    let pos = 0;
    const len = pdCode.length;

    function skipWhitespace() {
      while (pos < len && (pdCode[pos] === ' ' || pdCode[pos] === '\t' || pdCode[pos] === '\n' || pdCode[pos] === '\r')) {
        pos++;
      }
    }

    function parseString() {
      let s = '"';
      pos++;
      while (pos < len) {
        if (pdCode[pos] === '\\' && pos + 1 < len) {
          s += pdCode[pos] + pdCode[pos + 1];
          pos += 2;
        } else if (pdCode[pos] === '"') {
          s += '"';
          pos++;
          break;
        } else {
          s += pdCode[pos];
          pos++;
        }
      }
      return JSON.parse(s);
    }

    function parseIdentifier() {
      const start = pos;
      while (pos < len && /[a-zA-Z0-9_\$]/.test(pdCode[pos])) {
        pos++;
      }
      return pdCode.substring(start, pos);
    }

    function parseNumberLiteral() {
      const start = pos;
      if (pdCode[pos] === '-') pos++;
      while (pos < len && /[0-9]/.test(pdCode[pos])) pos++;
      if (pos < len && pdCode[pos] === '.') {
        pos++;
        while (pos < len && /[0-9]/.test(pdCode[pos])) pos++;
      }
      return Number(pdCode.substring(start, pos));
    }

    function parseValue() {
      skipWhitespace();
      if (pos >= len) return null;
      const c = pdCode[pos];

      if (c === '{') {
        return parseObject();
      } else if (c === '[') {
        return parseArray();
      } else if (c === '"') {
        return parseString();
      } else if (c === '-' || /[0-9]/.test(c)) {
        return parseNumberLiteral();
      } else {
        const id = parseIdentifier();
        if (id === 'true') return true;
        if (id === 'false') return false;
        if (id === 'null' || id === 'undefined' || id === 'void') return null;
        if (varMap.has(id)) {
          return varMap.get(id);
        }
        // Strict fallback: do not return variable identifier string silently
        return null;
      }
    }

    function parseArray() {
      pos++; // skip '['
      const arr = [];
      skipWhitespace();
      if (pdCode[pos] === ']') {
        pos++;
        return arr;
      }
      while (pos < len) {
        skipWhitespace();
        arr.push(parseValue());
        skipWhitespace();
        if (pdCode[pos] === ',') {
          pos++;
        } else if (pdCode[pos] === ']') {
          pos++;
          break;
        } else {
          break;
        }
      }
      return arr;
    }

    function parseObject() {
      pos++; // skip '{'
      const obj = {};
      skipWhitespace();
      if (pdCode[pos] === '}') {
        pos++;
        return obj;
      }
      while (pos < len) {
        skipWhitespace();
        let key = null;
        if (pdCode[pos] === '"') {
          key = parseString();
        } else {
          key = parseIdentifier();
        }
        skipWhitespace();
        if (pdCode[pos] === ':') {
          pos++;
        }
        skipWhitespace();
        const val = parseValue();
        obj[key] = val;
        skipWhitespace();
        if (pdCode[pos] === ',') {
          pos++;
        } else if (pdCode[pos] === '}') {
          pos++;
          break;
        } else {
          break;
        }
      }
      return obj;
    }

    return parseValue();
  } catch (err) {
    return null;
  }
}

function fetchNuxtData(url, maxRedirects = 3) {
  return new Promise((resolve) => {
    if (maxRedirects < 0) {
      return resolve({
        ok: false,
        error_type: 'TOO_MANY_REDIRECTS',
        error: 'Too many redirects',
        http_status: 301,
        data: null
      });
    }
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
      },
      timeout: 10000
    }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        let redirectUrl = res.headers.location;
        if (!redirectUrl.startsWith('http')) {
          redirectUrl = new URL(redirectUrl, url).toString();
        }
        return fetchNuxtData(redirectUrl, maxRedirects - 1).then(resolve);
      }
      if (res.statusCode !== 200) {
        return resolve({
          ok: false,
          error_type: 'HTTP_STATUS_NON_200',
          error: `HTTP ${res.statusCode}`,
          http_status: res.statusCode,
          data: null
        });
      }
      let html = '';
      res.on('data', chunk => { html += chunk; });
      res.on('end', () => {
        const match = html.match(/<script>\s*(window\.__NUXT__\s*=[\s\S]*?);?\s*<\/script>/);
        if (!match) {
          return resolve({
            ok: false,
            error_type: 'MISSING_NUXT_STATE',
            error: 'Nuxt script tag not found in page HTML',
            http_status: 200,
            data: null
          });
        }
        
        const p = parseNuxtPayloadSafely(match[1]);
        if (!p) {
          return resolve({
            ok: false,
            error_type: 'NUXT_PARSE_FAILURE',
            error: 'Failed to statically parse Nuxt payload',
            http_status: 200,
            data: null
          });
        }

        const specsFlat = {};
        const groups = p.specification?.full_by_group || [];
        for (const g of groups) {
          if (Array.isArray(g.value)) {
            for (const item of g.value) {
              if (item.label && item.value !== undefined && item.value !== null) {
                const cleanVal = String(item.value).replace(/<br\s*\/?>/gi, ' ').replace(/\s+/g, ' ').trim();
                specsFlat[item.label.trim()] = cleanVal;
              }
            }
          }
        }

        // Strict NULL: Do NOT fall back listed_price_vnd to sale_price_vnd!
        const specialPrice = Number(p.filterable?.special_price) || null;
        const originalPrice = Number(p.filterable?.price) || null;

        const salePrice = (specialPrice && specialPrice > 0) ? specialPrice : ((originalPrice && originalPrice > 0) ? originalPrice : null);
        const listedPrice = (originalPrice && originalPrice > 0) ? originalPrice : null;

        resolve({
          ok: true,
          http_status: 200,
          data: {
            name: p.general?.name || null,
            sku: p.general?.sku || null,
            manufacturer: p.general?.manufacturer || null,
            warranty_raw: p.filterable?.warranty_information || null,
            listed_price_vnd: listedPrice,
            sale_price_vnd: salePrice,
            image_url: p.filterable?.thumbnail || (p.general?.galleries?.[0]?.image) || null,
            specs: specsFlat
          }
        });
      });
    });

    req.on('error', (err) => resolve({
      ok: false,
      error_type: 'NETWORK_ERROR',
      error: err.message,
      http_status: null,
      data: null
    }));
    req.on('timeout', () => {
      req.destroy();
      resolve({
        ok: false,
        error_type: 'NETWORK_TIMEOUT',
        error: 'Request timeout after 10000ms',
        http_status: null,
        data: null
      });
    });
  });
}

async function runEnrichment() {
  console.log('=== KHỞI ĐỘNG TIẾN TRÌNH LÀM GIÀU DỮ LIỆU TỪ NUXT STATE CELLPHONES (STATIC AST PARSER) ===');

  // 1. Gather all candidate URLs
  const candidateUrls = new Set();

  // From legacy raw JSON
  const legacyFile = path.join(RAW_DIR, 'cellphones_laptops_raw.json');
  if (fs.existsSync(legacyFile)) {
    const legacy = JSON.parse(fs.readFileSync(legacyFile, 'utf8'));
    for (const it of legacy) {
      if (it.source_url && !isUnreleasedOrBlacklisted(it.source_url, it.source_product_id)) {
        candidateUrls.add(it.source_url);
      }
    }
  }

  // From net-new raw JSON
  const netNewFile = path.join(RAW_DIR, 'cellphones_net_new_raw.json');
  if (fs.existsSync(netNewFile)) {
    const netNew = JSON.parse(fs.readFileSync(netNewFile, 'utf8'));
    for (const it of netNew) {
      if (it.source_url && !isUnreleasedOrBlacklisted(it.source_url, it.source_product_id)) {
        candidateUrls.add(it.source_url);
      }
    }
  }

  // From candidate sitemap URLs
  const sitemapFile = path.join(RAW_DIR, 'candidate_sitemap_urls.txt');
  if (fs.existsSync(sitemapFile)) {
    const lines = fs.readFileSync(sitemapFile, 'utf8').split(/\r?\n/);
    for (const line of lines) {
      const u = line.trim();
      if (u && !isUnreleasedOrBlacklisted(u, '')) {
        candidateUrls.add(u);
      }
    }
  }

  const urlList = Array.from(candidateUrls);
  console.log(`Tổng số URL ứng viên hợp lệ sau sàng lọc loại trừ: ${urlList.length} URLs`);

  // Controlled concurrency pool (8 workers to prevent rate-limiting)
  const CONCURRENCY = 8;
  const results = [];
  const failedUrls = [];
  let completed = 0;
  let successCount = 0;

  async function worker(queue) {
    while (queue.length > 0) {
      const url = queue.shift();
      let res = await fetchNuxtData(url);
      
      // Exponential backoff retry on failure
      if (!res.ok || !res.data) {
        await new Promise(r => setTimeout(r, 600));
        res = await fetchNuxtData(url);
      }

      completed++;
      const data = res.data;
      if (res.ok && data && data.sale_price_vnd && Object.keys(data.specs || {}).length >= 5) {
        const slug = url.replace(/https?:\/\/cellphones\.com\.vn\//, '').replace(/\.html$/, '');
        const pid = `cps_${slug}`;
        
        // Strict double-check on unreleased M5 / A18 or generic names
        const nameLower = (data.name || '').toLowerCase();
        if (!nameLower.includes('m5') && !nameLower.includes('a18') && 
            !['macbook', 'macbook air', 'macbook pro', 'laptop'].includes(nameLower.trim())) {
          results.push({
            source: 'cellphones',
            source_product_id: pid,
            product_name_raw: data.name,
            source_url: url,
            crawled_at: new Date().toISOString(),
            listed_price_vnd: data.listed_price_vnd,
            sale_price_vnd: data.sale_price_vnd,
            sku_official: data.sku,
            manufacturer_official: data.manufacturer,
            warranty_raw: data.warranty_raw,
            image_url_remote: data.image_url,
            specs_raw: data.specs
          });
          successCount++;
        }
      } else {
        let errType = res.error_type || 'UNKNOWN_ERROR';
        let reason = res.error || 'Failed to extract valid product specs';

        if (res.ok && data) {
          if (!data.sale_price_vnd) {
            errType = 'OUT_OF_STOCK_OR_ZERO_PRICE';
            reason = 'Sản phẩm hết hàng hoặc không có giá bán hoạt động (sale_price_vnd is null/0)';
          } else if (Object.keys(data.specs || {}).length < 5) {
            errType = 'INSUFFICIENT_SPECS';
            reason = `Thiếu thông số kỹ thuật tối thiểu (chỉ có ${Object.keys(data.specs || {}).length}/5 thông số)`;
          }
        }

        failedUrls.push({
          url,
          http_status: res.http_status || null,
          error_type: errType,
          reason: reason,
          timestamp: new Date().toISOString()
        });
      }

      if (completed % 25 === 0 || completed === urlList.length) {
        const pct = ((completed / urlList.length) * 100).toFixed(1);
        console.log(`[${pct}%] Đã xử lý ${completed}/${urlList.length} - Thành công: ${successCount} - Thất bại/bỏ qua: ${failedUrls.length}`);
      }
    }
  }

  const queue = [...urlList];
  const workers = [];
  for (let i = 0; i < CONCURRENCY; i++) {
    workers.push(worker(queue));
  }

  const startTime = Date.now();
  await Promise.all(workers);
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

  console.log(`\n=== HOÀN TẤT CÀO DỮ LIỆU NUXT ===`);
  console.log(`Thời gian: ${elapsed}s`);
  console.log(`Tổng số sản phẩm đạt chuẩn chất lượng cao: ${results.length}`);

  // Deduplicate by source_product_id
  const uniqueMap = new Map();
  for (const item of results) {
    if (!uniqueMap.has(item.source_product_id)) {
      uniqueMap.set(item.source_product_id, item);
    }
  }
  const finalResults = Array.from(uniqueMap.values());
  console.log(`Số sản phẩm duy nhất (deduplicated): ${finalResults.length}`);

  fs.writeFileSync(OUT_FILE, JSON.stringify(finalResults, null, 2), 'utf8');
  console.log(`Đã ghi toàn bộ dữ liệu giàu thông số vào ${OUT_FILE}`);

  fs.writeFileSync(FAILED_FILE, JSON.stringify(failedUrls, null, 2), 'utf8');
  console.log(`Đã lưu nhật ký URL không thành công/bỏ qua (${failedUrls.length}) vào ${FAILED_FILE}`);
}

runEnrichment();
