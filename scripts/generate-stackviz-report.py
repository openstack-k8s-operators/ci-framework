import sys
import json
import datetime
import argparse
from subunit import ByteStreamToStreamResult
from testtools import StreamResult

REPORT_TEMPLATE = r"""<!DOCTYPE html>
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
        }

        h1,
        h2,
        h3 {
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
        }

        .test-table-wrapper {
            flex: 1;
            overflow-y: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th,
        td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            position: sticky;
            top: 0;
            background-color: var(--card-bg);
            color: var(--text-secondary);
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

        .status-success {
            background-color: rgba(35, 134, 54, 0.2);
            color: #7ee787;
        }

        .status-fail {
            background-color: rgba(218, 54, 51, 0.2);
            color: #f85149;
        }

        .status-skip {
            background-color: rgba(158, 106, 3, 0.2);
            color: #ffdf5d;
        }

        /* Modal for details */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
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
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            font-size: 12px;
            color: var(--text-primary);
        }
    </style>
</head>

<body>

    <div class="header">
        <h1>Test Execution Report</h1>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="stats-total">-</div>
            <div class="stat-label">Total Tests</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="stats-passed" style="color: #7ee787">-</div>
            <div class="stat-label">Passed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="stats-failed" style="color: #f85149">-</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="stats-skipped" style="color: #ffdf5d">-</div>
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
            <div
                style="margin-top: 10px; height: 60px; position: relative; background: #0d1117; border: 1px solid var(--border-color); border-radius: 4px;">
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
        let viewStart = 0.0; // 0.0 to 1.0
        let viewEnd = 1.0;   // 0.0 to 1.0
        let workers = [];
        let minTime = 0;
        let maxTime = 0;
        let totalDuration = 0;

        // Constants
        const rowHeight = 40;
        const leftMargin = 150; // Increased for better readability
        const minimapHeight = 60;

        // Interaction State
        let isDragging = false;
        let dragMode = null; // 'MOVE', 'RESIZE_LEFT', 'RESIZE_RIGHT'
        let dragStartX = 0;
        let dragStartViewStart = 0;
        let dragStartViewEnd = 0;

        function init() {
            processData();

            renderStats();
            renderTable(reportData.tests);
            renderTimeline();
            renderMinimap();

            // Search
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

        function processData() {
            workers = [...new Set(reportData.tests.map(t => t.worker))].sort();

            const validTests = reportData.tests.filter(t => t.start_ts && t.end_ts);
            if (validTests.length > 0) {
                minTime = Math.min(...validTests.map(t => t.start_ts));
                maxTime = Math.max(...validTests.map(t => t.end_ts));
                totalDuration = maxTime - minTime;
            } else {
                totalDuration = 1; // Fallback
            }
        }

        // --- Rendering ---

        function renderTimeline() {
            const container = document.getElementById('timeline-canvas-container');
            const canvas = document.getElementById('timelineCanvas');
            const ctx = canvas.getContext('2d');

            // Fix canvas size to container (viewport model)
            canvas.width = container.clientWidth;
            const contentHeight = Math.max(container.clientHeight, workers.length * rowHeight);
            canvas.height = contentHeight;

            const width = canvas.width;
            const height = canvas.height;

            ctx.clearRect(0, 0, width, height);

            if (workers.length === 0) return;

            // Time range for current view
            const currentDuration = totalDuration * (viewEnd - viewStart);
            const currentStartTime = minTime + (totalDuration * viewStart);

            // Draw rows
            workers.forEach((worker, index) => {
                const y = index * rowHeight;
                if (index % 2 === 0) {
                    ctx.fillStyle = '#1c2128';
                    ctx.fillRect(0, y, width, rowHeight);
                }
                // Worker Label
                ctx.fillStyle = '#8b949e';
                ctx.font = '12px sans-serif';
                ctx.textAlign = 'left';
                ctx.fillText(worker, 5, y + rowHeight / 2 + 4);
            });

            // Draw Separator Line
            ctx.strokeStyle = '#30363d';
            ctx.beginPath();
            ctx.moveTo(leftMargin, 0);
            ctx.lineTo(leftMargin, height);
            ctx.stroke();

            // Draw Tests
            const timelineWidth = width - leftMargin;
            const validTests = reportData.tests.filter(t => t.start_ts && t.end_ts);

            validTests.forEach(test => {
                // Optimization: Skip tests strictly outside view
                if (test.end_ts < currentStartTime || test.start_ts > currentStartTime + currentDuration) return;

                const workerIndex = workers.indexOf(test.worker);
                if (workerIndex === -1) return;

                // Calculate Pct relative to VIEW
                const startPct = (test.start_ts - currentStartTime) / currentDuration;
                const endPct = (test.end_ts - currentStartTime) / currentDuration;

                const x = leftMargin + (startPct * timelineWidth);
                const w = Math.max(1, (endPct - startPct) * timelineWidth);
                const y = workerIndex * rowHeight + 2;
                const h = rowHeight - 4;

                // Clip validation (basic)
                if (x + w < leftMargin) return;

                if (test.status === 'success') ctx.fillStyle = '#238636';
                else if (test.status === 'fail') ctx.fillStyle = '#da3633';
                else if (test.status === 'skip') ctx.fillStyle = '#9e6a03';
                else ctx.fillStyle = '#238636';

                // Clip drawing to timeline area
                const drawX = Math.max(leftMargin, x);
                const drawW = Math.min(x + w, width) - drawX;

                if (drawW > 0) {
                    ctx.fillRect(drawX, y, drawW, h);
                }
            });

            // Labels
            ctx.fillStyle = '#8b949e';
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

            // Draw simplified representation of ALL tests
            // Flatten to single timeline or simplified rows?
            // "Video editor" style usually shows mini waveform or tracks.
            // Let's show mini tracks.

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

                // Use muted colors
                if (test.status === 'success') ctx.fillStyle = '#1b5e28';
                else if (test.status === 'fail') ctx.fillStyle = '#8f2321';
                else ctx.fillStyle = '#6e4a02';

                ctx.fillRect(x, y, wid, rowH);
            });

            // Draw Viewport Overlay
            const vx = viewStart * w;
            const vw = (viewEnd - viewStart) * w;

            // Dim outside areas
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, 0, vx, h); // Left dim
            ctx.fillRect(vx + vw, 0, w - (vx + vw), h); // Right dim

            // Highlight active area border
            ctx.strokeStyle = '#58a6ff';
            ctx.lineWidth = 2;
            ctx.strokeRect(vx, 0, vw, h);

            // Handles
            ctx.fillStyle = '#58a6ff';
            // Left Handle
            ctx.fillRect(vx, 0, 4, h);
            // Right Handle
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

                // Hit test
                // Margin of error for handles
                const handleWidth = 10;

                if (Math.abs(x - vx) < handleWidth) {
                    dragMode = 'RESIZE_LEFT';
                } else if (Math.abs(x - vy) < handleWidth) {
                    dragMode = 'RESIZE_RIGHT';
                } else if (x > vx && x < vy) {
                    dragMode = 'MOVE';
                } else {
                    // Click outside: Center view on click, maintaining zoom
                    const currentSpan = viewEnd - viewStart;
                    let newStart = pct - (currentSpan / 2);
                    let newEnd = pct + (currentSpan / 2);

                    if (newStart < 0) { newStart = 0; newEnd = currentSpan; }
                    if (newEnd > 1) { newEnd = 1; newStart = 1 - currentSpan; }

                    viewStart = newStart;
                    viewEnd = newEnd;
                    renderTimeline();
                    renderMinimap();
                    return; // Don't start drag immediately on jump
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

                // Delta normalized
                const dxPx = e.clientX - rect.left - dragStartX;
                const dPct = dxPx / w;

                if (dragMode === 'MOVE') {
                    let s = dragStartViewStart + dPct;
                    let e = dragStartViewEnd + dPct;

                    // Clamp
                    const span = dragStartViewEnd - dragStartViewStart;
                    if (s < 0) { s = 0; e = span; }
                    if (e > 1) { e = 1; s = 1 - span; }

                    viewStart = s;
                    viewEnd = e;

                } else if (dragMode === 'RESIZE_LEFT') {
                    let s = dragStartViewStart + dPct;
                    if (s < 0) s = 0;
                    if (s > viewEnd - 0.01) s = viewEnd - 0.01; // Min width
                    viewStart = s;

                } else if (dragMode === 'RESIZE_RIGHT') {
                    let e = dragStartViewEnd + dPct;
                    if (e > 1) e = 1;
                    if (e < viewStart + 0.01) e = viewStart + 0.01; // Min width
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

                    // Fixed positioning relative to viewport
                    let left = e.clientX + 15;
                    let top = e.clientY + 15;

                    // Boundary checks
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

            // Map x to timestamp based on VIEW WINDOW
            const canvas = document.getElementById('timelineCanvas');
            const timelineWidth = canvas.width - leftMargin;
            const pct = (x - leftMargin) / timelineWidth;

            // Time = StartTime + Pct * Duration
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
            return [h, m, s]
                .map(v => v < 10 ? "0" + v : v)
                .join(":");
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
                // Collapsible traceback
                detailsContainer.innerHTML = `
                    <details open>
                        <summary style="cursor: pointer; font-weight: bold; margin-bottom: 5px; outline: none;">Traceback / Details</summary>
                        <pre>${escapeHtml(test.details)}</pre>
                    </details>
                `;
            } else {
                detailsContainer.innerHTML = '';
            }

            document.getElementById('detailModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('detailModal').style.display = 'none';
        }

        window.onclick = function (event) {
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
            elif test_status in (
                "success",
                "fail",
                "skip",
                "xfail",
                "uxsuccess",
            ):
                test["end_time"] = ts
                # If we missed the start time, try to infer or leave incomplete
                if not test["start_time"]:
                    # Some streams might not have explicit inprogress?
                    pass

        if test_status:
            # Map statuses
            # success, fail, skip are the main ones we care about
            if test_status == "inprogress":
                pass
            else:
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
                # file_bytes is a memoryview, needs conversion to bytes
                content = bytes(file_bytes).decode("utf-8", errors="replace")
                test["details"].append(content)
            except Exception as e:
                # Fallback
                test["details"].append(str(file_bytes))

    def get_results(self):
        # Convert to list and clean up
        final_tests = []

        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0.0,
        }

        # Calculate global duration (min start to max end)
        all_starts = []
        all_ends = []

        for test_id, data in self.tests.items():
            if not data["status"]:
                # Maybe it started but didn't finish, or just log output?
                # If no status, skip or mark as unknown
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
                entry["start_time"] = datetime.datetime.fromtimestamp(
                    data["start_time"]
                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                all_starts.append(data["start_time"])

            if data["end_time"]:
                entry["end_time"] = datetime.datetime.fromtimestamp(
                    data["end_time"]
                ).strftime("%Y-%m-%d %H:%M:%S.%f")
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

    # Use embedded template
    template = REPORT_TEMPLATE

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
