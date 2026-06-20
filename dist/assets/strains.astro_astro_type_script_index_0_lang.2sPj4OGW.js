const o=JSON.parse(document.getElementById("strain-data").textContent),u=document.getElementById("strain-grid"),c=document.getElementById("strain-search"),g=document.getElementById("result-count"),h=document.getElementById("empty-state"),l=document.getElementById("detail-panel"),d=document.getElementById("panel-backdrop"),m=document.getElementById("panel-content"),y=e=>{const t=e.cbdRange[1],n=e.thcRange[1];return t>=8&&n<=8?"high-cbd":t>=5&&n>=3?"balanced":"high-thc"},a={type:null,ratio:null,effect:null,condition:null,flavour:null};function v(){const e=new URLSearchParams(location.search);for(const t of Object.keys(a))a[t]=e.get(t);c.value=e.get("q")||"",document.querySelectorAll(".filter-group .pill").forEach(t=>{const n=t.closest(".filter-group").dataset.group;t.classList.toggle("active",a[n]===t.dataset.val)})}function b(){const e=new URLSearchParams;for(const[t,n]of Object.entries(a))n&&e.set(t,n);c.value.trim()&&e.set("q",c.value.trim()),history.replaceState(null,"",e.toString()?`?${e}`:location.pathname)}const $=e=>e.ukAvailability.startsWith("Standardised")?["RX UK","rx"]:e.ukAvailability.startsWith("Available")?["UK CLINICS","clinic"]:["NAME VARIES","varies"];function E(e){const[t,n]=$(e);return`<article class="strain-card" data-id="${e.id}" tabindex="0" role="button" aria-label="Open ${e.name} details">
      <div class="strain-top">
        <h2>${e.name}</h2>
        <span class="type-badge type-${e.type}">${e.type}</span>
      </div>
      <p class="ranges">THC ${e.thcRange[0]}–${e.thcRange[1]}% · CBD ${e.cbdRange[0]}–${e.cbdRange[1]}%</p>
      <p class="effects">${e.effects.slice(0,3).join(" · ")}</p>
      <p class="flavours">${e.flavours.map(i=>`<span>${i}</span>`).join("")}</p>
      <span class="uk-badge uk-${n}">${t}</span>
    </article>`}function k(e){return`
      <p class="kicker">${e.type.toUpperCase()} · ${e.lineage}</p>
      <h2>${e.name}</h2>
      <p class="ranges big">THC ${e.thcRange[0]}–${e.thcRange[1]}% · CBD ${e.cbdRange[0]}–${e.cbdRange[1]}%</p>
      <p class="desc">${e.description}</p>
      <h3>Terpene profile</h3>
      <p class="tags">${e.terpenes.map(t=>`<span>${t}</span>`).join("")}</p>
      <h3>Reported effects</h3>
      <p class="tags">${e.effects.map(t=>`<span>${t}</span>`).join("")}</p>
      <h3>Cited medical uses</h3>
      <p class="tags">${e.medicalUses.map(t=>`<span>${t}</span>`).join("")}</p>
      <h3>UK availability</h3>
      <p class="desc">${e.ukAvailability}.</p>
      <p class="panel-note">Figures are typical published ranges — prescribed products carry batch-specific
      certificates of analysis. Discuss product selection with your prescribing clinician.</p>
      <a class="panel-cta" href="/clinics">Compare UK clinics <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;display:inline-block;margin-left:2px" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>`}function L(e){m.innerHTML=k(e),l.classList.add("open"),l.setAttribute("aria-hidden","false"),d.hidden=!1}function p(){l.classList.remove("open"),l.setAttribute("aria-hidden","true"),d.hidden=!0}function s(){const e=c.value.trim().toLowerCase(),t=o.filter(n=>(!e||n.name.toLowerCase().includes(e))&&(!a.type||n.type===a.type)&&(!a.ratio||y(n)===a.ratio)&&(!a.effect||n.effects.includes(a.effect))&&(!a.condition||n.medicalUses.includes(a.condition))&&(!a.flavour||n.flavours.includes(a.flavour)));u.innerHTML=t.map(E).join(""),g.textContent=`${t.length} of ${o.length} strains`,h.hidden=t.length>0,u.querySelectorAll(".strain-card").forEach(n=>{const i=()=>L(o.find(r=>r.id===n.dataset.id));n.addEventListener("click",i),n.addEventListener("keydown",r=>{r.key==="Enter"&&i()})}),b()}document.querySelectorAll(".filter-group .pill").forEach(e=>{e.addEventListener("click",()=>{const t=e.closest(".filter-group").dataset.group,n=e.dataset.val;a[t]=a[t]===n?null:n,e.closest(".filter-group").querySelectorAll(".pill").forEach(i=>i.classList.remove("active")),a[t]&&e.classList.add("active"),s()})});const f=()=>{for(const e of Object.keys(a))a[e]=null;c.value="",document.querySelectorAll(".filter-group .pill").forEach(e=>e.classList.remove("active")),s()};document.getElementById("strain-reset").addEventListener("click",f);document.getElementById("empty-reset").addEventListener("click",f);c.addEventListener("input",s);document.getElementById("panel-close").addEventListener("click",p);d.addEventListener("click",p);document.addEventListener("keydown",e=>{e.key==="Escape"&&p()});v();s();
