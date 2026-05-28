'use strict';

// ── State ──────────────────────────────────────────────────────────────────
let mediaRecorder = null;
let audioChunks = [];
let timerInterval = null;
let recordingSeconds = 0;
let recordedBlob = null;
let uploadedFile = null;
let currentTab = 'record';

// ── DOM ───────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const tabBtns      = document.querySelectorAll('.tab-btn');
const tabPanels    = document.querySelectorAll('.tab-panel');
const recordBtn    = $('record-btn');
const recordLabel  = $('record-label');
const timerEl      = $('timer');
const dropZone     = $('drop-zone');
const fileInput    = $('file-input');
const fileNameEl   = $('file-name');
const submitBtn    = $('submit-btn');
const errorMsg     = $('error-msg');
const inputSection = $('input-section');
const progressSec  = $('progress-section');
const resultSec    = $('result-section');
const transcriptEl = $('transcript-text');
const minutesEl    = $('minutes-output');
const downloadBtn  = $('download-btn');
const resetBtn     = $('reset-btn');

// ── Tabs ──────────────────────────────────────────────────────────────────
tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    currentTab = btn.dataset.tab;
    tabBtns.forEach(b => b.classList.remove('active'));
    tabPanels.forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    $(`tab-${currentTab}`).classList.add('active');
    updateSubmitState();
  });
});

// ── Recording ─────────────────────────────────────────────────────────────
recordBtn.addEventListener('click', async () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    stopRecording();
  } else {
    await startRecording();
  }
});

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    recordedBlob = null;
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = () => {
      recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
      stream.getTracks().forEach(t => t.stop());
      updateSubmitState();
    };
    mediaRecorder.start();
    recordBtn.classList.add('recording');
    recordLabel.textContent = '녹음 중지';
    startTimer();
  } catch {
    showError('마이크 접근 권한이 필요합니다. 브라우저 설정을 확인해주세요.');
  }
}

function stopRecording() {
  mediaRecorder.stop();
  recordBtn.classList.remove('recording');
  recordLabel.textContent = '녹음 시작';
  stopTimer();
  timerEl.style.display = 'none';
}

function startTimer() {
  recordingSeconds = 0;
  timerEl.style.display = 'block';
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    recordingSeconds++;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}

function updateTimerDisplay() {
  const m = String(Math.floor(recordingSeconds / 60)).padStart(2, '0');
  const s = String(recordingSeconds % 60).padStart(2, '0');
  timerEl.textContent = `${m}:${s}`;
}

// ── File Upload ────────────────────────────────────────────────────────────
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) setUploadFile(fileInput.files[0]);
});
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  if (e.dataTransfer.files[0]) setUploadFile(e.dataTransfer.files[0]);
});

function setUploadFile(file) {
  uploadedFile = file;
  fileNameEl.textContent = `✓ ${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)`;
  updateSubmitState();
}

// ── Submit ─────────────────────────────────────────────────────────────────
function updateSubmitState() {
  const hasAudio = currentTab === 'record' ? !!recordedBlob : !!uploadedFile;
  submitBtn.disabled = !hasAudio;
}

submitBtn.addEventListener('click', async () => {
  hideError();
  const audioFile = currentTab === 'record' ? recordedBlob : uploadedFile;
  if (!audioFile) return;

  showProgress();

  try {
    // Step 1: Upload & STT
    setStep('step-upload', 'active');
    setStep('step-stt', 'active');

    const form = new FormData();
    const filename = currentTab === 'record' ? 'recording.webm' : uploadedFile.name;
    form.append('file', audioFile, filename);

    const sttRes = await fetch('/api/transcribe', { method: 'POST', body: form });
    if (!sttRes.ok) {
      const err = await sttRes.json();
      throw new Error(err.detail || 'STT 변환 실패');
    }
    const sttData = await sttRes.json();

    setStep('step-upload', 'done');
    setStep('step-stt', 'done');

    // Step 2: Minutes
    setStep('step-minutes', 'active');
    const minutesRes = await fetch('/api/minutes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript: sttData.transcript }),
    });
    if (!minutesRes.ok) {
      const err = await minutesRes.json();
      throw new Error(err.detail || '회의록 생성 실패');
    }
    const minutesData = await minutesRes.json();
    setStep('step-minutes', 'done');

    showResult(sttData.transcript, minutesData.minutes);

  } catch (err) {
    hideProgress();
    showError(err.message);
  }
});

// ── Progress helpers ───────────────────────────────────────────────────────
function showProgress() {
  inputSection.style.display = 'none';
  progressSec.style.display = 'block';
  resultSec.style.display = 'none';
  ['step-upload', 'step-stt', 'step-minutes'].forEach(id => {
    const el = $(id);
    el.className = 'step';
    el.querySelector('.spinner').style.display = 'none';
  });
}

function hideProgress() {
  inputSection.style.display = 'block';
  progressSec.style.display = 'none';
}

function setStep(id, state) {
  const el = $(id);
  el.className = `step ${state}`;
  el.querySelector('.spinner').style.display = state === 'active' ? 'block' : 'none';
}

// ── Result ─────────────────────────────────────────────────────────────────
function showResult(transcript, minutesMarkdown) {
  progressSec.style.display = 'none';
  resultSec.style.display = 'block';
  resetBtn.style.display = 'block';

  transcriptEl.textContent = transcript;
  minutesEl.innerHTML = renderMarkdown(minutesMarkdown);

  downloadBtn.onclick = () => {
    const blob = new Blob([minutesMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `회의록_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };
}

// Minimal Markdown renderer (h2, ul, table, hr, p)
function renderMarkdown(md) {
  return md
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^\| (.+) \|$/gm, (line) => {
      const cells = line.split('|').slice(1, -1).map(c => c.trim());
      return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
    })
    .replace(/(<tr>[\s\S]*?<\/tr>)/g, m => `<table>${m}</table>`)
    .replace(/^---+$/gm, '<hr>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, m => `<ul>${m}</ul>`)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/^(?!<[htupl])/gm, '')
    .trim();
}

// ── Transcript toggle ───────────────────────────────────────────────────────
$('transcript-toggle').addEventListener('click', () => {
  const body = $('transcript-body');
  const header = $('transcript-toggle');
  const isCollapsed = body.classList.contains('collapsed');
  body.classList.toggle('collapsed', !isCollapsed);
  header.classList.toggle('collapsed', !isCollapsed);
});

// ── Reset ──────────────────────────────────────────────────────────────────
resetBtn.addEventListener('click', () => {
  recordedBlob = null;
  uploadedFile = null;
  fileInput.value = '';
  fileNameEl.textContent = '';
  recordLabel.textContent = '녹음 시작';
  recordBtn.classList.remove('recording');
  timerEl.style.display = 'none';
  stopTimer();
  hideError();
  inputSection.style.display = 'block';
  progressSec.style.display = 'none';
  resultSec.style.display = 'none';
  resetBtn.style.display = 'none';
  updateSubmitState();
});

// ── Error ──────────────────────────────────────────────────────────────────
function showError(msg) {
  errorMsg.textContent = `⚠ ${msg}`;
  errorMsg.style.display = 'block';
}
function hideError() {
  errorMsg.style.display = 'none';
}
