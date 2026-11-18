/* 3D 課程島的場景層。由 island.js 的 initScene() 呼叫 buildWorld()。島、海、光影與效能機制移植自 ds-cpp-selfstudy 的 /island/。
 *
 * 做法（全部程序化，沒有模型或圖檔）：
 *   - 島：不規則輪廓 → 分層倒角擠出（沙底、深崖帶、草頂），外圈淺水與浪花環；主島拉長，Lab 3 的島尾以拱橋接到三座小島
 *   - 靜態零件：PartKit 收集（box／圓角 box／cyl／cone／sphere／rock／prism／torus），依種類合併成 InstancedMesh 並逐實例上色；陰影只烘一次
 *   - 地標：每頁一組建築＋會動的零件。可動零件共用動態池（不投影），動畫是純函式：IDLE（輪播、不露結果）與 POSE（答完猜題才播）
 *   - 拱橋只表示建議順序，樣式和地標裡的繩索不同
 *   - 標籤是 HTML，每次繪製時投影定位，依優先序避讓；地面標示是一張貼花圖集，放大才看得到
 * 本檔與 island.js、island-compare.js 共用頂層名稱：PAGES、BY、ISLES、items、trail、select、closePanel、$、reduceMotion、DATA。
 */
function buildWorld(THREE, addons, renderer, stage, canvas) {
  const { OrbitControls, RoundedBoxGeometry } = addons;
  const motion = () => !reduceMotion.matches;
  const SHOW = document.documentElement.classList.contains('show-mode');   // 會場投影版：沒有人操作
  const narrow = () => stage.clientWidth < 768;
  const rnd = mulberry32(208);
  const SQ = Math.SQRT1_2;
  // 初始視角的螢幕座標（u 往右、v 往前＝畫面下方）→ 世界座標 xz
  const toWorld = (u, v) => ({ x: (u + v) * SQ, z: (v - u) * SQ });
  const world = new THREE.Scene();
  const anims = [];          // 地標小動畫 (t) => void
  const life = [];           // 生活感動畫 (t, dt) => void；效能不足時整組停用
  let need = true, raf = 0, onScreen = true, alive = true, lowPower = false, dprLevel = 0, tagsDirty = true, draws = 0;

  /* ── 色盤：黏土色；網站的磚紅、深藍、金、森林綠作為屋頂與重點色 ── */
  const C = {
    grass: '#b4d18a', grass2: '#a3c67e', grass3: '#c4dc9c', sand: '#eedbb0', cliff: '#dcc39a', cliffDark: '#c2a477',
    foam: '#fbfaf2', shallow: '#bfe0d6',
    cream: '#fff4de', wall: '#f5e6cb', wall2: '#efdcc0', peach: '#f0c7a5', roof: '#b9563f', roofDark: '#924231',
    roofNavy: '#2c3e7a', roofGreen: '#3f7f61',
    leaf: '#9fb889', leaf2: '#8fae86', leaf3: '#7c9a76', pine: '#7b997c', pine2: '#68876c',
    wood: '#ab875d', woodDark: '#7a5c3e', stone: '#dacdb6', stoneDark: '#b6a78c', ink: '#4f5a55',
    glass: '#8cbcbc', gold: '#f5b82e', white: '#fffcf3', navy: '#2f4566', forest: '#1a6b4a',
    red: '#b9654f', blue: '#5d7b93', blueL: '#c3d0dc', redL: '#ebc7bb', amber: '#d6a35c', teal: '#5aa39a',
  };
  const DAY = { bg: '#a2dbe6', hemiSky: '#fff4dc', hemiGround: '#7d9d8f', hemi: 1.3, sun: '#ffe4c4', sunI: 2.9, fill: .45, sea: '#ffffff', exposure: 1.0 };
  const NIGHT = { bg: '#1f2e44', hemiSky: '#9fb2da', hemiGround: '#2a3a52', hemi: .85, sun: '#c3cff5', sunI: .55, fill: .18, sea: '#56708f', exposure: 1.15 };

  /* ── Renderer ── */
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;      // r18x 起 PCF 以 shadow.radius 柔化
  renderer.shadowMap.autoUpdate = false;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = DAY.exposure;
  world.background = new THREE.Color(DAY.bg);
  world.fog = new THREE.Fog(DAY.bg, 150, 300);       // 只讓最遠的外海淡出

  // 黏土風幾乎沒有反光：除了海面，一律用較輕的 Lambert（roughness／metalness 參數直接略過）
  const std = (color, extra = {}) => { const { roughness, metalness, ...rest } = extra; void roughness; void metalness; return new THREE.MeshLambertMaterial({ color, ...rest }); };
  const basic = (color, extra) => new THREE.MeshBasicMaterial({ color, ...extra });

  /* ── instancify：把會動的小階層（小人、船、鳥、雲、噴泉球…）合併繪製 ──
     階層本身照常用 Object3D 建立與做動畫，但不加進場景；同幾何＋同類材質的 mesh 合成一個 InstancedMesh，
     不透明的 Lambert 材質改用逐實例顏色共用一份材質。每個動畫幀呼叫 syncProxies() 同步世界矩陣。 */
  const proxyRoots = [], proxyPools = new Map();
  const dynSolid = { [THREE.FrontSide]: null, [THREE.DoubleSide]: null };
  function instancify(root) {
    proxyRoots.push(root);
    root.traverse(o => {
      if (!o.isMesh) return;
      const m = o.material;
      const solid = m.isMeshLambertMaterial && !m.transparent && m.emissive.getHex() === 0;
      const key = o.geometry.uuid + '|' + (solid ? 'solid' + m.side : m.uuid);
      if (!proxyPools.has(key)) {
        if (solid && !dynSolid[m.side]) dynSolid[m.side] = new THREE.MeshLambertMaterial({ color: '#ffffff', side: m.side });
        proxyPools.set(key, { geo: o.geometry, mat: solid ? dynSolid[m.side] : m, list: [] });
      }
      proxyPools.get(key).list.push({ o, color: solid ? m.color.clone() : null });
    });
  }
  function finishProxies() {
    proxyPools.forEach(pool => {
      const mesh = new THREE.InstancedMesh(pool.geo, pool.mat, pool.list.length);
      mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage); mesh.frustumCulled = false;
      pool.list.forEach((r, i) => { if (r.color) mesh.setColorAt(i, r.color); });
      pool.mesh = mesh; world.add(mesh);
    });
    syncProxies();
  }
  function syncProxies() {
    proxyRoots.forEach(r => r.updateMatrixWorld(true));
    proxyPools.forEach(pool => {
      if (!pool.mesh) return;
      pool.list.forEach((r, i) => pool.mesh.setMatrixAt(i, r.o.matrixWorld));
      pool.mesh.instanceMatrix.needsUpdate = true;
    });
  }

  /* ═════════ PartKit：零件 → InstancedMesh ═════════ */
  const prismGeo = (() => {
    const tri = new THREE.Shape();
    tri.moveTo(-.5, -.5); tri.lineTo(.5, -.5); tri.lineTo(0, .5); tri.closePath();
    const g = new THREE.ExtrudeGeometry(tri, { depth: 1, bevelEnabled: false });
    g.translate(0, 0, -.5); g.computeVertexNormals(); return g;
  })();
  const GEO = {
    box: new THREE.BoxGeometry(1, 1, 1),
    round: new RoundedBoxGeometry(1, 1, 1, 1, .14),
    cyl: new THREE.CylinderGeometry(.5, .5, 1, 10),
    cone: new THREE.ConeGeometry(.5, 1, 8),
    sphere: new THREE.SphereGeometry(.5, 9, 6),
    rock: new THREE.DodecahedronGeometry(.5, 0),
    prism: prismGeo,
    torus: new THREE.TorusGeometry(.5, .12, 8, 22),
  };
  const kitMat = std('#ffffff');
  const glowMat = new THREE.MeshLambertMaterial({ color: '#ffffff', emissive: '#ffc46b', emissiveIntensity: 0 });
  const glassMat = new THREE.MeshLambertMaterial({ color: '#ffffff', transparent: true, opacity: .15, depthWrite: false });
  const parts = [];
  const lamps = [];          // 夜間光暈的位置
  const ao = [];             // 接觸暗部（假環境光遮蔽）：[x, y, z, r]
  // y 一律是「底面高度」；rx/ry/rz 以 YXZ 順序套用（先轉向、再俯仰）
  function part(kind, x, y, z, w, h, d, color, o = {}) {
    parts.push({ kind, x, y, z, w, h, d, color, rx: o.rx || 0, ry: o.ry || 0, rz: o.rz || 0, glow: !!o.glow, glass: !!o.glass });
  }
  // 以 (ox,oz) 為原點、轉 rot、縮放 s 的區域座標畫零件
  function at(ox, oy, oz, rot = 0, s = 1) {
    const c = Math.cos(rot), sn = Math.sin(rot);
    const f = (kind, x, y, z, w, h, d, color, o = {}) =>
      part(kind, ox + (x * c + z * sn) * s, oy + y * s, oz + (-x * sn + z * c) * s, w * s, h * s, d * s, color,
        { ...o, ry: (o.ry || 0) + rot });
    f.ao = (x, z, r) => ao.push([ox + (x * c + z * sn) * s, oy, oz + (-x * sn + z * c) * s, r * s]);
    return f;
  }
  // 在畫筆 p 的區域座標裡再疊一層平移／旋轉／縮放
  function sub(p, ox, oz, rot = 0, s = 1) {
    const c = Math.cos(rot), sn = Math.sin(rot);
    const f = (kind, x, y, z, w, h, d, color, o = {}) =>
      p(kind, ox + (x * c + z * sn) * s, y * s, oz + (-x * sn + z * c) * s, w * s, h * s, d * s, color, { ...o, ry: (o.ry || 0) + rot });
    f.ao = (x, z, r) => p.ao && p.ao(ox + (x * c + z * sn) * s, oz + (-x * sn + z * c) * s, r * s);
    return f;
  }
  function flushParts() {
    const groups = new Map();
    parts.forEach(p => { const k = p.kind + (p.glow ? '|g' : p.glass ? '|x' : ''); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(p); });
    const o = new THREE.Object3D(); o.rotation.order = 'YXZ';
    const col = new THREE.Color();
    groups.forEach((list, k) => {
      const glow = k.endsWith('|g'), glass = k.endsWith('|x');
      const mesh = new THREE.InstancedMesh(GEO[list[0].kind], glow ? glowMat : glass ? glassMat : kitMat, list.length);
      list.forEach((p, i) => {
        o.position.set(p.x, p.y + p.h / 2, p.z); o.rotation.set(p.rx, p.ry, p.rz); o.scale.set(p.w, p.h, p.d);
        o.updateMatrix(); mesh.setMatrixAt(i, o.matrix); mesh.setColorAt(i, col.set(p.color));
      });
      mesh.castShadow = !glow && !glass; mesh.receiveShadow = !glass;
      mesh.computeBoundingSphere();
      world.add(mesh);
    });
    parts.length = 0;
  }

  /* ── 共用道具配方（p 是 part 或 at(...) 回傳的畫筆）── */
  const LEAVES = [C.leaf, C.leaf2, C.leaf3];
  // 畫筆外加一個「記錄接觸暗部」的通道：p.ao(x, z, r)
  function tree(p, x, z, s = 1, k = 0) {
    p.ao && p.ao(x, z, .75 * s);
    p('cyl', x, 0, z, .16 * s, 1.0 * s, .16 * s, C.woodDark);
    [[-.24, .75, .08, .9], [.26, .9, .05, .82], [0, 1.18, -.1, .8], [-.05, .86, -.28, .74]].forEach(([dx, dy, dz, d], i) =>
      p('sphere', x + dx * s, dy * s, z + dz * s, d * s, d * .92 * s, d * s, LEAVES[(k + i) % 3]));
  }
  function pine(p, x, z, s = 1, k = 0) {
    p.ao && p.ao(x, z, .7 * s);
    p('cyl', x, 0, z, .13 * s, .7 * s, .13 * s, C.woodDark);
    for (let i = 0; i < 3; i++) p('cone', x, (.45 + i * .42) * s, z, (1.05 - i * .24) * s, .95 * s, (1.05 - i * .24) * s, (i + k) % 2 ? C.pine : C.pine2);
  }
  function bush(p, x, z, s = 1, k = 0) {
    p.ao && p.ao(x, z, .55 * s);
    p('sphere', x, 0, z, .62 * s, .46 * s, .56 * s, LEAVES[k % 3]);
    p('sphere', x + .26 * s, 0, z + .12 * s, .42 * s, .34 * s, .4 * s, LEAVES[(k + 1) % 3]);
  }
  function flowers(p, x, z, k = 0) {
    const petals = ['#f2b8a0', '#f7e1b5', '#e9967a', '#fff4de', '#d9a0c0'];
    for (let i = 0; i < 5; i++) {
      const a = i * 1.3 + k, r = .28 + (i % 2) * .12;
      p('sphere', x + Math.cos(a) * r, 0, z + Math.sin(a) * r, .2, .16, .2, C.leaf2);
      p('sphere', x + Math.cos(a) * r, .1, z + Math.sin(a) * r, .13, .12, .13, petals[(i + k) % petals.length]);
    }
  }
  function rock(p, x, z, s = 1) {
    p('rock', x, -.05 * s, z, .7 * s, .5 * s, .6 * s, C.stoneDark, { ry: rnd() * 6 });
    p('rock', x + .35 * s, -.05 * s, z + .2 * s, .4 * s, .3 * s, .4 * s, C.stone, { ry: rnd() * 6 });
  }
  function lamp(p, x, z) {
    p('cyl', x, 0, z, .12, .12, .12, C.ink);
    p('cyl', x, 0, z, .06, 1.35, .06, C.ink);
    p('sphere', x, 1.3, z, .22, .22, .22, '#ffe9b8', { glow: true });
    p('cone', x, 1.48, z, .3, .16, .3, C.ink);
    return [x, 1.42, z];
  }
  function bench(p, x, z, ry = 0) {
    const q = sub(p, x, z, ry);
    q('box', 0, .32, 0, .9, .07, .32, C.wood); q('box', 0, .45, -.14, .9, .26, .06, C.wood);
    q('box', -.38, 0, 0, .07, .32, .28, C.woodDark); q('box', .38, 0, 0, .07, .32, .28, C.woodDark);
  }
  function cottage(p, x, z, ry, roofC = C.roof, wallC = C.wall, s = 1) {
    const q = sub(p, x, z, ry, s);
    q.ao(0, 0, 1.25);
    q('round', 0, -.02, 0, 1.62, .14, 1.38, C.stoneDark);
    q('round', 0, 0, 0, 1.5, 1.05, 1.25, wallC);
    q('prism', 0, 1.0, 0, 1.75, .78, 1.45, roofC);
    q('box', .45, 1.25, -.25, .26, .62, .26, C.stoneDark);
    q('round', 0, 0, .6, .36, .66, .08, C.woodDark);
    [-.45, .45].forEach(dx => { q('box', dx, .38, .615, .38, .36, .04, C.white); q('box', dx, .42, .62, .3, .28, .05, '#ffe1a0', { glow: true }); });
    q('box', 0, .99, .7, 1.8, .06, .08, C.white);
    q('box', -.76, .42, 0, .05, .28, .3, '#ffe1a0', { glow: true });
  }
  function crate(p, x, z, s = 1, c = C.wood) { p('round', x, 0, z, .5 * s, .5 * s, .5 * s, c, { ry: rnd() }); }

  /* ═════════ 島工廠：分層倒角擠出 ═════════ */
  const M = {
    grass: std(C.grass), grass2: std(C.grass2), grass3: std(C.grass3), sand: std(C.sand),
    cliff: std(C.cliff), cliffDark: std(C.cliffDark),
    foam: basic(C.foam, { transparent: true, opacity: .6, depthWrite: false, side: THREE.DoubleSide }),
    shallow: basic(C.shallow, { transparent: true, opacity: .5, depthWrite: false, side: THREE.DoubleSide }),
  };
  const BASE_H = 1.0, BEVEL = .08, GROUND = BASE_H + BEVEL;
  function outline(seed, radius, wobble = .17, n = 56) {
    const r = mulberry32(seed);
    const hs = [[2, .45], [3, .3], [4, .15], [7, .1]].map(([f, w]) => [f, w, r() * Math.PI * 2]);
    // 一到兩個小灣：在隨機方向往內凹，打破圓餅輪廓
    const bays = Array.from({ length: 1 + Math.floor(r() * 2) }, () => [r() * Math.PI * 2, .12 + r() * .1]);
    return Array.from({ length: n }, (_, i) => {
      const a = i / n * Math.PI * 2;
      let k = 1 + wobble * hs.reduce((s, [f, w, ph]) => s + w * Math.sin(f * a + ph), 0);
      bays.forEach(([b, d]) => { const t = Math.atan2(Math.sin(a - b), Math.cos(a - b)); k -= d * (wobble / .17) * Math.exp(-t * t / .045); });
      return [Math.cos(a) * radius * k, Math.sin(a) * radius * k];
    });
  }
  const scaled = (pts, s, inset = 0) => pts.map(([x, z]) => {
    const r = Math.hypot(x, z), k = inset ? Math.max(r - inset, r * .05) / r : 1;
    return [x * s * k, z * s * k];
  });
  const shapeOf = pts => {                 // shape 的 y＝世界的 -z（rotateX(-π/2) 之後對回 z）
    const sh = new THREE.Shape();
    pts.forEach(([x, z], i) => (i ? sh.lineTo(x, -z) : sh.moveTo(x, -z)));
    sh.closePath(); return sh;
  };
  function slab(pts, depth, mats, y) {
    const g = new THREE.ExtrudeGeometry(shapeOf(pts), { depth, bevelEnabled: true, bevelThickness: BEVEL, bevelSize: .1, bevelSegments: 2, curveSegments: 4 });
    g.rotateX(-Math.PI / 2);
    const m = new THREE.Mesh(g, mats); m.position.y = y; m.castShadow = true; m.receiveShadow = true; return m;
  }
  function ring(pts, inner, outer, mat, y) {
    const sh = shapeOf(scaled(pts, outer));
    const hole = new THREE.Path();
    [...scaled(pts, inner)].reverse().forEach(([x, z], i) => (i ? hole.lineTo(x, -z) : hole.moveTo(x, -z)));
    sh.holes.push(hole);
    const g = new THREE.ShapeGeometry(sh, 2); g.rotateX(-Math.PI / 2);
    const m = new THREE.Mesh(g, mat); m.position.y = y; m.renderOrder = 1; return m;
  }
  const isles = [], isleGroups = [];
  // 所有島的各層（沙底、崖帶、草頂、浪花環）建好後依材質合併：21 座島 × 4 層 → 每種材質一個 mesh
  function mergeIsles() {
    const buckets = new Map();
    isleGroups.forEach(g => {
      g.updateMatrixWorld(true);
      g.traverse(o => {
        if (!o.isMesh) return;
        const geo = (o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone()).applyMatrix4(o.matrixWorld);
        const pos = geo.attributes.position.array, nor = geo.attributes.normal.array;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        const groups = geo.groups.length ? geo.groups : [{ start: 0, count: geo.attributes.position.count, materialIndex: 0 }];
        groups.forEach(gr => {
          const mat = mats[gr.materialIndex];
          if (!buckets.has(mat.uuid)) buckets.set(mat.uuid, { mat, pos: [], nor: [], shadow: o.castShadow, order: o.renderOrder });
          const bk = buckets.get(mat.uuid);
          for (let i = gr.start * 3, e = (gr.start + gr.count) * 3; i < e; i++) { bk.pos.push(pos[i]); bk.nor.push(nor[i]); }
        });
        geo.dispose(); o.geometry.dispose();
      });
    });
    buckets.forEach(bk => {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(bk.pos, 3));
      geo.setAttribute('normal', new THREE.Float32BufferAttribute(bk.nor, 3));
      geo.computeBoundingSphere();
      const m = new THREE.Mesh(geo, bk.mat); m.castShadow = m.receiveShadow = bk.shadow; m.renderOrder = bk.order; world.add(m);
    });
  }
  function makeIsle({ u, v, radius, seed, grass = 'grass', highland = 0, wobble = .17, su = 1, sv = 1 }) {
    const { x, z } = toWorld(u, v);
    // 沿螢幕的 u／v 方向拉長：先換成螢幕座標縮放，再換回世界座標
    const pts = outline(seed, radius, wobble).map(([px, pz]) => { const pu = (px - pz) * SQ * su, pv = (px + pz) * SQ * sv; return [(pu + pv) * SQ, (pv - pu) * SQ]; });
    const g = new THREE.Group(); g.position.set(x, 0, z);
    g.add(ring(pts, 1.13, 1.19, M.foam, .05));
    g.add(slab(scaled(pts, 1.12), .2, [M.sand, M.sand], -.14));
    g.add(slab(scaled(pts, 1.0), .34, [M.cliffDark, M.cliffDark], 0));
    g.add(slab(scaled(pts, 1, .07), BASE_H, [M[grass], M.cliff], 0));
    let top = GROUND;
    if (highland) {
      g.add(slab(scaled(pts, highland, .05), 1.0, [M.grass2, M.cliff], GROUND));
      top = GROUND + 1.0 + BEVEL;
    }
    isleGroups.push(g);
    const angR = a => {                    // 該方向的海岸半徑：射線與輪廓線段的交點（拉長的島角度不均勻，不能用索引內插）
      const dx = Math.cos(a), dz = Math.sin(a), n = pts.length;
      for (let i = 0; i < n; i++) {
        const [x0, z0] = pts[i], [x1, z1] = pts[(i + 1) % n], ex = x1 - x0, ez = z1 - z0;
        const den = dx * ez - dz * ex; if (Math.abs(den) < 1e-9) continue;
        const r = (x0 * ez - z0 * ex) / den, t = (x0 * dz - z0 * dx) / den;
        if (r > 0 && t >= -1e-6 && t <= 1 + 1e-6) return r;
      }
      return radius;
    };
    const isle = { x, z, radius, su, sv, pts, top, angR, gaps: [] };
    isle.inside = (wx, wz, m = .8) => Math.hypot(wx - x, wz - z) < angR(Math.atan2(wz - z, wx - x)) * m;
    isles.push(isle);
    return isle;
  }


  /* ═════════ 佈局（螢幕座標：u 往右、v 往前）═════════
     主島拉長成一條：西岸是啟航港（總覽、課前），中間是現場步道（第一次對話 → 三個 Lab）。
     Lab 3 的島尾分出三座拱橋：北邊工坊島、東邊數學島、東南筆記島。速查燈船停在主島前方的海上。 */
  const M_SCHED = DATA.schedule;
  const MAIN = makeIsle({ u: 1, v: 1, radius: 13, su: 2.35, sv: .82, seed: 11, wobble: .06 });
  const TOOLS = makeIsle({ u: 14, v: -27, radius: 9, su: 1.5, sv: 1, seed: 57, wobble: .08, grass: 'grass2' });
  const MATHI = makeIsle({ u: 43, v: -8, radius: 6.2, seed: 73, wobble: .1, grass: 'grass3' });
  const NOTES = makeIsle({ u: 40, v: 13, radius: 5.6, seed: 91, wobble: .1 });
  const SEA = { x: 0, z: 0, top: .08, radius: 3, inside: () => false, angR: () => 3, gaps: [] };   // 燈船沒有島
  const STOP_UV = {
    index: [MAIN, -24, -4], prep: [MAIN, -19, 6], 'first-run': [MAIN, -12, -2],
    'lab1-cluster': [MAIN, -2, -3.4], 'lab2-pca': [MAIN, 8.6, -3.4], 'lab3-notes': [MAIN, 19.2, -3.4],
    // 工坊島前後兩排錯開：前排的高塔不能擋住後排（全景時要點得到）
    'agent-workflows': [TOOLS, 5, -31], 'agents-md': [TOOLS, 13, -31.5], 'git-safety': [TOOLS, 21, -31],
    'mcp-skills': [TOOLS, 8.5, -23.5], 'local-models': [TOOLS, 16.5, -23], herdr: [TOOLS, 23.5, -23.5],
    'math-applications': [MATHI, 43, -8], 'research-notes': [NOTES, 40, 13], cheatsheet: [SEA, -7, 21],
  };
  const SLOT = {};       // stem → { isle, x, z, y(base) }
  PAGES.forEach(p => {
    const [I, u, v] = STOP_UV[p.stem], w = toWorld(u, v);
    SLOT[p.stem] = { isle: I, x: w.x, z: w.z, y: I.top };
  });
  const GRP_ISLE = { start: MAIN, live: MAIN, tools: TOOLS, math: MATHI, notes: NOTES };

  /* ── 拱橋：二次貝茲，木板兩色交替、細扶手、每 3 片一根柱；起點可以指定島上的某一點 ── */
  const bridges = [];
  function shore(I, x0, z0, ux, uz, out) {        // 從島內一點沿方向走到海岸（最後一個仍在島內的點）
    let t = 0; while (t < 80 && I.inside(x0 + ux * (t + .25), z0 + uz * (t + .25), .92)) t += .25;
    return out ? t + .25 : t;
  }
  function bridge(A, B, from) {
    const ax = from ? from.x : A.x, az = from ? from.z : A.z;
    const dx = B.x - ax, dz = B.z - az, L = Math.hypot(dx, dz), ux = dx / L, uz = dz / L;
    const s0 = shore(A, ax, az, ux, uz), s1 = L - shore(B, B.x, B.z, -ux, -uz);
    A.gaps.push(Math.atan2(az + uz * s0 - A.z, ax + ux * s0 - A.x)); B.gaps.push(Math.atan2(-uz, -ux));
    const p0 = new THREE.Vector3(ax + ux * s0, A.top - .04, az + uz * s0);
    const p2 = new THREE.Vector3(ax + ux * s1, B.top - .04, az + uz * s1);
    const p1 = p0.clone().lerp(p2, .5); p1.y = Math.max(p0.y, p2.y) + Math.min(1.6, .22 * (s1 - s0) + .4);
    const curve = new THREE.QuadraticBezierCurve3(p0, p1, p2);
    const n = Math.max(4, Math.round(curve.getLength() / .3)), pts = curve.getSpacedPoints(n);
    const ry = Math.atan2(ux, uz);
    for (let i = 0; i < n; i++) {
      const a = pts[i], b = pts[i + 1], h = Math.hypot(b.x - a.x, b.z - a.z), m = a.clone().lerp(b, .5);
      const rx = -Math.atan2(b.y - a.y, h);
      part('box', m.x, m.y - .035, m.z, 1.12, .07, h * .92, i % 3 ? C.wood : C.woodDark, { rx, ry });
      [-1, 1].forEach(side => {
        const ox = uz * .56 * side, oz = -ux * .56 * side;
        part('box', m.x + ox, m.y + .44, m.z + oz, .05, .05, h + .02, C.woodDark, { rx, ry });
        if (i % 3 === 0) part('cyl', m.x + ox, m.y - .1, m.z + oz, .08, .58, .08, C.woodDark);
      });
    }
    [[A, -1, p0], [B, 1, p2]].forEach(([I, sgn, end]) => {
      for (let k = 1; k <= 3; k++) {
        const t = k * .45; part('cyl', end.x + ux * t * sgn, I.top - .02, end.z + uz * t * sgn, .5, .05, .5, '#e9dcc0', { ry: rnd() * 3 });
      }
    });
    bridges.push({ A, B, curve, pts });
  }
  const lab3 = SLOT['lab3-notes'];
  bridge(MAIN, TOOLS, { x: lab3.x, z: lab3.z });
  bridge(MAIN, MATHI, { x: lab3.x, z: lab3.z });
  bridge(MAIN, NOTES, { x: lab3.x, z: lab3.z });
  const nearGap = (I, a, tol = .42) => I.gaps.some(g => Math.abs(Math.atan2(Math.sin(a - g), Math.cos(a - g))) < tol);

  /* ═════════ 地標：每頁一組建築（靜態零件，會投影）＋會動的零件（動態池，不投影） ═════════
     每個地標有兩段動畫，都是純函式、u = 0 是同一個靜止姿態，結束時回到它：
       IDLE[stem]：沒選取時輪播的小動作，不能露出任何要學生自己觀察或判斷的結果
       POSE[stem]：答完猜題才播的完整動畫
     約束列在 tools/island_meta.py 開頭，check_island_browser.js 用 probe()／invariants() 實測。 */
  const FACE = Math.PI / 4;                       // 正面朝向初始視角
  const B = {};                                   // stem → { x, y, z, top, r, isle }
  const dynMat = new THREE.MeshLambertMaterial({ color: '#ffffff' });
  const _o = new THREE.Object3D(), _zero = new THREE.Matrix4().makeScale(0, 0, 0), _col = new THREE.Color();
  const _UY = new THREE.Vector3(0, 1, 0), _dir = new THREE.Vector3(), _v1 = new THREE.Vector3(), _m4 = new THREE.Matrix4();
  _o.rotation.order = 'YXZ';
  const pools = [];
  function pool(kind, cap) {
    const mesh = new THREE.InstancedMesh(GEO[kind], dynMat, cap);
    mesh.frustumCulled = false; mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage); mesh.receiveShadow = true;
    for (let i = 0; i < cap; i++) { mesh.setMatrixAt(i, _zero); mesh.setColorAt(i, _col.set('#ffffff')); }
    let n = 0; const cols = [];
    const P = {
      mesh,
      alloc(c) { if (n >= cap) throw new Error('動態池已滿：' + kind); cols[n] = c; mesh.setColorAt(n, _col.set(c)); mesh.instanceColor.needsUpdate = true; return n++; },
      color(id, c) { if (cols[id] === c) return; cols[id] = c; mesh.setColorAt(id, _col.set(c)); mesh.instanceColor.needsUpdate = true; },
      colorOf(id) { return cols[id]; },
      hide(id) { mesh.setMatrixAt(id, _zero); mesh.instanceMatrix.needsUpdate = true; },
      at(id, x, y, z, w, h, d, ry = 0) {
        _o.position.set(x, y + h / 2, z); _o.rotation.set(0, ry, 0); _o.quaternion.setFromEuler(_o.rotation); _o.scale.set(w, h, d); _o.updateMatrix();
        mesh.setMatrixAt(id, _o.matrix); mesh.instanceMatrix.needsUpdate = true;
      },
      beam(id, a, b, w) {            // 圓柱沿 a → b
        _dir.subVectors(b, a); const len = _dir.length();
        if (len < .02) { P.hide(id); return; }
        _o.position.addVectors(a, b).multiplyScalar(.5);
        _o.quaternion.setFromUnitVectors(_UY, _dir.divideScalar(len)); _o.scale.set(w, len, w); _o.updateMatrix();
        mesh.setMatrixAt(id, _o.matrix); mesh.instanceMatrix.needsUpdate = true;
      },
      pos(id) { mesh.getMatrixAt(id, _m4); return new THREE.Vector3().setFromMatrixPosition(_m4); },
      finish() { mesh.count = n; },  // 只畫用到的實例：藏起來的實例一樣會跑頂點著色器
    };
    world.add(mesh); pools.push(P);
    return P;
  }
  const RD = pool('round', 80), CY = pool('cyl', 110), SP = pool('sphere', 56);

  /* 地面上的標示：一張貼花圖集、一次繪製；全景時淡出 */
  const decals = [];
  // 區域座標：x 往畫面右、z 往畫面前；以地標中心為原點
  function LOC(S, y = S.y) {
    const c = Math.cos(FACE), sn = Math.sin(FACE);
    const X = (x, z) => S.x + x * c + z * sn, Z = (x, z) => S.z - x * sn + z * c;
    return {
      q: at(S.x, y, S.z, FACE), y,
      P: (x, h, z) => new THREE.Vector3(X(x, z), y + h, Z(x, z)),
      rd: (id, x, h, z, w, hh, d, ry = 0) => RD.at(id, X(x, z), y + h, Z(x, z), w, hh, d, FACE + ry),
      sp: (id, x, h, z, w, hh, d) => SP.at(id, X(x, z), y + h, Z(x, z), w, hh, d, FACE),
      cy: (id, x, h, z, w, hh, d) => CY.at(id, X(x, z), y + h, Z(x, z), w, hh, d, FACE),
      beam: (id, a, b, w) => CY.beam(id, a, b, w),
      // 世界座標 → 區域座標
      local: (wx, wz) => { const dx = wx - S.x, dz = wz - S.z; return [dx * c - dz * sn, dx * sn + dz * c]; },
      say: (text, x, z, size = .42, ink = '#2a3c78') => decals.push({ text, x: X(x, z), y: y + .03, z: Z(x, z), size: size * 1.3, ink }),
    };
  }
  function shed(q, x, z, w, d, h, roofC, wallC = C.wall) {     // 小型建築：牆＋山形屋頂＋門＋亮燈的窗
    q.ao(x, z, Math.max(w, d) * .62);
    q('round', x, 0, z, w, h, d, wallC);
    q('prism', x, h - .02, z, w + .22, Math.min(.72, w * .36), d + .16, roofC);
    q('box', x, 0, z + d / 2 + .01, Math.min(.42, w * .26), Math.min(.72, h * .6), .06, C.woodDark);
    q('box', x - w * .28, h * .46, z + d / 2 + .01, .28, .26, .04, '#ffe1a0', { glow: true });
    q('box', x + w * .28, h * .46, z + d / 2 + .01, .28, .26, .04, '#ffe1a0', { glow: true });
  }
  function hall(q, x, z, w, d, h, roofC, wallC = C.wall, trim = C.white) {   // 主建築：基座、壁柱、成排亮窗、門廊、山形屋頂
    const fz = z + d / 2, doorH = Math.min(1.15, h * .55), n = Math.max(2, Math.round(w / .95));
    q.ao(x, z, Math.max(w, d) * .66);
    q('box', x, 0, z, w + .3, .16, d + .3, C.stoneDark);
    q('box', x, .16, z, w, h - .16, d, wallC);
    [-1, 1].forEach(s => q('box', x + s * w / 2, .16, fz, .14, h - .16, .1, trim));
    for (let i = 0; i < n; i++) {
      const wx = x - w / 2 + (i + .5) * w / n;
      if (Math.abs(wx - x) < .5) continue;
      q('box', wx, h * .4, fz + .005, .46, h * .38, .05, trim);
      q('box', wx, h * .4 + .04, fz + .02, .34, h * .38 - .08, .05, '#ffe1a0', { glow: true });
    }
    q('box', x, .16, fz + .01, .74, doorH, .06, C.woodDark);
    q('box', x, .16 + doorH, fz + .25, 1.05, .08, .55, roofC);
    q('box', x, h, z, w + .18, .1, d + .18, trim);
    q('prism', x, h + .1, z, w + .36, Math.min(1.25, w * .3), d + .24, roofC);
  }
  function pavilion(q, x, z, w, d, h, roofC) {     // 四柱涼亭
    q('box', x, 0, z, w + .3, .12, d + .3, C.stone);
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, b]) => q('box', x + a * w / 2, .12, z + b * d / 2, .12, h, .12, C.woodDark));
    q('box', x, h + .1, z, w + .3, .1, d + .3, C.white);
    q('prism', x, h + .2, z, w + .5, .62, d + .45, roofC);
  }
  const SKIN = '#f1c9a5';
  // 小人（動態池）：身體＋頭
  const pawnAlloc = shirt => ({ b: RD.alloc(shirt), h: SP.alloc(SKIN) });
  function pawnAt(L, P, x, h, z, s = 1) { L.rd(P.b, x, h, z, .42 * s, .62 * s, .3 * s); L.sp(P.h, x, h + .6 * s, z, .34 * s, .34 * s, .34 * s); }
  function pawnHide(P) { RD.hide(P.b); SP.hide(P.h); }
  function pawnStatic(q, x, z, shirt, s = 1) { q('round', x, 0, z, .42 * s, .62 * s, .3 * s, shirt); q('sphere', x, .6 * s, z, .34 * s, .34 * s, .34 * s, SKIN); }

  const LM = {}, POSE = {}, IDLE = {}, INV = {}, PROBE = {};
  const clamp01 = x => Math.max(0, Math.min(1, x));
  const seg = (u, a, b) => { const t = clamp01((u - a) / (b - a)); return t * t * (3 - 2 * t); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const pulse = (u, a, b) => Math.sin(Math.PI * clamp01((u - a) / (b - a)));      // 0 → 1 → 0
  const MUTED = '#6f6a5f', GLASS = '#dcf3f0', DIM = '#8c8f8a';

  /* ── 啟航港 ── */
  // 總覽：瞭望台。望遠鏡輪流轉向三個 Lab；三個資料箱是三份為這堂課造的資料
  LM.index = S => {
    const L = LOC(S), { q } = L;
    q.ao(0, 0, 2.2);
    q('cyl', 0, 0, 0, 3.3, .3, 3.3, C.stoneDark);
    q('cyl', 0, .3, 0, 2.3, 2.6, 2.3, C.cream);
    for (let k = 0; k < 6; k++) { const a = k / 6 * Math.PI * 2; q('box', Math.cos(a) * 1.12, 1.4, Math.sin(a) * 1.12, .3, .5, .3, '#ffe1a0', { glow: true, ry: -a }); }
    q('cyl', 0, 2.9, 0, 3.1, .16, 3.1, C.white);
    for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; q('cyl', Math.cos(a) * 1.45, 3.06, Math.sin(a) * 1.45, .08, .5, .08, C.woodDark); }
    for (let k = 0; k < 12; k++) { const a = (k + .5) / 12 * Math.PI * 2; q('box', Math.cos(a) * 1.45, 3.5, Math.sin(a) * 1.45, .08, .06, .78, C.woodDark, { ry: -a }); }
    [-.25, .25].forEach(dx => q('cyl', dx, 3.06, .1, .06, .5, .06, C.ink)); q('cyl', 0, 3.06, -.25, .06, .5, .06, C.ink);   // 三腳架
    // 三個資料箱：手搖飲、外送、借閱
    q('cyl', -2.3, 0, 1.4, .8, .9, .8, '#e9d3b0'); q('cyl', -2.3, 0, 1.4, .82, .55, .82, '#c08a5a'); q('sphere', -2.3, .82, 1.4, .82, .28, .82, C.white);
    q('cyl', -2.15, .95, 1.4, .07, .7, .07, C.red, { rz: -.25 });
    q('round', 2.2, 0, 1.2, .95, .8, .95, C.red); q('box', 2.2, .8, 1.2, 1.0, .08, 1.0, C.roofDark);
    [0, 1, 2].forEach(i => q('box', .1, i * .16, 2.3, 1.0 - i * .08, .15, .7, [C.navy, C.roofGreen, C.amber][i], { ry: i * .2 }));
    L.say('三份 AI 沒見過的資料', 0, 3.3, .32, MUTED);
    const scope = RD.alloc(C.navy), lens = SP.alloc(C.gold);
    const aim = ['lab1-cluster', 'lab2-pca', 'lab3-notes'].map(s => { const [x, z] = L.local(SLOT[s].x, SLOT[s].z); return Math.atan2(x, z); });
    const set = ry => { L.rd(scope, 0, 3.52, 0, .3, .3, 1.3, ry); L.sp(lens, Math.sin(ry) * .68, 3.5, Math.cos(ry) * .68, .34, .34, .34); };
    const rest = aim[0];
    IDLE.index = { dur: 4, pose(u) { set(rest + Math.sin(u * Math.PI * 2) * .35 * pulse(u, 0, 1)); } };
    POSE.index = { dur: 6, pose(u) {
      const k = u < .3 ? lerp(rest, aim[1], seg(u, .05, .25)) : u < .6 ? lerp(aim[1], aim[2], seg(u, .35, .55)) : lerp(aim[2], rest, seg(u, .7, .95));
      set(k);
    } };
    return { h: 4.4, r: 3 };
  };

  // 課前準備：綠燈檢修棚。三盞燈 git、opencode、uv；答完才依序轉綠
  LM.prep = S => {
    const L = LOC(S), { q } = L;
    shed(q, 0, -.7, 3.4, 1.8, 1.6, C.roofGreen);
    q('box', 0, 0, 1.1, 3.6, .08, 1.4, C.stone);
    const LX = [-1.2, 0, 1.2];
    const lights = LX.map((x, i) => {
      q('cyl', x, 0, 1.3, .12, 1.5, .12, C.ink); q('round', x, 1.4, 1.3, .52, .52, .34, C.ink);
      L.say(['git', 'opencode', 'uv'][i], x, 2.25, .3);
      const id = SP.alloc(DIM); L.sp(id, x, 1.5, 1.46, .34, .34, .34); return id;
    });
    q('round', 1.9, 0, -.1, .55, .55, .55, C.amber); q('round', 2.2, 0, .5, .45, .45, .45, C.wood);
    const GREEN = '#3fbf6a';
    IDLE.prep = { dur: 3, pose(u) { SP.color(lights[0], (u > .2 && u < .4) || (u > .6 && u < .8) ? C.amber : DIM); } };
    POSE.prep = { dur: 5, pose(u) {
      lights.forEach((id, i) => SP.color(id, u > .1 + i * .2 && u < .9 ? GREEN : DIM));
    } };
    return { h: 2.4, r: 2.6 };
  };

  /* ── 現場步道 ── */
  // 第一次對話：權限柵欄。請求票停在柵欄前等你；三塊牌是三種回答。不演 agent 被拒之後的反應
  LM['first-run'] = S => {
    const L = LOC(S), { q } = L;
    q.ao(-1.5, -.6, 1.2);
    q('round', -1.6, 0, -.7, 1.7, 1.5, 1.3, C.navy);
    q('box', -1.6, .45, -.04, 1.3, .8, .04, '#1b1b2b');
    [0, 1, 2].forEach(i => q('box', -1.85 + i * .1, .95 - i * .17, -.01, .55 - i * .12, .06, .02, '#9fe0b0', { glow: true }));
    [.6, 2.3].forEach(x => q('box', x, 0, .3, .22, 1.3, .22, C.woodDark));
    for (let i = 0; i < 5; i++) q('box', .78 + i * .32, .95, .3, .32, .16, .12, i % 2 ? C.white : C.red);
    const SIGN = [['Allow once', '#3f9f6a', '#a9cdb5'], ['Always allow', '#2a3c78', '#a4adc8'], ['Reject', '#b8503c', '#ddb3a8']];
    const faces = SIGN.map(([t, , dim], i) => {
      const x = -.9 + i * 1.3;
      q('box', x, 0, 1.9, .1, .9, .1, C.woodDark);
      L.say(t, x, 2.45 + (i % 2) * .6, .21);           // 中間那塊往下錯開一行，三個字串才不會疊在一起
      const id = RD.alloc(dim); L.rd(id, x, .7, 1.9, 1.05, .5, .08); return id;
    });
    const ticket = RD.alloc(C.gold);
    const tk = t => L.rd(ticket, lerp(-.75, .25, t), .95 + Math.sin(t * Math.PI) * .3, lerp(-.05, .3, t), .5, .08, .36);
    tk(0);
    IDLE['first-run'] = { dur: 5, pose(u) { tk(u < .5 ? seg(u, .1, .4) : 1 - seg(u, .75, .95)); } };
    POSE['first-run'] = { dur: 6, pose(u) {
      tk(u < .5 ? seg(u, .05, .25) : 1 - seg(u, .8, .95));
      SIGN.forEach(([, on, dim], i) => RD.color(faces[i], u > .3 + i * .12 && u < .85 ? on : dim));
    } };
    return { h: 2.2, r: 3.4 };                    // 範圍放大到地面字的前緣，裝飾樹才不會擋住
  };

  // Lab 1：手搖飲攤車廣場。杯子＝一天的營業紀錄（資料點），永遠不動、只變色；旗桿＝群中心，k-means 真的算一次
  LM['lab1-cluster'] = S => {
    const L = LOC(S), { q } = L;
    q.ao(0, .4, 4.2);
    q('box', 0, 0, .5, 8.8, .08, 5.4, C.stone);
    for (let i = 0; i < 8; i++) q('box', -3.85 + i * 1.1, .08, .5, .04, .01, 5.3, C.stoneDark);
    // 攤車：車身、輪子、條紋遮陽棚、屋頂的大杯子
    const cz = -2.9;
    q.ao(0, cz, 2);
    q('round', 0, .45, cz, 3.2, 1.25, 1.4, C.cream);
    q('box', 0, 1.0, cz + .71, 2.6, .35, .04, C.roof);
    [-1.2, 1.2].forEach(x => q('cyl', x, .05, cz + .55, .8, .2, .8, C.ink, { rz: Math.PI / 2 }));
    [-1.45, 1.45].forEach(x => q('box', x, 1.7, cz + .55, .08, .9, .08, C.woodDark));
    for (let i = 0; i < 7; i++) q('box', -1.5 + i * .5, 2.5, cz + .35, .5, .08, 1.6, i % 2 ? C.white : C.red, { rx: .3 });
    q('cyl', 0, 1.7, cz - .2, 1.15, 1.9, 1.15, '#ecd9b8'); q('cyl', 0, 1.7, cz - .2, 1.18, 1.25, 1.18, '#c08a5a');
    for (let i = 0; i < 5; i++) q('sphere', -.35 + i * .18, 1.75, cz + .38, .2, .2, .2, '#3b2a20');
    q('sphere', 0, 3.5, cz - .2, 1.22, .42, 1.22, C.white); q('cyl', .25, 3.7, cz - .2, .14, 1.4, .14, C.red, { rz: -.25 });
    L.say('k-means：指派 → 更新', 0, 3.75, .36);
    // 資料點：三團不規則的杯子（固定種子）
    const blobs = [[-2.6, .2], [0, 1.9], [2.7, .1]], cups = [], ids = [];
    blobs.forEach(([bx, bz]) => { for (let k = 0; k < 8; k++) { const a = rnd() * Math.PI * 2, r = Math.sqrt(rnd()) * 1.05; cups.push([bx + Math.cos(a) * r, bz + Math.sin(a) * r * .8]); } });
    const NEUT = '#efe6d2', GC = [C.red, C.navy, C.forest];
    cups.forEach(([x, z]) => { const id = CY.alloc(NEUT); L.cy(id, x, .08, z, .32, .5, .32); ids.push(id); });
    // k-means：起點故意擺歪，真的跑到收斂
    const start = [[-1.2, -.7], [.9, -.6], [3.4, 2.2]], frames = [];
    let cen = start.map(c => c.slice());
    for (let it = 0; it < 6; it++) {
      const asg = cups.map(([x, z]) => { let b = 0, bd = 1e9; cen.forEach(([cx, cz2], j) => { const d = (x - cx) ** 2 + (z - cz2) ** 2; if (d < bd) { bd = d; b = j; } }); return b; });
      const nxt = cen.map((c, j) => { const m = cups.filter((_, i) => asg[i] === j); return m.length ? [m.reduce((s, p) => s + p[0], 0) / m.length, m.reduce((s, p) => s + p[1], 0) / m.length] : c; });
      frames.push({ asg, from: cen, to: nxt });
      const moved = nxt.some((c, j) => Math.hypot(c[0] - cen[j][0], c[1] - cen[j][1]) > 1e-3);
      cen = nxt; if (!moved) break;
    }
    const flags = GC.map(c => ({ pole: CY.alloc(C.white), cloth: RD.alloc(c) }));
    const flag = (F, x, z, wave = 0) => { L.cy(F.pole, x, .08, z, .1, 2.1, .1); L.rd(F.cloth, x + .32, 1.68, z, .62 + wave, .42, .05); };
    const rest = () => { flags.forEach((F, j) => flag(F, start[j][0], start[j][1])); ids.forEach(id => CY.color(id, NEUT)); };
    rest();
    INV['lab1-cluster'] = { iterations: frames.length };
    PROBE['lab1-cluster'] = () => ({ cups: ids.map(id => CY.pos(id).toArray()), flags: flags.map(F => CY.pos(F.pole).toArray()) });
    IDLE['lab1-cluster'] = { dur: 3, pose(u) { flags.forEach((F, j) => flag(F, start[j][0], start[j][1], Math.sin(u * Math.PI * 4 + j) * .12 * pulse(u, 0, 1))); } };
    POSE['lab1-cluster'] = { dur: 2 + frames.length * 1.6, pose(u) {
      if (u <= 0 || u >= .97) { rest(); return; }
      const run = clamp01((u - .04) / .82), n = frames.length, f = Math.min(n - 1, Math.floor(run * n)), t = run * n - f;
      const F0 = frames[f];
      ids.forEach((id, i) => CY.color(id, t > .1 || f > 0 ? GC[F0.asg[i]] : NEUT));          // 指派：杯子只變色
      flags.forEach((F, j) => {                                                            // 更新：旗桿走到該群的平均位置
        const k = seg(t, .45, .95), [x0, z0] = F0.from[j], [x1, z1] = F0.to[j];
        if (u > .86) { const b = seg(u, .88, .965), [ex, ez] = frames[n - 1].to[j]; flag(F, lerp(ex, start[j][0], b), lerp(ez, start[j][1], b)); }
        else flag(F, lerp(x0, x1, k), lerp(z0, z1, k));
      });
      if (u > .88) ids.forEach(id => CY.color(id, NEUT));
    } };
    return { h: 4.1, r: 4.8 };
  };

  // Lab 2：外送投影台。訂單點雲固定在桌上；一根軸轉動，金色點是每筆訂單投影到軸上的位置（二維示意）
  LM['lab2-pca'] = S => {
    const L = LOC(S), { q } = L;
    q.ao(0, .2, 4);
    q('round', 0, 0, .3, 7.4, .5, 5.0, C.wall2);
    q('box', 0, .5, .3, 7.0, .04, 4.6, C.cream);
    for (let i = -3; i <= 3; i++) q('box', i, .54, .3, .02, .01, 4.4, '#e3d6bd');
    for (let i = -2; i <= 2; i++) q('box', 0, .54, .3 + i, 6.8, .01, .02, '#e3d6bd');
    // 外送箱與機車
    q('round', -3.4, 0, -2.6, .95, .85, .95, C.red); q('box', -3.4, .85, -2.6, 1.0, .08, 1.0, C.roofDark);
    q('round', -2.3, 0, -2.75, .8, .7, .8, C.red); q('round', -2.3, .7, -2.75, .7, .55, .7, C.red);
    q('round', 2.6, .25, -2.7, 1.8, .45, .6, C.navy); [1.9, 3.3].forEach(x => q('cyl', x, 0, -2.7, .55, .2, .55, C.ink, { rz: Math.PI / 2 }));
    q('box', 3.2, .7, -2.7, .1, .7, .1, C.ink); q('box', 3.2, 1.35, -2.7, .1, .06, .7, C.ink);
    // 燈桿
    q('cyl', -3.5, 0, 2.6, .14, 3.4, .14, C.ink); q('cone', -3.5, 3.3, 2.6, .7, .4, .7, C.ink); q('sphere', -3.5, 3.2, 2.6, .36, .36, .36, '#ffe9b8', { glow: true });
    { const w = L.P(-3.5, 3.3, 2.6); lamps.push([w.x, w.y, w.z]); }
    L.say('二維示意', 2.6, 2.95, .34, MUTED);
    // 點雲：拉長、斜放的一團（固定種子）
    const C0 = [0, .3], th0 = .55, pts = [];
    for (let i = 0; i < 18; i++) {
      const g = () => { let s = 0; for (let k = 0; k < 4; k++) s += rnd(); return (s - 2) * 1.2; };
      const t = g() * 1.45, s = g() * .42;
      pts.push([C0[0] + t * Math.cos(th0) - s * Math.sin(th0), C0[1] + t * Math.sin(th0) + s * Math.cos(th0)]);
    }
    pts.forEach(([x, z]) => q('sphere', x, .56, z, .36, .36, .36, C.navy));
    const mx = pts.reduce((s, p) => s + p[0], 0) / pts.length, mz = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    let sxx = 0, sxz = 0, szz = 0; pts.forEach(([x, z]) => { sxx += (x - mx) ** 2; sxz += (x - mx) * (z - mz); szz += (z - mz) ** 2; });
    const thP = .5 * Math.atan2(2 * sxz, sxx - szz);                     // 變異最大的方向
    const thR = thP + 1.25;                                              // 靜止時的軸：故意不是最好的方向
    const axis = CY.alloc(C.gold), dots = pts.map(() => SP.alloc(C.amber)), drops = pts.map(() => CY.alloc('#c9b48a'));
    const H = .62;
    const setAxis = th => {
      const dx = Math.cos(th), dz = Math.sin(th);
      L.beam(axis, L.P(mx - dx * 3.3, H, mz - dz * 3.3), L.P(mx + dx * 3.3, H, mz + dz * 3.3), .07);
      pts.forEach(([x, z], i) => {
        const t = (x - mx) * dx + (z - mz) * dz, px = mx + t * dx, pz = mz + t * dz;
        L.sp(dots[i], px, H - .1, pz, .22, .22, .22);
        L.beam(drops[i], L.P(x, H, z), L.P(px, H, pz), .025);
      });
    };
    setAxis(thR);
    INV['lab2-pca'] = { principal: thP, rest: thR };
    IDLE['lab2-pca'] = { dur: 4, pose(u) { setAxis(thR + Math.sin(u * Math.PI * 2) * .16); } };
    POSE['lab2-pca'] = { dur: 6.5, pose(u) {
      const target = thR + Math.atan2(Math.sin(thP - thR), Math.cos(thP - thR));   // 走最近的那一圈
      setAxis(u < .7 ? lerp(thR, target, seg(u, .08, .55)) : lerp(target, thR, seg(u, .78, .97)));
    } };
    return { h: 3.4, r: 4.6 };
  };

  // Lab 3：圖書館門檻尺。書卡依風險分數排在尺上；門檻桿一定由人手推動，不停在任何特定門檻
  LM['lab3-notes'] = S => {
    const L = LOC(S), { q } = L;
    hall(q, 0, -2.6, 5.4, 2.0, 2.7, C.roofNavy);
    for (let i = 0; i < 9; i++) q('box', -1.9 + i * .18, 1.95, -1.58, .14, .5 + (i % 3) * .08, .04, [C.red, C.navy, C.forest, C.amber][i % 4]);
    const RX = x => -3.6 + 7.2 * x, RZ = 1.0;
    q('box', 0, 0, RZ, 7.8, .14, .8, C.white);
    for (let k = 0; k <= 10; k++) q('box', RX(k / 10), .14, RZ + .26, .04, .02, k % 5 ? .18 : .3, C.ink);
    L.say('0', RX(0), RZ + .85, .3, MUTED); L.say('1', RX(1), RZ + .85, .3, MUTED); L.say('逾期風險分數', 0, RZ + .85, .3, MUTED);
    const scores = [.04, .09, .13, .18, .24, .29, .33, .41, .47, .55, .62, .71, .8, .91];
    const books = scores.map(s => { const id = RD.alloc(C.cream); L.rd(id, RX(s), .14, RZ - .05, .2, .42, .3); return id; });
    // 提醒信箱：堆高＝這個門檻要寄幾封
    q('box', 3.6, 0, -.6, .12, 1.1, .12, C.ink); q('round', 3.6, 1.1, -.6, .9, .7, .7, C.red); q('box', 3.6, 1.5, -.24, .5, .06, .02, C.ink);
    L.say('提醒信箱', 3.6, .25, .3, MUTED);
    const stack = RD.alloc(C.white);
    const pole = CY.alloc(C.gold), bar = RD.alloc(C.gold), hand = SP.alloc(SKIN), sleeve = RD.alloc(C.forest);
    const REST = .66, at_ = { t: REST };
    const setT = t => {
      at_.t = t; const x = RX(t);
      L.cy(pole, x, .14, RZ, .1, 1.4, .1); L.rd(bar, x, 1.4, RZ, .16, .1, 1.0);
      L.sp(hand, x - .22, .95, RZ + .32, .26, .26, .26); L.rd(sleeve, x - .62, .86, RZ + .32, .6, .2, .2);
      let n = 0; scores.forEach((s, i) => { const on = s >= t; RD.color(books[i], on ? C.gold : C.cream); n += on; });
      L.rd(stack, 3.6, 1.82, -.6, .7, .04 + n * .07, .5);
    };
    setT(REST);
    PROBE['lab3-notes'] = () => ({ t: at_.t, hand: SP.pos(hand).toArray(), pole: CY.pos(pole).toArray() });
    IDLE['lab3-notes'] = { dur: 3, pose(u) { setT(REST + Math.sin(u * Math.PI * 2) * .025); } };
    POSE['lab3-notes'] = { dur: 7, pose(u) { setT(u < .6 ? lerp(REST, .12, seg(u, .08, .55)) : lerp(.12, REST, seg(u, .62, .97))); } };
    return { h: 4.1, r: 4.8 };
  };

  /* ── 工坊島：課後 OpenCode 操作 ── */
  // 交接驛站：五格任務單、進度卷軸櫃。一個小人把 progress.md 放進櫃子，新對話的小人取出來讀
  LM['agent-workflows'] = S => {
    const L = LOC(S), { q } = L;
    shed(q, -1.3, -1.0, 1.9, 1.4, 1.3, C.roof);
    [-.1, 2.3].forEach(x => q('box', x, 0, -.5, .1, 1.6, .1, C.woodDark));
    q('box', 1.1, .7, -.5, 2.6, .9, .08, C.wood);
    const CC = [C.navy, C.forest, C.amber, C.red, C.gold];
    CC.forEach((c, i) => q('box', .1 + i * .5, .8, -.44, .42, .7, .04, c));
    L.say('目標 輸入 限制 輸出 判準', 1.1, .25, .26, MUTED);
    q('round', 1.6, 0, 1.3, .9, 1.0, .65, C.wood);
    const drawer = RD.alloc(C.woodDark), scroll = CY.alloc(C.white), A = pawnAlloc(C.navy), Bp = pawnAlloc('#2f7a6a');
    const dr = k => L.rd(drawer, 1.6, .55, 1.65 + k * .35, .7, .3, .1);
    const rest = () => { dr(0); pawnAt(L, A, 0, 0, .3); L.cy(scroll, .25, .45, .3, .14, .5, .14); pawnAt(L, Bp, 2.6, 0, .7); };
    rest();
    IDLE['agent-workflows'] = { dur: 3, pose(u) { dr(pulse(u, .1, .9)); } };
    POSE['agent-workflows'] = { dur: 7, pose(u) {
      if (u <= 0 || u >= .97) { rest(); return; }
      const a = seg(u, .05, .3), back = seg(u, .42, .55);
      const ax = lerp(lerp(0, 1.2, a), 0, back), az = lerp(lerp(.3, 1.9, a), .3, back);
      pawnAt(L, A, ax, 0, az);
      dr(pulse(u, .3, .45) + pulse(u, .6, .75));
      const b = seg(u, .55, .65), b2 = seg(u, .75, .92);
      pawnAt(L, Bp, lerp(lerp(2.6, 2.1, b), 2.9, b2), 0, lerp(lerp(.7, 1.95, b), .2, b2));
      if (u < .36) L.cy(scroll, ax + .25, .45, az, .14, .5, .14);
      else if (u < .68) CY.hide(scroll);
      else L.cy(scroll, lerp(lerp(2.6, 2.1, b), 2.9, b2) + .25, .45, lerp(lerp(.7, 1.95, b), .2, b2), .14, .5, .14);
    } };
    return { h: 2.4, r: 2.6 };
  };

  // AGENTS.md：入口告示牌（提示）和另一道矮柵欄（permission）。兩者是不同的物件
  LM['agents-md'] = S => {
    const L = LOC(S), { q } = L;
    [-.4, 1.2].forEach(x => q('box', x, 0, -1.1, .2, 2.2, .2, C.stoneDark)); q('box', .4, 2.2, -1.1, 1.9, .3, .3, C.stoneDark);
    L.say('project/', .4, -.3, .3, MUTED);
    const SX = -1.5, SZ = .6;
    q('box', SX - .45, 0, SZ, .1, 1.3, .1, C.woodDark); q('box', SX + .45, 0, SZ, .1, 1.3, .1, C.woodDark);
    q('box', SX, 1.0, SZ, 1.25, 1.35, .1, C.cream); q('prism', SX, 2.35, SZ, 1.4, .3, .2, C.roof);
    L.say('AGENTS.md', SX, SZ + .8, .3);
    const lines = [0, 1, 2, 3, 4].map(i => { const id = RD.alloc(DIM); L.rd(id, SX, 2.1 - i * .23, SZ + .07, .9, .07, .02); return id; });
    const FX = 1.6, FZ = 1.0;
    [-.6, .6].forEach(d => q('box', FX + d, 0, FZ, .12, .8, .12, C.ink));
    for (let i = 0; i < 4; i++) q('box', FX - .45 + i * .3, .5, FZ, .3, .18, .08, i % 2 ? C.white : C.red);
    q('round', FX, 0, FZ - 1.0, .8, .6, .6, C.amber); L.say('data/', FX, FZ + .65, .28, MUTED); L.say('permission', FX, FZ + 1.05, .28);
    INV['agents-md'] = { sign: [SX, SZ], fence: [FX, FZ] };
    const ON = '#2a3c78';
    IDLE['agents-md'] = { dur: 3, pose(u) { RD.color(lines[0], u > .2 && u < .7 ? ON : DIM); } };
    POSE['agents-md'] = { dur: 5, pose(u) { lines.forEach((id, i) => RD.color(id, u > .1 + i * .12 && u < .9 ? ON : DIM)); } };
    return { h: 2.6, r: 2.6 };
  };

  // git 安全網：commit 標柱（起跑線）、跳台、安全網、diff 看板
  LM['git-safety'] = S => {
    const L = LOC(S), { q } = L;
    const PX = -1.7, PZ = 1.0;
    q('box', PX, 0, PZ, .5, .1, .5, C.stoneDark); q('cyl', PX, .1, PZ, .12, 2.1, .12, C.white); q('prism', PX + .3, 1.75, PZ, .5, .35, .05, C.gold, { rz: -Math.PI / 2 });
    q('box', PX, .02, PZ + .5, 1.6, .02, .12, C.white); L.say('commit', PX, PZ + .95, .3);
    const TX = .2, TZ = -1.0;
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, b]) => q('box', TX + a * .4, 0, TZ + b * .4, .1, 2.4, .1, C.woodDark));
    q('box', TX, 2.4, TZ, 1.0, .1, 1.0, C.wood); q('box', TX + .2, 2.45, TZ + .7, .4, .06, 1.2, C.wood);
    for (let k = 0; k < 6; k++) q('box', TX - .4, .3 + k * .36, TZ + .45, .3, .05, .05, C.woodDark);
    const NX = .9, NZ = 1.2;
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, b]) => q('box', NX + a * .7, 0, NZ + b * .55, .08, .55, .08, C.ink));
    for (let i = 0; i < 6; i++) q('box', NX - .6 + i * .24, .45, NZ, .03, .03, 1.1, C.forest);
    for (let i = 0; i < 5; i++) q('box', NX, .45, NZ - .45 + i * .22, 1.4, .03, .03, C.forest);
    q('box', 2.1, 0, -.9, .1, 1.5, .1, C.woodDark); q('box', 2.1, 1.0, -.9, 1.0, 1.0, .08, C.white);
    const diff = [0, 1, 2, 3].map(i => { const id = RD.alloc(i % 2 ? '#e0a89a' : '#9fd0aa'); L.rd(id, 2.1, 1.75 - i * .2, -.84, .75, .08, .02); return id; });
    const P = pawnAlloc(C.red);
    const deck = [TX + .2, 2.5, TZ + 1.1];
    const rest = () => { pawnAt(L, P, ...deck); diff.forEach((id, i) => RD.color(id, i % 2 ? '#e0a89a' : '#9fd0aa')); };
    rest();
    IDLE['git-safety'] = { dur: 3, pose(u) { diff.forEach((id, i) => RD.color(id, (u * 4 + i) % 2 < 1 ? (i % 2 ? '#c96a55' : '#4fa66a') : (i % 2 ? '#e0a89a' : '#9fd0aa'))); } };
    POSE['git-safety'] = { dur: 6, pose(u) {
      if (u <= 0 || u >= .97) { rest(); return; }
      if (u < .4) { const t = seg(u, .05, .38); pawnAt(L, P, lerp(deck[0], NX, t), lerp(deck[1], .5, t) + Math.sin(t * Math.PI) * .8, lerp(deck[2], NZ, t)); }
      else if (u < .55) pawnAt(L, P, NX, .5 + pulse(u, .4, .55) * .7, NZ);
      else if (u < .8) { const t = seg(u, .55, .78); pawnAt(L, P, lerp(NX, PX + .45, t), lerp(.5, 0, Math.min(1, t * 3)), lerp(NZ, PZ, t)); }
      else pawnAt(L, P, PX + .45, 0, PZ);
    } };
    return { h: 3.2, r: 2.6 };
  };

  // MCP、skills 與 subagent：機械手臂（MCP）、流程卡抽屜（skill）、只拿放大鏡的審查員（subagent）
  LM['mcp-skills'] = S => {
    const L = LOC(S), { q } = L;
    shed(q, -1.3, -1.1, 1.8, 1.3, 1.3, C.roofNavy);
    const BX = 2.0, BZ = -1.2;
    q('box', BX, 0, BZ, 1.0, 1.9, .5, C.woodDark);
    for (let r = 0; r < 3; r++) for (let i = 0; i < 5; i++) q('box', BX - .36 + i * .18, .2 + r * .58, BZ + .2, .13, .45, .1, [C.red, C.navy, C.forest, C.amber, C.cream][(i + r) % 5]);
    const AX = .1, AZ = .5;
    q('cyl', AX, 0, AZ, .7, .3, .7, C.ink); q('cyl', AX, .3, AZ, .2, .8, .2, C.amber);
    const seg1 = CY.alloc(C.amber), seg2 = CY.alloc(C.amber), grip = RD.alloc(C.ink), doc = RD.alloc(C.white);
    const shoulder = [AX, 1.1, AZ], shelf = [BX - .2, 1.2, BZ + .55];
    const arm = (k, carry) => {
      const tx = lerp(AX + .6, shelf[0], k), ty = lerp(1.0, shelf[1], k), tz = lerp(AZ + .3, shelf[2], k);
      const ex = (shoulder[0] + tx) / 2, ey = Math.max(shoulder[1], ty) + .6, ez = (shoulder[2] + tz) / 2;
      L.beam(seg1, L.P(shoulder[0], shoulder[1], shoulder[2]), L.P(ex, ey, ez), .16);
      L.beam(seg2, L.P(ex, ey, ez), L.P(tx, ty, tz), .13);
      L.rd(grip, tx, ty - .1, tz, .25, .2, .25);
      if (carry) L.rd(doc, tx, ty - .3, tz, .34, .04, .44); else RD.hide(doc);
    };
    arm(0, false);
    q('round', -1.8, 0, 1.2, .8, .7, .6, C.wood); L.say('skill', -1.8, 1.85, .28, MUTED);
    const drawer = RD.alloc(C.woodDark); const dr = k => L.rd(drawer, -1.8, .4, 1.53 + k * .3, .6, .22, .08); dr(0);
    pawnStatic(q, 1.6, 1.3, '#2f7a6a'); q('torus', 1.95, .7, 1.4, .3, .3, .3, C.gold); q('box', 1.95, .45, 1.4, .05, .25, .05, C.woodDark);
    L.say('MCP', AX, 1.7, .28, MUTED);
    IDLE['mcp-skills'] = { dur: 3, pose(u) { dr(pulse(u, .1, .9)); } };
    POSE['mcp-skills'] = { dur: 6, pose(u) {
      if (u <= 0 || u >= .97) { arm(0, false); return; }
      arm(u < .45 ? seg(u, .05, .4) : 1 - seg(u, .5, .9), u > .42 && u < .93);
    } };
    return { h: 2.4, r: 2.6 };
  };

  // 本地模型：自家機房。模型箱輪流往記憶體槽放，放不下就退出；context 會跟著長
  LM['local-models'] = S => {
    const L = LOC(S), { q } = L;
    q('box', 0, 0, -.2, 3.8, .1, 2.8, C.stone);
    q('box', 0, .1, -1.5, 3.6, 2.2, .2, C.wall); [-1.8, 1.8].forEach(x => q('box', x, .1, -.6, .2, 2.2, 2.0, C.wall));
    q('prism', 0, 2.3, -.6, 4.0, .8, 2.4, C.roofDark);
    const RX = -.4, RZ = -.8;
    q('box', RX, .1, RZ, 1.6, 1.8, .9, '#3a4150');
    for (let k = 0; k < 4; k++) q('box', RX, .3 + k * .4, RZ + .46, 1.3, .26, .02, '#1b1b2b');
    q('box', 1.15, .1, RZ, .5, 1.8, .5, C.white); L.say('context', 1.15, .45, .26, MUTED);
    L.say('localhost', 0, 1.6, .3);
    const ctx = RD.alloc(C.amber), small = RD.alloc(C.forest), big = RD.alloc(C.red);
    const leds = [0, 1, 2].map(i => { const id = SP.alloc(DIM); L.sp(id, RX - .5 + i * .2, 1.75, RZ + .48, .1, .1, .1); return id; });
    const rest = () => { L.rd(ctx, 1.15, .12, RZ + .26, .4, .3, .04); L.rd(small, -1.1, .1, .9, .55, .35, .55); L.rd(big, 1.0, .1, 1.0, 1.3, .7, .8); };
    rest();
    IDLE['local-models'] = { dur: 3, pose(u) { leds.forEach((id, i) => SP.color(id, ((u * 6 + i) | 0) % 3 === 0 ? '#3fbf6a' : DIM)); } };
    POSE['local-models'] = { dur: 7, pose(u) {
      if (u <= 0 || u >= .97) { rest(); return; }
      const a = seg(u, .05, .3);
      L.rd(small, lerp(-1.1, RX, a), lerp(.1, .3, a), lerp(.9, RZ + .5, a), .55, .3, lerp(.55, .4, a));
      L.rd(ctx, 1.15, .12, RZ + .26, .4, lerp(.3, 1.5, seg(u, .3, .55)), .04);
      const b = u < .72 ? seg(u, .55, .7) : 1 - seg(u, .74, .9);
      L.rd(big, lerp(1.0, RX + .3, b * .7), .1, lerp(1.0, RZ + .9, b * .7), 1.3, .7, .8);
    } };
    return { h: 3.1, r: 2.6 };
  };

  // Herdr：雙塔觀測站。兩座塔各住一個 OpenCode，靠繩子傳話，不共用記憶；塔頂的旗是狀態
  LM.herdr = S => {
    const L = LOC(S), { q } = L;
    const T = [[-1.3, -.3], [1.3, -.3]], H = 3.0;
    T.forEach(([x, z]) => {
      q.ao(x, z, .9);
      q('round', x, 0, z, 1.05, H, 1.05, C.navy);
      q('box', x, 1.6, z + .53, .75, .55, .03, '#1b1b2b'); q('box', x - .1, 1.85, z + .55, .4, .05, .02, '#9fe0b0', { glow: true });
      q('box', x, H, z, 1.25, .12, 1.25, C.white); q('cyl', x, H + .12, z, .06, 1.0, .06, C.white);
    });
    const rope = CY.alloc(C.woodDark); L.beam(rope, L.P(T[0][0] + .5, H - .3, T[0][1]), L.P(T[1][0] - .5, H - .3, T[1][1]), .05);
    L.say('不共用記憶', 0, 1.3, .3, MUTED);
    const IDLEC = '#c9c2b2', WORK = '#e7a33e', DONE = '#4f78ab';
    const cloth = T.map(() => RD.alloc(IDLEC)), msg = SP.alloc(C.gold);
    const fl = (i, wave = 0) => L.rd(cloth[i], T[i][0] + .3, H + .75, T[i][1], .55 + wave, .32, .04);
    const rest = () => { fl(0); fl(1); RD.color(cloth[0], DONE); RD.color(cloth[1], IDLEC); SP.hide(msg); };
    rest();
    const ride = t => L.sp(msg, lerp(T[0][0] + .5, T[1][0] - .5, t), H - .45 - Math.sin(t * Math.PI) * .25, -.3, .3, .3, .3);
    IDLE.herdr = { dur: 3, pose(u) { fl(0, Math.sin(u * 12) * .08 * pulse(u, 0, 1)); fl(1, Math.cos(u * 12) * .08 * pulse(u, 0, 1)); } };
    POSE.herdr = { dur: 7, pose(u) {
      if (u <= 0 || u >= .97) { rest(); return; }
      if (u < .3) ride(seg(u, .05, .28)); else if (u < .7) SP.hide(msg); else ride(1 - seg(u, .7, .92));
      RD.color(cloth[1], u < .3 ? IDLEC : u < .62 ? WORK : DONE);
    } };
    return { h: 4.2, r: 2.6 };
  };

  /* ── 數學島、筆記島 ── */
  // 數學應用：三題涼亭（低秩近似、梯度下降、最短路徑）。不演三種步長的結局，只演一般的下坡
  LM['math-applications'] = S => {
    const L = LOC(S), { q } = L;
    const XS = [-2.6, 0, 2.6];
    XS.forEach((x, i) => pavilion(q, x, 0, 1.8, 1.8, 1.9, [C.roofNavy, C.roof, C.roofGreen][i]));
    // 低秩近似：一層一層疊起來的透明板
    const plates = [0, 1, 2].map(k => { q('box', XS[0], .35 + k * .3, 0, 1.1, .04, 1.1, GLASS, { glass: true }); const id = RD.alloc('#d8e6ea'); L.rd(id, XS[0], .34 + k * .3, 0, 1.0, .03, 1.0); return id; });
    L.say('低秩近似', XS[0], 1.55, .28, MUTED);
    // 梯度下降：碗與三顆球
    q('cone', XS[1], .12, 0, 1.5, .55, 1.5, C.stone, { rx: Math.PI }); q('torus', XS[1], .58, 0, 1.5, 1.5, 1.5, C.stoneDark, { rx: Math.PI / 2 });
    const rim = [[-.6, -.1]];                     // 只放一顆球：三顆會讓人聯想到三種步長，那是要學生自己判讀的
    const balls = rim.map(() => SP.alloc(C.red));
    const ball = (i, t) => { const [x, z] = rim[i]; L.sp(balls[i], XS[1] + x * (1 - t), lerp(.62, .2, t), z * (1 - t), .26, .26, .26); };
    L.say('梯度下降', XS[1], 1.55, .28, MUTED);
    // 最短路徑：教材 content/math-applications.md 的同一張帶權圖與固定座標（A=(0,1)…E=(3,1)）。
    // 不演任何路線、不依邊數擴散（邊數最少不等於最短），只亮起點 A 和終點 E；邊長放大才看得到
    const gp = ([x, y]) => [(x - 1.5) * .42, (1 - y) * .42], N = { A: gp([0, 1]), B: gp([1, 2]), C: gp([1, 0]), D: gp([2, 1]), E: gp([3, 1]) };
    const EDG = [['A', 'B', 2], ['A', 'C', 5], ['B', 'C', 1], ['B', 'D', 4], ['C', 'D', 1], ['C', 'E', 5], ['D', 'E', 1]];
    EDG.forEach(([a, b, w]) => { const [ax, az] = N[a], [bx, bz] = N[b]; q('box', XS[2] + (ax + bx) / 2, .14, (az + bz) / 2, .05, .03, Math.hypot(bx - ax, bz - az), C.ink, { ry: Math.atan2(bx - ax, bz - az) });
      L.say(String(w), XS[2] + (ax + bx) / 2 + .1, (az + bz) / 2 + .1, .16, MUTED); });
    const ends = { A: 1, E: 1 };
    const nodes = Object.entries(N).map(([k, [x, z]]) => { const id = SP.alloc(C.cream); L.sp(id, XS[2] + x, .12, z, .22, .22, .22); return [k, id]; });
    L.say('最短路徑', XS[2], 1.55, .28, MUTED);
    const rest = () => { plates.forEach(id => RD.color(id, '#d8e6ea')); ball(0, 0); nodes.forEach(([, id]) => SP.color(id, C.cream)); };
    rest();
    IDLE['math-applications'] = { dur: 3, pose(u) { RD.color(plates[2], u > .25 && u < .75 ? '#a9d3dc' : '#d8e6ea'); } };
    POSE['math-applications'] = { dur: 6, pose(u) {
      if (u <= 0 || u >= .97) { rest(); return; }
      plates.forEach((id, k) => RD.color(id, u > .05 + k * .1 && u < .9 ? '#6fb3c4' : '#d8e6ea'));
      ball(0, u < .85 ? seg(u, .2, .6) : 1 - seg(u, .86, .96));
      nodes.forEach(([k, id]) => SP.color(id, ends[k] && u > .55 && u < .9 ? C.gold : C.cream));
    } };
    return { h: 2.7, r: 3.9 };
  };

  // 閱讀與筆記：核對桌。三枚印章 [原文]、[AI 解釋]、[我推導]；「我推導」那格只能你自己填，永遠空白
  LM['research-notes'] = S => {
    const L = LOC(S), { q } = L;
    pavilion(q, 0, -.3, 3.6, 2.2, 2.0, C.roofNavy);
    q('box', 0, .82, -.2, 3.0, .1, 1.2, C.wood); [[-1.35, -.65], [1.35, -.65], [-1.35, .25], [1.35, .25]].forEach(([x, z]) => q('box', x, .12, z, .1, .7, .1, C.woodDark));
    q('box', -.85, .92, -.2, 1.0, .02, .8, '#f5ead0'); q('cyl', -.85, .92, -.62, .14, .14, .14, C.wood); L.say('原文', -.85, 1.25, .26, MUTED);
    q('box', .7, .92, -.2, 1.25, .02, .85, C.white);
    const COLS = ['#4f78ab', '#e7a33e', '#3f9f6a'], BOXZ = [-.45, -.2, .05];
    const fills = BOXZ.map(z => { q('box', .45, .94, z, .3, .01, .18, '#e5ddcc'); const id = RD.alloc('#e5ddcc'); L.rd(id, .45, .945, z, .26, .01, .14); return id; });
    const stamps = COLS.map(c => ({ body: RD.alloc(c), knob: SP.alloc(C.woodDark) }));
    const SX = [1.0, 1.25, 1.5];
    const st = (i, x, h, z) => { L.rd(stamps[i].body, x, h, z, .22, .16, .22); L.sp(stamps[i].knob, x, h + .16, z, .16, .16, .16); };
    L.say('[原文] [AI 解釋] [我推導]', 0, 1.25, .26);
    const rest = () => { stamps.forEach((_, i) => st(i, SX[i], 1.15, .3)); fills.forEach(id => RD.color(id, '#e5ddcc')); };
    rest();
    INV['research-notes'] = { blank: 2 };
    PROBE['research-notes'] = () => ({ fills: fills.map(id => RD.colorOf(id)) });
    IDLE['research-notes'] = { dur: 3, pose(u) { stamps.forEach((_, i) => st(i, SX[i], 1.15 + pulse(u, i * .2, i * .2 + .4) * .12, .3)); } };
    POSE['research-notes'] = { dur: 6, pose(u) {
      if (u <= 0 || u >= .97) { rest(); return; }
      [0, 1].forEach(i => {
        const a = .1 + i * .35, t = pulse(u, a, a + .3), k = seg(u, a, a + .1);
        st(i, lerp(SX[i], .45, k), lerp(1.15, .97, t), lerp(.3, BOXZ[i], k));
        if (u > a + .15 && u < .92) RD.color(fills[i], COLS[i]); else RD.color(fills[i], '#e5ddcc');
      });
      st(2, SX[2], 1.15, .3);                       // 「我推導」：阿卡不替你蓋
    } };
    return { h: 2.8, r: 2.6 };
  };

  // 速查表：燈船，停在主島前方的海上，頂燈旋轉
  LM.cheatsheet = S => {
    const L = LOC(S), { q } = L;
    q('round', 0, -.3, 0, 1.7, 1.0, 3.6, C.navy); q('box', 0, .62, 0, 1.5, .08, 3.2, C.wood);
    q('round', 0, .7, -.5, 1.15, .95, 1.3, C.cream);
    [-.3, .3].forEach(x => q('box', x, 1.1, .16, .26, .26, .04, '#ffe1a0', { glow: true }));
    q('cyl', 0, .7, .7, .14, 2.3, .14, C.woodDark); q('cyl', 0, 3.0, .7, .55, .45, .55, '#fff1c2', { glow: true }); q('cone', 0, 3.45, .7, .7, .4, .7, C.red);
    const lw = L.P(0, 3.2, .7); lamps.push([lw.x, lw.y, lw.z, 1.6, true]);
    const beam = RD.alloc(C.gold);
    const set = a => L.rd(beam, Math.sin(a) * 1.2, 3.15, .7 + Math.cos(a) * 1.2, .1, .1, 2.2, a);
    set(0);
    IDLE.cheatsheet = { dur: 4, pose(u) { set(u * Math.PI * 2); } };
    POSE.cheatsheet = { dur: 4, pose(u) { set(u * Math.PI * 4); } };
    return { h: 3.9, r: 2.4 };
  };

  PAGES.forEach(p => {
    const s = SLOT[p.stem], { h, r } = LM[p.stem](s);
    B[p.stem] = { x: s.x, y: s.y, z: s.z, top: s.y + h, r, isle: s.isle, grp: p.grp };
  });

  /* ── 主島的步道、時刻牌、休息長椅、收尾碼頭 ── */
  const PATH_UV = [[-26, 2.5], [-20, 1.5], [-14.5, 3.6], [-8, 4.2], [-2, 4.6], [3.3, 4.2], [8.6, 4.6], [14, 4.2], [19.2, 4.6], [25.5, 3]];
  const pathPts = PATH_UV.map(([u, v]) => { const w = toWorld(u, v); return new THREE.Vector3(w.x, MAIN.top, w.z); });
  const mainPath = new THREE.CatmullRomCurve3(pathPts);
  { const n = Math.round(mainPath.getLength() / .8); mainPath.getSpacedPoints(n).forEach((p, i) => part('cyl', p.x, MAIN.top - .02, p.z, .62 + (i % 3) * .08, .05, .62, '#e9dcc0', { ry: rnd() * 3 })); }
  const signAt = (u, v, text) => {
    const w = toWorld(u, v), L = LOC({ x: w.x, y: MAIN.top, z: w.z });
    L.q('box', 0, 0, 0, .1, 1.1, .1, C.woodDark); L.q('box', 0, .8, .05, .9, .45, .06, C.white);
    L.q('box', 0, .88, .09, .7, .28, .02, C.gold);
    L.say(text, 0, .75, .32);
  };
  [['first-run', -12], ['lab1-cluster', -2], ['lab2-pca', 8.6], ['lab3-notes', 19.2]].forEach(([s, u]) => signAt(u - 2.6, 6.4, M_SCHED[s]));
  [[2.6, 6.9], [4.3, 6.9]].forEach(([u, v]) => { const w = toWorld(u, v); bench(at(w.x, MAIN.top, w.z), 0, 0, 0); }); signAt(3.45, 8.3, '休息 ' + M_SCHED.rest);
  signAt(25.4, 4.6, '收尾 ' + M_SCHED.wrap);

  /* ── 裝飾：樹、花、灌木、路燈、岩石；避開地標、步道與橋 ── */
  function decorate(I, { trees = 8, avoid = [], bushes = 3, flowersN = 2, lampsN = 1 } = {}) {
    const ok = (x, z, pad = 0) => I.inside(x, z, .86) && !avoid.some(([ax, az, r]) => Math.hypot(x - ax, z - az) < r + pad)
      && !nearGap(I, Math.atan2(z - I.z, x - I.x), .3);
    const spot = pad => { for (let k = 0; k < 60; k++) { const a = rnd() * Math.PI * 2, r = Math.sqrt(rnd()) * I.radius * 2.4; const x = I.x + Math.cos(a) * r, z = I.z + Math.sin(a) * r; if (ok(x, z, pad)) return [x, z]; } return null; };
    for (let t = 0; t < trees; t++) { const s = spot(.6); if (s) { (t % 2 ? pine : tree)(at(s[0], I.top, s[1]), 0, 0, .55 + rnd() * .3, t); avoid.push([s[0], s[1], .9]); } }
    for (let k = 0; k < bushes; k++) { const s = spot(.3); if (s) { bush(at(s[0], I.top, s[1]), 0, 0, .8 + rnd() * .3, k); avoid.push([s[0], s[1], .6]); } }
    for (let k = 0; k < flowersN; k++) { const s = spot(.3); if (s) flowers(at(s[0], I.top, s[1]), 0, 0, k); }
    for (let k = 0; k < lampsN; k++) { const s = spot(.3); if (s) { lamp(at(s[0], I.top, s[1]), 0, 0); lamps.push([s[0], I.top + 1.42, s[1]]); } }
    for (let r = 0; r < 3; r++) { const a = rnd() * Math.PI * 2; if (!nearGap(I, a, .5)) rock(at(I.x + Math.cos(a) * I.angR(a) * 1.02, 0, I.z + Math.sin(a) * I.angR(a) * 1.02), 0, 0, .8 + rnd() * .5); }
  }
  const avoidStops = I => PAGES.filter(p => SLOT[p.stem].isle === I).map(p => [B[p.stem].x, B[p.stem].z, B[p.stem].r + .3]);
  const pathAvoid = mainPath.getSpacedPoints(40).map(p => [p.x, p.z, 1.1]);
  // 主島步道旁的路燈
  mainPath.getSpacedPoints(9).slice(1, -1).forEach((p, i) => { if (i % 2) return; const w = { x: p.x + 1.1, z: p.z + 1.1 }; lamp(at(w.x, MAIN.top, w.z), 0, 0); lamps.push([w.x, MAIN.top + 1.42, w.z]); });
  decorate(MAIN, { trees: 26, bushes: 8, flowersN: 6, lampsN: 0, avoid: [...avoidStops(MAIN), ...pathAvoid] });
  decorate(TOOLS, { trees: 9, bushes: 4, flowersN: 3, avoid: avoidStops(TOOLS) });
  decorate(MATHI, { trees: 4, bushes: 2, avoid: avoidStops(MATHI) });
  decorate(NOTES, { trees: 4, bushes: 2, avoid: avoidStops(NOTES) });
  // 外圍的小沙洲與礁岩，替畫面收邊
  const framed = isles.slice();          // 取景只算主要島嶼；外圍沙洲可以出血
  const sandbars = [[-40, 12, 2.2], [-38, -14, 1.8], [-8, -24, 2.4], [32, -30, 1.8], [56, 2, 2], [22, 24, 1.8], [-24, 22, 1.6]];
  sandbars.forEach(([u, v, r], k) => {
    const I = makeIsle({ u, v, radius: r, seed: 300 + k * 13, grass: 'grass3' });
    if (k % 2 === 0) tree(at(I.x, I.top, I.z), 0, 0, .7, k); else rock(at(I.x, I.top - .1, I.z), 0, 0, .9);
  });
  pools.forEach(P => P.finish());

  mergeIsles();
  flushParts();
  // 接觸暗部：柔邊的深色圓盤，貼在地面上（不參與陰影）
  {
    const cv = document.createElement('canvas'); cv.width = cv.height = 64;
    const g = cv.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(40,52,40,.55)'); gr.addColorStop(.55, 'rgba(40,52,40,.25)'); gr.addColorStop(1, 'rgba(40,52,40,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    const tex = new THREE.CanvasTexture(cv);
    const geo = new THREE.PlaneGeometry(1, 1); geo.rotateX(-Math.PI / 2);
    const mesh = new THREE.InstancedMesh(geo, new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, opacity: .55 }), ao.length);
    const o = new THREE.Object3D();
    ao.forEach(([x, y, z, r], i) => { o.position.set(x, y + .015, z); o.scale.set(r * 2.2, 1, r * 2.2); o.updateMatrix(); mesh.setMatrixAt(i, o.matrix); });
    mesh.renderOrder = 2; world.add(mesh);
  }
  /* 地面標示：貼花圖集，只畫一次 */
  const decalMat = (() => {
    const cv = document.createElement('canvas'); cv.width = 2048; cv.height = 1024;
    const g = cv.getContext('2d'), PX = 44;
    g.font = `700 ${PX}px ui-monospace,'SFMono-Regular','Cascadia Mono',Menlo,Consolas,'Noto Sans CJK TC','Microsoft JhengHei',monospace`;
    g.textBaseline = 'middle'; g.textAlign = 'center';
    let cx = 2, cy = 2; const pos = [], uv = [], idx = []; const H = PX + 22, c = Math.cos(FACE), sn = Math.sin(FACE); let n = 0;
    decals.forEach(d => {
      const tw = Math.ceil(g.measureText(d.text).width) + 26;
      if (cx + tw > 2046) { cx = 2; cy += H + 4; }
      g.fillStyle = 'rgba(255,253,247,.86)'; g.beginPath(); g.roundRect(cx, cy, tw, H, 12); g.fill();
      g.fillStyle = d.ink; g.fillText(d.text, cx + tw / 2, cy + H / 2 + 2);
      const hw = d.size * .5 * tw / PX, hh = d.size * .5 * H / PX;
      [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]].forEach(([x, z]) => pos.push(d.x + x * c + z * sn, d.y, d.z - x * sn + z * c));
      uv.push(cx / 2048, 1 - cy / 1024, (cx + tw) / 2048, 1 - cy / 1024, (cx + tw) / 2048, 1 - (cy + H) / 1024, cx / 2048, 1 - (cy + H) / 1024);
      idx.push(n, n + 2, n + 1, n, n + 3, n + 2); n += 4; cx += tw + 4;
    });
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx);
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 });
    const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false; mesh.renderOrder = 3; world.add(mesh);
    mat.userData.mesh = mesh;
    return mat;
  })();
  // 全景時地面文字只有幾個像素，看不清又變成雜訊：放大之後才淡入
  let decalZoom = -1;
  function stepDecals() {
    if (camera.zoom === decalZoom) return;
    decalZoom = camera.zoom;
    const k = clamp01((decalZoom - 1.35) / .5);
    decalMat.opacity = k; decalMat.userData.mesh.visible = k > 0;
  }

  /* ═════════ 海面：頂點起伏＋依離岸距離的淺深色 ═════════ */
  const SEA_DAY_SHALLOW = new THREE.Color('#86dcd8'), SEA_DAY_DEEP = new THREE.Color('#3f9fcb');
  const seaGeo = new THREE.PlaneGeometry(300, 300, 90, 90); seaGeo.rotateX(-Math.PI / 2);
  {
    const pos = seaGeo.attributes.position, cols = new Float32Array(pos.count * 3), c = new THREE.Color();
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), z = pos.getZ(i);
      let d = 1e9; isles.forEach(I => { d = Math.min(d, Math.hypot(x - I.x, z - I.z) - I.radius * 1.1); });
      const t = Math.min(1, Math.max(0, d / 12)), k = t * t * (3 - 2 * t);
      c.copy(SEA_DAY_SHALLOW).lerp(SEA_DAY_DEEP, k);
      cols[i * 3] = c.r; cols[i * 3 + 1] = c.g; cols[i * 3 + 2] = c.b;
    }
    seaGeo.setAttribute('color', new THREE.BufferAttribute(cols, 3));
  }
  const seaU = { uTime: { value: 0 } };
  const seaMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .55, metalness: 0 });
  seaMat.onBeforeCompile = sh => {
    sh.uniforms.uTime = seaU.uTime;
    sh.vertexShader = 'uniform float uTime;\n' + sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\n transformed.y += sin(position.x * .32 + uTime * .9) * .05 + cos(position.z * .27 + uTime * .7) * .05;');
  };
  const sea = new THREE.Mesh(seaGeo, seaMat); sea.position.y = -.02; sea.receiveShadow = true; world.add(sea);
  // 風格化短浪線
  const dash = new THREE.InstancedMesh(new RoundedBoxGeometry(1, .02, .1, 1, .04), basic('#ffffff', { transparent: true, opacity: .6, depthWrite: false, fog: false }), 46);
  const dashes = [];
  for (let k = 0, n = 0; k < 2000 && n < 46; k++) {
    const x = (rnd() - .5) * 110, z = (rnd() - .5) * 110;
    if (isles.some(I => Math.hypot(x - I.x, z - I.z) < I.radius * 1.7)) continue;
    dashes.push({ x, z, l: .8 + rnd() * 1.0, ph: rnd() * 6 }); n++;
  }
  const dObj = new THREE.Object3D();
  const placeDashes = t => {
    dashes.forEach((d, i) => {
      dObj.position.set(d.x + Math.sin(t * .25 + d.ph) * .6, .06, d.z + Math.cos(t * .2 + d.ph) * .3);
      dObj.rotation.set(0, FACE, 0);              // 與畫面水平方向平行 dObj.scale.set(d.l * (.75 + .25 * Math.sin(t * .6 + d.ph)), 1, 1);
      dObj.updateMatrix(); dash.setMatrixAt(i, dObj.matrix);
    });
    dash.count = dashes.length; dash.instanceMatrix.needsUpdate = true;
  };
  placeDashes(0); world.add(dash);
  life.push(t => { seaU.uTime.value = t; placeDashes(t); });

  /* ═════════ 燈光 ═════════ */
  const hemi = new THREE.HemisphereLight(DAY.hemiSky, DAY.hemiGround, DAY.hemi); world.add(hemi);
  const bounds = isles.reduce((b, I) => ({ minX: Math.min(b.minX, I.x - I.radius), maxX: Math.max(b.maxX, I.x + I.radius),
    minZ: Math.min(b.minZ, I.z - I.radius), maxZ: Math.max(b.maxZ, I.z + I.radius) }), { minX: 1e9, maxX: -1e9, minZ: 1e9, maxZ: -1e9 });
  const center = new THREE.Vector3((bounds.minX + bounds.maxX) / 2, 0, (bounds.minZ + bounds.maxZ) / 2);
  const sun = new THREE.DirectionalLight(DAY.sun, DAY.sunI);
  sun.position.set(center.x - 30, 55, center.z + 24); sun.target.position.copy(center);
  sun.castShadow = true;
  const SM = window.innerWidth < 768 ? 1024 : 2048;   // 陰影只烘一次
  sun.shadow.mapSize.set(SM, SM);
  const ext = Math.max(bounds.maxX - bounds.minX, bounds.maxZ - bounds.minZ) / 2 + 6;
  Object.assign(sun.shadow.camera, { left: -ext, right: ext, top: ext, bottom: -ext, near: 1, far: 160 });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -.0005; sun.shadow.normalBias = .07; sun.shadow.radius = 2;
  world.add(sun, sun.target);
  const fill = new THREE.DirectionalLight('#d6ecf2', DAY.fill); fill.position.set(center.x + 40, 30, center.z - 50); world.add(fill);
  /* ═════════ 生活感：小人、帆船、鳥、雲 ═════════ */
  const blobMat = basic('#20343a', { transparent: true, opacity: .16, depthWrite: false });
  const blobGeo = new THREE.CircleGeometry(.34, 16); blobGeo.rotateX(-Math.PI / 2);
  function person(shirt, pants, skin, hair) {
    const g = new THREE.Group(), body = new THREE.Group(); g.add(body);
    const m = c => std(c, { roughness: .8 });
    const limb = (c, x, y, w, h) => { const piv = new THREE.Group(); piv.position.set(x, y, 0); const b = new THREE.Mesh(GEO.round, m(c)); b.scale.set(w, h, w); b.position.y = -h / 2; piv.add(b); body.add(piv); return piv; };
    const legL = limb(pants, -.09, .42, .13, .42), legR = limb(pants, .09, .42, .13, .42);
    const torso = new THREE.Mesh(GEO.round, m(shirt)); torso.scale.set(.36, .42, .22); torso.position.y = .63; body.add(torso);
    const armL = limb(shirt, -.24, .8, .1, .36), armR = limb(shirt, .24, .8, .1, .36);
    const head = new THREE.Mesh(GEO.sphere, m(skin)); head.scale.setScalar(.3); head.position.y = 1.0; body.add(head);
    const cap = new THREE.Mesh(GEO.sphere, m(hair)); cap.scale.set(.32, .18, .32); cap.position.set(0, 1.08, -.02); body.add(cap);
    const blob = new THREE.Mesh(blobGeo, blobMat); blob.position.y = .02; g.add(blob);
    g.userData = { legL, legR, armL, armR, body };
    return g;
  }
  const people = [];
  const PALETTE = [['#c4553a', '#3f5b80'], ['#3f7f61', '#4f5a55'], ['#e7a33e', '#2f4566'], ['#4f78ab', '#7a5c3e'], ['#f0c7a5', '#3f7f61'], ['#fff4de', '#924231']];
  const SKINS = ['#f1c9a5', '#d9a77f', '#b98063', '#f6dcc0'], HAIR = ['#3b2a20', '#1f1d1c', '#7a5c3e', '#c9a46a'];
  const ways = bridges.map(b => {
    const n = b.pts.length, d0 = b.pts[1].clone().sub(b.pts[0]).setY(0).normalize(), d1 = b.pts[n - 1].clone().sub(b.pts[n - 2]).setY(0).normalize();
    return [b.pts[0].clone().addScaledVector(d0, -1.4), ...b.pts, b.pts[n - 1].clone().addScaledVector(d1, 1.4)];
  });
  const mainWay = mainPath.getSpacedPoints(70);
  ways.push(mainWay, mainWay, mainWay);
  ways.forEach((path, i) => {
    const [sh, pa] = PALETTE[i % PALETTE.length];
    const g = person(sh, pa, SKINS[i % 4], HAIR[(i + 1) % 4]); g.scale.setScalar(.72); instancify(g);
    const lens = [0]; for (let k = 1; k < path.length; k++) lens.push(lens[k - 1] + path[k].distanceTo(path[k - 1]));
    people.push({ g, path, lens, total: lens[lens.length - 1], s: rnd() * lens[lens.length - 1], dir: rnd() < .5 ? 1 : -1, wait: 0, speed: .75 + rnd() * .35 });
  });
  const pv = new THREE.Vector3();
  const walk = (t, dt) => people.forEach(P => {
    const u = P.g.userData;
    if (P.wait > 0) { P.wait -= dt; u.legL.rotation.x = u.legR.rotation.x = u.armL.rotation.x = 0; u.armR.rotation.x = Math.sin(t * 6) * .8 - .8; return; }
    P.s += P.dir * P.speed * dt;
    if (P.s > P.total || P.s < 0) { P.s = Math.max(0, Math.min(P.total, P.s)); P.dir *= -1; P.wait = 1 + rnd() * 2.5; }
    let k = 1; while (k < P.lens.length - 1 && P.lens[k] < P.s) k++;
    const f = (P.s - P.lens[k - 1]) / Math.max(1e-6, P.lens[k] - P.lens[k - 1]);
    pv.copy(P.path[k - 1]).lerp(P.path[k], f); P.g.position.copy(pv);
    const a = P.path[k], b0 = P.path[k - 1];
    P.g.rotation.y = Math.atan2((a.x - b0.x) * P.dir, (a.z - b0.z) * P.dir);
    const sw = Math.sin(t * 8 * P.speed) * .55;
    u.legL.rotation.x = sw; u.legR.rotation.x = -sw; u.armL.rotation.x = -sw * .8; u.armR.rotation.x = sw * .8;
    u.body.position.y = Math.abs(Math.sin(t * 8 * P.speed)) * .04;
  });
  walk(1.3, 0); life.push(walk);

  /* ── 嚮導阿卡：青綠外套、耳機，腰間掛著需求卡、驗收卡、決策卡 ──
     跳到下一站是和 fly 一樣的狀態，由 frame() 裡的 stepGuide() 推進，不另開繪製迴圈。 */
  const guide = (() => {
    const g = person('#2f7a6a', '#3f4a5c', '#f1c9a5', '#2b2420'), u = g.userData;
    const m = c => std(c);
    const band = new THREE.Mesh(GEO.torus, m('#2f4566')); band.scale.set(.4, .4, .4); band.position.set(0, 1.02, 0); u.body.add(band);
    [-1, 1].forEach(s => { const cup = new THREE.Mesh(GEO.round, m('#2f4566')); cup.scale.set(.07, .14, .12); cup.position.set(s * .17, 1.0, 0); u.body.add(cup); });
    ['#f5b82e', '#3f7f61', '#b9563f'].forEach((c, i) => { const card = new THREE.Mesh(GEO.box, m(c)); card.scale.set(.08, .11, .025); card.position.set(-.11 + i * .11, .5, .125); u.body.add(card); });
    g.scale.setScalar(1.6);                          // 比路人（.72）大一倍，遠看也認得出來
    world.add(g);
    return g;
  })();
  const camFlat = new THREE.Vector3();
  // 某一站的落腳點：島上朝鏡頭那一側的前緣、略偏一邊，免得被地標擋住
  function guideSpot(stem, out) {
    const b = B[stem]; if (!b) return null;
    camFlat.copy(camera.position).sub(controls.target); camFlat.y = 0; camFlat.normalize();
    const a = Math.atan2(camFlat.z, camFlat.x) - .4, r = b.r * .9 + .5;
    return out.set(b.x + Math.cos(a) * r, b.y, b.z + Math.sin(a) * r);
  }
  function faceCamera() {
    guide.rotation.y = Math.atan2(camera.position.x - guide.position.x, camera.position.z - guide.position.z);
  }
  let hop = null, waveUntil = 0;
  function stepGuide(now) {
    if (!hop) return false;
    const k = Math.min(1, (now - hop.t0) / hop.dur), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    guide.position.lerpVectors(hop.from, hop.to, e);
    guide.position.y += Math.sin(Math.PI * k) * hop.h;
    const u = guide.userData; u.legL.rotation.x = -.6; u.legR.rotation.x = .3; u.armR.rotation.x = -2.4 * Math.sin(Math.PI * k);
    if (k >= 1) { hop = null; faceCamera(); waveUntil = now + 2600; u.legL.rotation.x = u.legR.rotation.x = 0; }
    return true;
  }
  function guideTo(stem) {
    const to = guideSpot(stem, new THREE.Vector3()); if (!to) return;
    if (!motion()) { hop = null; guide.position.copy(to); faceCamera(); requestRender(); return; }
    const d = to.distanceTo(guide.position);
    hop = { from: guide.position.clone(), to, t0: performance.now(), dur: Math.min(1300, 550 + d * 14), h: 1.1 + Math.min(4, d * .1) };
    guide.rotation.y = Math.atan2(to.x - guide.position.x, to.z - guide.position.z);
    requestRender();
  }
  const guideHomeStem = 'index';   // 平時站在啟航港的瞭望台旁
  anims.push(t => {
    if (hop) return;
    const u = guide.userData, now = t * 1000;
    // 平時偶爾揮手（約每 9 秒一次）；剛到一站時揮比較久
    const waving = now < waveUntil || (t % 9) < 1.4;
    u.armR.rotation.x = waving ? -2.5 + Math.sin(t * 9) * .35 : 0;
    u.armR.rotation.z = waving ? .25 : 0;
    u.armL.rotation.x = -.35 + Math.sin(t * 1.6) * .08;
    u.body.position.y = Math.abs(Math.sin(t * 1.6)) * .025;
  });

  const WAKE_GEO = new THREE.PlaneGeometry(.7, 2.6), WAKE_MAT = basic('#ffffff', { transparent: true, opacity: .35, depthWrite: false });
  function sailboat(sail, hull) {
    const g = new THREE.Group();
    const h = new THREE.Mesh(GEO.round, std(hull, { roughness: .8 })); h.scale.set(.75, .35, 1.9); h.position.y = .12; g.add(h);
    const deck = new THREE.Mesh(GEO.round, std(C.wood)); deck.scale.set(.62, .08, 1.6); deck.position.y = .3; g.add(deck);
    const mast = new THREE.Mesh(GEO.cyl, std(C.woodDark)); mast.scale.set(.07, 2.0, .07); mast.position.y = 1.3; g.add(mast);
    const s = new THREE.Mesh(GEO.prism, std(sail, { roughness: .9, side: THREE.DoubleSide })); s.scale.set(.06, 1.6, 1.2); s.position.set(0, 1.35, -.2); g.add(s);
    const wake = new THREE.Mesh(WAKE_GEO, WAKE_MAT);
    wake.rotation.x = -Math.PI / 2; wake.position.set(0, .04, -2.1); g.add(wake);
    return g;
  }
  // 外圈的兩艘帆船繞著整片島群；第三艘繞數學島。橢圓的半徑由島群在螢幕 u／v 方向的範圍算出，不會開上島
  let EU = 0, EV = 0;
  framed.forEach(I => { const du = ((I.x - center.x) - (I.z - center.z)) * SQ, dv = ((I.x - center.x) + (I.z - center.z)) * SQ; EU = Math.max(EU, Math.abs(du) + I.radius * I.su * 1.2); EV = Math.max(EV, Math.abs(dv) + I.radius * I.sv * 1.2); });
  const boats = [[C.cream, C.navy, EU + 6, EV + 5, .04, 0], [C.redL, C.white, EU + 6, EV + 5, .04, Math.PI], [C.white, C.red, MATHI.radius * 1.5, MATHI.radius * 1.5, -.12, 1]].map(([s, h, a, b, w, ph], i) => {
    const g = sailboat(s, h); instancify(g);
    const c0 = i === 2 ? new THREE.Vector3(MATHI.x, 0, MATHI.z) : center.clone();
    return { g, a, b, w, ph, c0 };
  });
  const sail = t => boats.forEach(B0 => {
    const ang = t * B0.w + B0.ph, rot = -FACE;
    const lx = Math.cos(ang) * B0.a, lz = Math.sin(ang) * B0.b;
    const x = B0.c0.x + lx * Math.cos(rot) - lz * Math.sin(rot), z = B0.c0.z + lx * Math.sin(rot) + lz * Math.cos(rot);
    const dx = -Math.sin(ang) * B0.a * Math.sign(B0.w), dz = Math.cos(ang) * B0.b * Math.sign(B0.w);
    const wx = dx * Math.cos(rot) - dz * Math.sin(rot), wz = dx * Math.sin(rot) + dz * Math.cos(rot);
    B0.g.position.set(x, .05 + Math.sin(t * 1.4 + B0.ph) * .05, z);
    B0.g.rotation.set(Math.sin(t * 1.1 + B0.ph) * .04, Math.atan2(wx, wz), Math.sin(t * .9) * .05);
  });
  sail(2); life.push(sail);

  const birds = new THREE.Group();
  const birdMat = std('#fbfaf2', { roughness: .8 });
  const flock = Array.from({ length: 7 }, (_, i) => {
    const g = new THREE.Group();
    const body = new THREE.Mesh(GEO.sphere, birdMat); body.scale.set(.18, .14, .42); g.add(body);
    const wings = [-1, 1].map(s => { const piv = new THREE.Group(); const w = new THREE.Mesh(GEO.box, birdMat); w.scale.set(.6, .03, .22); w.position.x = .3 * s; piv.add(w); g.add(piv); return piv; });
    g.position.set((i % 3 - 1) * 1.1, (i % 2) * .4, -Math.floor(i / 2) * .9); birds.add(g);
    return { g, wings, ph: i * .7 };
  });
  const flapBirds = t => {
    const a = t * .07;
    birds.position.set(center.x + Math.cos(a) * 26, 12 + Math.sin(t * .5) * .6, center.z + Math.sin(a) * 18);
    birds.rotation.y = -a + Math.PI;
    flock.forEach(b => { const f = Math.sin(t * 7 + b.ph) * .7; b.wings[0].rotation.z = f; b.wings[1].rotation.z = -f; });
  };
  flapBirds(3); life.push(flapBirds); instancify(birds);

  const cloudMat = std('#ffffff', { roughness: 1, transparent: true, opacity: .92, emissive: '#ffffff', emissiveIntensity: .25 });
  const clouds = [[-38, 30], [36, 30], [-46, -4], [44, -2]].map(([u, v], k) => {
    const g = new THREE.Group(); const w = toWorld(u, v);
    [[0, 0, 0, 2.2], [1.6, -.3, .3, 1.6], [-1.6, -.4, -.2, 1.5], [.5, .5, -.6, 1.4]].forEach(([x, y, z, r]) => {
      const m = new THREE.Mesh(GEO.sphere, cloudMat); m.scale.set(r * 1.4, r, r * 1.2); m.position.set(x, y, z); g.add(m);
    });
    g.position.set(w.x, 9 + k % 2, w.z); instancify(g);
    return { g, x0: w.x, z0: w.z, ph: k * 1.7 };
  });
  const drift = t => clouds.forEach(c => { c.g.position.x = c.x0 + Math.sin(t * .03 + c.ph) * 6; c.g.position.z = c.z0 + Math.cos(t * .025 + c.ph) * 4; });
  life.push(drift);

  finishProxies();

  /* ═════════ 夜：星星、光暈 ═════════ */
  const glowTex = (() => {
    const cv = document.createElement('canvas'); cv.width = cv.height = 64;
    const g = cv.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,214,140,1)'); gr.addColorStop(.35, 'rgba(255,190,100,.45)'); gr.addColorStop(1, 'rgba(255,170,80,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const haloMat = new THREE.SpriteMaterial({ map: glowTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
  const nightOnly = [];            // 白天完全不畫（透明度 0 也會佔繪製呼叫）
  lamps.forEach(([x, y, z, s = 1.1]) => { const sp = new THREE.Sprite(haloMat); sp.position.set(x, y, z); sp.scale.setScalar(s * 1.6); world.add(sp); nightOnly.push(sp); });
  // 路燈照在地上的光斑（俯瞰視角看不到天空，所以不放星星）
  const poolMat = new THREE.MeshBasicMaterial({ map: glowTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
  const poolGeo = new THREE.PlaneGeometry(1, 1); poolGeo.rotateX(-Math.PI / 2);
  lamps.forEach(([x, y, z, s = 1.1, noPool]) => { if (noPool) return; const m = new THREE.Mesh(poolGeo, poolMat); m.position.set(x, y - 1.38, z); m.scale.set(s * 3.2, 1, s * 3.2); m.renderOrder = 3; world.add(m); nightOnly.push(m); });

  let night = 0, nightTarget = 0;
  const cA = new THREE.Color(), cB = new THREE.Color();
  const mix = (a, b, k) => cA.set(a).lerp(cB.set(b), k);
  function applyNight(k) {
    world.background.copy(mix(DAY.bg, NIGHT.bg, k)); world.fog.color.copy(world.background);
    hemi.color.copy(mix(DAY.hemiSky, NIGHT.hemiSky, k)); hemi.groundColor.copy(mix(DAY.hemiGround, NIGHT.hemiGround, k));
    hemi.intensity = DAY.hemi + (NIGHT.hemi - DAY.hemi) * k;
    sun.color.copy(mix(DAY.sun, NIGHT.sun, k)); sun.intensity = DAY.sunI + (NIGHT.sunI - DAY.sunI) * k;
    fill.intensity = DAY.fill + (NIGHT.fill - DAY.fill) * k;
    seaMat.color.copy(mix(DAY.sea, NIGHT.sea, k));
    renderer.toneMappingExposure = DAY.exposure + (NIGHT.exposure - DAY.exposure) * k;
    glowMat.emissiveIntensity = k * 1.5; haloMat.opacity = k * .95; poolMat.opacity = k * .7;
    decalMat.color.copy(mix('#ffffff', '#8c9ab8', k));
    nightOnly.forEach(o => { o.visible = k > .01; });
    cloudMat.opacity = .92 - k * .5; cloudMat.emissiveIntensity = .25 - k * .2;
    M.foam.color.copy(mix(C.foam, '#8fa3bd', k));
    dash.material.opacity = .6 - k * .45;
  }
  applyNight(0);
  /* ═════════ 足跡、選取、先備高亮 ═════════ */
  const GLOW_VISIT = new THREE.MeshLambertMaterial({ color: '#ffe0a0', emissive: '#ffb84d', emissiveIntensity: .9 });
  const FLAG = std(C.forest, { roughness: .8, side: THREE.DoubleSide });
  const refMat = basic('#3f5b9a', { transparent: true, opacity: .85, depthWrite: false });
  const refGeo = new THREE.TorusGeometry(1, .07, 6, 40); refGeo.rotateX(Math.PI / 2);
  PAGES.forEach(p => {
    const b = B[p.stem], L = LOC(b);
    // 地標前緣（朝向鏡頭）的燈籠與旗子
    const e = L.P(b.r * .78, 0, b.r * .82), f = L.P(-b.r * .78, 0, b.r * .82);
    const lan = new THREE.Group(); lan.position.copy(e);
    const post = new THREE.Mesh(GEO.cyl, std(C.woodDark)); post.scale.set(.07, 1.05, .07); post.position.y = .52; lan.add(post);
    const bulb = new THREE.Mesh(GEO.round, GLOW_VISIT); bulb.scale.set(.24, .3, .24); bulb.position.y = 1.15; lan.add(bulb);
    lan.visible = false; world.add(lan);
    const flag = new THREE.Group(); flag.position.copy(f);
    const pole = new THREE.Mesh(GEO.cyl, std(C.white)); pole.scale.set(.06, 1.9, .06); pole.position.y = .95; flag.add(pole);
    const cloth = new THREE.Mesh(GEO.prism, FLAG); cloth.scale.set(.05, .5, .7); cloth.rotation.x = Math.PI / 2; cloth.position.set(0, 1.62, .35); flag.add(cloth);
    flag.visible = false; world.add(flag);
    const ref = new THREE.Mesh(refGeo, refMat); ref.scale.setScalar(b.r * 1.12); ref.position.set(b.x, b.y + .06, b.z); ref.visible = false; world.add(ref);
    Object.assign(b, { lan, flag, ref });
  });
  const marker = new THREE.Mesh(new THREE.ConeGeometry(.42, .9, 4), new THREE.MeshLambertMaterial({ color: '#f3c15a', emissive: '#f0a83a', emissiveIntensity: .6 }));
  marker.rotation.x = Math.PI; marker.visible = false; world.add(marker);
  let selected = null, refs = [];
  anims.push(t => {
    if (selected) marker.position.y = B[selected].top + 1.4 + Math.sin(t * 3) * .18;
    refMat.opacity = .55 + .35 * Math.sin(t * 3);
  });
  // 「需要時可查閱」的頁只用光圈標出來（不拉線：相關頁可能在島的另一頭）
  pools.forEach(P => P.finish());
  function setWires() {}

  /* ═════════ 相機與操作 ═════════ */
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, .1, 500);
  const POLAR = 52 * Math.PI / 180, DIST = 110;
  const HOME = center.clone();
  const controls = new OrbitControls(camera, canvas);
  controls.enablePan = false;
  controls.minPolarAngle = 46 * Math.PI / 180; controls.maxPolarAngle = 62 * Math.PI / 180;
  controls.minZoom = .7; controls.maxZoom = 7;
  controls.enableDamping = motion(); controls.dampingFactor = .08;
  controls.rotateSpeed = .6; controls.zoomSpeed = 1.1;
  // 會場投影版沒有人操作，讓島慢慢轉；不動畫偏好優先
  controls.autoRotate = SHOW && motion();
  controls.autoRotateSpeed = .35;
  controls.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_ROTATE };
  camera.position.set(HOME.x + Math.sin(POLAR) * Math.sin(FACE) * DIST, Math.cos(POLAR) * DIST, HOME.z + Math.sin(POLAR) * Math.cos(FACE) * DIST);
  camera.lookAt(HOME); camera.updateMatrixWorld();
  // 自動取景：把主要島嶼（含地標與標籤高度）投影到鏡頭的左右／上下軸，取外接範圍
  const RV = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), UV = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
  const FV = camera.getWorldDirection(new THREE.Vector3());
  const FIT = { r: 30, u: 18 };
  {
    let r0 = 1e9, r1 = -1e9, u0 = 1e9, u1 = -1e9; const q = new THREE.Vector3();
    framed.forEach(I => {
      for (let k = 0; k < 32; k++) {
        const a = k / 32 * Math.PI * 2;
        [0, I.top + 3].forEach(h => {
          q.set(I.x + Math.cos(a) * I.angR(a) * 1.15 - HOME.x, h, I.z + Math.sin(a) * I.angR(a) * 1.15 - HOME.z);
          const r = q.dot(RV), u = q.dot(UV); r0 = Math.min(r0, r); r1 = Math.max(r1, r); u0 = Math.min(u0, u); u1 = Math.max(u1, u);
        });
      }
    });
    FIT.r = (r1 - r0) / 2; FIT.u = (u1 - u0) / 2;
    HOME.addScaledVector(RV, (r0 + r1) / 2).addScaledVector(UV, (u0 + u1) / 2);
    HOME.addScaledVector(FV, -HOME.y / FV.y);              // 沿視線滑回地面，畫面位置不變
  }
  controls.target.copy(HOME);
  camera.position.copy(HOME).addScaledVector(FV, -DIST); camera.lookAt(HOME);
  if (SHOW) { camera.zoom = .8; camera.updateProjectionMatrix(); }   // 投影版：島群縮小一點，留出左上標題卡與右下 QR 卡的位置
  guideSpot(guideHomeStem, guide.position); faceCamera();
  // 視錐：寬度涵蓋整個群島（約 ±36），窄螢幕略裁兩翼
  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    const aspect = w / h;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, DPRS[dprLevel]));
    renderer.setSize(w, h, false);
    // 上方多留一點給島嶼跳轉鈕；窄螢幕允許兩翼略為裁切
    const half = Math.max(FIT.u * 1.12 + 1.5, FIT.r * 1.03 / aspect);
    Object.assign(camera, { left: -half * aspect, right: half * aspect, top: half, bottom: -half });
    camera.updateProjectionMatrix(); measureTags(); tagsDirty = true; requestRender();
  }

  let fly = null;
  function flyTo(target, zoom) {
    if (!motion()) {
      const off = camera.position.clone().sub(controls.target);
      controls.target.copy(target); camera.position.copy(target).add(off);
      camera.zoom = zoom; camera.updateProjectionMatrix(); controls.update(); requestRender(); return;
    }
    fly = { from: controls.target.clone(), to: target.clone(), z0: camera.zoom, z1: zoom, t0: performance.now(), dur: 800 };
    requestRender();
  }
  function stepFly(now) {
    if (!fly) return false;
    const k = Math.min(1, (now - fly.t0) / fly.dur), e = 1 - Math.pow(1 - k, 3);
    const off = camera.position.clone().sub(controls.target);
    controls.target.lerpVectors(fly.from, fly.to, e); camera.position.copy(controls.target).add(off);
    camera.zoom = fly.z0 + (fly.z1 - fly.z0) * e; camera.updateProjectionMatrix();
    if (k >= 1) fly = null;
    return true;
  }

  /* ── 拾取：每個地標一個看不見的圓柱 ── */
  const picks = [];
  const pickMat = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false });
  PAGES.forEach(p => {
    const b = B[p.stem], h = b.top - b.y + 1.2;
    const m = new THREE.Mesh(new THREE.CylinderGeometry(b.r * .95, b.r * .95, h, 16), pickMat);
    m.position.set(b.x, b.y + h / 2, b.z); m.userData.stem = p.stem;
    m.visible = false;              // 不繪製；Raycaster 不看 visible，照樣點得到
    world.add(m); picks.push(m);
  });
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), v3 = new THREE.Vector3();
  function pickAt(cx, cy) {
    const r = canvas.getBoundingClientRect();
    ndc.set((cx - r.left) / r.width * 2 - 1, -(cy - r.top) / r.height * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hit = ray.intersectObjects(picks, false)[0];
    return hit ? hit.object.userData.stem : null;
  }
  let hover = null, down = null;
  function setHover(stem) {
    if (stem === hover) return;
    hover = stem; canvas.classList.toggle('is-hover', !!stem);
    tags.forEach(T => T.el.classList.toggle('is-hover', !!stem && T.stem === stem));
    tagsDirty = true; requestRender();
  }
  canvas.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
  canvas.addEventListener('pointermove', e => { if (e.pointerType === 'mouse' && !e.buttons) setHover(pickAt(e.clientX, e.clientY)); });
  canvas.addEventListener('pointerleave', () => setHover(null));
  canvas.addEventListener('pointerup', e => {
    if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) { down = null; return; }
    down = null;
    const stem = pickAt(e.clientX, e.clientY);
    if (stem) { select(stem, { trigger: canvas, fly: true }); scrollListTo(stem); } else closePanel();
  });
  function scrollListTo(stem) {
    const it = items.get(stem);
    if (it && window.innerWidth >= 768) { const list = $('islList'); list.scrollTop = it.li.offsetTop - list.clientHeight / 2; }
  }
  canvas.addEventListener('keydown', e => {
    const step = Math.PI / 12;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      const off = camera.position.clone().sub(controls.target);
      off.applyAxisAngle(new THREE.Vector3(0, 1, 0), e.key === 'ArrowLeft' ? -step : step);
      camera.position.copy(controls.target).add(off); controls.update(); requestRender(); e.preventDefault();
    } else if (['+', '=', '-', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
      const zin = e.key === '+' || e.key === '=' || e.key === 'ArrowUp';
      camera.zoom = Math.min(controls.maxZoom, Math.max(controls.minZoom, camera.zoom * (zin ? 1.2 : 1 / 1.2)));
      camera.updateProjectionMatrix(); requestRender(); e.preventDefault();
    }
  });
  controls.addEventListener('change', () => { tagsDirty = true; requestRender(); });

  /* ═════════ 標籤層（HTML）═════════ */
  const layer = $('islLabels');
  const tags = [];
  const UNIT_ZOOM = 1.6;               // 放大到這個倍率以上，區域名稱標籤就收起來
  function addTag({ stem = null, grp, kind, text, code, anchor, prio }) {
    const el = document.createElement('button');
    el.type = 'button'; el.className = `isl-tag isl-tag-${kind} isl-tag-${grp}`; el.tabIndex = -1; el.setAttribute('aria-hidden', 'true');
    if (code) { const n = document.createElement('span'); n.className = 'isl-tag-num'; n.textContent = code; el.appendChild(n); }
    const t = document.createElement('span'); t.className = 'isl-tag-t'; t.textContent = text; el.appendChild(t);
    el.addEventListener('click', () => {
      if (stem) { select(stem, { trigger: canvas, fly: true }); scrollListTo(stem); } else flyToIsle(grp);
    });
    layer.appendChild(el);
    tags.push({ el, stem, grp, kind, anchor, prio, w: 0, h: 0, cw: 0, num: el.querySelector('.isl-tag-num') });
  }
  PAGES.forEach(p => {
    const b = B[p.stem];
    addTag({ stem: p.stem, grp: p.grp, kind: 'stop', text: p.short, code: p.code, anchor: new THREE.Vector3(b.x, b.top + .4, b.z), prio: p.grp === 'live' ? 1 : 2 });
  });
  // 區域名稱：只標工坊島（六個單元擠在一起）和現場步道（標在步道前方）；其他區域的單元標籤已經夠清楚
  ['tools', 'live'].forEach(grp => {
    const st = PAGES.filter(p => p.grp === grp).map(p => B[p.stem]);
    const c = st.reduce((s, b) => s.add(new THREE.Vector3(b.x, 0, b.z)), new THREE.Vector3()).multiplyScalar(1 / st.length);
    const I = GRP_ISLE[grp], anchor = LOC({ x: c.x, y: I.top, z: c.z }).P(0, grp === 'live' ? .3 : 5, grp === 'live' ? 9.5 : -6.5);
    addTag({ grp, kind: 'isle', text: ISLES[grp].name, anchor, prio: 3 });
  });
  function measureTags() {
    tags.forEach(T => {
      T.el.classList.remove('is-compact'); T.st = -1; T.w = T.el.offsetWidth; T.h = T.el.offsetHeight;
      T.cw = T.num ? T.num.offsetWidth + 10 : T.w;
    });
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { measureTags(); tagsDirty = true; requestRender(); });
  const placed = [];
  function placeTags() {
    const W = canvas.clientWidth, H = canvas.clientHeight, zoomed = camera.zoom >= UNIT_ZOOM;
    placed.length = 0;
    const sel = T => (!!T.stem && T.stem === selected ? 0 : 1);
    const order = tags.slice().sort((a, b) => sel(a) - sel(b) || a.prio - b.prio);
    order.forEach(T => {
      const isSel = !!T.stem && T.stem === selected, isRef = !!T.stem && refs.includes(T.stem);
      let show = T.kind === 'stop' || !zoomed || isSel || isRef;
      v3.copy(T.anchor).project(camera);
      const x = (v3.x + 1) / 2 * W, y = (1 - v3.y) / 2 * H;
      // 完整標籤與已放好的重疊時，退成只顯示編號的小圓章；仍然重疊才隱藏
      const hits = r => placed.some(q => !(r.r < q.l || r.l > q.r || r.b < q.t || r.t > q.b));
      const box = (w, lift = 0) => ({ l: x - w / 2 - 3, r: x + w / 2 + 3, t: y - lift - T.h - 8, b: y - lift, lift });
      // 手機上單元標籤預設只顯示編號（選取或滑過時才展開）
      let compact = narrow() && T.kind === 'stop' && !isSel && T.stem !== hover, r = box(compact ? T.cw : T.w);
      if (show && (r.l < 2 || r.r > W - 2 || r.t < 0 || r.b > H)) show = false;   // 會被切掉的就不顯示
      if (show && !isSel && hits(r)) {
        // 重疊時依序試：抬高一層的完整標籤 → 原位的編號 → 抬高一層、兩層的編號；都不行才隱藏
        const lift = T.h + 6, tries = compact ? [[T.cw, lift, true], [T.cw, 2 * lift, true]] : [[T.w, lift, false], [T.cw, 0, true], [T.cw, lift, true], [T.cw, 2 * lift, true]];
        const hit = T.num || !compact ? tries.find(([w, l, c]) => (c ? T.num : true) && !hits(box(w, l))) : null;
        if (hit) { compact = hit[2]; r = box(hit[0], hit[1]); } else show = false;
      }
      if (show) placed.push(r);
      // 只在狀態或位置真的改變時才寫 DOM（每次寫入都會讓瀏覽器重算樣式）
      const st = show ? (compact ? 2 : 1) : 0;
      if (st !== T.st) { T.el.classList.toggle('is-off', !show); T.el.classList.toggle('is-compact', st === 2); T.st = st; }
      if (show) {
        const tf = `translate(${Math.round(x)}px, ${Math.round(y - r.lift)}px) translate(-50%, calc(-100% - 6px))`;
        if (tf !== T.tf) { T.el.style.transform = tf; T.tf = tf; }
      }
    });
  }

  /* ═════════ 地標播放 ═════════
     POSE＝答完猜題才播的完整動畫；IDLE＝沒選取時輪播的小動作，不露結果 */
  const playing = new Map();     // stem → { t0, mode }
  const attractLog = [];         // 給檢查腳本：輪播放過哪些（只能是 idle）
  function playLM(stem, mode = 'pose') {
    const A = mode === 'idle' ? IDLE : POSE;
    if (!A[stem] || !motion()) return;
    playing.set(stem, { t0: performance.now(), mode });
    wake(); requestRender();
  }
  function stepPlays(now) {
    playing.forEach(({ t0, mode }, stem) => {
      const A = mode === 'idle' ? IDLE : POSE, u = (now - t0) / (A[stem].dur * 1000);
      if (u >= 1) { POSE[stem].pose(0); playing.delete(stem); } else A[stem].pose(u);
    });
  }
  // 沒有選取時，島上輪流跑一個地標的 idle（不露結果）；選到地標時停止輪播
  const ALL_STEMS = PAGES.map(p => p.stem);
  let attractAt = 0, attractI = 0;
  function stepAttract(now) {
    if (nightTarget || playing.size || selected || lowPower || now < attractAt) return;
    attractAt = now + 4500;
    if (attractI > 0 || now > 3000) { const s = ALL_STEMS[attractI++ % ALL_STEMS.length]; playLM(s, 'idle'); attractLog.push(s); }
  }
  Object.values(POSE).forEach(l => l.pose(0));

  /* ═════════ 繪製迴圈 ═════════
     - 互動（拖曳、縮放、飛行、日夜過渡）時全速；只剩環境動畫時每 33 ms 才畫一幀
     - 閒置 45 秒（沒有任何 pointer／wheel／key／touch）就停止動畫，有輸入立即恢復
     - 解析度自動調整：最近 2 秒偏慢就降一級 DPR；互動時連續夠快再升回；最低一級仍慢才停用生活感
     - 標籤只在鏡頭、選取或滑過改變時重排 */
  const DPRS = narrow() ? [1.25, 1] : [1.5, 1.25, 1];
  const IDLE_MS = () => window.__islandIdleMs || 45000;          // 檢查腳本可以把門檻調短
  let last = performance.now(), lastDraw = 0, lastInput = performance.now(), sampleT = 0, sampleN = 0, fastWin = 0;
  const idle = () => !SHOW && performance.now() - lastInput > IDLE_MS();   // 投影版沒人操作，不能轉一會兒就停
  const animating = () => motion() && onScreen && document.visibilityState === 'visible' && !idle();
  function wake() { const was = idle(); lastInput = performance.now(); if (was) requestRender(); }
  ['pointerdown', 'pointermove', 'wheel', 'keydown', 'touchstart'].forEach(ev => window.addEventListener(ev, wake, { passive: true }));
  function setDprLevel(k) { dprLevel = Math.max(0, Math.min(DPRS.length - 1, k)); resize(); }
  // 任何時候最多只有一個待執行的 frame（raf 非 0 就表示已排程）
  function requestRender() { need = true; if (!raf && alive) raf = requestAnimationFrame(frame); }
  function frame(now) {
    raf = 0; if (!alive) return;
    const dt = Math.min(.1, (now - last) / 1000); last = now;
    // 投影版的自轉依實際經過的時間：軟體算圖或慢機器上轉速也一樣（約 170 秒一圈）
    const flying = stepFly(now), hopping = stepGuide(now), moved = controls.update(SHOW ? dt : null), anim = animating();
    let fading = false;
    if (night !== nightTarget) {
      night = motion() ? (nightTarget > night ? Math.min(nightTarget, night + dt / 1.2) : Math.max(nightTarget, night - dt / 1.2)) : nightTarget;
      applyNight(night); fading = true;
    }
    const playingNow = anim && playing.size > 0;
    const busy = need || flying || hopping || moved || fading || playingNow;
    // 只有環境動畫時限制在約 30fps
    if (!busy && anim && now - lastDraw < 32) { if (!raf) raf = requestAnimationFrame(frame); return; }
    if (anim) {
      const t = now / 1000;
      anims.forEach(f => f(t));
      stepPlays(now); stepAttract(now);
      if (!lowPower) life.forEach(f => f(t, Math.min(.1, (now - (lastDraw || now)) / 1000)));
      syncProxies();
    }
    if (busy || anim) {
      if (lastDraw) {                                   // 幀間隔取樣（略過第一幀與長時間停頓）
        const gap = now - lastDraw;
        if (gap < 250) { sampleT += gap; sampleN++; }
        if (sampleT > 2000) {
          const avg = sampleT / sampleN, target = busy ? 22 : 40;
          if (avg > target * 1.6) { if (dprLevel < DPRS.length - 1) setDprLevel(dprLevel + 1); else if (!lowPower) lowPower = true; fastWin = 0; }
          else if (busy && avg < 19 && dprLevel > 0 && ++fastWin >= 3) { setDprLevel(dprLevel - 1); fastWin = 0; }
          sampleT = 0; sampleN = 0;
        }
      }
      stepDecals(); renderer.render(world, camera); lastDraw = now; draws++;
      if (tagsDirty || flying || moved) { placeTags(); tagsDirty = false; }
      need = false;
    }
    // 只排一次：controls.update() 會觸發 change → requestRender() 已經排了下一幀，不能再多排一條迴圈
    if ((anim || flying || hopping || moved || fading) && !raf) raf = requestAnimationFrame(frame);
  }
  const ro = new ResizeObserver(resize); ro.observe(stage);
  new IntersectionObserver(es => { onScreen = es[0].isIntersecting; requestRender(); }).observe(stage);
  document.addEventListener('visibilitychange', requestRender);
  reduceMotion.addEventListener('change', () => { controls.enableDamping = motion(); requestRender(); });
  anims.forEach(f => f(1.7)); life.forEach(f => f(1.7, 0)); syncProxies();
  resize();
  renderer.shadowMap.needsUpdate = true;

  function flyToIsle(grp) {
    const st = PAGES.filter(p => p.grp === grp).map(p => B[p.stem]); if (!st.length) return;
    const c = st.reduce((s, b) => s.add(new THREE.Vector3(b.x, b.y, b.z)), new THREE.Vector3()).multiplyScalar(1 / st.length);
    flyTo(c, { start: 2.3, live: 1.45, tools: 2.0, math: 3, notes: 3, ref: 3 }[grp] || 2);
  }

  /* ═════════ 對外介面 ═════════ */
  return {
    select(stem, doFly) {
      refs.forEach(r => { B[r].ref.visible = false; });
      selected = stem && B[stem] ? stem : null;
      refs = selected ? BY[selected].refs.filter(r => B[r]) : [];
      refs.forEach(r => { B[r].ref.visible = true; });
      setWires(selected);
      if (selected && playing.has(selected)) { playing.delete(selected); POSE[selected].pose(0); }   // 剛選到的地標先回到靜止，答案不提早露出
      marker.visible = !!selected;
      tags.forEach(T => { T.el.classList.toggle('is-current', !!T.stem && T.stem === selected); T.el.classList.toggle('is-ref', !!T.stem && refs.includes(T.stem)); });
      tagsDirty = true;
      if (selected) {
        const b = B[selected];
        marker.position.set(b.x, b.top + 1.4, b.z);
        if (doFly) {
          setHover(null);
          // 讓選到的島落在面板以外的區域：桌機面板在左下，往右讓；手機面板從下方升起，往上讓
          const zoom = Math.max(camera.zoom, b.r > 4 ? 3.9 : 5.2), W = canvas.clientWidth, H = canvas.clientHeight;
          const wpp = (camera.right - camera.left) / zoom / W;
          camera.updateMatrixWorld();
          const R = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), U = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
          const tgt = new THREE.Vector3(b.x, b.y, b.z);
          if (window.innerWidth >= 768) tgt.addScaledVector(R, -Math.min(210, W * .22) * wpp);
          else tgt.addScaledVector(U, -H * .2 * wpp);
          flyTo(tgt, zoom);
        }
      }
      requestRender();
    },
    flyToIsle,
    reset() { flyTo(HOME.clone(), 1); },
    guideTo,
    // 走完路線：多跳一步，站到最後一站的外面（end() 的位置）
    guideEnd(stem) {
      const b = B[stem]; if (!b) return;
      guideTo(stem);
      if (hop) { const d = hop.to.clone().sub(new THREE.Vector3(b.x, hop.to.y, b.z)).normalize(); hop.to.addScaledVector(d, 1.8); }
    },
    guidePos() { const p = guide.position; return { x: p.x, y: p.y, z: p.z }; },
    play(stem) { playLM(stem); },
    setNight(on, instant) {
      nightTarget = on ? 1 : 0;
      if (instant || !motion()) { night = nightTarget; applyNight(night); }
      requestRender();
    },
    updateTrail() {
      PAGES.forEach(p => {
        const b = B[p.stem], done = !!trail.done[p.stem], visited = !!trail.visited[p.stem];
        b.flag.visible = done; b.lan.visible = visited && !done;
      });
      tags.forEach(T => {
        if (!T.stem) return;
        T.el.classList.toggle('is-done', !!trail.done[T.stem]);
        T.el.classList.toggle('is-visited', !!trail.visited[T.stem] && !trail.done[T.stem]);
      });
      renderer.shadowMap.needsUpdate = true;
      requestRender();
    },
    // 以下給 tools/check_island_browser.js 用
    stats() { return { draws, dprLevel, lowPower, calls: renderer.info.render.calls, triangles: renderer.info.render.triangles, night }; },
    // 省略 local 時取地標中央；local = [x, 高度, z] 是地標區域座標
    screenPos(stem, local) {
      const b = B[stem]; if (!b) return null;
      if (local) v3.copy(LOC(b).P(...local)); else v3.set(b.x, b.y + (b.top - b.y) * .3, b.z);
      v3.project(camera);
      const r = canvas.getBoundingClientRect();
      return { x: r.left + (v3.x + 1) / 2 * r.width, y: r.top + (1 - v3.y) / 2 * r.height };
    },
    pickAt,
    invariants() { return JSON.parse(JSON.stringify(INV)); },
    pose(stem, u, mode = 'pose') { const A = mode === 'idle' ? IDLE : POSE; if (!A[stem]) return false; playing.delete(stem); A[stem].pose(u); syncProxies(); requestRender(); return true; },
    plays() { return [...playing.entries()].map(([s, v]) => [s, v.mode]); },
    attract() { return attractLog.slice(); },
    probe(stem) { return PROBE[stem] ? PROBE[stem]() : null; },
    stops() { return Object.fromEntries(Object.entries(B).map(([s, b]) => [s, { x: b.x, y: b.y, z: b.z, top: b.top, r: b.r }])); },
    bridges() { return bridges.map(b => ({ A: [b.A.x, b.A.z], B: [b.B.x, b.B.z], p0: b.pts[0].toArray(), p1: b.pts[b.pts.length - 1].toArray() })); },
    // 先編譯所有著色器（支援平行編譯時不卡主執行緒）並畫好第一幀，再讓畫布淡入
    async warm() {
      try { await renderer.compileAsync(world, camera); } catch (e) { /* 舊版瀏覽器：第一幀時再編譯 */ }
      renderer.shadowMap.needsUpdate = true; stepDecals(); renderer.render(world, camera); placeTags(); tagsDirty = false; lastDraw = performance.now();
      requestRender();
    },
    dispose() { alive = false; ro.disconnect(); controls.dispose(); renderer.dispose(); layer.replaceChildren(); },
  };
}

function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
