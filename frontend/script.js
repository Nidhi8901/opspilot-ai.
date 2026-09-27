const q=s=>document.querySelector(s),qa=s=>[...document.querySelectorAll(s)];
function clock(){q('#clock').textContent=new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});} setInterval(clock,1000);clock();
const fallbackServices=[{id:1,name:'payment-api',status:'healthy',cpu:34},{id:2,name:'checkout-api',status:'degraded',cpu:89},{id:3,name:'user-service',status:'healthy',cpu:27}];
const fallbackIncidents=[{id:1001,title:'Checkout API High Error Rate',severity:'high',status:'investigating',summary:'Checkout requests are returning increased HTTP 500 errors.'},{id:1002,title:'Payment API Latency Increase',severity:'medium',status:'monitoring',summary:'Payment API response time temporarily exceeded the normal threshold.'}];
async function load(){let services=fallbackServices,incidents=fallbackIncidents;try{let r=await fetch('/services');if(r.ok)services=await r.json();}catch(e){}try{let r=await fetch('/incidents');if(r.ok)incidents=await r.json();}catch(e){}q('#serviceCount').textContent=services.length;q('#incidentCount').textContent=incidents.length;let healthy=services.filter(x=>x.status==='healthy').length;q('#healthyCount').textContent=healthy;if(incidents[0])q('#signalTitle').textContent=incidents[0].title;q('#serviceNodes').innerHTML=services.map(s=>'<div class="node '+(s.status==='healthy'?'ok':'bad')+'"><small>SERVICE</small><b>'+s.name+'</b><span>CPU '+(s.cpu||'--')+'%</span></div>').join('');q('#incidentList').innerHTML=incidents.map(i=>'<article class="incident"><span class="incident-id">INC-'+i.id+'</span><div><h4>'+i.title+'</h4><p>'+(i.summary||'')+'</p></div><span class="sev '+i.severity+'">'+i.severity+'</span><span class="status">'+i.status+'</span></article>').join('');}
const ob=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('visible')}),{threshold:.1});qa('.reveal').forEach(e=>ob.observe(e));qa('nav a').forEach(a=>a.onclick=()=>{qa('nav a').forEach(x=>x.classList.remove('active'));a.classList.add('active')});load();

// OpsPilot Create Incident modal
document.addEventListener("DOMContentLoaded", () => {
  const incidentSection = document.querySelector("#incidents");
  const modal = document.querySelector("#incidentModal");
  const form = document.querySelector("#incidentForm");
  const closeBtn = document.querySelector("#closeIncidentModal");
  const cancelBtn = document.querySelector("#cancelIncidentModal");
  const submitBtn = document.querySelector("#submitIncident");
  const toast = document.querySelector("#toast");

  function showToast(message, type="success"){
    if(!toast) return;
    toast.textContent = message;
    toast.className = "toast show " + type;
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => {
      toast.className = "toast";
    }, 3200);
  }

  function ensureCreateButton(){
    if(document.querySelector("#openIncidentModal")) return;
    const button = document.createElement("button");
    button.id = "openIncidentModal";
    button.type = "button";
    button.className = "button primary compact";
    button.textContent = "+ Create incident";

    if(incidentSection){
      const heading = incidentSection.querySelector(".panel-heading");
      if(heading){
        let actions = heading.querySelector(".incident-actions");
        if(!actions){
          actions = document.createElement("div");
          actions.className = "incident-actions";
          heading.appendChild(actions);
        }
        actions.appendChild(button);
      } else {
        incidentSection.insertBefore(button, incidentSection.firstChild);
      }
    } else {
      document.body.appendChild(button);
    }
    button.addEventListener("click", openModal);
  }

  async function loadServiceOptions(){
    const select = document.querySelector("#incidentService");
    select.innerHTML = '<option value="">Loading services...</option>';
    try{
      const response = await fetch("/services");
      if(!response.ok) throw new Error("Could not load services");
      const services = await response.json();
      select.innerHTML = services.map(service =>
        '<option value="' + service.id + '">' +
        service.name + ' - ' + service.environment + ' - ' + service.status +
        '</option>'
      ).join("");
    }catch(error){
      select.innerHTML = '<option value="">Unable to load services</option>';
      showToast("Could not load service list.", "error");
    }
  }

  async function openModal(){
    await loadServiceOptions();
    modal.classList.add("open");
    modal.setAttribute("aria-hidden","false");
    document.body.style.overflow = "hidden";
    setTimeout(() => document.querySelector("#incidentTitle").focus(), 80);
  }

  function closeModal(){
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden","true");
    document.body.style.overflow = "";
  }

  ensureCreateButton();
  closeBtn?.addEventListener("click", closeModal);
  cancelBtn?.addEventListener("click", closeModal);

  modal?.addEventListener("click", (event) => {
    if(event.target === modal) closeModal();
  });

  document.addEventListener("keydown", (event) => {
    if(event.key === "Escape" && modal?.classList.contains("open")) closeModal();
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const severity = document.querySelector('input[name="severity"]:checked')?.value || "high";
    const evidence = document.querySelector("#incidentEvidence").value
      .split("\n").map(item => item.trim()).filter(Boolean);

    const payload = {
      service_id: Number(document.querySelector("#incidentService").value),
      title: document.querySelector("#incidentTitle").value.trim(),
      severity,
      status: document.querySelector("#incidentStatus").value,
      summary: document.querySelector("#incidentSummary").value.trim(),
      evidence,
      recent_deployment: document.querySelector("#incidentDeployment").value.trim() || null
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Creating...";

    try{
      const response = await fetch("/incidents", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
      });
      if(!response.ok){
        const data = await response.json();
        throw new Error(data.detail ? JSON.stringify(data.detail) : "Incident creation failed");
      }

      const created = await response.json();
      form.reset();
      closeModal();

      if(typeof loadData === "function"){
        await loadData();
      } else {
        window.location.reload();
        return;
      }

      showToast("INC-" + created.id + " created and saved to PostgreSQL.", "success");
      document.querySelector("#incidents")?.scrollIntoView({behavior:"smooth",block:"start"});
    }catch(error){
      showToast("Could not create incident. " + error.message, "error");
    }finally{
      submitBtn.disabled = false;
      submitBtn.textContent = "Create incident";
    }
  });
});

// OpsPilot incident details drawer
document.addEventListener("DOMContentLoaded", () => {
  const drawer = document.querySelector("#incidentDrawer");
  const backdrop = document.querySelector("#incidentDrawerBackdrop");
  const closeBtn = document.querySelector("#closeIncidentDrawer");
  const analyzeBtn = document.querySelector("#analyzeIncidentBtn");
  const reanalyzeBtn = document.querySelector("#reanalyzeIncidentBtn");

  let activeIncidentId = null;

  function closeDrawer(){
    drawer?.classList.remove("open");
    backdrop?.classList.remove("open");
    drawer?.setAttribute("aria-hidden","true");
    backdrop?.setAttribute("aria-hidden","true");
    document.body.style.overflow = "";
  }

  function formatDate(value){
    if(!value) return "-";
    const date = new Date(value);
    if(Number.isNaN(date.getTime())) return value;
    return date.toLocaleString([], {
      year:"numeric", month:"short", day:"2-digit",
      hour:"2-digit", minute:"2-digit"
    });
  }

  function setAIState(state){
    const empty = document.querySelector("#aiEmptyState");
    const loading = document.querySelector("#aiLoadingState");
    const result = document.querySelector("#aiResultState");
    const badge = document.querySelector("#aiStateBadge");

    empty.hidden = state !== "empty";
    loading.hidden = state !== "loading";
    result.hidden = state !== "result";

    if(state === "loading") badge.textContent = "Analyzing";
    else if(state === "result") badge.textContent = "Complete";
    else badge.textContent = "Ready";
  }

  function renderAnalysis(data){
    document.querySelector("#aiConfidence").textContent = data.confidence_percent + "%";
    document.querySelector("#aiConfidenceBar").style.width = data.confidence_percent + "%";
    document.querySelector("#aiSummary").textContent = data.summary;
    document.querySelector("#aiProbableCause").textContent = data.probable_cause;
    document.querySelector("#aiImpact").textContent = data.impact;
    document.querySelector("#aiRollback").textContent = data.rollback_consideration;

    const actions = Array.isArray(data.recommended_actions) ? data.recommended_actions : [];
    document.querySelector("#aiActions").innerHTML =
      actions.map(item => "<li>" + item + "</li>").join("");

    document.querySelector("#aiModel").textContent = data.model_id;
    document.querySelector("#aiUsage").textContent =
      "Tokens " + (data.total_tokens ?? 0);
    document.querySelector("#aiLatency").textContent =
      "Latency " + (data.latency_ms ?? 0) + " ms";

    setAIState("result");
  }

  async function loadLatestAnalysis(incidentId){
    setAIState("empty");
    try{
      const response = await fetch("/incidents/" + incidentId + "/analysis/latest");
      if(response.status === 404) return;
      if(!response.ok) throw new Error("Could not load latest analysis");
      renderAnalysis(await response.json());
    }catch(error){
      console.warn("Latest AI analysis unavailable:", error);
    }
  }

  async function runAnalysis(){
    if(!activeIncidentId) return;

    setAIState("loading");
    if(analyzeBtn) analyzeBtn.disabled = true;
    if(reanalyzeBtn) reanalyzeBtn.disabled = true;

    try{
      const response = await fetch(
        "/incidents/" + activeIncidentId + "/analyze",
        {method:"POST"}
      );
      const data = await response.json();
      if(!response.ok) throw new Error(data.detail || "AI analysis failed");
      renderAnalysis(data);
    }catch(error){
      setAIState("empty");
      alert("AI analysis failed: " + error.message);
    }finally{
      if(analyzeBtn) analyzeBtn.disabled = false;
      if(reanalyzeBtn) reanalyzeBtn.disabled = false;
    }
  }

  async function openDrawer(incidentId){
    if(!drawer || !backdrop) return;
    activeIncidentId = incidentId;

    drawer.classList.add("open");
    backdrop.classList.add("open");
    drawer.setAttribute("aria-hidden","false");
    backdrop.setAttribute("aria-hidden","false");
    document.body.style.overflow = "hidden";

    document.querySelector("#incidentDrawerTitle").textContent = "Loading incident...";
    document.querySelector("#drawerIncidentId").textContent = "INC-" + incidentId;
    document.querySelector("#drawerSummary").textContent = "Loading...";
    document.querySelector("#drawerEvidence").innerHTML = "";

    try{
      const response = await fetch("/incidents/" + incidentId);
      if(!response.ok) throw new Error("Incident could not be loaded");
      const incident = await response.json();

      document.querySelector("#incidentDrawerTitle").textContent = incident.title;
      document.querySelector("#drawerIncidentId").textContent = "INC-" + incident.id;

      const severity = document.querySelector("#drawerSeverity");
      severity.textContent = incident.severity;
      severity.className = "severity " + incident.severity;

      document.querySelector("#drawerStatus").textContent = incident.status;
      document.querySelector("#drawerSummary").textContent = incident.summary;
      document.querySelector("#drawerDetectedAt").textContent = formatDate(incident.detected_at);
      document.querySelector("#drawerDeployment").textContent =
        incident.recent_deployment || "No deployment linked";

      const evidence = Array.isArray(incident.evidence) ? incident.evidence : [];
      document.querySelector("#drawerEvidence").innerHTML = evidence.length
        ? evidence.map(item => "<li>" + item + "</li>").join("")
        : "<li>No evidence recorded yet.</li>";

      await loadLatestAnalysis(incidentId);
    }catch(error){
      document.querySelector("#incidentDrawerTitle").textContent = "Unable to load incident";
      document.querySelector("#drawerSummary").textContent = error.message;
      setAIState("empty");
    }
  }

  function wireIncidentCards(){
    document.querySelectorAll(".incident").forEach(card => {
      if(card.dataset.drawerWired === "1") return;

      const idText = card.querySelector(".incident-id")?.textContent || "";
      const incidentId = idText.replace(/\D/g,"");
      if(!incidentId) return;

      card.dataset.drawerWired = "1";
      card.tabIndex = 0;
      card.setAttribute("role","button");
      card.setAttribute("aria-label","Open details for incident " + incidentId);

      card.addEventListener("click", () => openDrawer(incidentId));
      card.addEventListener("keydown", event => {
        if(event.key === "Enter" || event.key === " "){
          event.preventDefault();
          openDrawer(incidentId);
        }
      });
    });
  }

  analyzeBtn?.addEventListener("click", runAnalysis);
  reanalyzeBtn?.addEventListener("click", runAnalysis);
  closeBtn?.addEventListener("click", closeDrawer);
  backdrop?.addEventListener("click", closeDrawer);

  document.addEventListener("keydown", event => {
    if(event.key === "Escape" && drawer?.classList.contains("open")) closeDrawer();
  });

  wireIncidentCards();

  const list = document.querySelector("#incidentList");
  if(list){
    const observer = new MutationObserver(wireIncidentCards);
    observer.observe(list, {childList:true,subtree:true});
  }
});

// OpsPilot RAG source indicator
document.addEventListener("DOMContentLoaded", () => {
  const resultState = document.querySelector("#aiResultState");
  const runbookTitle = document.querySelector("#aiRunbookTitle");
  const grounding = document.querySelector("#aiGrounding");
  const incidentLabel = document.querySelector("#drawerIncidentId");

  if (!resultState || !runbookTitle || !grounding || !incidentLabel) return;

  let lastLoadedIncidentId = null;
  let requestSequence = 0;

  function currentIncidentId(){
    const value = incidentLabel.textContent || "";
    const match = value.match(/\d+/);
    return match ? match[0] : null;
  }

  function setGroundingState(title){
    const icon = grounding.querySelector(".ai-grounding-icon");
    const detail = grounding.querySelector("span");

    if(title){
      grounding.classList.remove("no-source");
      runbookTitle.textContent = title;
      if(icon) icon.textContent = "RAG";
      if(detail){
        detail.textContent =
          "Retrieved from PostgreSQL using semantic vector search.";
      }
    }else{
      grounding.classList.add("no-source");
      runbookTitle.textContent = "No runbook source stored";
      if(icon) icon.textContent = "—";
      if(detail){
        detail.textContent =
          "This analysis was created before runbook grounding, or no matching runbook was retrieved.";
      }
    }
  }

  async function refreshGrounding(force = false){
    if(resultState.hidden) return;

    const incidentId = currentIncidentId();
    if(!incidentId) return;
    if(!force && incidentId === lastLoadedIncidentId) return;

    const sequence = ++requestSequence;
    runbookTitle.textContent = "Loading source...";

    try{
      const response = await fetch(
        "/incidents/" + incidentId + "/analysis/latest"
      );

      if(!response.ok){
        throw new Error("Could not load latest analysis");
      }

      const analysis = await response.json();
      if(sequence !== requestSequence) return;

      lastLoadedIncidentId = incidentId;
      setGroundingState(analysis.runbook_title || null);

      const semanticMatch = document.querySelector("#aiSemanticMatch");
      if(semanticMatch){
        if(typeof analysis.runbook_similarity === "number"){
          semanticMatch.textContent =
            Math.round(analysis.runbook_similarity * 100) + "%";
        }else{
          semanticMatch.textContent = "--";
        }
      }
    }catch(error){
      if(sequence !== requestSequence) return;
      lastLoadedIncidentId = incidentId;
      setGroundingState(null);
      const semanticMatch = document.querySelector("#aiSemanticMatch");
      if(semanticMatch) semanticMatch.textContent = "--";
      console.warn("RAG source unavailable:", error);
    }
  }

  const resultObserver = new MutationObserver(() => {
    if(!resultState.hidden){
      refreshGrounding(true);
    }
  });

  resultObserver.observe(resultState, {
    attributes:true,
    attributeFilter:["hidden"]
  });

  const incidentObserver = new MutationObserver(() => {
    lastLoadedIncidentId = null;
    if(!resultState.hidden){
      refreshGrounding(true);
    }
  });

  incidentObserver.observe(incidentLabel, {
    childList:true,
    subtree:true,
    characterData:true
  });

  if(!resultState.hidden){
    refreshGrounding(true);
  }
});

// Recommended runbook modal
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector("#runbookModal");
  const backdrop = document.querySelector("#runbookModalBackdrop");
  const closeBtn = document.querySelector("#closeRunbookModal");

  function currentIncidentId(){
    const label = document.querySelector("#drawerIncidentId");
    const value = label?.textContent || "";
    const match = value.match(/\d+/);
    return match ? match[0] : null;
  }

  function openModal(){
    if(!modal || !backdrop) return;
    modal.hidden = false;
    backdrop.hidden = false;
    modal.setAttribute("aria-hidden","false");
  }

  function closeModal(){
    if(!modal || !backdrop) return;
    modal.hidden = true;
    backdrop.hidden = true;
    modal.setAttribute("aria-hidden","true");
  }

  function renderKeywords(keywords){
    const container = document.querySelector("#runbookKeywords");
    if(!container) return;
    container.innerHTML = "";
    (Array.isArray(keywords) ? keywords : []).forEach(keyword => {
      const chip = document.createElement("span");
      chip.textContent = keyword;
      container.appendChild(chip);
    });
  }

  async function openRecommendedRunbook(event){
    const target = event.target.closest("#openRecommendedRunbook");
    if(!target) return;

    event.preventDefault();
    event.stopPropagation();

    const incidentId = currentIncidentId();
    if(!incidentId){
      alert("Open an incident first.");
      return;
    }

    document.querySelector("#runbookModalTitle").textContent = "Loading...";
    document.querySelector("#runbookProblemType").textContent = "";
    document.querySelector("#runbookDescription").textContent = "";
    document.querySelector("#runbookContent").textContent = "";
    renderKeywords([]);
    openModal();

    try{
      const response = await fetch(
        "/incidents/" + incidentId + "/recommended-runbook"
      );
      const data = await response.json();

      if(!response.ok){
        throw new Error(data.detail || "Recommended runbook could not be loaded");
      }

      document.querySelector("#runbookModalTitle").textContent =
        data.title || "Recommended runbook";
      document.querySelector("#runbookProblemType").textContent =
        data.problem_type || "Operational runbook";
      document.querySelector("#runbookDescription").textContent =
        data.description || "No description available.";
      document.querySelector("#runbookContent").textContent =
        data.content || "No troubleshooting steps available.";
      renderKeywords(data.keywords);
    }catch(error){
      document.querySelector("#runbookModalTitle").textContent =
        "Unable to load runbook";
      document.querySelector("#runbookDescription").textContent =
        error.message;
    }
  }

  document.addEventListener("click", openRecommendedRunbook);
  closeBtn?.addEventListener("click", closeModal);
  backdrop?.addEventListener("click", closeModal);

  document.addEventListener("keydown", event => {
    if(event.key === "Escape" && modal && !modal.hidden){
      closeModal();
    }
  });
});

