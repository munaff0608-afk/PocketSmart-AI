function showLoading() {
  const el = document.getElementById("result");
  if (el) el.innerHTML = '<div class="card">⏳ Generating your plan...</div>';
}
function renderResult(data) {
  const el = document.getElementById("result");
  const allocations = Object.entries(data.allocation || {}).map(([k,v]) =>
    `<div><span>${k.replaceAll("_"," ")}</span><strong>₹${Math.round(v)}</strong></div>`).join("");
  const cards = (data.recommendations || []).map(item => `
    <div class="card product-card">
      <div class="pill">${item.platform || "Platform"}</div>
      <h3>${escapeHtml(item.name || "Suggestion")}</h3>
      <p>${escapeHtml(item.reason || "")}</p>
      ${item.estimated_price !== undefined ? `<strong>₹${item.estimated_price}</strong>` : ""}
      ${item.url ? `<a class="btn small" target="_blank" rel="noopener" href="${item.url}">Open platform</a>` : ""}
    </div>`).join("");
  el.innerHTML = `
    <div class="card"><h2>Your plan</h2><p>${escapeHtml(data.summary || "")}</p>
      <div class="allocation">${allocations}</div>
      <p class="muted">Source: ${escapeHtml(data.source || "AI")}</p>
    </div>
    <h2 class="section-title">Suggestions</h2>
    <div class="grid two">${cards}</div>`;
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));}

async function sendJSON(url, payload){
  showLoading();
  const res = await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const data = await res.json();
  if(!res.ok) throw new Error(data.detail || "Request failed");
  renderResult(data);
}

document.addEventListener("DOMContentLoaded",()=>{
  const home=document.getElementById("home-form");
  if(home) home.addEventListener("submit",async e=>{
    e.preventDefault();
    const f=new FormData(home);
    try{
      await sendJSON("/generate-home",{
        budget:Number(f.get("budget")),room_type:f.get("room_type"),style:f.get("style"),
        items:{lights:Number(f.get("lights")),fans:Number(f.get("fans")),tables:Number(f.get("tables"))},
        notes:f.get("notes")
      });
    }catch(err){document.getElementById("result").innerHTML=`<div class="alert">${escapeHtml(err.message)}</div>`}
  });

  const party=document.getElementById("party-form");
  if(party) party.addEventListener("submit",async e=>{
    e.preventDefault();const f=new FormData(party);
    try{await sendJSON("/generate-party",{
      budget:Number(f.get("budget")),guests:Number(f.get("guests")),event_type:f.get("event_type"),
      venue:f.get("venue"),food_preference:f.get("food_preference"),notes:f.get("notes")
    })}catch(err){document.getElementById("result").innerHTML=`<div class="alert">${escapeHtml(err.message)}</div>`}
  });

  const jewelry=document.getElementById("jewelry-form");
  if(jewelry) jewelry.addEventListener("submit",async e=>{
    e.preventDefault();showLoading();
    const form=new FormData(jewelry);
    const res=await fetch("/generate-jewelry",{method:"POST",body:form});
    const data=await res.json();
    if(!res.ok){document.getElementById("result").innerHTML=`<div class="alert">${escapeHtml(data.detail||"Request failed")}</div>`;return;}
    renderResult(data);
  });
});
