const API = "/api";

const state = {
  patients: [],
  patientId: "p001",
  sessionId: crypto.randomUUID(),
  channel: "inbound",
  campaignId: null,
};

const $ = (id) => document.getElementById(id);

async function init() {
  await checkHealth();
  state.patients = await fetchJson(`${API}/patients`);
  renderPatients();
  bindEvents();
}

async function checkHealth() {
  try {
    await fetchJson(`${API}/health`);
    $("health").textContent = "Online";
  } catch {
    $("health").textContent = "Offline";
  }
}

function bindEvents() {
  $("patient").addEventListener("change", (event) => {
    state.patientId = event.target.value;
    renderPatientProfile();
  });

  document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      $("utterance").value = button.dataset.prompt;
    });
  });

  $("inboundBtn").addEventListener("click", () => setMode("inbound"));
  $("outboundBtn").addEventListener("click", startReminder);
  $("sendBtn").addEventListener("click", sendTurn);
  $("bargeBtn").addEventListener("click", () => speechSynthesis.cancel());
  $("micBtn").addEventListener("click", startMic);
}

function renderPatients() {
  $("patient").innerHTML = state.patients
    .map((patient) => `<option value="${patient.id}">${patient.name}</option>`)
    .join("");
  $("patient").value = state.patientId;
  renderPatientProfile();
}

function renderPatientProfile() {
  const patient = currentPatient();
  if (!patient) return;
  $("avatar").textContent = patient.name.slice(0, 1);
  $("patientName").textContent = patient.name;
  $("patientPhone").textContent = patient.phone;
  $("patientLanguage").textContent = patient.language_preference.toUpperCase();
}

function currentPatient() {
  return state.patients.find((patient) => patient.id === state.patientId);
}

function setMode(mode) {
  state.channel = mode;
  $("inboundBtn").classList.toggle("active", mode === "inbound");
  $("outboundBtn").classList.toggle("active", mode === "outbound");
}

async function startReminder() {
  setMode("outbound");
  const campaign = await fetchJson(`${API}/campaigns/reminders?patient_id=${state.patientId}`, { method: "POST" });
  state.campaignId = campaign.id;
  $("utterance").value = "No, not now please";
  $("callTitle").textContent = "Outbound reminder";
}

async function sendTurn() {
  const text = $("utterance").value.trim();
  if (!text) return;

  $("sendBtn").textContent = "Sending...";
  $("sendBtn").disabled = true;

  try {
    const response = await fetchJson(`${API}/agent/turn`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: state.sessionId,
        patient_id: state.patientId,
        audio_text: text,
        channel: state.channel,
        campaign_id: state.campaignId,
      }),
    });
    renderResponse(response);
    speak(response.text, response.language);
  } finally {
    $("sendBtn").textContent = "Send turn";
    $("sendBtn").disabled = false;
  }
}

function renderResponse(response) {
  $("callTitle").textContent = response.text;
  $("answer").textContent = response.text;
  $("latency").textContent = `${response.latency.first_audio_ready_ms} ms`;
  $("toolCount").textContent = response.trace.length;
  $("latencyBreakdown").innerHTML = formatLatency(response.latency);

  $("conversation").innerHTML = response.session.transcript
    .map((turn) => `
      <article class="bubble ${turn.role}">
        <span>${turn.role}</span>
        ${escapeHtml(turn.content)}
      </article>
    `)
    .join("");

  $("trace").className = "traceList";
  $("trace").innerHTML = response.trace.length
    ? response.trace.map(formatToolCall).join("")
    : "No tool call yet";
}

function formatToolCall(call) {
  const result = call.result || {};
  const appointment = result.appointment;
  const status = result.ok === true ? "Booked" : "Alternative needed";
  const alternatives = result.alternatives?.length
    ? result.alternatives.map((slot) => `<li>${formatDate(slot)}</li>`).join("")
    : "<li>None</li>";

  return `
    <div class="traceItem">
      <div class="traceHead">
        <strong>${titleCase(call.name.replaceAll("_", " "))}</strong>
        <span>${call.elapsed_ms} ms</span>
      </div>
      <dl>
        ${prettyRow("Status", status)}
        ${prettyRow("Patient", call.arguments.patient_id ?? "-")}
        ${prettyRow("Doctor", call.arguments.doctor_hint ?? appointment?.doctor_id ?? "-")}
        ${prettyRow("Slot", formatDate(call.arguments.starts_at ?? appointment?.starts_at))}
        ${appointment ? prettyRow("Appointment", shortId(appointment.id)) : ""}
      </dl>
      <div class="altBlock">
        <span>Alternatives</span>
        <ul>${alternatives}</ul>
      </div>
    </div>
  `;
}

function prettyRow(label, value) {
  return `<div><dt>${label}</dt><dd>${escapeHtml(String(value))}</dd></div>`;
}

function shortId(value) {
  return value ? `${value.slice(0, 8)}...${value.slice(-4)}` : "-";
}

function titleCase(value) {
  return value.replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1));
}

function formatLatency(latency) {
  const rows = [
    ["STT", latency.stt_ms],
    ["Language", latency.language_ms],
    ["Reasoning", latency.reasoning_ms],
    ["TTS", latency.tts_ms],
    ["Ready", latency.first_audio_ready_ms],
  ];
  return rows.map(([label, value]) => `
    <div>
      <span>${label}</span>
      <strong>${value ?? "-"} ms</strong>
    </div>
  `).join("");
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function startMic() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    $("utterance").value = "Browser microphone is not available. Type a request instead.";
    return;
  }
  const patient = currentPatient();
  const recognition = new SpeechRecognition();
  recognition.lang = patient?.language_preference === "hi" ? "hi-IN" : patient?.language_preference === "ta" ? "ta-IN" : "en-IN";
  recognition.interimResults = false;
  recognition.onresult = (event) => {
    $("utterance").value = event.results[0][0].transcript;
    sendTurn();
  };
  recognition.start();
}

function speak(text, language) {
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = language === "hi" ? "hi-IN" : language === "ta" ? "ta-IN" : "en-IN";
  speechSynthesis.speak(utterance);
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#039;",
  }[char]));
}

init();
