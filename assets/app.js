const locale=document.documentElement.lang.startsWith("pt")?"pt":"en";
const root=document.body.dataset.root||".";
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
async function loadJSON(path){const r=await fetch(path+"?v="+Date.now());if(!r.ok)throw new Error("HTTP "+r.status);return r.json()}
async function initTicker(){
  const el=document.querySelector("#tickeritems"); if(!el)return;
  try{
    const d=await loadJSON(root.replace(/\/$/,"")+"/data/site.json");
    el.innerHTML=(d.ticker||[]).map(x=>`<span><b>${esc(x.label?.[locale])}</b> ${esc(x.value?.[locale])}</span>`).join("");
  }catch(e){el.innerHTML=`<span><b>CS2NEWS</b> ${locale==="pt"?"dados temporariamente indisponíveis":"data temporarily unavailable"}</span>`}
}
async function initSearch(){
  const input=document.querySelector("#site-search"),out=document.querySelector("#search-results"); if(!input||!out)return;
  let items=[];
  try{items=await loadJSON(root.replace(/\/$/,"")+"/data/search-"+locale+".json")}catch(e){out.innerHTML='<div class="empty">Search index unavailable.</div>';return}
  const render=()=>{
    const q=input.value.trim().toLowerCase();
    if(q.length<2){out.innerHTML="";return}
    const hits=items.filter(x=>String(x.title||"").toLowerCase().includes(q)).slice(0,30);
    out.innerHTML=hits.length?hits.map(x=>`<a class="searchitem" href="${esc(x.url)}"><small>${esc(x.type)}</small><div><b>${esc(x.title)}</b></div></a>`).join(""):`<div class="empty">${locale==="pt"?"Nenhum resultado.":"No results."}</div>`;
  };
  input.addEventListener("input",render);input.focus();
}
initTicker();initSearch();
