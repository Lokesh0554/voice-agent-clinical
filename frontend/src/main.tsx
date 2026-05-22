import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  CalendarClock,
  CheckCircle2,
  Clock3,
  FileText,
  Languages,
  Mic,
  PhoneCall,
  RefreshCw,
  Send,
  ShieldCheck,
  Square,
  Stethoscope,
} from "lucide-react";
import "./styles.css";

type Language = "en" | "hi" | "ta";

type Patient = {
  id: string;
  name: string;
  phone: string;
  language_preference: Language;
  notes: string[];
};

type AgentResponse = {
  text: string;
  language: Language;
  audio_url: string;
  trace: Array<{ name: string; arguments: Record<string, unknown>; result: Record<string, unknown>; elapsed_ms: number }>;
  latency: Record<string, number | string>;
  session: { transcript: Array<{ role: string; content: string }>; turn_count: number };
};

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";

const samplePrompts = [
  { label: "Book", text: "Book an appointment with Dr Iyer tomorrow at 12" },
  { label: "Reschedule", text: "Change my appointment to tomorrow evening" },
  { label: "Cancel", text: "Cancel my appointment" },
  { label: "Hindi", text: "नमस्ते, appointment book karna hai kal 10 baje" },
  { label: "Tamil", text: "வணக்கம், நாளை appointment புக் செய்ய வேண்டும்" },
];

function App() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientId, setPatientId] = useState("p001");
  const [channel, setChannel] = useState<"inbound" | "outbound">("inbound");
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [input, setInput] = useState("Book an appointment with Dr Iyer tomorrow at 12");
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);

  useEffect(() => {
    fetch(`${API}/patients`).then((res) => res.json()).then(setPatients).catch(() => setPatients([]));
  }, []);

  const selectedPatient = useMemo(
    () => patients.find((patient) => patient.id === patientId),
    [patientId, patients],
  );

  async function sendTurn(nextInput = input) {
    setLoading(true);
    try {
      const res = await fetch(`${API}/agent/turn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          patient_id: patientId,
          audio_text: nextInput,
          channel,
          campaign_id: campaignId,
        }),
      });
      const data = await res.json();
      setResponse(data);
      speak(data.text, data.language);
    } finally {
      setLoading(false);
    }
  }

  async function startCampaign() {
    const params = new URLSearchParams({ patient_id: patientId });
    const res = await fetch(`${API}/campaigns/reminders?${params.toString()}`, { method: "POST" });
    const campaign = await res.json();
    setCampaignId(campaign.id);
    setChannel("outbound");
    setInput("No, not now please");
  }

  function useBrowserSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.lang = selectedPatient?.language_preference === "hi" ? "hi-IN" : selectedPatient?.language_preference === "ta" ? "ta-IN" : "en-IN";
    recognition.interimResults = false;
    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      sendTurn(transcript);
    };
    recognition.start();
  }

  function speak(text: string, language: Language) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === "hi" ? "hi-IN" : language === "ta" ? "ta-IN" : "en-IN";
    window.speechSynthesis.speak(utterance);
  }

  return (
    <main>
      <header className="topbar">
        <div className="brand">
          <div className="mark">
            <Stethoscope size={22} />
          </div>
          <div>
            <h1>Clinical Voice Agent</h1>
            <p>Appointment desk</p>
          </div>
        </div>
        <div className="topStats">
          <div className="metric">
            <Activity size={18} />
            <span>{response ? `${response.latency.first_audio_ready_ms} ms` : "ready"}</span>
            <small>first audio</small>
          </div>
          <div className="metric">
            <ShieldCheck size={18} />
            <span>{response?.trace.length ?? 0}</span>
            <small>tool calls</small>
          </div>
        </div>
      </header>

      <section className="workspace">
        <aside className="sidebar">
          <div className="panelTitle">
            <PhoneCall size={17} />
            <span>Call</span>
          </div>
          <label>
            Patient
            <select value={patientId} onChange={(event) => setPatientId(event.target.value)}>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>{patient.name}</option>
              ))}
            </select>
          </label>
          <div className="patientSummary">
            <strong>{selectedPatient?.name ?? "Patient"}</strong>
            <span>{selectedPatient?.phone}</span>
            <span className="languageTag"><Languages size={14} /> {selectedPatient?.language_preference.toUpperCase()}</span>
          </div>
          <div className="mode">
            <button className={channel === "inbound" ? "active" : ""} onClick={() => setChannel("inbound")}>
              <PhoneCall size={17} /> Inbound
            </button>
            <button className={channel === "outbound" ? "active" : ""} onClick={startCampaign}>
              <CalendarClock size={17} /> Reminder
            </button>
          </div>
          <button className="secondary" onClick={() => window.speechSynthesis.cancel()}>
            <Square size={17} /> Barge in
          </button>

          <div className="guardrails">
            <div><CheckCircle2 size={15} /> Verified slot</div>
            <div><CheckCircle2 size={15} /> Patient context</div>
            <div><CheckCircle2 size={15} /> Multilingual</div>
          </div>
        </aside>

        <section className="console">
          <div className="callHeader">
            <div>
              <h2>Live Conversation</h2>
              <p>{selectedPatient?.name ?? "Patient"} · {selectedPatient?.phone ?? "No phone"}</p>
            </div>
            <div className={`callBadge ${channel}`}>
              {channel === "inbound" ? <PhoneCall size={16} /> : <CalendarClock size={16} />}
              {channel}
            </div>
          </div>

          <div className="samples">
            {samplePrompts.map((prompt) => (
              <button key={prompt.label} onClick={() => setInput(prompt.text)}>{prompt.label}</button>
            ))}
          </div>

          <div className="composer">
            <textarea value={input} onChange={(event) => setInput(event.target.value)} />
            <div className="actions">
              <button title="Use browser microphone" onClick={useBrowserSpeech} disabled={listening}>
                <Mic size={18} /> {listening ? "Listening" : "Mic"}
              </button>
              <button onClick={() => sendTurn()} disabled={loading}>
                {loading ? <RefreshCw className="spin" size={18} /> : <Send size={18} />} Send
              </button>
            </div>
          </div>

          <div className="conversation">
            {(response?.session.transcript.length ? response.session.transcript : [
              { role: "agent", content: "Ready for the next patient request." },
            ]).map((turn, index) => (
              <div key={`${turn.role}-${index}`} className={`bubble ${turn.role}`}>
                <span>{turn.role}</span>
                {turn.content}
              </div>
            ))}
          </div>
        </section>

        <aside className="inspector">
          <div className="panelTitle">
            <Clock3 size={17} />
            <span>Details</span>
          </div>

          <div className="summaryCard">
            <span>Last response</span>
            <strong>{response?.text ?? "No turn yet"}</strong>
          </div>

          <h2>Trace</h2>
          {response?.trace.length ? response.trace.map((call, index) => (
            <div className="trace" key={`${call.name}-${index}`}>
              <strong>{call.name}</strong>
              <span>{call.elapsed_ms} ms</span>
              <pre>{JSON.stringify(call.result, null, 2)}</pre>
            </div>
          )) : <p className="empty">Tool calls appear here after each turn.</p>}

          <h2>Latency</h2>
          <pre className="latency">{JSON.stringify(response?.latency ?? {}, null, 2)}</pre>

          <h2>Memory</h2>
          <div className="memoryCard">
            <FileText size={16} />
            <span>{response?.session.turn_count ?? 0} turns</span>
            <span>{response?.language?.toUpperCase() ?? selectedPatient?.language_preference.toUpperCase() ?? "EN"}</span>
          </div>
        </aside>
      </section>
    </main>
  );
}

declare global {
  interface Window {
    SpeechRecognition?: typeof SpeechRecognition;
    webkitSpeechRecognition?: typeof SpeechRecognition;
  }
}

createRoot(document.getElementById("root")!).render(<App />);
