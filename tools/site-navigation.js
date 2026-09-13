/* Progressive enhancement: navigation and disclosure work without JavaScript. */
(function(){
  'use strict';
  var pageName=location.pathname.split('/').pop()||'index.html';
  document.querySelectorAll('.topnav nav a').forEach(function(a){
    if(a.getAttribute('href')===pageName) a.setAttribute('aria-current','page');
  });

  var sections=Array.from(document.querySelectorAll('.lesson-main h2[id]'));
  var sectionLinks=Array.from(document.querySelectorAll('.section-nav a'));
  var scheduled=false;
  function markSection(){
    scheduled=false;
    var current=sections[0];
    sections.forEach(function(section){if(section.getBoundingClientRect().top<=145) current=section;});
    sectionLinks.forEach(function(link){
      if(current&&link.getAttribute('href')==='#'+current.id) link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    });
  }
  function scheduleSection(){
    if(!scheduled){scheduled=true;requestAnimationFrame(markSection);}
  }
  window.addEventListener('scroll',scheduleSection,{passive:true});
  window.addEventListener('resize',scheduleSection);
  window.addEventListener('hashchange',scheduleSection);
  markSection();
  document.querySelectorAll('.course-menu .section-nav a').forEach(function(link){
    link.addEventListener('click',function(){
      link.closest('details').open=false;
      // Closing the menu moves the heading; resolve the anchor after that reflow.
      var id=link.getAttribute('href').slice(1),target=document.getElementById(id);
      if(target){
        requestAnimationFrame(function(){
          var reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          window.scrollTo({top:window.scrollY+target.getBoundingClientRect().top-88,behavior:reduced?'auto':'smooth'});
        });
      }
    });
  });

  var status=document.createElement('span');
  status.className='sr-only';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
  document.body.appendChild(status);
  function fallbackCopy(text){
    var active=document.activeElement,selection=window.getSelection();
    var ranges=[];
    if(selection) for(var i=0;i<selection.rangeCount;i++) ranges.push(selection.getRangeAt(i).cloneRange());
    var area=document.createElement('textarea');
    area.value=text;area.setAttribute('readonly','');
    area.style.cssText='position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;';
    document.body.appendChild(area);area.select();
    var copied=false;
    try{copied=document.execCommand('copy');}catch(error){}
    area.remove();
    if(active&&active.focus) active.focus({preventScroll:true});
    if(selection){selection.removeAllRanges();ranges.forEach(function(range){selection.addRange(range);});}
    return copied;
  }
  async function copyText(text){
    if(navigator.clipboard&&navigator.clipboard.writeText){
      try{await navigator.clipboard.writeText(text);return true;}catch(error){}
    }
    return fallbackCopy(text);
  }
  document.querySelectorAll('pre.cmd').forEach(function(pre){
    var button=document.createElement('button');
    button.className='copy';button.type='button';button.textContent='複製';
    button.addEventListener('click',async function(){
      var code=pre.querySelector('code')||pre;
      var text=(code===pre?Array.from(pre.childNodes).filter(function(node){return node!==button;}).map(function(node){return node.textContent;}).join(''):code.textContent).trim();
      if(await copyText(text)){
        button.textContent='已複製';status.textContent='指令已複製。';
      }else{
        var range=document.createRange();range.selectNodeContents(code);
        var selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);
        button.textContent='請按 Ctrl+C';status.textContent='已選取指令，請按 Ctrl+C 複製。';
      }
      setTimeout(function(){button.textContent='複製';status.textContent='';},2200);
    });
    pre.appendChild(button);
  });

  // Keep the existing storage key and checkbox IDs so prior progress survives.
  var key='ocmw:'+pageName,saved={};
  try{
    var parsed=JSON.parse(localStorage.getItem(key)||'{}');
    if(parsed&&typeof parsed==='object'&&!Array.isArray(parsed)) saved=parsed;
  }catch(error){}
  document.querySelectorAll('.ckl input[type=checkbox]').forEach(function(checkbox,index){
    var id=checkbox.id||('ck'+index);checkbox.id=id;
    if(saved[id]) checkbox.checked=true;
    checkbox.addEventListener('change',function(){
      saved[id]=checkbox.checked;
      try{localStorage.setItem(key,JSON.stringify(saved));}catch(error){}
    });
  });
  // Wide output stays readable and can be scrolled from the keyboard.
  document.querySelectorAll('pre.out,.tw').forEach(function(block){
    block.tabIndex=0;
    block.setAttribute('aria-label',block.matches('.tw')?'表格；較寬時可左右捲動':'程式輸出；較寬時可左右捲動');
  });
})();
