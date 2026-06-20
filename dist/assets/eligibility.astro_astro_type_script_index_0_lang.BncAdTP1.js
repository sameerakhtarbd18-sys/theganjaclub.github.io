const o=document.querySelectorAll(".step"),t=document.getElementById("result"),l=document.getElementById("result-body"),n=document.getElementById("result-cta");let s=[];const d=["likely","records-help"],c={likely:`
      <p class="kicker good">BASED ON YOUR ANSWERS</p>
      <h2>You match the profile clinics typically assess</h2>
      <p>You're an adult with a diagnosed condition, prior treatments tried, and accessible records —
      the same starting point as most UK patients who go on to receive a prescription. The decision
      itself always rests with a specialist, but you have a clear next step:</p>
      <ol>
        <li><strong>Request your GP Summary Care Record</strong> (free, via your practice or the NHS App).</li>
        <li><strong>Compare clinics</strong> — fees, models and onboarding speed differ a lot.</li>
        <li><strong>Book an initial consultation</strong> — most are video calls within 1–2 weeks.</li>
      </ol>
      <a class="cta" href="/clinics">Compare UK clinics <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;display:inline-block;margin-left:2px" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>`,under18:`
      <p class="kicker">ABOUT UNDER-18 ACCESS</p>
      <h2>The route for under-18s is different</h2>
      <p>Medical cannabis for children and young people in the UK runs through paediatric specialists —
      most prominently for severe, treatment-resistant epilepsy — usually with parental involvement and
      sometimes via the NHS. Private adult clinics won't assess under-18s. The right starting point is a
      conversation between a parent or guardian and the young person's existing specialist or GP.</p>
      <a class="cta" href="/guides/patient-rights">Read the patient guide <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;display:inline-block;margin-left:2px" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>`,undiagnosed:`
      <p class="kicker">NEXT STEP: DIAGNOSIS FIRST</p>
      <h2>A diagnosis comes before a prescription</h2>
      <p>Specialists prescribe against a documented diagnosis, so the system effectively requires one
      before a clinic can help. The most useful step you can take is booking a GP appointment to get
      your symptoms properly assessed and recorded — that documentation later becomes the evidence a
      cannabis clinic would need.</p>
      <a class="cta" href="/guides/getting-started">How the process works <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;display:inline-block;margin-left:2px" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>`,none:`
      <p class="kicker">HONEST ANSWER</p>
      <h2>Medical cannabis is prescribed for ongoing conditions</h2>
      <p>UK prescriptions are tied to diagnosed, persistent conditions where other treatments haven't
      worked. Without one, there's no route to a legal prescription — and any service suggesting
      otherwise is one to avoid. If you're curious about the medical system, our guides explain how it
      works for the patients it exists for.</p>
      <a class="cta" href="/guides">Browse the guides <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;display:inline-block;margin-left:2px" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>`,"no-treatments":`
      <p class="kicker">NEXT STEP: FIRST-LINE TREATMENTS</p>
      <h2>Specialists look for treatments tried first</h2>
      <p>UK prescribing guidance treats cannabis-based medicines as an option when standard licensed
      treatments haven't delivered adequate relief. Working through first-line options with your GP —
      and having that documented — is both good medicine and, practically, the path that makes a future
      clinic assessment possible.</p>
      <a class="cta" href="/guides/getting-started">What the pathway looks like <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;display:inline-block;margin-left:2px" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>`,"records-help":`
      <p class="kicker good">YOU'RE CLOSE — ONE PRACTICAL STEP</p>
      <h2>Getting your records is straightforward</h2>
      <p>Your GP Summary Care Record is free to access: ask your GP practice's reception for a copy, or
      use the NHS App (Profile → GP health record). Clinics need it to evidence your diagnosis and
      treatment history. Once you have it, you match the typical assessment profile.</p>
      <ol>
        <li>Request the record (practice or NHS App).</li>
        <li>Compare clinics while you wait.</li>
      </ol>
      <a class="cta" href="/clinics">Compare UK clinics <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;display:inline-block;margin-left:2px" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>`};function r(e){o.forEach(i=>i.hidden=i.dataset.step!==e)}function p(e){o.forEach(a=>a.hidden=!0);let i=c[e];e==="likely"&&s.includes("one-treatment")&&(i=i.replace("<ol>",`<p class="flag-note">One note: with a single treatment tried so far, some clinics may ask you to
        try a second first — others will assess regardless. Worth checking condition pages when comparing.</p><ol>`)),l.innerHTML=i,t.hidden=!1,n.hidden=!d.includes(e),t.scrollIntoView({behavior:"smooth",block:"start"})}document.querySelectorAll(".answer").forEach(e=>{e.addEventListener("click",()=>{e.dataset.flag&&s.push(e.dataset.flag),e.dataset.result?p(e.dataset.result):e.dataset.next&&r(e.dataset.next)})});document.getElementById("restart").addEventListener("click",()=>{s=[],t.hidden=!0,n.hidden=!0,r("1")});
