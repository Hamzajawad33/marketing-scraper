// Page Navigation
let currentPage = 'home';

function navigateTo(pageName) {
    // Deactivate all pages and nav links
    document.querySelectorAll('.page-section').forEach(page => {
        page.classList.remove('active');
    });

    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Activate target page and nav link
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
        currentPage = pageName;

        // Update URL hash
        window.location.hash = pageName;

        // Update active nav link
        const activeLink = document.querySelector(`.nav-link[onclick="navigateTo('${pageName}')"]`);
        if (activeLink) {
            activeLink.classList.add('active');
            updateNavBlob(activeLink);
        }
    }
}

// Gooey Nav Blob Tracking
function updateNavBlob(activeLink) {
    const blob = document.querySelector('.nav-blob');
    if (blob && activeLink) {
        const linkRect = activeLink.getBoundingClientRect();
        const navRect = document.querySelector('.nav-menu').getBoundingClientRect();

        const left = linkRect.left - navRect.left - 20;
        blob.style.transform = `translateX(${left}px)`;
    }
}

// Initialize nav blob on page load
document.addEventListener('DOMContentLoaded', () => {
    const activeLink = document.querySelector('.nav-link.active');
    if (activeLink) {
        setTimeout(() => updateNavBlob(activeLink), 100);
    }

    // Handle URL hash navigation
    const hash = window.location.hash.substring(1);
    if (hash) {
        navigateTo(hash);
    }

    // Initialize max_results field based on license
    initializeMaxResultsField();
});

// Initialize max results field with license restrictions
function initializeMaxResultsField() {
    const maxResultsInput = document.getElementById('max_results');
    const lockIcon = document.getElementById('max-results-lock');

    if (!maxResultsInput || !lockIcon) return;

    // Get license features from window object (injected by Flask)
    const features = window.licenseFeatures || {};
    const licenseType = window.licenseType || 'unknown';
    const maxAllowed = features.max_results || 100; // Default to 100 if not set

    if (maxAllowed === -1) {
        // Unlimited license (Developer)
        maxResultsInput.max = 10000; // Set a reasonable UI limit
        lockIcon.style.display = 'none'; // Hide lock icon
        maxResultsInput.title = 'Unlimited (Developer License)';
    } else {
        // Limited license (Client or other)
        maxResultsInput.max = maxAllowed;
        lockIcon.style.display = 'inline-block'; // Show lock icon
        lockIcon.title = `Maximum: ${maxAllowed} results (${licenseType.toUpperCase()} License)`;
        maxResultsInput.title = `Maximum: ${maxAllowed} results`;
    }

    // Add input validation
    maxResultsInput.addEventListener('input', function () {
        const value = parseInt(this.value);
        const max = parseInt(this.max);

        if (value > max) {
            this.value = max;
            // Show a brief visual feedback
            this.style.borderColor = '#ef4444';
            setTimeout(() => {
                this.style.borderColor = '';
            }, 1000);
        }
    });
}


// App Logic
let isRunning = false;
let logSource = null;
let statsInterval = null;


function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('stat-total').innerText = data.total || 0;
            document.getElementById('stat-website').innerText = data.with_website || 0;
            document.getElementById('stat-phone').innerText = data.with_phone || 0;

            // New v6.0 Stats
            document.getElementById('stat-social').innerText = data.with_social || 0;
            document.getElementById('stat-pixels').innerText = data.with_pixels || 0;
            document.getElementById('stat-emails').innerText = data.with_email || 0;

            // Update Progress
            const progress = data.progress || 0;
            const progressBar = document.getElementById('progress-bar');
            if (progressBar) {
                progressBar.style.width = progress + '%';
            }
            const progressPercent = document.getElementById('progress-percent');
            if (progressPercent) {
                progressPercent.innerText = progress + '%';
            }

            // Check for completion
            if (data.status === 'Completed' || data.status === 'Error') {
                if (data.status === 'Completed') {
                    addLog('Mission Accomplished! Data exported.', 'success');
                }
                resetUI();
            }
        });
}

function resetUI() {
    document.getElementById('start-btn').disabled = false;
    document.getElementById('stop-btn').disabled = true;
    document.getElementById('status-text').innerText = 'SYSTEM READY';
    document.querySelector('.status-dot').style.backgroundColor = 'var(--accent-blue)';

    if (statsInterval) clearInterval(statsInterval);
    if (logSource) {
        logSource.close();
        logSource = null;
    }
}

function addLog(message, type) {
    const terminal = document.getElementById('terminal');
    const div = document.createElement('div');
    div.className = `log-line ${type}`;

    // Format timestamp
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { hour12: false });

    div.innerText = `[${time}] ${message}`;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize stats
    updateStats();
});

// Start Scraping Function
function startScraping() {
    const keyword = document.getElementById('keyword').value;
    const location = document.getElementById('location').value;
    const maxResults = document.getElementById('max_results').value;
    const headless = document.getElementById('headless').checked;
    const noWebsite = document.getElementById('no-website')?.checked || false;

    if (!keyword || !location) {
        addLog('Error: Keyword and Location are required', 'error');
        return;
    }

    // UI Updates
    document.getElementById('start-btn').disabled = true;
    document.getElementById('stop-btn').disabled = false;
    document.getElementById('status-text').innerText = 'MISSION ACTIVE';
    document.getElementById('status-badge').style.borderColor = 'var(--accent-green)';
    document.querySelector('.status-dot').style.backgroundColor = 'var(--accent-green)';

    // Clear logs (use correct terminal element ID)
    const terminal = document.getElementById('terminal');
    if (terminal) terminal.innerHTML = '';
    addLog('Initializing mission parameters...', 'system');

    // Start Log Stream
    if (logSource) logSource.close();
    logSource = new EventSource('/api/logs');
    logSource.onmessage = function (event) {
        if (event.data) {
            addLog(event.data, 'info');
        }
    };

    // Start Stats Polling
    if (statsInterval) clearInterval(statsInterval);
    statsInterval = setInterval(updateStats, 2000);

    // API Call with no_website flag
    fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            keyword: keyword,
            location: location,
            max_results: maxResults,
            headless: headless,
            no_website: noWebsite
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addLog(data.error, 'error');
                resetUI();
            }
        })
        .catch(error => {
            addLog('Connection error: ' + error, 'error');
            resetUI();
        });
}

// Stop Scraping Function
function stopScraping() {
    fetch('/api/stop', { method: 'POST' })
        .then(() => { addLog('Abort signal sent...', 'warning'); });
}
