// Đọc dữ liệu 360° và chính sách từ bản clone (chỉ đọc), ghi ra JSON cho gen_extra.py
import fs from 'fs';
const L = 'C:/Users/PC/Desktop/clone-nirvana/src/lib/';
const t = fs.readFileSync(L + 'tour360-content.ts', 'utf8');
const scenes = eval(t.slice(t.indexOf('[', t.indexOf('export const TOUR_SCENES')), t.lastIndexOf(']') + 1));
const p = fs.readFileSync(L + 'privacy-content.ts', 'utf8');
const body = p.slice(p.indexOf('const COMPANY')).replace(/: PolicyItem\[\]/, '').replace(/export /g, '');
const items = new Function(body + '; return PRIVACY_ITEMS;')();
fs.writeFileSync('_src/extra.json', JSON.stringify({ scenes, privacy: items }, null, 1));
console.log(scenes.length, items.length);
