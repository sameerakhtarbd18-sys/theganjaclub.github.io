// Affiliate auto-link engine for The Ganja Club
// Reads affiliates.json and injects relevant affiliate links + partner banners into articles
// based on tag matching rules defined in affiliates.json

(function() {
  fetch('/affiliates.json')
    .then(r => r.json())
    .then(aff => {
      if (!aff.active) return;
      
      const rules = aff.auto_link_rules?.tags_to_categories || {};
      const body = document.getElementById('pbd');
      if (!body) return;
      
      const postTags = (document.querySelector('#pmet')?.textContent || '').toLowerCase();
      
      // Check which categories match this post's tags
      let matchedCategories = new Set();
      for (const [tag, category] of Object.entries(rules)) {
        if (postTags.includes(tag.toLowerCase())) {
          matchedCategories.add(category);
        }
      }
      
      if (matchedCategories.size === 0) return;
      
      // Build affiliate link HTML
      let links = [];
      for (const cat of matchedCategories) {
        const affiliates = aff[cat] || [];
        for (const a of affiliates.slice(0, 2)) { // max 2 links per category
          links.push(`<a href="${a.url}" target="_blank" rel="sponsored" style="color:var(--green)">${a.name}</a>`);
        }
      }
      
      if (links.length === 0) return;
      
      // Inject after the article body
      const div = document.createElement('div');
      div.style.cssText = 'margin-top:24px;padding:16px 20px;background:var(--card);border:1px solid var(--line);border-radius:6px;font-size:.85rem';
      div.innerHTML = `<strong style="color:var(--dim);text-transform:uppercase;letter-spacing:.05em;font-size:.7rem">Resources</strong><br>${links.join(' · ')}`;
      body.appendChild(div);
    })
    .catch(() => {}); // Fail silently if no affiliates configured
})();
