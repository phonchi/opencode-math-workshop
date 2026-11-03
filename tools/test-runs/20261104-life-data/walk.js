/* 逐步走過頁內互動並截圖。用法：node walk.js <page> <section-selector> <out-dir> [actionsJSON]
 * actionsJSON：每步要先點的 selector 陣列，例如 {"0":["[data-guess=\"3\"]"],"3":["#kmeans-run"]} */
const path=require('path'),fs=require('fs');
const PPT=path.join(process.env.HOME,'.cache/selfstudy-node');
const puppeteer=require(path.join(PPT,'node_modules','puppeteer-core'));
const b=path.join(process.env.HOME,'.cache/puppeteer/chrome');const d=fs.readdirSync(b).sort();
const CHROME=path.join(b,d[d.length-1],'chrome-linux64','chrome');
const [page,sel,out,acts='{}',prefix]=process.argv.slice(2);const actions=JSON.parse(acts);
const pre=prefix||sel.replace(/[^a-z]/g,'');
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const br=await puppeteer.launch({executablePath:CHROME,args:['--no-sandbox','--disable-dev-shm-usage']});
  const errs=[];
  for(const [tag,w,h,rm] of [['desktop',1280,900,false],['mobile',390,844,false],['reduced',1280,900,true]]){
    const p=await br.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(tag+': '+m.text());});p.on('pageerror',e=>errs.push(tag+': '+e.message));
    await p.setViewport({width:w,height:h,deviceScaleFactor:1});
    if(rm)await p.emulateMediaFeatures([{name:'prefers-reduced-motion',value:'reduce'}]);
    await p.goto('file://'+path.resolve(__dirname,'../../..',page+'.html'),{waitUntil:'networkidle0'});
    const next=await p.$(sel+' [id$="-next"]');
    for(let s=0;s<12;s++){
      for(const a of (actions[s]||[])){await p.click(sel+' '+a);await new Promise(r=>setTimeout(r,a.includes('run')?6000:300));}
      await new Promise(r=>setTimeout(r,900));
      const el=await p.$(sel+' > div');await el.screenshot({path:path.join(out,`${pre}-${tag}-step${s+1}.png`)});
      const ds=await p.$eval(sel,n=>({...n.dataset}));fs.appendFileSync(path.join(out,'dataset.log'),`${tag} step${s+1} ${JSON.stringify(ds)}\n`);
      const ov=await p.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);if(ov)errs.push(tag+` step${s+1}: horizontal overflow`);
      if(!next||await p.$eval(sel+' [id$="-next"]',n=>n.disabled))break;
      await p.click(sel+' [id$="-next"]');
    }
    await p.close();
  }
  await br.close();
  console.log(errs.length?'ERRORS\n'+errs.join('\n'):'no console errors');
})();
