#!/usr/bin/env python3
import sys
import json
import datetime
import argparse
from pathlib import Path
from subunit import ByteStreamToStreamResult
from testtools import StreamResult

# Path to the HTML template file (relative to this script)
TEMPLATE_PATH = Path(__file__).parent / "stackviz-report-template.html"

REPORT_TEMPLATE_FALLBACK = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Report</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --border-color: #30363d;
            --accent-color: #58a6ff;
            --success-color: #238636;
            --fail-color: #da3633;
            --skip-color: #9e6a03;
            --timeline-stripe: #1c2128;
            --timeline-text: #8b949e;
            --timeline-line: #30363d;
        }

        [data-theme="light"] {
            --bg-color: #ffffff;
            --card-bg: #f6f8fa;
            --text-primary: #24292f;
            --text-secondary: #57606a;
            --border-color: #d0d7de;
            --accent-color: #0969da;
            --success-color: #1a7f37;
            --fail-color: #cf222e;
            --skip-color: #9a6700;
            --timeline-stripe: #eaeef2;
            --timeline-text: #57606a;
            --timeline-line: #d0d7de;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            height: 100vh;
            box-sizing: border-box;
            transition: background-color 0.3s, color 0.3s;
        }

        h1, h2, h3 {
            margin-top: 0;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .theme-toggle-btn {
            background: none;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            padding: 8px 12px;
            cursor: pointer;
            font-size: 14px;
            background-color: var(--card-bg);
        }

        .theme-toggle-btn:hover {
            background-color: var(--bg-color);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            cursor: pointer;
            transition: background-color 0.3s, border-color 0.3s;
        }

        .stat-value {
            font-size: 24px;
            font-weight: bold;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            flex: 1;
            overflow: hidden;
        }

        .timeline-container {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            overflow-x: auto;
            flex: 0 0 300px;
            display: flex;
            flex-direction: column;
            transition: background-color 0.3s, border-color 0.3s;
        }

        #timeline-canvas-container {
            position: relative;
            width: 100%;
            height: 100%;
            overflow-x: auto;
            overflow-y: hidden;
        }

        canvas {
            display: block;
        }

        .test-list-container {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: background-color 0.3s, border-color 0.3s;
        }

        .search-bar {
            width: 100%;
            padding: 10px;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            margin-bottom: 10px;
            box-sizing: border-box;
            transition: background-color 0.3s, border-color 0.3s, color 0.3s;
        }

        .test-table-wrapper {
            flex: 1;
            overflow-y: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            position: sticky;
            top: 0;
            background-color: var(--card-bg);
            color: var(--text-secondary);
            transition: background-color 0.3s;
        }

        tr:hover {
            background-color: var(--bg-color);
            cursor: pointer;
        }

        .status-badge {
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }

        .status-success { background-color: rgba(35, 134, 54, 0.2); color: var(--success-color); }
        .status-fail { background-color: rgba(218, 54, 51, 0.2); color: var(--fail-color); }
        .status-skip { background-color: rgba(158, 106, 3, 0.2); color: var(--skip-color); }

        /* Modal for details */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background-color: var(--card-bg);
            padding: 20px;
            border-radius: 6px;
            width: 80%;
            max-width: 800px;
            max-height: 80%;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }
        .close-btn {
            float: right;
            cursor: pointer;
            font-size: 20px;
        }
        pre {
            background-color: var(--bg-color);
            padding: 10px;
            overflow-x: auto;
            border-radius: 4px;
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }

        #timeline-tooltip {
            position: fixed;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 10px;
            border-radius: 4px;
            pointer-events: none;
            display: none;
            z-index: 1001;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            font-size: 12px;
            color: var(--text-primary);
        }
    </style>
</head>
<body>

<div class="header">
    <h1>Test Execution Report</h1>
    <button id="theme-toggle" class="theme-toggle-btn" onclick="toggleTheme()">Switch Theme</button>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value" id="stats-total">-</div>
        <div class="stat-label">Total Tests</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" id="stats-passed" style="color: var(--success-color)">-</div>
        <div class="stat-label">Passed</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" id="stats-failed" style="color: var(--fail-color)">-</div>
        <div class="stat-label">Failed</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" id="stats-skipped" style="color: var(--skip-color)">-</div>
        <div class="stat-label">Skipped</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" id="stats-duration">-</div>
        <div class="stat-label">Total Duration</div>
    </div>
</div>

<div class="container">
    <div class="timeline-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h3 style="margin: 0;">Execution Timeline (by Worker)</h3>
            <small style="color: var(--text-secondary)">Drag Navigator below to Zoom/Scroll</small>
        </div>
        <div id="timeline-canvas-container">
            <canvas id="timelineCanvas"></canvas>
        </div>
        <!-- Minimap Navigator -->
        <div style="margin-top: 10px; height: 60px; position: relative; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 4px;">
            <canvas id="minimapCanvas" style="width: 100%; height: 100%; display: block;"></canvas>
        </div>
    </div>

    <div class="test-list-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search tests...">
        <div class="test-table-wrapper">
            <table id="testTable">
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Test Name</th>
                        <th>Duration (s)</th>
                        <th>Worker</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Rows will be injected here -->
                </tbody>
            </table>
        </div>
    </div>
</div>

<div id="detailModal" class="modal">
    <div class="modal-content">
        <span class="close-btn" onclick="closeModal()">&times;</span>
        <h2 id="modalTitle" style="overflow-wrap: break-word; word-break: break-all;"></h2>
        <p><strong>Status:</strong> <span id="modalStatus"></span></p>
        <p><strong>Duration:</strong> <span id="modalDuration"></span>s</p>
        <p><strong>Worker:</strong> <span id="modalWorker"></span></p>
        <p><strong>Timestamps:</strong> <span id="modalTimes"></span></p>
        <div id="modalDetails"></div>
    </div>
</div>

<div id="timeline-tooltip"></div>

<script>
    // Data injection point
    const reportData = {{ REPORT_DATA }};

    // State
    let viewStart = 0.0;
    let viewEnd = 1.0;
    let workers = [];
    let minTime = 0;
    let maxTime = 0;
    let totalDuration = 0;

    // Constants
    const rowHeight = 40;
    const leftMargin = 150;
    const minimapHeight = 60;

    // Interaction State
    let isDragging = false;
    let dragMode = null;
    let dragStartX = 0;
    let dragStartViewStart = 0;
    let dragStartViewEnd = 0;

    function init() {
        // Theme Init
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeButtonText(savedTheme);

        processData();

        renderStats();
        renderTable(reportData.tests);
        renderTimeline();
        renderMinimap();

        document.getElementById('searchInput').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = reportData.tests.filter(t => t.id.toLowerCase().includes(query));
            renderTable(filtered);
        });

        // Filters
        document.getElementById('stats-total').parentElement.onclick = () => filterByStatus(null);
        document.getElementById('stats-passed').parentElement.onclick = () => filterByStatus('success');
        document.getElementById('stats-failed').parentElement.onclick = () => filterByStatus('fail');
        document.getElementById('stats-skipped').parentElement.onclick = () => filterByStatus('skip');

        // Resize
        window.addEventListener('resize', () => {
            renderTimeline();
            renderMinimap();
        });

        setupTimelineInteractions();
        setupMinimapInteractions();
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeButtonText(next);

        renderTimeline();
        renderMinimap();
    }

    function updateThemeButtonText(theme) {
        const btn = document.getElementById('theme-toggle');
        btn.textContent = theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode';
    }

    function processData() {
        workers = [...new Set(reportData.tests.map(t => t.worker))].sort();
        const validTests = reportData.tests.filter(t => t.start_ts && t.end_ts);
        if (validTests.length > 0) {
            minTime = Math.min(...validTests.map(t => t.start_ts));
            maxTime = Math.max(...validTests.map(t => t.end_ts));
            totalDuration = maxTime - minTime;
        } else {
            totalDuration = 1;
        }
    }

    function getVar(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }

    function renderTimeline() {
        const container = document.getElementById('timeline-canvas-container');
        const canvas = document.getElementById('timelineCanvas');
        const ctx = canvas.getContext('2d');

        canvas.width = container.clientWidth;
        const contentHeight = Math.max(container.clientHeight, workers.length * rowHeight);
        canvas.height = contentHeight;

        const width = canvas.width;
        const height = canvas.height;

        ctx.clearRect(0, 0, width, height);

        if (workers.length === 0) return;

        // Get Theme Colors
        const stripeColor = getVar('--timeline-stripe');
        const textColor = getVar('--timeline-text');
        const lineColor = getVar('--timeline-line');
        const successColor = getVar('--success-color');
        const failColor = getVar('--fail-color');
        const skipColor = getVar('--skip-color');

        const currentDuration = totalDuration * (viewEnd - viewStart);
        const currentStartTime = minTime + (totalDuration * viewStart);

        workers.forEach((worker, index) => {
            const y = index * rowHeight;
            if (index % 2 === 0) {
                ctx.fillStyle = stripeColor;
                ctx.fillRect(0, y, width, rowHeight);
            }
            ctx.fillStyle = textColor;
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText(worker, 5, y + rowHeight / 2 + 4);
        });

        ctx.strokeStyle = lineColor;
        ctx.beginPath();
        ctx.moveTo(leftMargin, 0);
        ctx.lineTo(leftMargin, height);
        ctx.stroke();

        const timelineWidth = width - leftMargin;
        const validTests = reportData.tests.filter(t => t.start_ts && t.end_ts);

        validTests.forEach(test => {
            if (test.end_ts < currentStartTime || test.start_ts > currentStartTime + currentDuration) return;

            const workerIndex = workers.indexOf(test.worker);
            if (workerIndex === -1) return;

            const startPct = (test.start_ts - currentStartTime) / currentDuration;
            const endPct = (test.end_ts - currentStartTime) / currentDuration;

            const x = leftMargin + (startPct * timelineWidth);
            const w = Math.max(1, (endPct - startPct) * timelineWidth);
            const y = workerIndex * rowHeight + 2;
            const h = rowHeight - 4;

            if (x + w < leftMargin) return;

            if (test.status === 'success') ctx.fillStyle = successColor;
            else if (test.status === 'fail') ctx.fillStyle = failColor;
            else if (test.status === 'skip') ctx.fillStyle = skipColor;
            else ctx.fillStyle = successColor;

            const drawX = Math.max(leftMargin, x);
            const drawW = Math.min(x + w, width) - drawX;

            if (drawW > 0) {
                ctx.fillRect(drawX, y, drawW, h);
            }
        });

        ctx.fillStyle = textColor;
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(currentStartTime.toFixed(1) + 's', leftMargin + 5, height - 5);
        ctx.textAlign = 'right';
        ctx.fillText((currentStartTime + currentDuration).toFixed(1) + 's', width - 5, height - 5);
    }

    function renderMinimap() {
        const canvas = document.getElementById('minimapCanvas');
        const ctx = canvas.getContext('2d');
        const rect = canvas.parentElement.getBoundingClientRect();

        canvas.width = rect.width;
        canvas.height = rect.height;

        const w = canvas.width;
        const h = canvas.height;

        ctx.clearRect(0, 0, w, h);

        const rowH = h / Math.max(1, workers.length);

        reportData.tests.forEach(test => {
            if (!test.start_ts || !test.end_ts) return;
            const workerIndex = workers.indexOf(test.worker);
            if (workerIndex === -1) return;

            const startPct = (test.start_ts - minTime) / totalDuration;
            const endPct = (test.end_ts - minTime) / totalDuration;

            const x = startPct * w;
            const wid = Math.max(1, (endPct - startPct) * w);
            const y = workerIndex * rowH;

            if (test.status === 'success') ctx.fillStyle = '#1b5e28';
            else if (test.status === 'fail') ctx.fillStyle = '#8f2321';
            else ctx.fillStyle = '#6e4a02';

            ctx.fillRect(x, y, wid, rowH);
        });

        const vx = viewStart * w;
        const vw = (viewEnd - viewStart) * w;

        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(0, 0, vx, h);
        ctx.fillRect(vx + vw, 0, w - (vx + vw), h);

        ctx.strokeStyle = '#58a6ff';
        ctx.lineWidth = 2;
        ctx.strokeRect(vx, 0, vw, h);

        ctx.fillStyle = '#58a6ff';
        ctx.fillRect(vx, 0, 4, h);
        ctx.fillRect(vx + vw - 4, 0, 4, h);
    }

    // --- Interactions ---

    function setupMinimapInteractions() {
        const canvas = document.getElementById('minimapCanvas');

        canvas.addEventListener('mousedown', e => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const w = rect.width;
            const pct = x / w;

            const vx = viewStart * w;
            const vw = (viewEnd - viewStart) * w;
            const vy = viewEnd * w;

            const handleWidth = 10;

            if (Math.abs(x - vx) < handleWidth) {
                dragMode = 'RESIZE_LEFT';
            } else if (Math.abs(x - vy) < handleWidth) {
                dragMode = 'RESIZE_RIGHT';
            } else if (x > vx && x < vy) {
                dragMode = 'MOVE';
            } else {
                const currentSpan = viewEnd - viewStart;
                let newStart = pct - (currentSpan / 2);
                let newEnd = pct + (currentSpan / 2);

                if (newStart < 0) { newStart = 0; newEnd = currentSpan; }
                if (newEnd > 1) { newEnd = 1; newStart = 1 - currentSpan; }

                viewStart = newStart;
                viewEnd = newEnd;
                renderTimeline();
                renderMinimap();
                return;
            }

            isDragging = true;
            dragStartX = x;
            dragStartViewStart = viewStart;
            dragStartViewEnd = viewEnd;
        });

        window.addEventListener('mousemove', e => {
            if (!isDragging) return;

            const canvas = document.getElementById('minimapCanvas');
            const rect = canvas.getBoundingClientRect();
            const w = rect.width;

            const dxPx = e.clientX - rect.left - dragStartX;
            const dPct = dxPx / w;

            if (dragMode === 'MOVE') {
                let s = dragStartViewStart + dPct;
                let e = dragStartViewEnd + dPct;

                const span = dragStartViewEnd - dragStartViewStart;
                if (s < 0) { s = 0; e = span; }
                if (e > 1) { e = 1; s = 1 - span; }

                viewStart = s;
                viewEnd = e;

            } else if (dragMode === 'RESIZE_LEFT') {
                let s = dragStartViewStart + dPct;
                if (s < 0) s = 0;
                if (s > viewEnd - 0.01) s = viewEnd - 0.01;
                viewStart = s;

            } else if (dragMode === 'RESIZE_RIGHT') {
                let e = dragStartViewEnd + dPct;
                if (e > 1) e = 1;
                if (e < viewStart + 0.01) e = viewStart + 0.01;
                viewEnd = e;
            }

            renderTimeline();
            renderMinimap();
        });

        window.addEventListener('mouseup', () => {
            isDragging = false;
            dragMode = null;
        });
    }

    function setupTimelineInteractions() {
        const canvas = document.getElementById('timelineCanvas');

        canvas.addEventListener('mousemove', e => {
            if (isDragging) return;

            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const test = getTestAt(x, y);
            const tooltip = document.getElementById('timeline-tooltip');

            if (test) {
                tooltip.style.display = 'block';
                let left = e.clientX + 15;
                let top = e.clientY + 15;

                if (left + 250 > window.innerWidth) left = e.clientX - 260;
                if (top + 100 > window.innerHeight) top = e.clientY - 110;

                tooltip.style.left = left + 'px';
                tooltip.style.top = top + 'px';
                tooltip.innerHTML = `<strong>${test.id}</strong><br>Duration: ${test.duration.toFixed(3)}s<br>Status: ${test.status}`;
                canvas.style.cursor = 'pointer';
            } else {
                tooltip.style.display = 'none';
                canvas.style.cursor = 'default';
            }
        });

        canvas.addEventListener('mouseleave', () => {
            document.getElementById('timeline-tooltip').style.display = 'none';
        });

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const test = getTestAt(x, y);
            if (test) {
                showDetails(test);
            }
        });
    }

    function getTestAt(x, y) {
        if (x < leftMargin) return null;

        const workerIndex = Math.floor(y / rowHeight);
        if (workerIndex < 0 || workerIndex >= workers.length) return null;

        const worker = workers[workerIndex];

        const canvas = document.getElementById('timelineCanvas');
        const timelineWidth = canvas.width - leftMargin;
        const pct = (x - leftMargin) / timelineWidth;

        const currentDuration = totalDuration * (viewEnd - viewStart);
        const currentStartTime = minTime + (totalDuration * viewStart);

        const timestamp = currentStartTime + (pct * currentDuration);

        return reportData.tests.find(t =>
            t.worker === worker &&
            t.start_ts <= timestamp &&
            t.end_ts >= timestamp
        );
    }

    function formatDuration(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return [h, m, s].map(v => v < 10 ? "0" + v : v).join(":");
    }

    function renderStats() {
        document.getElementById('stats-total').textContent = reportData.summary.total;
        document.getElementById('stats-passed').textContent = reportData.summary.passed;
        document.getElementById('stats-failed').textContent = reportData.summary.failed;
        document.getElementById('stats-skipped').textContent = reportData.summary.skipped;
        document.getElementById('stats-duration').textContent = formatDuration(reportData.summary.duration);
    }

    function filterByStatus(status) {
        let filtered;
        if (status) {
            filtered = reportData.tests.filter(t => t.status === status);
        } else {
            filtered = reportData.tests;
        }
        renderTable(filtered);
    }

    function renderTable(tests) {
        const tbody = document.querySelector('#testTable tbody');
        tbody.innerHTML = '';
        const limit = 500;
        const displayTests = tests.slice(0, limit);
        displayTests.forEach(test => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span class="status-badge status-${test.status}">${test.status}</span></td>
                <td title="${test.id}">${test.id}</td>
                <td>${test.duration.toFixed(3)}</td>
                <td>${test.worker}</td>
            `;
            tr.onclick = () => showDetails(test);
            tbody.appendChild(tr);
        });
        if (tests.length > limit) {
             const tr = document.createElement('tr');
             tr.innerHTML = `<td colspan="4" style="text-align:center; color: var(--text-secondary)">... showing first ${limit} of ${tests.length} matches ...</td>`;
             tbody.appendChild(tr);
        }
    }

    function showDetails(test) {
        document.getElementById('modalTitle').textContent = test.id;
        document.getElementById('modalStatus').textContent = test.status;
        document.getElementById('modalDuration').textContent = test.duration.toFixed(3);
        document.getElementById('modalWorker').textContent = test.worker;
        document.getElementById('modalTimes').textContent = `Start: ${test.start_time}, End: ${test.end_time}`;

        const detailsContainer = document.getElementById('modalDetails');
        if (test.details) {
            detailsContainer.innerHTML = '<h3>Details/Traceback</h3><pre>' + escapeHtml(test.details) + '</pre>';
        } else {
            detailsContainer.innerHTML = '';
        }
        document.getElementById('detailModal').style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('detailModal').style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == document.getElementById('detailModal')) {
            closeModal();
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    init();
</script>

</body>
</html>"""


def format_timestamp(timestamp):
    """Convert Unix timestamp to formatted datetime string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")


class ReportAccumulator(StreamResult):
    def __init__(self):
        super().__init__()
        self.tests = {}  # key: test_id
        self.events = []

    def status(
        self,
        test_id=None,
        test_status=None,
        test_tags=None,
        runnable=True,
        file_name=None,
        file_bytes=None,
        eof=False,
        mime_type=None,
        route_code=None,
        timestamp=None,
    ):
        if not test_id:
            return

        if test_id not in self.tests:
            self.tests[test_id] = {
                "id": test_id,
                "status": None,
                "start_time": None,
                "end_time": None,
                "worker": "unknown",
                "tags": set(),
                "details": [],
            }

        test = self.tests[test_id]

        if timestamp:
            ts = timestamp.timestamp()
            if test_status == "inprogress":
                test["start_time"] = ts
            elif test_status in ("success", "fail", "skip", "xfail", "uxsuccess"):
                test["end_time"] = ts

        if test_status and test_status != "inprogress":
            test["status"] = test_status

        if test_tags:
            test["tags"].update(test_tags)
            # Try to extract worker from tags
            for tag in test_tags:
                if tag.startswith("worker-"):
                    test["worker"] = tag

        if file_bytes:
            # Accumulate output/tracebacks
            try:
                content = bytes(file_bytes).decode("utf-8", errors="replace")
                test["details"].append(content)
            except (UnicodeDecodeError, AttributeError, TypeError):
                test["details"].append(str(file_bytes))

    def get_results(self):
        # Convert to list and clean up
        final_tests = []

        summary = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "duration": 0.0}

        # Calculate global duration (min start to max end)
        all_starts = []
        all_ends = []

        for test_id, data in self.tests.items():
            if not data["status"]:
                # Tests without status indicate incomplete data or stream parsing issues
                print(
                    f"WARNING: Test '{test_id}' has no status - skipping",
                    file=sys.stderr,
                )
                continue

            entry = {
                "id": data["id"],
                "status": data["status"],
                "worker": data["worker"],
                "start_ts": data["start_time"],
                "end_ts": data["end_time"],
                "duration": 0.0,
                "details": "".join(data["details"]),
            }

            # Timestamp formatting
            if data["start_time"]:
                entry["start_time"] = format_timestamp(data["start_time"])
                all_starts.append(data["start_time"])

            if data["end_time"]:
                entry["end_time"] = format_timestamp(data["end_time"])
                all_ends.append(data["end_time"])

            if data["start_time"] and data["end_time"]:
                entry["duration"] = data["end_time"] - data["start_time"]

            # Summary counts
            summary["total"] += 1
            if data["status"] == "success":
                summary["passed"] += 1
            elif data["status"] == "fail":
                summary["failed"] += 1
            elif data["status"] == "skip":
                summary["skipped"] += 1

            final_tests.append(entry)

        if all_starts and all_ends:
            summary["duration"] = max(all_ends) - min(all_starts)

        return {"summary": summary, "tests": final_tests}


def process_file(input_file, output_file):
    # Depending on how the file is opened (binary)
    # subunit v2 stream is binary

    accumulator = ReportAccumulator()

    with open(input_file, "rb") as f:
        parser = ByteStreamToStreamResult(f)
        parser.run(accumulator)

    data = accumulator.get_results()

    # Load template from external file, fallback to embedded if not found
    try:
        with open(TEMPLATE_PATH, "r") as template_file:
            template = template_file.read()
    except FileNotFoundError:
        print(
            f"WARNING: Template file not found at {TEMPLATE_PATH}, using embedded fallback",
            file=sys.stderr,
        )
        template = REPORT_TEMPLATE_FALLBACK

    # Embed data
    json_data = json.dumps(data)
    html_content = template.replace("{{ REPORT_DATA }}", json_data)

    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"Generated {output_file} with {data['summary']['total']} tests.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input .subunit file")
    parser.add_argument(
        "output",
        nargs="?",
        default="tempest-viz.html",
        help="Output .html file (default: tempest-viz.html)",
    )

    args = parser.parse_args()
    process_file(args.input, args.output)
