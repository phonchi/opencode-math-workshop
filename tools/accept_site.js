#!/usr/bin/env node
/* Bounded browser acceptance. All output stays in one named evidence directory.
 * node tools/accept_site.js [page-slug ...]
 * RUN_DIR may select a separate directory for focused repair checks.
 */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),http=require('http');
const ROOT=path.resolve(__dirname,'..');
const OUT=path.resolve(process.env.RUN_DIR||path.join(ROOT,'tools/test-runs/20260912-workshop-refresh/browser'));
const PPT=process.env.PPT_HOME||path.join(process.env.HOME,'.cache/selfstudy-node');
const puppeteer=require(path.join(PPT,'node_modules/puppeteer-core'));
const chromeRoot=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const CHROME=process.env.CHROME_PATH||path.join(chromeRoot,fs.readdirSync(chromeRoot).sort().at(-1),'chrome-linux64/chrome');
const config=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/pages.json'),'utf8'));
const requested=process.argv.slice(2);
const pages=requested.length?requested:config.groups.flatMap(group=>group.pages);
const views=[['desktop',1440,1000],['laptop',1280,900],['tablet',1024,900],['mobile',390,844]];
const fileURL=slug=>'file://'+path.join(ROOT,slug+'.html');
const digest=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
fs.mkdirSync(OUT,{recursive:true});
const runlog=fs.createWriteStream(path.join(OUT,'run.log'),{flags:'w'});
function log(text){console.log(text);runlog.write(new Date().toISOString()+' '+text+'\n');}
const report={started:new Date().toISOString(),environment:{chrome:CHROME,node:process.version,platform:process.platform,entry:'file:// plus loopback HTTP'},views,pages,files:{},layout:[],links:[],interactions:[],screenshots:[],failures:[]};
let browser,server;
function failure(label,details){report.failures.push({label,details});log('FAIL '+label+' '+JSON.stringify(details));}
function expect(condition,label,details={}){if(!condition)throw new Error(label+' '+JSON.stringify(details));}
async function screenshot(page,name,fullPage=true){
  const file=name+'.png';await page.screenshot({path:path.join(OUT,file),fullPage});
  report.screenshots.push({name,file,width:page.viewport().width,height:page.viewport().height});return file;
}
async function load(page,url){
  const issues=[];
  function consoleError(message){if(message.type()==='error')issues.push({kind:'console',text:message.text()});}
  function pageError(error){issues.push({kind:'pageerror',text:error.message});}
  function requestError(request){issues.push({kind:'requestfailed',url:request.url(),text:request.failure().errorText});}
  page.on('console',consoleError);page.on('pageerror',pageError);page.on('requestfailed',requestError);
  try{
    await page.goto(url,{waitUntil:'networkidle0',timeout:60000});
    await page.waitForFunction(()=>Boolean(window.MathJax&&MathJax.startup&&MathJax.startup.promise),{timeout:20000});
    await page.evaluate(async()=>{
      await Promise.all([document.fonts.load('17px "Noto Sans TC"','數學'),document.fonts.load('24px "Noto Serif TC"','數學'),document.fonts.load('14px "JetBrains Mono"','command')]);
      await document.fonts.ready;await MathJax.startup.promise;
    });
    return issues;
  }finally{
    page.off('console',consoleError);page.off('pageerror',pageError);page.off('requestfailed',requestError);
  }
}
async function inspect(page){
  return page.evaluate(()=>{
    const clipping=[],scrollable=[];
    document.querySelectorAll('pre,.tw,.term-body').forEach(element=>{
      if(!element.getClientRects().length)return;
      const delta=element.scrollWidth-element.clientWidth;
      if(delta<=1)return;
      const item={tag:element.tagName,className:element.className,over:delta,text:(element.textContent||'').trim().slice(0,80)};
      if(/^(auto|scroll)$/.test(getComputedStyle(element).overflowX))scrollable.push(item);else clipping.push(item);
    });
    const loadedFamilies=Array.from(document.fonts).filter(font=>font.status==='loaded').map(font=>font.family.replaceAll('"',''));
    const requiredFonts=['Noto Sans TC','Noto Serif TC','JetBrains Mono'];
    return {
      viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,
      pageOverflow:document.documentElement.scrollWidth-innerWidth,clipping,scrollable,
      requiredFonts,loadedFamilies:Array.from(new Set(loadedFamilies)),
      fontsLoaded:requiredFonts.every(family=>loadedFamilies.includes(family)),
      mathJaxVersion:MathJax.version,mathContainers:document.querySelectorAll('mjx-container').length,
      mathErrors:Array.from(document.querySelectorAll('mjx-merror')).map(node=>node.textContent),
      imageErrors:Array.from(document.images).filter(image=>!image.complete||image.naturalWidth===0).map(image=>image.src),
      outputFonts:Array.from(new Set(Array.from(document.querySelectorAll('pre.out')).map(node=>getComputedStyle(node).fontSize))),
      diagramTextSizes:Array.from(document.querySelectorAll('.lesson-diagram svg')).map(svg=>({id:svg.id,scale:svg.getBoundingClientRect().width/svg.viewBox.baseVal.width})),
      horizontalScrollTargets:scrollable.length
    };
  });
}
async function checkLinks(page,slug){
  const links=await page.evaluate(()=>Array.from(document.querySelectorAll('a[href]')).map(a=>({href:a.getAttribute('href'),resolved:a.href})));
  const bad=[];let checked=0;
  for(const link of links){
    if(/^(https?:|mailto:|tel:)/.test(link.href))continue;
    let url;try{url=new URL(link.resolved);}catch(error){bad.push(link);continue;}
    if(url.protocol!=='file:'){bad.push({...link,reason:'Unexpected local link scheme'});continue;}
    const file=decodeURIComponent(url.pathname);
    if(!fs.existsSync(file)){bad.push({...link,reason:'Missing local file'});continue;}
    if(url.hash){
      const anchor=decodeURIComponent(url.hash.slice(1));
      const html=fs.readFileSync(file,'utf8');
      const ids=Array.from(html.matchAll(/\bid\s*=\s*(["'])(.*?)\1/g),m=>m[2]);
      if(!ids.includes(anchor))bad.push({...link,reason:'Missing fragment target',anchor});
    }
    checked++;
  }
  report.links.push({slug,checked,failures:bad});
  if(bad.length)failure('local-links/'+slug,bad);
}
async function scenario(name,work){
  const page=await browser.newPage();
  await page.setViewport({width:1440,height:1000});
  try{const detail=await work(page);report.interactions.push({name,status:'passed',detail});log('PASS interaction '+name);}
  catch(error){report.interactions.push({name,status:'failed',error:error.message});failure('interaction/'+name,error.stack);}
  finally{await page.close();}
}
async function checkAnchor(page,selector){
  const href=await page.$eval(selector,node=>node.getAttribute('href'));
  await page.click(selector);
  // Poll from Node: a no-JavaScript page cannot run an in-page rAF waiter.
  let settled=false,lastTop;
  for(let attempt=0;attempt<50;attempt++){
    lastTop=await page.evaluate(anchor=>{
      const target=document.getElementById(anchor.slice(1));
      return target?target.getBoundingClientRect().top:null;
    },href);
    if(lastTop!==null&&lastTop>=55&&lastTop<=100){settled=true;break;}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  expect(settled,'Anchor did not settle below the header',{href,lastTop});
  await new Promise(resolve=>setTimeout(resolve,100));
  return page.evaluate(anchor=>({href:location.hash,top:document.getElementById(anchor.slice(1)).getBoundingClientRect().top}),href);
}
async function interactionChecks(){
  if(pages.includes('first-run')){
    await scenario('desktop-section-anchor',async page=>{
      expect(!(await load(page,fileURL('first-run'))).length,'Runtime errors');
      const detail=await checkAnchor(page,'.desktop-course-menu .section-nav li:nth-child(3) a');
      const current=await page.$eval('.desktop-course-menu .section-nav a[aria-current="location"]',a=>a.getAttribute('href'));
      expect(current===decodeURIComponent(detail.href),'Wrong current section',{current,detail});
      await screenshot(page,'interaction-desktop-anchor',false);return detail;
    });
    await scenario('mobile-disclosure-and-anchor',async page=>{
      await page.setViewport({width:390,height:844});await load(page,fileURL('first-run'));
      expect(!await page.$eval('.course-menu',node=>node.open),'Mobile menu must start closed');
      await page.click('.course-menu > summary');
      expect(await page.$eval('.course-menu',node=>node.open),'Mobile menu did not open');
      await screenshot(page,'interaction-mobile-menu',false);
      const detail=await checkAnchor(page,'.course-menu .section-nav li:nth-child(3) a');
      expect(!await page.$eval('.course-menu',node=>node.open),'Mobile menu did not close');
      await screenshot(page,'interaction-mobile-anchor',false);return detail;
    });
    await scenario('file-copy-fallback',async page=>{
      await page.evaluateOnNewDocument(()=>{
        Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true});
        const original=document.execCommand.bind(document);
        document.execCommand=function(command,...args){
          const selected=document.activeElement&&document.activeElement.value;
          const result=original(command,...args);
          if(command==='copy')window.__copyEvidence={text:selected,result};return result;
        };
      });
      await load(page,fileURL('first-run'));
      const expected=await page.$eval('pre.cmd code',code=>code.textContent.trim());
      await page.click('pre.cmd .copy');
      await page.waitForFunction(()=>document.querySelector('pre.cmd .copy').textContent==='已複製');
      const detail=await page.evaluate(()=>window.__copyEvidence);
      expect(detail&&detail.result&&detail.text===expected,'Fallback copy payload mismatch',detail);return detail;
    });
    for(const width of [1440,390])await scenario('no-js-navigation-'+width,async page=>{
      await page.setViewport({width,height:900});await page.setJavaScriptEnabled(false);
      await page.goto(fileURL('first-run'),{waitUntil:'networkidle0'});
      if(width===390)await page.click('.course-menu > summary');
      const menu=width===390?'.course-menu':'.desktop-course-menu';
      const detail=await checkAnchor(page,menu+' .section-nav li:nth-child(2) a');
      await Promise.all([page.waitForNavigation({waitUntil:'networkidle0'}),page.click('.pager a.next')]);
      expect(page.url().endsWith('/lab1-cluster.html'),'No-JS pager destination mismatch');
      return {...detail,next:page.url()};
    });
  }
  if(pages.includes('lab1-cluster'))await scenario('checkbox-persists-after-reload',async page=>{
    await load(page,fileURL('lab1-cluster'));
    const original=await page.$eval('.ckl input',node=>node.checked);
    await page.click('.ckl input');
    await page.reload({waitUntil:'networkidle0'});
    const restored=await page.$eval('.ckl input',node=>node.checked);
    expect(restored!==original,'Checkbox state was not restored');
    return {original,restored};
  });
  if(pages.includes('lab2-pca')){
    await scenario('background-disclosure',async page=>{
      await load(page,fileURL('lab2-pca'));
      expect(!await page.$eval('details.bg',node=>node.open),'Background starts unexpectedly open');
      await page.click('details.bg > summary');
      expect(await page.$eval('details.bg',node=>node.open),'Background did not open');
      await page.click('details.bg > summary');
      expect(!await page.$eval('details.bg',node=>node.open),'Background did not close');return {expandedAndClosed:true};
    });
    await scenario('pca-reference-buttons-keyboard',async page=>{
      await load(page,fileURL('lab2-pca'));
      const reference=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/test-runs/20260912-workshop-refresh/wsl/math/pca-browser-reference.json'),'utf8'));
      const checks=[];
      for(const expected of reference){
        if(expected===reference.at(-1))await page.click('#projection-principal');
        else await page.$eval('#projection-angle',(input,angle)=>{input.value=String(angle);input.dispatchEvent(new Event('input',{bubbles:true}));},expected.angle);
        const actual=await page.$eval('.pca-explorer',node=>({...node.dataset}));
        for(const key of ['angle','variance','error'])expect(Math.abs(Number(actual[key])-expected[key])<=1e-10,'PCA reference mismatch',{key,actual,expected});
        checks.push({expected,actual});
      }
      await screenshot(page,'interaction-pca-principal',false);
      await page.click('#projection-reset');
      expect(await page.$eval('#projection-angle',input=>input.value)==='0','PCA reset failed');
      await page.focus('#projection-angle');await page.keyboard.press('ArrowRight');
      const keyboard=await page.$eval('.pca-explorer',node=>({...node.dataset}));
      expect(Number(keyboard.angle)>0&&Number.isFinite(Number(keyboard.variance)),'PCA keyboard change failed',keyboard);
      return {tolerance:1e-10,checks,keyboard};
    });
  }
}
async function httpChecks(){
  server=http.createServer((request,response)=>{
    const url=new URL(request.url,'http://localhost');
    const file=path.resolve(ROOT,'.'+decodeURIComponent(url.pathname));
    if(!file.startsWith(ROOT+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){response.writeHead(404);response.end('Not found');return;}
    const type={'.html':'text/html; charset=utf-8','.svg':'image/svg+xml','.js':'text/javascript','.css':'text/css'}[path.extname(file)]||'application/octet-stream';
    response.setHeader('Content-Type',type);fs.createReadStream(file).pipe(response);
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const origin='http://127.0.0.1:'+server.address().port;
  report.environment.httpOrigin=origin;
  for(const slug of ['index','first-run','lab2-pca'].filter(slug=>pages.includes(slug))){
    await scenario('http-'+slug,async page=>{
      const issues=await load(page,origin+'/'+slug+'.html');expect(!issues.length,'HTTP runtime errors',issues);
      const state=await inspect(page);expect(state.pageOverflow<=1&&state.fontsLoaded&&!state.mathErrors.length,'HTTP readiness/layout',state);
      if(slug==='first-run'){
        await browser.defaultBrowserContext().overridePermissions(origin,['clipboard-read','clipboard-write']);
        await page.bringToFront();
        const expected=await page.$eval('pre.cmd code',node=>node.textContent.trim());
        await page.click('pre.cmd .copy');
        await page.waitForFunction(()=>document.querySelector('pre.cmd .copy').textContent==='已複製');
        const copied=await page.evaluate(()=>navigator.clipboard.readText());
        expect(copied===expected,'HTTP clipboard content mismatch',{expected,copied});
      }
      return {url:page.url(),fontsLoaded:state.fontsLoaded,mathJaxVersion:state.mathJaxVersion};
    });
  }
}
async function contactSheet(){
  const cards=report.screenshots.map(item=>`<figure><img src="${escape(item.file)}" alt="${escape(item.name)}"><figcaption>${escape(item.name)}</figcaption></figure>`).join('\n');
  const html='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>工作坊瀏覽器驗收總覽</title><style>body{margin:24px;background:#f6f2e9;color:#1b1b2b;font:14px sans-serif}h1{font-size:24px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}figure{margin:0;background:white;border:1px solid #ded6c6}img{display:block;width:100%;height:260px;object-fit:cover;object-position:top}figcaption{padding:8px;overflow-wrap:anywhere}</style><h1>全部頁面與互動截圖</h1><p>每張卡片顯示截圖頂部；完整長頁截圖保存在同一目錄。</p><div class="grid">'+cards+'</div></html>';
  fs.writeFileSync(path.join(OUT,'all-items-contact-sheet.html'),html);
  const page=await browser.newPage();await page.setViewport({width:1440,height:1000});
  await page.goto('file://'+path.join(OUT,'all-items-contact-sheet.html'),{waitUntil:'load'});
  await page.screenshot({path:path.join(OUT,'all-items-contact-sheet.png'),fullPage:true});await page.close();
}
(async()=>{
  log('START '+JSON.stringify({pages,views,chrome:CHROME}));
  for(const slug of pages){expect(config.pages[slug],'Unknown page '+slug);report.files[slug]={before:digest(path.join(ROOT,slug+'.html'))};}
  browser=await puppeteer.launch({executablePath:CHROME,args:['--no-sandbox','--disable-dev-shm-usage','--font-render-hinting=none']});
  report.environment.browser=await browser.version();
  const page=await browser.newPage();
  for(const slug of ['index','lab2-pca'].filter(slug=>pages.includes(slug))){
    for(const [tag,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
      await page.setViewport({width,height,deviceScaleFactor:1});await load(page,fileURL(slug));
      await screenshot(page,'review-'+slug+'-'+tag+'-viewport',false);
      if(slug==='lab2-pca'){
        const name='review-pca-explorer-'+tag,file=name+'.png';
        const clip=await page.$eval('.pca-explorer',element=>{
          const rect=element.getBoundingClientRect();
          return {x:rect.x+scrollX,y:rect.y+scrollY,width:rect.width,height:rect.height};
        });
        // Clip document coordinates without auto-scrolling under the sticky header.
        await page.screenshot({path:path.join(OUT,file),clip,captureBeyondViewport:true});
        report.screenshots.push({name,file,width,height});
      }
      log('REVIEW SCREENSHOT '+slug+'/'+tag);
    }
  }
  for(const slug of pages){
    for(const [tag,width,height] of views){
      try{
        await page.setViewport({width,height,deviceScaleFactor:1});
        const issues=await load(page,fileURL(slug));
        const state=await inspect(page);report.layout.push({slug,tag,...state,runtimeIssues:issues});
        if(issues.length)failure(slug+'/'+tag+'/runtime',issues);
        if(state.pageOverflow>1||state.clipping.length||!state.fontsLoaded||state.mathErrors.length||state.imageErrors.length)failure(slug+'/'+tag+'/layout-or-readiness',state);
        if(tag==='desktop')await checkLinks(page,slug);
        await screenshot(page,slug+'-'+tag,true);
        log('CHECK '+slug+'/'+tag+' overflow='+state.pageOverflow+' scrollable='+state.scrollable.length+' fonts='+state.fontsLoaded);
      }catch(error){failure(slug+'/'+tag,error.stack);}
    }
  }
  await page.close();
  await interactionChecks();await httpChecks();await contactSheet();
  for(const slug of pages){report.files[slug].after=digest(path.join(ROOT,slug+'.html'));report.files[slug].changedDuringRun=report.files[slug].before!==report.files[slug].after;}
})().catch(error=>failure('harness',error.stack)).finally(async()=>{
  if(server)await new Promise(resolve=>server.close(resolve));
  if(browser)await browser.close();
  report.finished=new Date().toISOString();report.status=report.failures.length?'failed':'passed';
  fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify(report,null,2)+'\n');
  log('DONE '+report.status+' failures='+report.failures.length+' screenshots='+report.screenshots.length);
  await new Promise(resolve=>runlog.end(resolve));
  process.exitCode=report.failures.length?1:0;
});
