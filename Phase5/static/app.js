document.addEventListener("DOMContentLoaded", () => {
    // Navigation State
    let currentView = "dashboard";
    
    // Initial Load
    init();

    // Setup Login and Register forms
    window.toggleAuthMode = function(mode) {
        document.getElementById('auth-error').style.display = 'none';
        if (mode === 'register') {
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('register-form').style.display = 'block';
            document.getElementById('auth-title').innerText = 'Create Account';
            document.getElementById('auth-subtitle').innerText = 'Join TripManager Pro';
        } else {
            document.getElementById('register-form').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
            document.getElementById('auth-title').innerText = 'TripManager Pro';
            document.getElementById('auth-subtitle').innerText = 'Please enter your credentials';
        }
    };

    function showAuthError(msg) {
        const errDiv = document.getElementById('auth-error');
        errDiv.innerText = msg;
        errDiv.style.display = 'block';
    }

    window.doLogin = async function() {
        const username = document.getElementById('login-user').value.trim();
        const password = document.getElementById('login-pass').value.trim();
        
        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            
            if (!res.ok) {
                showAuthError(data.error || 'Login failed');
                return;
            }
            
            // Login success
            setupSidebarUser(data.user.username, data.user.role);
            document.getElementById('login-overlay').style.display = 'none';
            document.getElementById('app-shell').style.display = 'flex';
        } catch (e) {
            showAuthError('Connection error');
        }
    };

    window.doRegister = async function() {
        const username = document.getElementById('reg-user').value.trim();
        const password = document.getElementById('reg-pass').value.trim();
        
        try {
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            
            if (!res.ok) {
                showAuthError(data.error || 'Registration failed');
                return;
            }
            
            // Registration success, log them in automatically
            document.getElementById('login-user').value = username;
            document.getElementById('login-pass').value = password;
            doLogin();
        } catch (e) {
            showAuthError('Connection error');
        }
    };

    function setupSidebarUser(username, role) {
        const nameEl = document.getElementById('admin-name');
        const roleEl = document.getElementById('admin-role');
        const avatarEl = document.getElementById('admin-avatar');
        
        if (nameEl) nameEl.textContent = username;
        if (roleEl) roleEl.textContent = role;
        
        if (avatarEl) {
            const parts = username.split(' ');
            let initials = '';
            if (parts.length >= 2) {
                initials = (parts[0][0] + parts[parts.length-1][0]).toUpperCase();
            } else {
                initials = username.substring(0, 2).toUpperCase();
            }
            avatarEl.textContent = initials;
        }
    }

    // Form Validation shake handler
    document.querySelectorAll('form').forEach(form => {
        const submitBtn = form.querySelector('button[onclick^="save"]');
        if (submitBtn) {
            submitBtn.addEventListener('click', (e) => {
                if (!form.checkValidity()) {
                    // Find invalid fields
                    form.querySelectorAll(':invalid').forEach(field => {
                        field.classList.remove('shake');
                        void field.offsetWidth; // trigger reflow
                        field.classList.add('shake');
                    });
                }
            });
        }
    });

    // ----------------- Event Listeners -----------------

    // Navigation Menu Clicks
    document.querySelectorAll(".nav-menu .nav-item").forEach(item => {
        item.addEventListener("click", (e) => {
            const targetView = item.getAttribute("data-view");
            switchView(targetView);
        });
    });

    // Dashboard Quick Links
    document.addEventListener("click", (e) => {
        if (e.target.classList.contains("block-link")) {
            const linkView = e.target.getAttribute("data-link");
            if (linkView) {
                switchView(linkView);
            }
        }
    });

    // DB Settings Modal
    document.getElementById("db-settings-btn").addEventListener("click", () => {
        openDbSettingsModal();
    });

    // Quick Create Modal
    document.getElementById("quick-create-btn").addEventListener("click", () => {
        openModal("quick-create-modal");
    });

    // Advanced Panel Queries
    document.getElementById("run-query-btn").addEventListener("click", () => {
        runCustomQuery();
    });

    document.getElementById("run-fn-cost-btn").addEventListener("click", () => {
        runCalculateCost();
    });

    document.getElementById("run-fn-region-btn").addEventListener("click", () => {
        runTripsByRegion();
    });

    document.getElementById("run-pr-age-btn").addEventListener("click", () => {
        callProcedureAge();
    });

    document.getElementById("run-pr-vip-btn").addEventListener("click", () => {
        callProcedureVip();
    });
});

// ----------------- Core Initialization & Routing -----------------

function init() {
    // Default load dashboard
    switchView("dashboard");
    loadSettingsFromBackend();
    loadQueriesDropdown();
}

function switchView(viewName) {
    // Update active nav item
    document.querySelectorAll(".nav-menu .nav-item").forEach(item => {
        if (item.getAttribute("data-view") === viewName) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });

    // Hide all views, show target view
    document.querySelectorAll(".page-view").forEach(view => {
        view.classList.remove("active");
    });
    
    const targetElement = document.getElementById(`view-${viewName}`);
    if (targetElement) {
        targetElement.classList.add("active");
    }

    currentView = viewName;

    // Load data specific to that view
    refreshViewData(viewName);
}

function refreshViewData(viewName) {
    switch (viewName) {
        case "dashboard":
            loadDashboard();
            break;
        case "trips":
            loadTrips();
            break;
        case "groups":
            loadGroups();
            break;
        case "guides":
            loadGuides();
            break;
        case "participants":
            loadParticipants();
            break;
        case "events":
            loadEvents();
            break;
        case "locations":
            loadLocations();
            break;
        case "advanced":
            loadAdvancedHelpers();
            break;
    }
}

// ----------------- Modal Controls -----------------

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("active");
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
    }
}

// ----------------- DB Configuration -----------------

function openDbSettingsModal() {
    openModal("db-settings-modal");
}

function loadSettingsFromBackend() {
    fetch("/api/config")
        .then(res => res.json())
        .then(config => {
            const form = document.getElementById("db-settings-form");
            form.db_host.value = config.db_host;
            form.db_port.value = config.db_port;
            form.db_name.value = config.db_name;
            form.db_user.value = config.db_user;
            form.db_password.value = config.db_password;
        })
        .catch(err => console.error("Error loading config:", err));
}

function testDbConnection() {
    const form = document.getElementById("db-settings-form");
    const data = {
        db_host: form.db_host.value,
        db_port: form.db_port.value,
        db_name: form.db_name.value,
        db_user: form.db_user.value,
        db_password: form.db_password.value
    };

    fetch("/api/db-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            alert("SUCCESS: Connection successful!");
        } else {
            alert("ERROR: Connection failed:\n" + result.message);
        }
    })
    .catch(err => alert("ERROR: System request failed. Details: " + err));
}

function saveDbSettings() {
    const form = document.getElementById("db-settings-form");
    const data = {
        db_host: form.db_host.value,
        db_port: form.db_port.value,
        db_name: form.db_name.value,
        db_user: form.db_user.value,
        db_password: form.db_password.value
    };

    fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        if (result.status === "success") {
            alert("Settings saved successfully.");
            closeModal("db-settings-modal");
            refreshViewData(currentView);
        } else {
            alert("Error saving settings: " + result.message);
        }
    })
    .catch(err => alert("Error communicating with server: " + err));
}

// ----------------- Form Helper Populators -----------------

// Populate dropdown elements with names from parent tables instead of ID typing
function loadFormHelpers(entityType) {
    if (entityType === "trip") {
        // Load guides, routes, transport-types
        fetchHelperList("guides", "trip-guide-select");
        fetchHelperList("routes", "trip-route-select");
        fetchHelperList("transport-types", "trip-transport-select");
    } else if (entityType === "group") {
        fetchHelperList("guides", "group-guide-select");
    } else if (entityType === "event") {
        fetchHelperList("trips", "event-trip-select");
        fetchHelperList("poi", "event-location-select");
    } else if (entityType === "location") {
        // Regions are statically defined in index.html, no need to fetch dynamically.
    }
}

function fetchHelperList(helperName, selectElementId) {
    const select = document.getElementById(selectElementId);
    if (!select) return;

    fetch(`/api/helpers/${helperName}`)
        .then(res => res.json())
        .then(data => {
            // Keep the first default option
            const defaultOpt = select.options[0];
            select.innerHTML = "";
            select.appendChild(defaultOpt);
            
            data.forEach(item => {
                const opt = document.createElement("option");
                opt.value = item.id;
                opt.textContent = `${item.name} (${item.id})`;
                select.appendChild(opt);
            });
        })
        .catch(err => console.error(`Error loading helpers for ${helperName}:`, err));
}

// ----------------- Dashboard Loader -----------------

function loadDashboard() {
    // Stats
    fetch("/api/stats")
        .then(res => res.json())
        .then(stats => {
            document.getElementById("stat-trips").textContent = stats.trip || 0;
            document.getElementById("stat-group").textContent = stats.group || 0;
            document.getElementById("stat-guide").textContent = stats.guide || 0;
            document.getElementById("stat-participant").textContent = stats.participant || 0;
            document.getElementById("stat-event").textContent = stats.event || 0;
        })
        .catch(err => console.error("Error loading stats:", err));

    // Upcoming Trips List
    fetch("/api/upcoming-trips")
        .then(res => res.json())
        .then(trips => {
            const list = document.getElementById("upcoming-trips-list");
            list.innerHTML = "";
            
            if (trips.length === 0) {
                list.innerHTML = "<p class='color-text-muted'>No upcoming trips scheduled.</p>";
                return;
            }
            
            trips.forEach(trip => {
                const item = document.createElement("div");
                item.className = "trip-list-item";
                
                // Set badge class based on status
                let statusClass = "badge-neutral";
                if (trip.status === "Upcoming") statusClass = "badge-warning";
                else if (trip.status === "Ongoing") statusClass = "badge-success";
                else if (trip.status === "Completed") statusClass = "badge-neutral";
                else if (trip.status === "Adults Only") statusClass = "badge-danger";

                item.innerHTML = `
                    <div class="trip-item-info">
                        <div class="trip-item-image">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
                        </div>
                        <div class="trip-item-text">
                            <h4 onclick="showDetails('trips', ${trip.tripid})">${trip.tripname}</h4>
                            <div class="trip-item-meta">
                                <span>
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect></svg>
                                    ${formatDate(trip.startdate)}
                                </span>
                                <span>
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path></svg>
                                    Guide: ${trip.guidename || 'Unassigned'}
                                </span>
                                <span>
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon></svg>
                                    Route: ${trip.route_name || 'N/A'}
                                </span>
                            </div>
                        </div>
                    </div>
                    <span class="badge ${statusClass}">${trip.status || 'Upcoming'}</span>
                `;
                list.appendChild(item);
            });
        })
        .catch(err => console.error("Error loading upcoming trips:", err));

    // Guides by Region Distribution
    fetch("/api/guides-by-region")
        .then(res => res.json())
        .then(data => {
            const grid = document.getElementById("guides-by-region-list");
            grid.innerHTML = "";
            
            if (data.length === 0) {
                grid.innerHTML = "<p class='color-text-muted'>No regional guides data.</p>";
                return;
            }
            
            data.slice(0, 4).forEach(item => {
                const box = document.createElement("div");
                box.className = "region-box";
                box.innerHTML = `
                    <div class="region-name">${item.region}</div>
                    <div class="region-count">${item.count}</div>
                `;
                grid.appendChild(box);
            });
        })
        .catch(err => console.error("Error loading guides by region:", err));

    // Timeline Events
    fetch("/api/recent-events")
        .then(res => res.json())
        .then(events => {
            const timeline = document.getElementById("recent-events-timeline");
            timeline.innerHTML = "";
            
            if (events.length === 0) {
                timeline.innerHTML = "<p class='color-text-muted'>No scheduled events found.</p>";
                return;
            }
            
            events.forEach(event => {
                const timeStr = event.start_hour ? event.start_hour.substring(0, 5) : (event.eventtime ? event.eventtime.substring(0, 5) : '00:00');
                const item = document.createElement("div");
                item.className = "timeline-item active";
                item.innerHTML = `
                    <div class="timeline-time">${formatDate(event.eventdate)} @ ${timeStr}</div>
                    <div class="timeline-title">${event.eventname}</div>
                    <div class="timeline-desc">Location: ${event.locationname || 'N/A'} | Trip: ${event.tripname}</div>
                `;
                timeline.appendChild(item);
            });
        })
        .catch(err => console.error("Error loading events timeline:", err));
}

// ----------------- CRUD Entity Pages Loader -----------------

// 1. TRIPS
function loadTrips() {
    fetch("/api/trips")
        .then(res => res.json())
        .then(trips => {
            const grid = document.getElementById("trips-grid");
            grid.innerHTML = "";
            
            trips.forEach(trip => {
                let statusClass = "badge-neutral";
                if (trip.status === "Upcoming") statusClass = "badge-warning";
                else if (trip.status === "Ongoing") statusClass = "badge-success";
                else if (trip.status === "Completed") statusClass = "badge-neutral";
                else if (trip.status === "Adults Only") statusClass = "badge-danger";

                const card = document.createElement("div");
                card.className = "catalog-card";
                card.innerHTML = `
                    <div class="card-image-section" style="background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.8)), url('https://picsum.photos/seed/${trip.tripid}/400/200'); background-size: cover; background-position: center;">
                        <span class="badge ${statusClass} card-badge">${trip.status || 'Upcoming'}</span>
                        <h3 style="z-index: 2; position: absolute; bottom: 16px; left: 16px; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">${trip.tripname}</h3>
                    </div>
                    <div class="card-content">
                        <div class="card-title" style="margin-bottom: 8px; font-size:13px; color: var(--color-text-muted); font-family: var(--font-mono)">ID: ${trip.tripid}</div>
                        <div class="card-details">
                            <div class="card-detail-item">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect></svg>
                                <span>${formatDate(trip.startdate)} &rarr; ${formatDate(trip.enddate)}</span>
                            </div>
                            <div class="card-detail-item">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path></svg>
                                <span>Guide: <strong>${trip.guidename || 'Unassigned'}</strong></span>
                            </div>
                            <div class="card-detail-item">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon></svg>
                                <span>Route: ${trip.route_name || 'N/A'}</span>
                            </div>
                            <div class="card-detail-item">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"></circle><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path></svg>
                                <span>Max Size: ${trip.groupsize || 'N/A'} | Class: ${trip.triptype || 'Regular'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <a class="block-link" onclick="showDetails('trips', ${trip.tripid})">Details &rarr;</a>
                        <div class="table-actions">
                            <button class="action-icon-btn edit-btn" onclick="openEditModal('trip', ${trip.tripid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button class="action-icon-btn delete-btn" onclick="deleteEntity('trips', ${trip.tripid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        })
        .catch(err => console.error("Error loading trips:", err));
}

// 2. GROUPS
function loadGroups() {
    fetch("/api/groups")
        .then(res => res.json())
        .then(groups => {
            const tbody = document.getElementById("groups-table-body");
            tbody.innerHTML = "";
            
            groups.forEach(group => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><span class="id-text">${group.groupid}</span></td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 32px; height: 32px; border-radius: 6px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                                ${group.groupname.substring(0, 2).toUpperCase()}
                            </div>
                            <strong onclick="showDetails('groups', ${group.groupid})" style="color:var(--color-accent); cursor:pointer;">${group.groupname}</strong>
                        </div>
                    </td>
                    <td>${group.guidename || 'Unassigned'}</td>
                    <td class="font-mono">${formatDate(group.createddate)}</td>
                    <td>
                        <div class="table-actions">
                            <button class="action-icon-btn edit-btn" onclick="openEditModal('group', ${group.groupid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button class="action-icon-btn delete-btn" onclick="deleteEntity('groups', ${group.groupid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading groups:", err));
}

// 3. GUIDES
function loadGuides() {
    fetch("/api/guides")
        .then(res => res.json())
        .then(guides => {
            const tbody = document.getElementById("guides-table-body");
            tbody.innerHTML = "";
            
            guides.forEach(guide => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><span class="id-text">${guide.guideid}</span></td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="https://ui-avatars.com/api/?name=${guide.guidename}&background=0f172a&color=34d399&rounded=true&size=32" style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid #34d399;">
                            <strong onclick="showDetails('guides', ${guide.guideid})" style="color:var(--color-accent); cursor:pointer;">${guide.guidename}</strong>
                        </div>
                    </td>
                    <td><span class="badge badge-info">${guide.specialization || 'General'}</span></td>
                    <td>${guide.region || 'N/A'}</td>
                    <td>${guide.experienceyears || 0} yrs</td>
                    <td class="font-mono">${guide.license_number || 'N/A'}</td>
                    <td>
                        <div style="font-size: 11px;">
                            <div>📞 ${guide.phone || 'N/A'}</div>
                            <div>✉️ ${guide.email || 'N/A'}</div>
                        </div>
                    </td>
                    <td>
                        <div class="table-actions">
                            <button class="action-icon-btn edit-btn" onclick="openEditModal('guide', ${guide.guideid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button class="action-icon-btn delete-btn" onclick="deleteEntity('guides', ${guide.guideid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading guides:", err));
}

// 4. PARTICIPANTS
function loadParticipants() {
    fetch("/api/participants")
        .then(res => res.json())
        .then(participants => {
            const tbody = document.getElementById("participants-table-body");
            tbody.innerHTML = "";
            
            participants.forEach(p => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><span class="id-text">${p.participantid}</span></td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="https://ui-avatars.com/api/?name=${p.firstname}+${p.lastname}&background=random&color=fff&size=32" style="width: 32px; height: 32px; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                            <strong onclick="showDetails('participants', ${p.participantid})" style="color:var(--color-accent); cursor:pointer;">${p.firstname}</strong>
                        </div>
                    </td>
                    <td>${p.lastname}</td>
                    <td>${p.age || 'N/A'}</td>
                    <td class="font-mono">${formatDate(p.birthdate)}</td>
                    <td>${p.phone || 'N/A'}</td>
                    <td>${p.email || 'N/A'}</td>
                    <td>
                        <div class="table-actions">
                            <button class="action-icon-btn edit-btn" onclick="openEditModal('participant', ${p.participantid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button class="action-icon-btn delete-btn" onclick="deleteEntity('participants', ${p.participantid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading participants:", err));
}

// 5. EVENTS
function loadEvents() {
    fetch("/api/events")
        .then(res => res.json())
        .then(events => {
            const tbody = document.getElementById("events-table-body");
            tbody.innerHTML = "";
            
            events.forEach(e => {
                const tr = document.createElement("tr");
                const timeStr = e.start_hour ? e.start_hour.substring(0, 5) : (e.eventtime ? e.eventtime.substring(0, 5) : 'N/A');
                tr.innerHTML = `
                    <td><span class="id-text">${e.eventid}</span></td>
                    <td><strong onclick="showDetails('events', ${e.eventid})" style="color:var(--color-accent); cursor:pointer;">${e.eventname}</strong></td>
                    <td>
                        <div style="font-size: 11px;">
                            <div>📅 ${formatDate(e.eventdate)}</div>
                            <div>🕒 ${timeStr}</div>
                        </div>
                    </td>
                    <td>${e.tripname || 'N/A'}</td>
                    <td>${e.locationname || 'N/A'}</td>
                    <td class="font-mono">$${e.cost || 0.0}</td>
                    <td><span class="badge badge-success">${e.status || 'Active'}</span></td>
                    <td>
                        <div class="table-actions">
                            <button class="action-icon-btn edit-btn" onclick="openEditModal('event', ${e.eventid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button class="action-icon-btn delete-btn" onclick="deleteEntity('events', ${e.eventid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading events:", err));
}

// 6. LOCATIONS
function loadLocations() {
    fetch("/api/poi")
        .then(res => res.json())
        .then(locations => {
            const tbody = document.getElementById("locations-table-body");
            tbody.innerHTML = "";
            
            locations.forEach(l => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><span class="id-text">${l.locationid}</span></td>
                    <td><strong onclick="showDetails('poi', ${l.locationid})" style="color:var(--color-accent); cursor:pointer;">${l.locationname}</strong></td>
                    <td><span class="badge badge-neutral">${l.region || 'N/A'}</span></td>
                    <td>${l.address || 'N/A'}</td>
                    <td>
                        <div class="table-actions">
                            <button class="action-icon-btn edit-btn" onclick="openEditModal('location', ${l.locationid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button class="action-icon-btn delete-btn" onclick="deleteEntity('poi', ${l.locationid})">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading locations:", err));
}

// ----------------- CRUD Action Trigger Handlers -----------------

function loadFormHelpers(entityType) {
    if (entityType === "trip") {
        fetch("/api/helpers/routes").then(res => res.json()).then(data => {
            const select = document.getElementById("trip-route-select");
            if (select) {
                select.innerHTML = '<option value="">None</option>';
                data.forEach(d => select.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            }
        }).catch(e => console.error(e));
        
        fetch("/api/helpers/transport-types").then(res => res.json()).then(data => {
            const select = document.getElementById("trip-transport-select");
            if (select) {
                select.innerHTML = '<option value="">None</option>';
                data.forEach(d => select.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            }
        }).catch(e => console.error(e));
        
        fetch("/api/helpers/guides").then(res => res.json()).then(data => {
            const select = document.getElementById("trip-guide-select");
            if (select) {
                select.innerHTML = '<option value="">None</option>';
                data.forEach(d => select.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            }
        }).catch(e => console.error(e));
    } else if (entityType === "group") {
        fetch("/api/helpers/guides").then(res => res.json()).then(data => {
            const select = document.getElementById("group-guide-select");
            if (select) {
                select.innerHTML = '<option value="">None</option>';
                data.forEach(d => select.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            }
        }).catch(e => console.error(e));
    } else if (entityType === "event") {
        fetch("/api/helpers/trips").then(res => res.json()).then(data => {
            const select = document.getElementById("event-trip-select");
            if (select) {
                select.innerHTML = '<option value="">None</option>';
                data.forEach(d => select.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            }
        }).catch(e => console.error(e));
        
        fetch("/api/helpers/poi").then(res => res.json()).then(data => {
            const select = document.getElementById("event-location-select");
            if (select) {
                select.innerHTML = '<option value="">None</option>';
                data.forEach(d => select.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            }
        }).catch(e => console.error(e));
    }
}

function openCreateModal(entityType) {
    // Load helper selects before showing
    loadFormHelpers(entityType);

    const form = document.getElementById(`${entityType}-form`);
    form.reset();
    form.is_edit.value = "false";
    
    // Enable PK field for inserts
    const pkField = form.querySelector('input[type="number"]');
    if (pkField) {
        pkField.disabled = false;
        // Generate a random ID suggestion
        pkField.value = Math.floor(10000 + Math.random() * 90000);
    }
    
    document.getElementById(`${entityType}-modal-title`).textContent = `Create New ${capitalize(entityType)}`;
    openModal(`${entityType}-modal`);
}

function openEditModal(entityType, id) {
    loadFormHelpers(entityType);

    let apiEndpoint = entityType + "s";
    if (entityType === "location") apiEndpoint = "poi";

    fetch(`/api/${apiEndpoint}/${id}`)
        .then(res => res.json())
        .then(data => {
            const form = document.getElementById(`${entityType}-form`);
            form.reset();
            form.is_edit.value = "true";
            
            // Disable PK field for updates (users fill keys first)
            const pkField = form.querySelector('input[type="number"]');
            if (pkField) {
                pkField.disabled = true;
            }

            // Prefill inputs
            for (const key in data) {
                const input = form.elements[key];
                if (input) {
                    if (input.type === "date" && data[key]) {
                        input.value = data[key].substring(0, 10);
                    } else if (input.type === "time" && data[key]) {
                        input.value = data[key].substring(0, 5);
                    } else {
                        input.value = data[key] === null ? "" : data[key];
                    }
                }
            }
            
            document.getElementById(`${entityType}-modal-title`).textContent = `Edit ${capitalize(entityType)}`;
            openModal(`${entityType}-modal`);
        })
        .catch(err => alert("Error fetching entity details: " + err));
}

function saveTrip() {
    submitEntityForm("trip", "trips");
}
function saveGroup() {
    submitEntityForm("group", "groups");
}
function saveGuide() {
    submitEntityForm("guide", "guides");
}
function saveParticipant() {
    submitEntityForm("participant", "participants");
}
function saveEvent() {
    submitEntityForm("event", "events");
}
function saveLocation() {
    submitEntityForm("location", "poi");
}

function submitEntityForm(entityType, apiEndpoint) {
    const form = document.getElementById(`${entityType}-form`);
    
    // Check validation
    if (!form.reportValidity()) return;

    const isEdit = form.is_edit.value === "true";
    const formData = new FormData(form);
    const data = {};
    
    // Read all values (even disabled elements like Primary Keys on updates)
    for (const [key, val] of formData.entries()) {
        if (key !== "is_edit") {
            data[key] = val === "" ? null : val;
        }
    }
    
    // Handle disabled primary key input value manually
    const pkField = form.querySelector('input[type="number"]');
    if (pkField && pkField.disabled) {
        data[pkField.name] = pkField.value;
    }

    const url = isEdit ? `/api/${apiEndpoint}/${data[pkField.name]}` : `/api/${apiEndpoint}`;
    const method = isEdit ? "PUT" : "POST";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            alert("Record saved successfully.");
            closeModal(`${entityType}-modal`);
            
            // If details view was open, reload it, else refresh table
            if (currentView === "details") {
                showDetails(apiEndpoint, data[pkField.name]);
            } else {
                refreshViewData(currentView);
            }
        } else {
            alert("Error: " + result.error);
        }
    })
    .catch(err => alert("Error communicating with server: " + err));
}

function deleteEntity(apiEndpoint, id) {
    if (!confirm(`Are you sure you want to delete this record (ID: ${id})?`)) return;

    fetch(`/api/${apiEndpoint}/${id}`, {
        method: "DELETE"
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            alert("Record deleted successfully.");
            if (currentView === "details") {
                // Return to parent view
                switchView(apiEndpoint);
            } else {
                refreshViewData(currentView);
            }
        } else {
            alert("Error deleting record: " + result.error);
        }
    })
    .catch(err => alert("Network error: " + err));
}

// ----------------- Split Details View -----------------

function showDetails(apiEndpoint, id) {
    fetch(`/api/${apiEndpoint}/${id}`)
        .then(res => res.json())
        .then(data => {
            // Setup navigation shell
            document.querySelectorAll(".page-view").forEach(view => {
                view.classList.remove("active");
            });
            document.getElementById("view-details").classList.add("active");
            currentView = "details";
            
            // Set Back button behavior
            const backBtn = document.getElementById("details-back-btn");
            backBtn.onclick = () => {
                switchView(apiEndpoint);
            };

            // Set Action Sidebar handlers
            const entitySingle = apiEndpoint.substring(0, apiEndpoint.length - 1);
            document.getElementById("details-edit-btn").onclick = () => {
                openEditModal(entitySingle, id);
            };
            document.getElementById("details-delete-btn").onclick = () => {
                deleteEntity(apiEndpoint, id);
            };

            // Populate Fields
            document.getElementById("details-entity-type").textContent = entitySingle.toUpperCase();
            
            let titleVal = "";
            if (data.tripname) titleVal = data.tripname;
            else if (data.groupname) titleVal = data.groupname;
            else if (data.guidename) titleVal = data.guidename;
            else if (data.firstname) titleVal = `${data.firstname} ${data.lastname || ''}`;
            else if (data.eventname) titleVal = data.eventname;
            else if (data.locationname) titleVal = data.locationname;
            
            document.getElementById("details-title").textContent = titleVal;

            const grid = document.getElementById("details-fields-grid");
            grid.innerHTML = "";

            for (const key in data) {
                const val = data[key];
                const cleanVal = (val === null || val === undefined) ? "N/A" : (key.includes("date") ? formatDate(val) : val);
                
                const box = document.createElement("div");
                box.className = "detail-item";
                box.innerHTML = `
                    <span class="detail-item-label">${key}</span>
                    <span class="detail-item-value">${cleanVal}</span>
                `;
                grid.appendChild(box);
            }

            // Set relations text info
            const relationsText = document.getElementById("details-related-text");
            relationsText.textContent = `This record has constraints and links across the PostgreSQL schema. Any updates are protected by foreign key assertions.`;
        })
        .catch(err => alert("Error loading details card: " + err));
}

// ----------------- Advanced Panel Executions -----------------

function loadAdvancedHelpers() {
    // Load trips for cost function select
    const select = document.getElementById("plsql-cost-trip-select");
    if (select) {
        fetch("/api/helpers/trips")
            .then(res => res.json())
            .then(data => {
                select.innerHTML = '<option value="">Select Trip...</option>';
                data.forEach(item => {
                    const opt = document.createElement("option");
                    opt.value = item.id;
                    opt.textContent = `${item.name} (${item.id})`;
                    select.appendChild(opt);
                });
            });
    }

    // Load regions for RefCursor function select
    const regionSelect = document.getElementById("plsql-region-input");
    if (regionSelect) {
        fetch("/api/helpers/regions")
            .then(res => res.json())
            .then(data => {
                regionSelect.innerHTML = '<option value="">Select Region...</option>';
                data.forEach(region => {
                    const opt = document.createElement("option");
                    opt.value = region;
                    opt.textContent = region;
                    regionSelect.appendChild(opt);
                });
            });
    }
}

function loadQueriesDropdown() {
    fetch("/api/queries")
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById("query-select");
            select.innerHTML = "";
            data.forEach(q => {
                const opt = document.createElement("option");
                opt.value = q.id;
                opt.textContent = `${q.id}. ${q.name}`;
                select.appendChild(opt);
            });
        })
        .catch(err => console.error("Error loading queries list:", err));
}

function clearConsole() {
    document.getElementById("console-output").innerHTML = "Console cleared. Ready for next routine execution.";
}

function writeToConsole(title, content, type = "normal", notices = []) {
    const consoleBox = document.getElementById("console-output");
    
    let typeClass = "";
    if (type === "success") typeClass = "console-success";
    if (type === "error") typeClass = "console-error";
    
    let noticeHtml = "";
    if (notices.length > 0) {
        noticeHtml = `\n<span class="console-notice">PostgreSQL Notices & RAISE Outputs:</span>\n` + 
                     notices.map(n => `  [Notice] ${n}`).join("\n") + "\n";
    }

    const logBlock = `
<span class="console-notice">--------------------------------------------------</span>
[Execution] ${new Date().toLocaleTimeString()} - <strong>${title}</strong>
${noticeHtml}
<span class="${typeClass}">Result / Output:</span>
${content}
`;
    // Append or replace
    if (consoleBox.innerHTML.includes("Ready to execute")) {
        consoleBox.innerHTML = logBlock;
    } else {
        consoleBox.innerHTML += logBlock;
    }
    
    // Auto Scroll to bottom
    consoleBox.scrollTop = consoleBox.scrollHeight;
}

function renderConsoleTable(jsonData) {
    if (!jsonData || jsonData.length === 0) {
        return "No rows returned (Empty result set).";
    }

    const columns = Object.keys(jsonData[0]);
    let tableHtml = '<table class="console-table"><thead><tr>';
    columns.forEach(col => {
        tableHtml += `<th>${col}</th>`;
    });
    tableHtml += '</tr></thead><tbody>';

    jsonData.forEach(row => {
        tableHtml += 'tr>';
        columns.forEach(col => {
            const val = row[col];
            tableHtml += `<td>${val === null ? 'NULL' : val}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</tbody></table>';
    return tableHtml;
}

// EXECUTE CUSTOM QUERIES
function runCustomQuery() {
    const select = document.getElementById("query-select");
    const queryId = select.value;
    const queryName = select.options[select.selectedIndex].textContent;

    writeToConsole(`Running Query: ${queryName}`, "Contacting server, executing SQL query...", "normal");

    fetch(`/api/queries/${queryId}`, {
        method: "POST"
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            const table = renderConsoleTable(result);
            writeToConsole(`Query Executed: ${queryName}`, table, "success");
        } else {
            writeToConsole(`Query Failed: ${queryName}`, result.error, "error");
        }
    })
    .catch(err => writeToConsole("System Error", err, "error"));
}

// EXECUTE PL/SQL: TRIP COST
function runCalculateCost() {
    const tripId = document.getElementById("plsql-cost-trip-select").value;
    if (!tripId) {
        alert("Please select a trip ID first.");
        return;
    }

    writeToConsole("PL/SQL fn_calculate_trip_total_cost", `Executing cost compilation routine for Trip ID: ${tripId}...`);

    fetch("/api/plsql/calculate-cost", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trip_id: parseInt(tripId) })
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            writeToConsole("PL/SQL Function Output", `Total Cost for Trip ${tripId}: <strong>$${result.cost}</strong>`, "success", result.notices);
        } else {
            writeToConsole("PL/SQL Function Failed", result.error, "error");
        }
    })
    .catch(err => writeToConsole("System Error", err, "error"));
}

// EXECUTE PL/SQL: TRIPS BY REGION (REF CURSOR)
function runTripsByRegion() {
    const regionName = document.getElementById("plsql-region-input").value;
    if (!regionName) {
        alert("Please select a geographic region.");
        return;
    }

    writeToConsole("PL/SQL fn_get_trips_by_region_cursor", `Opening reference cursor (Refcursor) for region: ${regionName}...`);

    fetch("/api/plsql/trips-by-region", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ region_name: regionName })
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            const table = renderConsoleTable(result.data);
            writeToConsole("PL/SQL Ref Cursor Output", table, "success", result.notices);
        } else {
            writeToConsole("PL/SQL Function Failed", result.error, "error");
        }
    })
    .catch(err => writeToConsole("System Error", err, "error"));
}

// CALL PL/SQL: UPDATE STATUS BY AGE
function callProcedureAge() {
    writeToConsole("Calling Procedure (CALL pr_update_trip_status_by_age)", "Scanning trips age averages, updating adults only status tags...");

    fetch("/api/plsql/update-status-by-age", {
        method: "POST"
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            writeToConsole("PL/SQL Procedure Success", "Completed processing and age scans.", "success", result.notices);
        } else {
            writeToConsole("PL/SQL Procedure Failed", result.error, "error");
        }
    })
    .catch(err => writeToConsole("System Error", err, "error"));
}

// CALL PL/SQL: UPDATE VIP TYPES
function callProcedureVip() {
    writeToConsole("Calling Procedure (CALL pr_update_vip_trip_type)", "Scanning trip capacity configurations, allocating VIP designations...");

    fetch("/api/plsql/update-vip-trip-type", {
        method: "POST"
    })
    .then(async res => {
        const result = await res.json();
        if (res.ok) {
            writeToConsole("PL/SQL Procedure Success", "Completed size scans and VIP status allocations.", "success", result.notices);
        } else {
            writeToConsole("PL/SQL Procedure Failed", result.error, "error");
        }
    })
    .catch(err => writeToConsole("System Error", err, "error"));
}

// ----------------- Utility helper functions -----------------

function formatDate(dateStr) {
    if (!dateStr) return "";
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return dateStr;
        return date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
    } catch (e) {
        return dateStr;
    }
}

function calculateAgeFromBirth(birthInput) {
    if (!birthInput.value) return;
    const birthDate = new Date(birthInput.value);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    const ageInput = birthInput.closest("form").elements.age;
    if (ageInput) {
        ageInput.value = age >= 0 ? age : 0;
    }
}

function filterTable(input, elementId) {
    const filter = input.value.toUpperCase();
    const target = document.getElementById(elementId);
    
    if (target.tagName === "TABLE") {
        const rows = target.getElementsByTagName("tr");
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            let found = false;
            const cells = row.getElementsByTagName("td");
            for (let j = 0; j < cells.length - 1; j++) {
                if (cells[j].textContent.toUpperCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
            row.style.display = found ? "" : "none";
        }
    } else {
        // Grid cards
        const cards = target.getElementsByClassName("catalog-card");
        for (let i = 0; i < cards.length; i++) {
            const card = cards[i];
            const text = card.textContent || card.innerText;
            card.style.display = text.toUpperCase().indexOf(filter) > -1 ? "" : "none";
        }
    }
}

function capitalize(s) {
    if (typeof s !== 'string') return '';
    return s.charAt(0).toUpperCase() + s.slice(1);
}
