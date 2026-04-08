/* ═══════════════════════════════════════════════════════════════
   IRONPLAN 70.3 — Application Logic
   Calendar · Drag-and-Drop · Charts · localStorage
   ═══════════════════════════════════════════════════════════════ */

(function () {
    "use strict";

    // ── State ────────────────────────────────────────────────────
    const STATE = {
        workouts: [],
        metrics: [],
        viewMonth: new Date().getMonth(),
        viewYear: new Date().getFullYear(),
        viewMode: "month",
        currentView: "calendar",
        selectedWorkout: null,
        libraryOpen: false,
        detailOpen: false,
    };

    const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const $ = id => document.getElementById(id);

    // ── Init ─────────────────────────────────────────────────────
    function init() {
        loadOrGenerate();
        computeMetrics();
        renderTopBar();
        renderPhaseTimeline();
        renderMetricsGrid();
        renderCalendar();
        bindNav();
        bindCalendarControls();
        bindPanels();
        bindBuilder();
        bindLibrary();
        bindMobileMenu();
    }

    function loadOrGenerate() {
        const saved = localStorage.getItem("ironplan_workouts");
        if (saved) {
            try { STATE.workouts = JSON.parse(saved); return; } catch (e) { }
        }
        STATE.workouts = TrainingData.generatePlan();
        TrainingData.addSampleCompletionData(STATE.workouts);
        saveWorkouts();
    }

    function saveWorkouts() {
        localStorage.setItem("ironplan_workouts", JSON.stringify(STATE.workouts));
    }

    function computeMetrics() {
        STATE.metrics = TrainingData.calculateMetrics(STATE.workouts);
    }

    // ── Top Bar ──────────────────────────────────────────────────
    function renderTopBar() {
        $("countdownDays").textContent = TrainingData.daysToRace();
        $("metricWeek").textContent = TrainingData.getCurrentWeek(STATE.workouts);
        const phase = TrainingData.getCurrentPhase(STATE.workouts);
        $("metricPhase").textContent = phase.length > 15 ? phase.split("+")[0].trim().substring(0, 12) : phase.substring(0, 15);
        const m = STATE.metrics;
        if (m.length) {
            const last = m[m.length - 1];
            $("metricCTL").textContent = last.ctl.toFixed(0);
            $("metricTSB").textContent = last.tsb.toFixed(0);
            $("metricTSB").style.color = last.tsb > 0 ? "var(--accent-green)" : last.tsb < -20 ? "#ff6b6b" : "var(--accent-orange)";
        }
        const comp = TrainingData.calculateCompliance(STATE.workouts);
        $("metricCompliance").textContent = comp.overall + "%";
    }

    // ── Phase Timeline ───────────────────────────────────────────
    function renderPhaseTimeline() {
        const el = $("phaseTimeline");
        const current = TrainingData.getCurrentPhase(STATE.workouts);
        el.innerHTML = TrainingData.PHASES.map(p => {
            const active = current === p.name ? "active" : "";
            const shortName = p.name.includes("+") ? p.name.split("+")[0].trim() : p.name;
            return `<div class="phase-block ${active}" style="flex-grow:${p.weeks}" title="${p.desc}">
      <div style="position:absolute;inset:0;background:${p.color};opacity:inherit;border-radius:inherit" class="phase-bg"></div>
      <div class="phase-name" style="position:relative">${shortName}</div>
      <div class="phase-weeks" style="position:relative">${p.weeks}w</div>
    </div>`;
        }).join("");
    }

    // ── Metrics Grid ─────────────────────────────────────────────
    function renderMetricsGrid() {
        const m = STATE.metrics, w = STATE.workouts;
        const last = m.length ? m[m.length - 1] : { ctl: 0, atl: 0, tsb: 0 };
        const comp = TrainingData.calculateCompliance(w);
        const completed = w.filter(x => x.status === "completed").length;
        const today = TrainingData.formatDate(new Date());
        const total = w.filter(x => x.date <= today && x.sport !== "rest").length;
        const weekVol = TrainingData.calculateWeeklyVolume(w);
        const curWeek = TrainingData.getCurrentWeek(w);
        const wv = weekVol.find(x => x.week === curWeek);
        const weekMin = wv ? wv.total : 0;

        const cards = [
            { label: "Fitness (CTL)", value: last.ctl.toFixed(0), color: "var(--accent-blue)", delta: "Chronic load" },
            { label: "Fatigue (ATL)", value: last.atl.toFixed(0), color: "var(--accent-orange)", delta: "Acute load" },
            { label: "Form (TSB)", value: last.tsb.toFixed(0), color: last.tsb > 0 ? "var(--accent-green)" : "#ff6b6b", delta: last.tsb > 15 ? "Race ready" : last.tsb > 0 ? "Fresh" : last.tsb > -10 ? "Balanced" : "Fatigued" },
            { label: "Compliance", value: comp.overall + "%", color: "var(--accent-green)", delta: `${completed}/${total} sessions` },
            { label: "This Week", value: Math.round(weekMin / 60) + "h", color: "var(--accent)", delta: weekMin + " min total" },
            { label: "Days to Race", value: TrainingData.daysToRace(), color: "var(--accent-orange)", delta: TrainingData.RACE_NAME },
        ];

        $("metricsGrid").innerHTML = cards.map(c =>
            `<div class="metric-card"><div class="metric-label">${c.label}</div>
     <div class="metric-value" style="color:${c.color}">${c.value}</div>
     <div class="metric-delta text-muted">${c.delta}</div></div>`
        ).join("");
    }

    // ── Calendar ─────────────────────────────────────────────────
    function renderCalendar() {
        const grid = $("calendarGrid");
        const y = STATE.viewYear, m = STATE.viewMonth;
        $("calMonthLabel").textContent = `${MONTHS[m]} ${y}`;

        if (STATE.viewMode === "month") renderMonthView(grid, y, m);
        else renderWeekView(grid, y, m);
    }

    function renderMonthView(grid, y, m) {
        const firstDay = new Date(y, m, 1);
        let startDow = firstDay.getDay(); // 0=Sun
        startDow = startDow === 0 ? 6 : startDow - 1; // Convert to Mon=0
        const daysInMonth = new Date(y, m + 1, 0).getDate();
        const today = TrainingData.formatDate(new Date());

        let html = DAYS.map(d => `<div class="cal-day-header">${d}</div>`).join("");

        // Previous month padding
        const prevDays = new Date(y, m, 0).getDate();
        for (let i = startDow - 1; i >= 0; i--) {
            const d = prevDays - i;
            const dt = new Date(y, m - 1, d);
            html += buildDayCell(dt, today, true);
        }

        // Current month
        for (let d = 1; d <= daysInMonth; d++) {
            const dt = new Date(y, m, d);
            html += buildDayCell(dt, today, false);
        }

        // Next month padding
        const totalCells = startDow + daysInMonth;
        const remaining = (7 - (totalCells % 7)) % 7;
        for (let d = 1; d <= remaining; d++) {
            const dt = new Date(y, m + 1, d);
            html += buildDayCell(dt, today, true);
        }

        grid.innerHTML = html;
        bindWorkoutPills();
        bindDragDrop();
    }

    function renderWeekView(grid, y, m) {
        const today = new Date();
        const todayStr = TrainingData.formatDate(today);
        const dow = today.getDay();
        const mondayOffset = dow === 0 ? -6 : 1 - dow;
        const monday = new Date(today);
        monday.setDate(today.getDate() + mondayOffset);

        let html = DAYS.map(d => `<div class="cal-day-header">${d}</div>`).join("");
        for (let i = 0; i < 7; i++) {
            const dt = new Date(monday);
            dt.setDate(monday.getDate() + i);
            html += buildDayCell(dt, todayStr, false, true);
        }
        grid.innerHTML = html;
        bindWorkoutPills();
        bindDragDrop();
    }

    function buildDayCell(dt, today, otherMonth, weekView) {
        const dateStr = TrainingData.formatDate(dt);
        const workouts = TrainingData.getWorkoutsForDate(STATE.workouts, dateStr);
        const isToday = dateStr === today;
        const isDeload = workouts.some(w => w.isDeload);
        const classes = ["cal-day"];
        if (isToday) classes.push("today");
        if (otherMonth) classes.push("other-month");
        if (isDeload) classes.push("deload");
        const minH = weekView ? "style='min-height:200px'" : "";

        let pills = "";
        for (const w of workouts) {
            const sc = w.status === "completed" ? "completed" : w.status === "skipped" ? "skipped" : w.status === "modified" ? "modified" : "";
            const icon = TrainingData.SPORT_ICONS[w.sport] || "•";
            const dur = w.duration > 0 ? w.duration + "m" : "";
            pills += `<div class="workout-pill ${sc}" data-sport="${w.sport}" data-id="${w.id}" draggable="true">
      <span class="pill-icon">${icon}</span>
      <span class="pill-text">${w.desc}</span>
      <span class="pill-dur">${dur}</span>
    </div>`;
        }

        return `<div class="${classes.join(" ")}" data-date="${dateStr}" ${minH}>
    <div class="cal-date">${dt.getDate()}</div>
    <div class="cal-workouts">${pills}</div>
  </div>`;
    }

    function bindWorkoutPills() {
        document.querySelectorAll(".workout-pill").forEach(pill => {
            pill.addEventListener("click", e => {
                e.stopPropagation();
                openDetail(pill.dataset.id);
            });
        });
    }

    // ── Drag & Drop ──────────────────────────────────────────────
    function bindDragDrop() {
        document.querySelectorAll(".workout-pill[draggable]").forEach(pill => {
            pill.addEventListener("dragstart", e => {
                e.dataTransfer.setData("text/plain", JSON.stringify({ type: "workout", id: pill.dataset.id }));
                pill.classList.add("dragging");
                requestAnimationFrame(() => pill.style.opacity = "0.4");
            });
            pill.addEventListener("dragend", () => { pill.classList.remove("dragging"); pill.style.opacity = ""; });
        });

        document.querySelectorAll(".cal-day").forEach(cell => {
            cell.addEventListener("dragover", e => { e.preventDefault(); cell.classList.add("drop-target"); });
            cell.addEventListener("dragleave", () => cell.classList.remove("drop-target"));
            cell.addEventListener("drop", e => {
                e.preventDefault();
                cell.classList.remove("drop-target");
                try {
                    const data = JSON.parse(e.dataTransfer.getData("text/plain"));
                    const newDate = cell.dataset.date;
                    if (!newDate) return;
                    if (data.type === "workout") {
                        const w = STATE.workouts.find(x => x.id === data.id);
                        if (w) { w.date = newDate; saveWorkouts(); renderCalendar(); }
                    } else if (data.type === "library") {
                        addFromLibrary(data.libId, newDate);
                    }
                } catch (err) { }
            });
        });
    }

    function addFromLibrary(libId, dateStr) {
        const tmpl = TrainingData.WORKOUT_LIBRARY.find(l => l.id === libId);
        if (!tmpl) return;
        const id = "w-custom-" + Date.now();
        const phase = TrainingData.getCurrentPhase(STATE.workouts);
        STATE.workouts.push({
            id, date: dateStr, sport: tmpl.sport, type: tmpl.type, duration: tmpl.duration,
            intensity: tmpl.intensity, desc: tmpl.desc, warmup: "", main: tmpl.main, cooldown: "",
            purpose: "", zones: "", rpe: "", tssPlanned: tmpl.tss, tssActual: null,
            phase, phaseColor: "", weekNumber: 0, isDeload: false, status: "planned",
            actualDuration: null, actualHR: null, rpeActual: null, notes: "", bookmarked: false,
        });
        saveWorkouts(); renderCalendar();
    }

    // ── Detail Panel ─────────────────────────────────────────────
    function openDetail(id) {
        const w = STATE.workouts.find(x => x.id === id);
        if (!w) return;
        STATE.selectedWorkout = w;
        STATE.detailOpen = true;

        const sportColor = TrainingData.SPORT_COLORS[w.sport] || "#636E72";
        const icon = TrainingData.SPORT_ICONS[w.sport] || "";
        $("detailBadge").textContent = icon + " " + w.sport.toUpperCase();
        $("detailBadge").style.background = sportColor + "22";
        $("detailBadge").style.color = sportColor;
        $("detailTitle").textContent = w.desc;
        $("detailDate").textContent = formatDisplayDate(w.date) + (w.phase ? ` · ${w.phase}` : "") + (w.isDeload ? " · DELOAD" : "");

        const statusClass = "status-" + w.status;
        $("detailBody").innerHTML = `
    <div class="detail-metrics">
      <div class="detail-metric"><div class="detail-metric-label">Duration</div><div class="detail-metric-value">${w.duration}m</div></div>
      <div class="detail-metric"><div class="detail-metric-label">TSS</div><div class="detail-metric-value">${w.tssPlanned}</div></div>
      <div class="detail-metric"><div class="detail-metric-label">Status</div><div class="detail-metric-value"><span class="status-badge ${statusClass}">${w.status}</span></div></div>
    </div>
    ${w.zones ? `<div class="detail-metrics" style="grid-template-columns:1fr 1fr"><div class="detail-metric"><div class="detail-metric-label">Zone</div><div class="detail-metric-value" style="font-size:0.9rem">${w.zones}</div></div><div class="detail-metric"><div class="detail-metric-label">RPE</div><div class="detail-metric-value" style="font-size:0.9rem">${w.rpe}</div></div></div>` : ""}
    ${w.warmup ? `<div class="detail-section"><div class="detail-section-title">Warm-up</div><div class="detail-segment">${w.warmup}</div></div>` : ""}
    ${w.main ? `<div class="detail-section"><div class="detail-section-title">Main Set</div><div class="detail-segment">${w.main}</div></div>` : ""}
    ${w.cooldown && w.cooldown !== "—" ? `<div class="detail-section"><div class="detail-section-title">Cool-down</div><div class="detail-segment">${w.cooldown}</div></div>` : ""}
    ${w.purpose ? `<div class="detail-section"><div class="detail-section-title">Purpose</div><div class="detail-purpose">${w.purpose}</div></div>` : ""}
    ${w.actualDuration ? `<div class="detail-section"><div class="detail-section-title">Actual Results</div><div class="detail-metrics"><div class="detail-metric"><div class="detail-metric-label">Duration</div><div class="detail-metric-value">${w.actualDuration}m</div></div><div class="detail-metric"><div class="detail-metric-label">TSS</div><div class="detail-metric-value">${w.tssActual || "—"}</div></div><div class="detail-metric"><div class="detail-metric-label">HR</div><div class="detail-metric-value">${w.actualHR || "—"}</div></div></div></div>` : ""}
    <div class="detail-section"><div class="detail-section-title">Edit</div>
      <div class="detail-field"><label>Status</label><select id="editStatus"><option ${w.status === "planned" ? "selected" : ""}>planned</option><option ${w.status === "completed" ? "selected" : ""}>completed</option><option ${w.status === "skipped" ? "selected" : ""}>skipped</option><option ${w.status === "modified" ? "selected" : ""}>modified</option></select></div>
      <div class="detail-field"><label>Actual Duration (min)</label><input type="number" id="editDuration" value="${w.actualDuration || ""}"></div>
      <div class="detail-field"><label>RPE (1-10)</label><input type="number" id="editRPE" value="${w.rpeActual || ""}" min="1" max="10"></div>
      <div class="detail-field"><label>Notes</label><textarea id="editNotes">${w.notes || ""}</textarea></div>
    </div>`;

        $("detailActions").innerHTML = `
    <button class="btn btn-primary btn-full" id="saveDetail">Save Changes</button>
    <button class="btn btn-danger btn-sm" id="deleteDetail">Delete</button>`;

        $("saveDetail").addEventListener("click", () => {
            w.status = $("editStatus").value;
            const ad = parseInt($("editDuration").value);
            if (!isNaN(ad)) w.actualDuration = ad;
            const rpe = parseInt($("editRPE").value);
            if (!isNaN(rpe)) w.rpeActual = rpe;
            w.notes = $("editNotes").value;
            saveWorkouts(); computeMetrics(); renderTopBar(); renderMetricsGrid(); renderCalendar(); closeDetail();
        });

        $("deleteDetail").addEventListener("click", () => {
            STATE.workouts = STATE.workouts.filter(x => x.id !== w.id);
            saveWorkouts(); computeMetrics(); renderTopBar(); renderCalendar(); closeDetail();
        });

        $("detailPanel").classList.add("open");
    }

    function closeDetail() { $("detailPanel").classList.remove("open"); STATE.detailOpen = false; }

    function formatDisplayDate(ds) {
        const d = new Date(ds + "T00:00:00");
        return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
    }

    // ── Navigation ───────────────────────────────────────────────
    function bindNav() {
        document.querySelectorAll(".nav-item[data-view]").forEach(item => {
            item.addEventListener("click", () => {
                document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
                item.classList.add("active");
                switchView(item.dataset.view);
            });
        });
    }

    function switchView(view) {
        STATE.currentView = view;
        ["calendarView", "analyticsView", "planView", "profileView"].forEach(id => $(id).classList.add("hidden"));

        if (view === "calendar") {
            $("calendarView").classList.remove("hidden");
            $("pageTitle").textContent = "Training Calendar";
        } else if (view === "analytics") {
            $("analyticsView").classList.remove("hidden");
            $("pageTitle").textContent = "Performance Analytics";
            renderAnalytics();
        } else if (view === "plan") {
            $("planView").classList.remove("hidden");
            $("pageTitle").textContent = "Training Plan Overview";
            renderPlanView();
        } else if (view === "profile") {
            $("profileView").classList.remove("hidden");
            $("pageTitle").textContent = "Athlete Profile";
            renderProfile();
        }
        closeMobileMenu();
    }

    // ── Calendar Controls ────────────────────────────────────────
    function bindCalendarControls() {
        $("calPrev").addEventListener("click", () => { STATE.viewMonth--; if (STATE.viewMonth < 0) { STATE.viewMonth = 11; STATE.viewYear--; } renderCalendar(); });
        $("calNext").addEventListener("click", () => { STATE.viewMonth++; if (STATE.viewMonth > 11) { STATE.viewMonth = 0; STATE.viewYear++; } renderCalendar(); });
        $("calToday").addEventListener("click", () => { const t = new Date(); STATE.viewMonth = t.getMonth(); STATE.viewYear = t.getFullYear(); renderCalendar(); });
        $("viewMonth").addEventListener("click", () => { STATE.viewMode = "month"; $("viewMonth").classList.add("active"); $("viewWeek").classList.remove("active"); renderCalendar(); });
        $("viewWeek").addEventListener("click", () => { STATE.viewMode = "week"; $("viewWeek").classList.add("active"); $("viewMonth").classList.remove("active"); renderCalendar(); });
    }

    // ── Panels ───────────────────────────────────────────────────
    function bindPanels() {
        $("detailClose").addEventListener("click", closeDetail);
    }

    // ── Library ──────────────────────────────────────────────────
    function bindLibrary() {
        $("navLibrary").addEventListener("click", () => toggleLibrary());
        $("libraryClose").addEventListener("click", () => toggleLibrary(false));
        renderLibraryContent();
    }

    function toggleLibrary(force) {
        STATE.libraryOpen = force !== undefined ? force : !STATE.libraryOpen;
        $("libraryPanel").classList.toggle("open", STATE.libraryOpen);
    }

    function renderLibraryContent() {
        const groups = {};
        for (const item of TrainingData.WORKOUT_LIBRARY) {
            const g = item.sport; if (!groups[g]) groups[g] = [];
            groups[g].push(item);
        }
        let html = "";
        for (const [sport, items] of Object.entries(groups)) {
            const icon = TrainingData.SPORT_ICONS[sport] || "";
            html += `<div class="library-section"><div class="library-section-title">${icon} ${sport}</div>`;
            for (const item of items) {
                html += `<div class="library-item" draggable="true" data-lib-id="${item.id}">
        <span class="lib-icon">${icon}</span><span class="lib-name">${item.desc}</span><span class="lib-dur">${item.duration}m</span></div>`;
            }
            html += "</div>";
        }
        $("libraryContent").innerHTML = html;

        document.querySelectorAll(".library-item[draggable]").forEach(el => {
            el.addEventListener("dragstart", e => {
                e.dataTransfer.setData("text/plain", JSON.stringify({ type: "library", libId: el.dataset.libId }));
            });
        });
    }

    // ── Builder ──────────────────────────────────────────────────
    function bindBuilder() {
        $("navBuilder").addEventListener("click", () => { $("builderModal").classList.add("open"); $("builderDate").value = TrainingData.formatDate(new Date()); });
        $("builderClose").addEventListener("click", () => $("builderModal").classList.remove("open"));
        $("builderCancel").addEventListener("click", () => $("builderModal").classList.remove("open"));
        $("builderModal").addEventListener("click", e => { if (e.target === $("builderModal")) $("builderModal").classList.remove("open"); });

        $("addSegmentBtn").addEventListener("click", () => {
            const seg = document.createElement("div");
            seg.className = "builder-segment";
            seg.innerHTML = `<input type="text" placeholder="Segment name"><input type="number" placeholder="Min" value="10" min="0"><select><option>Z1</option><option>Z2</option><option>Z3</option><option>Z4</option><option>Z5</option></select><button class="remove-segment">✕</button>`;
            $("builderSegments").appendChild(seg);
            seg.querySelector(".remove-segment").addEventListener("click", () => seg.remove());
        });

        document.querySelectorAll(".remove-segment").forEach(btn => btn.addEventListener("click", () => btn.closest(".builder-segment").remove()));

        $("builderSave").addEventListener("click", () => {
            const sport = $("builderSport").value;
            const desc = $("builderDesc").value || "Custom Workout";
            const date = $("builderDate").value;
            const dur = parseInt($("builderDuration").value) || 45;
            const intensity = $("builderIntensity").value;
            const notes = $("builderNotes").value;
            if (!date) return;

            const segments = [];
            $("builderSegments").querySelectorAll(".builder-segment").forEach(seg => {
                const inputs = seg.querySelectorAll("input");
                const select = seg.querySelector("select");
                segments.push({ name: inputs[0].value, duration: parseInt(inputs[1].value) || 0, zone: select.value });
            });

            const warmup = segments[0] ? segments[0].name : "";
            const main = segments.slice(1, -1).map(s => s.name).join(" | ") || desc;
            const cooldown = segments.length > 1 ? segments[segments.length - 1].name : "";
            const tss = Math.round(dur * (intensity === "easy" ? 0.6 : intensity === "tempo" ? 0.9 : 1.1));

            STATE.workouts.push({
                id: "w-custom-" + Date.now(), date, sport, type: intensity, duration: dur,
                intensity, desc, warmup, main, cooldown, purpose: notes, zones: "", rpe: "",
                tssPlanned: tss, tssActual: null, phase: TrainingData.getCurrentPhase(STATE.workouts),
                phaseColor: "", weekNumber: 0, isDeload: false, status: "planned",
                actualDuration: null, actualHR: null, rpeActual: null, notes: "", bookmarked: false,
            });

            saveWorkouts(); renderCalendar();
            $("builderModal").classList.remove("open");
        });
    }

    // ── Analytics View ───────────────────────────────────────────
    function renderAnalytics() {
        const cg = $("chartsGrid");
        cg.innerHTML = `
    <div class="chart-card"><div class="chart-title">📈 Fitness / Fatigue / Form (CTL·ATL·TSB)</div><div class="chart-container"><canvas id="tsbCanvas"></canvas></div></div>
    <div class="chart-card"><div class="chart-title">📊 Weekly Volume (hours)</div><div class="chart-container"><canvas id="volumeCanvas"></canvas></div></div>
    <div class="chart-card"><div class="chart-title">🎯 Intensity Distribution</div><div id="zoneChart" class="zone-chart"></div></div>
    <div class="chart-card"><div class="chart-title">🏊🚴🏃 Sport Breakdown</div><div id="sportBreakdown"></div></div>`;

        requestAnimationFrame(() => { drawTSBChart(); drawVolumeChart(); drawZoneChart(); drawSportBreakdown(); });
    }

    function drawTSBChart() {
        const canvas = $("tsbCanvas"); if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width * 2; canvas.height = rect.height * 2;
        ctx.scale(2, 2);
        const W = rect.width, H = rect.height;
        const m = STATE.metrics; if (!m.length) return;

        const maxCTL = Math.max(...m.map(x => x.ctl), 1);
        const minTSB = Math.min(...m.map(x => x.tsb), -1);
        const maxTSB = Math.max(...m.map(x => x.tsb), 1);
        const range = Math.max(maxCTL, Math.abs(minTSB), maxTSB);

        ctx.clearRect(0, 0, W, H);

        // Zero line
        const zeroY = H * 0.5;
        ctx.strokeStyle = "rgba(255,255,255,0.1)"; ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]); ctx.beginPath(); ctx.moveTo(0, zeroY); ctx.lineTo(W, zeroY); ctx.stroke(); ctx.setLineDash([]);

        const drawLine = (data, color) => {
            ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath();
            data.forEach((v, i) => {
                const x = (i / (data.length - 1)) * W;
                const y = H / 2 - (v / range) * (H / 2 - 20);
                i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            });
            ctx.stroke();
        };

        drawLine(m.map(x => x.ctl), "#60a5fa");
        drawLine(m.map(x => x.atl), "#fb923c");
        drawLine(m.map(x => x.tsb), "#34d399");

        // Legend
        ctx.font = "11px Inter"; ctx.fillStyle = "#60a5fa"; ctx.fillText("CTL", 10, 16);
        ctx.fillStyle = "#fb923c"; ctx.fillText("ATL", 50, 16);
        ctx.fillStyle = "#34d399"; ctx.fillText("TSB", 90, 16);
    }

    function drawVolumeChart() {
        const canvas = $("volumeCanvas"); if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width * 2; canvas.height = rect.height * 2;
        ctx.scale(2, 2);
        const W = rect.width, H = rect.height;
        const weeks = TrainingData.calculateWeeklyVolume(STATE.workouts);
        if (!weeks.length) return;

        const maxTotal = Math.max(...weeks.map(w => w.total), 1);
        const barW = Math.max(4, (W - 40) / weeks.length - 2);
        const colors = { swim: "#0984E3", bike: "#00B894", run: "#E17055", strength: "#6C5CE7" };

        weeks.forEach((w, i) => {
            const x = 20 + i * (barW + 2);
            let y = H - 25;
            for (const sport of ["swim", "bike", "run", "strength"]) {
                const h = (w[sport] / maxTotal) * (H - 40);
                ctx.fillStyle = colors[sport] || "#636E72";
                ctx.fillRect(x, y - h, barW, h);
                y -= h;
            }
            if (i % 4 === 0) { ctx.fillStyle = "rgba(255,255,255,0.3)"; ctx.font = "9px Inter"; ctx.fillText("W" + w.week, x, H - 8); }
        });

        ctx.font = "10px Inter";
        Object.entries(colors).forEach(([s, c], i) => { ctx.fillStyle = c; ctx.fillText(s, 10 + i * 55, 14); });
    }

    function drawZoneChart() {
        const el = $("zoneChart"); if (!el) return;
        const w = STATE.workouts.filter(x => x.status === "completed" || x.status === "modified");
        const zones = { easy: 0, tempo: 0, threshold: 0, intervals: 0 };
        w.forEach(x => { if (zones.hasOwnProperty(x.intensity)) zones[x.intensity] += (x.actualDuration || x.duration); });
        const total = Object.values(zones).reduce((a, b) => a + b, 0) || 1;
        const colors = { easy: "#00B894", tempo: "#0984E3", threshold: "#E17055", intervals: "#D63031" };

        el.innerHTML = `<div class="zone-bar-container">${Object.entries(zones).map(([z, v]) => {
            const pct = Math.round(v / total * 100);
            return `<div class="zone-row"><div class="zone-label">${z}</div><div class="zone-bar-track"><div class="zone-bar-fill" style="width:${pct}%;background:${colors[z]}"></div></div><div class="zone-pct">${pct}%</div></div>`;
        }).join("")}</div>`;
    }

    function drawSportBreakdown() {
        const el = $("sportBreakdown"); if (!el) return;
        const w = STATE.workouts.filter(x => x.status === "completed" || x.status === "modified");
        const sports = {};
        w.forEach(x => { sports[x.sport] = (sports[x.sport] || 0) + (x.actualDuration || x.duration); });
        const total = Object.values(sports).reduce((a, b) => a + b, 0) || 1;

        el.innerHTML = `<div style="padding:var(--space-md)"><div class="zone-bar-container">${Object.entries(sports).sort((a, b) => b[1] - a[1]).map(([s, v]) => {
            const pct = Math.round(v / total * 100);
            const c = TrainingData.SPORT_COLORS[s] || "#636E72";
            const icon = TrainingData.SPORT_ICONS[s] || "";
            return `<div class="zone-row"><div class="zone-label">${icon} ${s}</div><div class="zone-bar-track"><div class="zone-bar-fill" style="width:${pct}%;background:${c}"></div></div><div class="zone-pct">${pct}%</div></div>`;
        }).join("")}</div></div>`;
    }

    // ── Plan View ────────────────────────────────────────────────
    function renderPlanView() {
        const phases = TrainingData.PHASES;
        let weekNum = 1;
        let html = '<div class="mb-lg" style="font-size:0.85rem;color:var(--text-secondary)">Science-based 30-week periodized plan · 80/20 polarized training · Progressive overload with deload weeks</div>';

        phases.forEach(p => {
            html += `<div class="glass-card mb-md">
      <div class="flex items-center justify-between mb-md">
        <div><div style="font-size:1rem;font-weight:700;color:${p.color}">${p.name}</div>
        <div style="font-size:0.75rem;color:var(--text-muted)">${p.desc}</div></div>
        <div style="font-size:0.75rem;color:var(--text-muted)">${p.weeks} weeks (W${weekNum}–W${weekNum + p.weeks - 1})</div>
      </div>`;

            const template = TrainingData.WORKOUT_LIBRARY; // Show sample sessions
            const phaseWorkouts = STATE.workouts.filter(w => w.phase === p.name);
            const weekWorkouts = phaseWorkouts.filter(w => w.weekNumber === weekNum);

            if (weekWorkouts.length) {
                html += `<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;color:var(--text-muted);margin-bottom:var(--space-sm)">Sample Week (W${weekNum})</div>`;
                DAYS.forEach((day, i) => {
                    const dayW = weekWorkouts.filter(w => new Date(w.date + "T00:00:00").getDay() === (i === 6 ? 0 : i + 1));
                    if (dayW.length) {
                        html += `<div style="margin-bottom:var(--space-xs);display:flex;gap:var(--space-sm);align-items:flex-start">
            <div style="min-width:35px;font-size:0.7rem;font-weight:600;color:var(--text-muted);padding-top:3px">${day}</div>
            <div style="flex:1;display:flex;flex-wrap:wrap;gap:4px">`;
                        dayW.forEach(w => {
                            html += `<div class="workout-pill" data-sport="${w.sport}" data-id="${w.id}" style="cursor:pointer">
              <span class="pill-icon">${TrainingData.SPORT_ICONS[w.sport] || ""}</span>
              <span class="pill-text">${w.desc}</span>
              <span class="pill-dur">${w.duration}m</span></div>`;
                        });
                        html += `</div></div>`;
                    }
                });
            }
            html += "</div>";
            weekNum += p.weeks;
        });

        $("planContent").innerHTML = html;
        $("planContent").querySelectorAll(".workout-pill").forEach(p => p.addEventListener("click", () => openDetail(p.dataset.id)));
    }

    // ── Profile View ─────────────────────────────────────────────
    function renderProfile() {
        const a = TrainingData.ATHLETE;
        const zones = [1, 2, 3, 4, 5].map(z => TrainingData.getHRZone(z));
        $("profileContent").innerHTML = `
    <div class="glass-card mb-lg">
      <div class="flex items-center gap-md mb-md">
        <div class="athlete-avatar" style="width:56px;height:56px;font-size:1.5rem">${a.name[0]}</div>
        <div><div style="font-size:1.25rem;font-weight:700">${a.name}</div><div class="text-muted">${a.goal}</div></div>
      </div>
      <div class="detail-metrics" style="grid-template-columns:repeat(4,1fr)">
        <div class="detail-metric"><div class="detail-metric-label">Age</div><div class="detail-metric-value">${a.age}</div></div>
        <div class="detail-metric"><div class="detail-metric-label">Weight</div><div class="detail-metric-value">${a.weightKg}kg</div></div>
        <div class="detail-metric"><div class="detail-metric-label">Height</div><div class="detail-metric-value">${a.heightCm}cm</div></div>
        <div class="detail-metric"><div class="detail-metric-label">Body Fat</div><div class="detail-metric-value">${a.bodyFatPct}%</div></div>
      </div>
    </div>
    <div class="glass-card mb-lg">
      <div style="font-size:0.9rem;font-weight:700;margin-bottom:var(--space-md)">Current Baselines</div>
      <div class="detail-metrics" style="grid-template-columns:repeat(3,1fr)">
        <div class="detail-metric"><div class="detail-metric-label">5K PB</div><div class="detail-metric-value">${a.fiveKPB}</div></div>
        <div class="detail-metric"><div class="detail-metric-label">5K Pace</div><div class="detail-metric-value">${a.fiveKPace}/km</div></div>
        <div class="detail-metric"><div class="detail-metric-label">Cycling</div><div class="detail-metric-value">${a.cyclingRange}km/h</div></div>
        <div class="detail-metric"><div class="detail-metric-label">Swim Level</div><div class="detail-metric-value">${a.swimLevel}/10</div></div>
        <div class="detail-metric"><div class="detail-metric-label">Max HR</div><div class="detail-metric-value">${a.maxHR}</div></div>
        <div class="detail-metric"><div class="detail-metric-label">Rest HR</div><div class="detail-metric-value">${a.restingHR}</div></div>
      </div>
    </div>
    <div class="glass-card">
      <div style="font-size:0.9rem;font-weight:700;margin-bottom:var(--space-md)">Heart Rate Zones (Karvonen)</div>
      <div class="zone-bar-container">
        ${zones.map(z => `<div class="zone-row"><div class="zone-label" style="min-width:90px"><span style="color:${z.color}">Z${Object.keys(TrainingData.HR_ZONES).find(k => TrainingData.HR_ZONES[k].name === z.name)}</span> ${z.name}</div><div class="zone-bar-track"><div class="zone-bar-fill" style="width:100%;background:${z.color};opacity:0.3"></div></div><div class="zone-pct" style="min-width:80px">${z.low}–${z.high} bpm</div></div>`).join("")}
      </div>
    </div>`;
    }

    // ── Mobile Menu ──────────────────────────────────────────────
    function bindMobileMenu() {
        $("hamburgerBtn").addEventListener("click", () => {
            $("sidebar").classList.toggle("open");
            $("sidebarOverlay").classList.toggle("open");
        });
        $("sidebarOverlay").addEventListener("click", closeMobileMenu);
    }

    function closeMobileMenu() {
        $("sidebar").classList.remove("open");
        $("sidebarOverlay").classList.remove("open");
    }

    // ── Boot ─────────────────────────────────────────────────────
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();

})();
