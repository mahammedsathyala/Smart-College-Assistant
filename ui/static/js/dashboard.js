/**
 * Smart College Assistant — Dashboard JavaScript
 * Loads and renders student dashboard with Chart.js charts.
 */

"use strict";

let attendanceChart, marksChart;

document.addEventListener('DOMContentLoaded', async () => {
  await loadDashboard();
});

async function loadDashboard() {
  try {
    const res = await fetch('/api/student/dashboard', { credentials: 'include' });
    const data = await res.json();

    if (!data.success) {
      if (data.error && data.error.includes('Authentication')) {
        window.location.href = '/login';
      }
      return;
    }

    hideDashLoader();
    renderStudentInfo(data.student);
    renderKPIs(data.student, data.stats);
    renderAttendanceChart(data.stats.subjects_data);
    renderMarksChart(data.stats.marks_data);
    renderTodaySchedule();
    renderNotifications(data.notifications);
    renderDrives(data.upcoming_drives);

  } catch (e) {
    console.error('Dashboard load failed:', e);
    hideDashLoader();
  }
}

function hideDashLoader() {
  const loader = document.getElementById('dashLoader');
  if (loader) loader.classList.add('hidden');
}

function renderStudentInfo(student) {
  const greeting = getGreeting();
  document.getElementById('welcomeText').textContent = `${greeting}, ${student.name.split(' ')[0]}! 👋`;
  document.getElementById('studentInfo').textContent =
    `${student.roll_number} · ${student.department} · Semester ${student.semester} · Batch ${student.batch}`;
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good Morning';
  if (h < 17) return 'Good Afternoon';
  return 'Good Evening';
}

function renderKPIs(student, stats) {
  document.getElementById('kpiCgpa').textContent = student.cgpa.toFixed(2);
  document.getElementById('kpiAttendance').textContent = stats.overall_attendance.toFixed(1) + '%';
  document.getElementById('kpiAtRisk').textContent = stats.at_risk_subjects;
  document.getElementById('kpiPlacement').textContent = student.placement_eligible ? '✅ Eligible' : '❌ Ineligible';

  // Attendance badge
  const att = stats.overall_attendance;
  const badge = document.getElementById('kpiAttBadge');
  if (badge) {
    badge.textContent = att >= 75 ? 'Safe' : att >= 65 ? 'Warning' : 'Critical';
    badge.style.cssText = `font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:99px;background:${att >= 75 ? 'rgba(34,211,165,0.15)' : 'rgba(248,113,113,0.15)'};color:${att >= 75 ? '#22d3a5' : '#f87171'};`;
  }
}

function renderAttendanceChart(subjects) {
  const canvas = document.getElementById('attendanceChart');
  if (!canvas || !subjects.length) return;

  if (attendanceChart) attendanceChart.destroy();

  const colors = subjects.map(s =>
    s.percentage >= 75 ? 'rgba(34,211,165,0.8)' :
    s.percentage >= 65 ? 'rgba(251,191,36,0.8)' : 'rgba(248,113,113,0.8)'
  );

  attendanceChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: subjects.map(s => s.course_code || s.course),
      datasets: [{
        label: 'Attendance %',
        data: subjects.map(s => s.percentage),
        backgroundColor: colors,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.parsed.y.toFixed(1)}% (${subjects[ctx.dataIndex].present}/${subjects[ctx.dataIndex].total})`,
          },
        },
      },
      scales: {
        y: {
          min: 0, max: 100,
          grid: { color: 'rgba(99,130,255,0.06)' },
          ticks: { color: '#8892b0', callback: v => v + '%' },
        },
        x: { grid: { display: false }, ticks: { color: '#8892b0' } },
      },
    },
  });
}

function renderMarksChart(marks) {
  const canvas = document.getElementById('marksChart');
  if (!canvas || !marks.length) return;

  if (marksChart) marksChart.destroy();

  marksChart = new Chart(canvas, {
    type: 'radar',
    data: {
      labels: marks.slice(0, 5).map(m => m.course_code || m.course),
      datasets: [{
        label: 'Marks %',
        data: marks.slice(0, 5).map(m => m.percentage),
        backgroundColor: 'rgba(99,130,255,0.15)',
        borderColor: 'rgba(99,130,255,0.8)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(99,130,255,1)',
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display: false } },
      scales: {
        r: {
          min: 0, max: 100,
          grid: { color: 'rgba(99,130,255,0.1)' },
          angleLines: { color: 'rgba(99,130,255,0.1)' },
          pointLabels: { color: '#8892b0', font: { size: 11 } },
          ticks: { display: false },
        },
      },
    },
  });
}

async function renderTodaySchedule() {
  const container = document.getElementById('todaySchedule');
  const badge = document.getElementById('todayBadge');
  const today = new Date().toLocaleString('en-us', { weekday: 'long' });
  if (badge) badge.textContent = today;

  try {
    const res = await fetch('/api/student/timetable', { credentials: 'include' });
    const data = await res.json();
    if (!data.success || !data.timetable || !data.timetable[today]) {
      container.innerHTML = '<p class="text-muted text-center small py-2">No classes today.</p>';
      return;
    }

    const slots = data.timetable[today];
    container.innerHTML = slots.map(s => `
      <div class="tt-slot tt-${s.type} mb-2">
        <div class="tt-time">${s.time}</div>
        <div class="tt-course">${s.course}</div>
        <div class="tt-meta">${s.faculty} · ${s.room}</div>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = '<p class="text-muted text-center small py-2">Could not load schedule.</p>';
  }
}

function renderNotifications(notifications) {
  const container = document.getElementById('latestNotifications');
  if (!container || !notifications.length) {
    if (container) container.innerHTML = '<p class="text-muted text-center small py-2">No notifications.</p>';
    return;
  }
  const priorityColors = { high: '#f87171', normal: '#6382ff', low: '#5a6785' };
  container.innerHTML = notifications.map(n => `
    <div class="notif-card mb-2 p-2" style="border-left-color:${priorityColors[n.priority]||'#6382ff'}">
      <div class="d-flex align-items-start gap-2">
        <div style="width:8px;height:8px;border-radius:50%;background:${priorityColors[n.priority]};flex-shrink:0;margin-top:5px;"></div>
        <div>
          <div class="fw-bold" style="font-size:0.82rem;color:var(--text-primary)">${n.title}</div>
          <small class="text-muted">${n.category} · ${new Date(n.created_at).toLocaleDateString()}</small>
        </div>
      </div>
    </div>
  `).join('');
}

function renderDrives(drives) {
  const container = document.getElementById('upcomingDrives');
  if (!container || !drives.length) {
    if (container) container.innerHTML = '<p class="text-muted text-center small py-2">No upcoming drives.</p>';
    return;
  }
  container.innerHTML = drives.map(d => `
    <div class="drive-card mb-2">
      <div class="drive-company">${d.company}</div>
      <div class="d-flex gap-3 mt-1" style="font-size:0.78rem;color:var(--text-secondary)">
        <span><i class="bi bi-briefcase me-1 text-primary"></i>${d.role}</span>
        <span><i class="bi bi-calendar me-1 text-warning"></i>${d.date}</span>
      </div>
      <div style="font-size:0.75rem;color:var(--accent-success);margin-top:4px;">Min CGPA: ${d.min_cgpa}</div>
    </div>
  `).join('');
}

async function refreshDashboard() {
  const loader = document.getElementById('dashLoader');
  if (loader) loader.classList.remove('hidden');
  await loadDashboard();
  showToast('Dashboard refreshed!', 'success');
}
