#!/usr/bin/env node
/* 頁面截圖與基本檢查。
 * 用法：node tools/shot.js index [lab2-pca ...]
 * 環境：puppeteer-core 與 chrome 放在 repo 外（沿用 selfstudy 慣例）
 */
const path=require('path'), fs=require('fs');
const PPT=process.env.PPT_HOME||path.join(process.env.HOME,'.cache/selfstudy-node');
const puppeteer=require(path.join(PPT,'node_modules','puppeteer-core'));
const ROOT=path.resolve(__dirname,'..');
const OUT=process.env.SHOT_DIR||path.join(ROOT,'tools/test-runs/shots');
const CHROME=process.env.CHROME_PATH||(()=>{
  const b=path.join(process.env.HOME,'.cache/puppeteer/chrome');
  const d=fs.readdirSync(b).sort();
  return path.join(b,d[d.length-1],'chrome-linux64','chrome');
})();
const pages=process.argv.slice(2).length?process.argv.slice(2)
  :fs.readdirSync(ROOT).filter(f=>f.endsWith('.html')).map(f=>f.replace(/\.html$/,''));

(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const browser=await puppeteer.launch({executablePath:CHROME,
    args:['--no-sandbox','--disable-dev-shm-usage','--font-render-hinting=none']});
  const problems=[];
  for(const name of pages){
    const file=path.join(ROOT,name+'.html');
    if(!fs.existsSync(file)){problems.push(`[${name}] 檔案不存在`);continue;}
    for(const [tag,w,h] of [['desktop',1440,1000],['mobile',390,844]]){
      const p=await browser.newPage();
      const errs=[];
      p.on('console',m=>{if(m.type()==='error')errs.push(m.text());});
      p.on('pageerror',e=>errs.push('pageerror: '+e.message));
      await p.setViewport({width:w,height:h,deviceScaleFactor:2});
      await p.goto('file://'+file,{waitUntil:'networkidle0',timeout:45000});
      await new Promise(r=>setTimeout(r,900));   // 等字體
      // 橫向溢出檢查
      const over=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
      if(over>2) problems.push(`[${name}/${tag}] 橫向溢出 ${over}px`);
      errs.filter(e=>!/favicon|net::ERR/.test(e)).forEach(e=>problems.push(`[${name}/${tag}] console: ${e}`));
      await p.screenshot({path:path.join(OUT,`${name}-${tag}.png`),fullPage:tag==='desktop'});
      await p.close();
    }
    console.log('  拍好 '+name);
  }
  await browser.close();
  console.log('\n'+(problems.length?'發現問題：\n'+problems.map(s=>'  '+s).join('\n')
                                   :'無橫向溢出、無 console 錯誤。'));
  console.log('截圖：'+OUT);
})().catch(e=>{console.error(e);process.exit(1);});
