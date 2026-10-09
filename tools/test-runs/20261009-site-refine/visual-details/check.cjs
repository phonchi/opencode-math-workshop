const fs=require('fs'),path=require('path'),assert=require('assert');
const ROOT=path.resolve(__dirname,'../../../..');
const puppeteer=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const chromeRoot=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome=path.join(chromeRoot,fs.readdirSync(chromeRoot).sort().at(-1),'chrome-linux64/chrome');
const items=[['index','.lab-preview','lab-preview'],['index','.after-routes','after-routes'],['lab1-cluster','.teaching-figure','lab1-figure'],['lab3-notes','.teaching-figure','lab3-figure'],['research-notes','.pagehead','reading-header'],['research-notes','pre[data-lang="markdown"]','reading-template']];
(async()=>{const browser=await puppeteer.launch({executablePath:chrome,args:['--no-sandbox','--disable-dev-shm-usage']});const report=[];
try{for(const [tag,width,height]of[['desktop',1440,1000],['mobile',390,844]]){const page=await browser.newPage();await page.setViewport({width,height});let previous;
for(const [slug,selector,label]of items){if(previous!==slug){await page.goto('file://'+path.join(ROOT,slug+'.html'),{waitUntil:'networkidle0'});await page.evaluate(async()=>{await document.fonts.ready;await MathJax.startup.promise});previous=slug;}
const state=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth-innerWidth,images:Array.from(document.querySelectorAll('picture img')).map(img=>({source:img.currentSrc,loaded:img.complete&&img.naturalWidth>0}))}));assert(state.overflow<=1);for(const img of state.images){assert(img.loaded);assert(img.source.endsWith((width<=720?'-mobile':'')+'.svg'));}
await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));const file=label+'-'+tag+'.png';const clip=await page.$eval(selector,node=>{const r=node.getBoundingClientRect();return {x:Math.max(0,r.x+scrollX-8),y:Math.max(0,r.y+scrollY-8),width:r.width+16,height:r.height+16}});await page.screenshot({path:path.join(__dirname,file),clip,captureBeyondViewport:true});report.push({slug,tag,file,...state});}
await page.goto('file://'+path.join(ROOT,'index.html'),{waitUntil:'networkidle0'});await page.click('.sample-response > summary');
assert(await page.$eval('.sample-response',node=>node.open&&Boolean(node.querySelector('.bg-body > .term'))&&!node.querySelector('.term .figure-note')));
const file='sample-expanded-'+tag+'.png';await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));const clip=await page.$eval('.sample-response',node=>{const r=node.getBoundingClientRect();return {x:Math.max(0,r.x+scrollX-8),y:Math.max(0,r.y+scrollY-8),width:r.width+16,height:r.height+16}});await page.screenshot({path:path.join(__dirname,file),clip,captureBeyondViewport:true});report.push({slug:'index',tag,file,sampleTermAndNoteSeparate:true});await page.close();}
fs.writeFileSync(path.join(__dirname,'report.json'),JSON.stringify({status:'passed',screenshots:report},null,2)+'\n');console.log('PASS: responsive picture sources, section layouts, reading template and expanded sample; '+report.length+' screenshots.');
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exit(1)});
