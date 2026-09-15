const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const server=http.createServer((req,res)=>{let rel;try{rel=decodeURIComponent(new URL(req.url,'http://local').pathname)}catch{res.writeHead(400).end();return}const p=path.resolve(root,'.'+rel);if(!p.startsWith(root+path.sep)||req.method!=='GET'){res.writeHead(403).end();return}if(!fs.existsSync(p)||!fs.statSync(p).isFile()){res.writeHead(404).end();return}const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png','.webp':'image/webp','.md':'text/plain; charset=utf-8'};res.setHeader('Content-Type',types[path.extname(p)]||'application/octet-stream');res.end(fs.readFileSync(p));});
(async()=>{const report={at:new Date().toISOString(),failures:[],externalRequests:[],images:[],outputs:[]};
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:'C:/Users/KIM TAEHYUNG/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe'});
try{const ctx=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1,locale:'zh-CN',reducedMotion:'reduce'});await ctx.route('**/*',route=>{if(!route.request().url().startsWith(base+'/')){report.externalRequests.push(route.request().url());return route.abort()}return route.continue()});
const page=await ctx.newPage();page.on('pageerror',e=>report.failures.push(String(e)));
async function open(file){await page.goto(base+'/'+file,{waitUntil:'networkidle'});await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()))});}
async function shot(file,selector){const opts={path:path.join(root,file),animations:'disabled'};const b=selector?await page.locator(selector).screenshot(opts):await page.screenshot({...opts,fullPage:true});report.outputs.push({file,width:b.readUInt32BE(16),height:b.readUInt32BE(20),bytes:b.length,sha256:hash(opts.path)});}
await open('index.html');report.browser=browser.version();report.images=await page.locator('.scene-image').evaluateAll(es=>es.map(e=>({src:e.getAttribute('src'),width:e.naturalWidth,height:e.naturalHeight,rendered:e.getBoundingClientRect().height,loaded:e.complete})));
report.layout=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,scenes:document.querySelectorAll('.scene').length,bodyHeight:document.body.scrollHeight,forms:document.forms.length,solid:[...document.querySelectorAll('.solid')].map(e=>({text:e.textContent,color:getComputedStyle(e).backgroundColor})),logoSources:[...document.querySelectorAll('.brand img,.official-footer-logo img')].map(e=>e.getAttribute('src'))}));
if(report.layout.scrollWidth!==1440||report.layout.scenes!==13)report.failures.push('Unexpected desktop layout geometry');
if(report.layout.solid.some(x=>x.color!=='rgb(0, 127, 168)'))report.failures.push('CTA token mismatch');
if(report.images.some(x=>!x.loaded))report.failures.push('Image load failure');
report.logo={source:'F:/pnpline-landing/resources/logo/PNP-LINE.webp',sha256:hash('F:/pnpline-landing/resources/logo/PNP-LINE.webp'),packagedSha256:hash(path.join(root,'assets/PNP-LINE.webp'))};
if(report.logo.sha256!==report.logo.packagedSha256)report.failures.push('Official logo mismatch');
await shot('00-fullpage.png');await shot('review/hero-1440.png','#hero');await shot('review/services-1440.png','#services');await shot('review/service-details-1440.png','#service-details');await shot('review/service-support-1440.png','#service-support');await shot('review/channels-1440.png','#channels');await shot('review/warehouse-responsibility-1440.png','#warehouse-evidence');await shot('review/wms-system-1440.png','#system');await shot('review/policy-customs-1440.png','#policy-customs');await shot('review/faq-1440.png','#faq');await shot('review/quote-1440.png','#quote');await shot('review/footer-1440.png','#footer');
await open('states.html');await shot('review/form-states-1440.png','.state-board');
await open('review.html');await shot('review/contact-sheet-1440.png');
fs.writeFileSync(path.join(root,'review/capture-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
if(report.failures.length||report.externalRequests.length)process.exitCode=1;
}finally{await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});

