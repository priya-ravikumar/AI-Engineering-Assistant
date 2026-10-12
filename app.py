
import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
DATABASE = "engineering.db"

# Gemini is optional: the application also works without an API key.
client = None
if os.getenv("GEMINI_API_KEY"):
    try:
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    except Exception as exc:
        print("Gemini initialization failed:", exc)


# ---------------- DATABASE ----------------

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment TEXT NOT NULL,
                issue TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TEXT NOT NULL
            )
        """)


# ---------------- AI ASSISTANT ----------------

def get_ai_reply(message):
    if client:
        try:
            prompt = f"""
You are a safety-conscious industrial engineering assistant.
Explain possible causes and safe initial checks in simple English.
Do not claim a confirmed diagnosis or invent sensor measurements.
Never recommend bypassing safety systems or performing dangerous
repairs. If danger is possible, advise stopping the equipment
according to site procedures and contacting a qualified engineer.

User's reported issue: {message}
"""
            result = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if result.text:
                return result.text
        except Exception as exc:
            print("Gemini request failed:", exc)

    # Local fallback: works without internet or a Gemini API key.
    text = message.lower()

    if "temperature" in text or "overheat" in text:
        return (
            "Possible causes: insufficient cooling, blocked ventilation, "
            "or equipment overload. Stop the equipment safely if it is "
            "overheating and follow site procedures. Request a qualified "
            "technician to inspect it before restarting."
        )

    if "vibration" in text or "noise" in text:
        return (
            "Possible causes include misalignment, loose components, "
            "or bearing wear. Severe vibration or unusual noise may "
            "indicate a safety risk. Follow site shutdown procedures "
            "and request a qualified inspection."
        )

    if "leak" in text or "pressure" in text:
        return (
            "A leak or abnormal pressure may indicate a system fault. "
            "Keep clear of hazardous fluids or pressurized components. "
            "Follow emergency and site safety procedures and notify "
            "the responsible technician."
        )

    if "power" in text or "not starting" in text:
        return (
            "Possible causes include a power supply issue, a safety "
            "interlock, or a component fault. Check only approved "
            "external indicators. Do not open electrical panels. "
            "Contact an authorized technician if the issue continues."
        )

    return (
        "Please provide the equipment name, symptoms, warning indicators, "
        "and when the issue started. The cause needs to be verified by "
        "a qualified engineer. If there is an immediate safety risk, "
        "stop work and follow your site's safety procedures."
    )


# ---------------- FRONTEND ----------------

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Engineering Assistant</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f1f5f9;color:#172033;
font-family:Arial,Helvetica,sans-serif}
header{background:#10243b;color:white;padding:24px 6%}
header h1{margin:0;font-size:27px}
header p{color:#cbd5e1;margin-bottom:0}
main{max-width:1150px;margin:26px auto;padding:0 18px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}
.card,.panel{background:white;padding:20px;border-radius:12px;
box-shadow:0 3px 14px #0f172a0b}
.card span{color:#64748b;font-size:14px}
.card strong{display:block;font-size:30px;margin-top:10px}
.layout{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:20px}
h2{font-size:19px;margin-top:0}
.hint{font-size:13px;color:#64748b;line-height:1.5}
label{display:block;font-size:13px;font-weight:bold;margin:13px 0 6px}
input,textarea,select{width:100%;padding:11px;border:1px solid #cbd5e1;
border-radius:7px;font:inherit;background:white;color:#172033}
textarea{min-height:90px;resize:vertical}
button{border:0;border-radius:7px;background:#1769aa;color:white;
padding:11px 15px;cursor:pointer;font-weight:bold;margin-top:12px}
button:hover{background:#124f80}
button:disabled{opacity:.6;cursor:wait}
.result{background:#eff6ff;padding:14px;border-radius:8px;
margin-top:14px;white-space:pre-wrap;line-height:1.55;font-size:14px}
.tablewrap{margin-top:20px;overflow-x:auto}
table{width:100%;border-collapse:collapse;min-width:670px}
th,td{text-align:left;padding:12px;border-bottom:1px solid #e2e8f0;
font-size:13px;vertical-align:top}
th{background:#f8fafc}
td select{min-width:110px;padding:7px}
footer{text-align:center;padding:25px;color:#64748b;font-size:12px}
@media(max-width:720px){
 .stats,.layout{grid-template-columns:1fr}
 header{padding:22px}
}
</style>
</head>
<body>
<header>
  <h1>AI Engineering Assistant</h1>
  <p>Equipment troubleshooting · Maintenance tickets · Issue tracking</p>
</header>

<main>
  <section class="stats">
    <div class="card"><span>Total Tickets</span><strong id="total">0</strong></div>
    <div class="card"><span>Open Issues</span><strong id="open">0</strong></div>
    <div class="card"><span>Resolved Issues</span><strong id="resolved">0</strong></div>
  </section>

  <section class="layout">
    <div class="panel">
      <h2>AI Troubleshooting Assistant</h2>
      <p class="hint">Describe the equipment problem to receive initial guidance.</p>
      <form id="chatForm">
        <label for="message">Describe the problem</label>
        <textarea id="message" maxlength="2000" required
        placeholder="Example: The machine temperature is increasing..."></textarea>
        <button type="submit">Analyse Issue</button>
      </form>
      <div id="answer" class="result" hidden></div>
    </div>

    <div class="panel">
      <h2>Create Maintenance Ticket</h2>
      <p class="hint">Record an issue so it can be tracked and resolved.</p>
      <form id="ticketForm">
        <label for="equipment">Equipment Name</label>
        <input id="equipment" maxlength="100" required
        placeholder="Example: Industrial Pump 01">
        <label for="issue">Issue Description</label>
        <textarea id="issue" maxlength="2000" required
        placeholder="Describe the observed problem"></textarea>
        <label for="priority">Priority</label>
        <select id="priority">
          <option>Low</option>
          <option selected>Medium</option>
          <option>High</option>
        </select>
        <button type="submit">Create Ticket</button>
      </form>
      <div id="ticketMessage" class="result" hidden></div>
    </div>
  </section>

  <section class="panel tablewrap">
    <h2>Maintenance Ticket Dashboard</h2>
    <p class="hint">Update the status of each ticket as work progresses.</p>
    <table>
      <thead>
        <tr><th>ID</th><th>Equipment</th><th>Issue</th>
        <th>Priority</th><th>Status</th><th>Update</th></tr>
      </thead>
      <tbody id="tickets"></tbody>
    </table>
    <p id="empty" class="hint">No tickets yet. Create your first ticket above.</p>
  </section>
</main>

<footer>Portfolio prototype · AI guidance must be verified by a qualified engineer</footer>

<script>
async function api(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
}

function jsonOptions(method, body) {
  return {
    method,
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  };
}

async function loadDashboard() {
  try {
    const data = await api('/api/tickets');
    document.getElementById('total').textContent = data.total;
    document.getElementById('open').textContent = data.open;
    document.getElementById('resolved').textContent = data.resolved;

    const tbody = document.getElementById('tickets');
    tbody.replaceChildren();
    document.getElementById('empty').hidden = data.items.length > 0;

    data.items.forEach(ticket => {
      const tr = document.createElement('tr');

      [ticket.id, ticket.equipment, ticket.issue, ticket.priority,
       ticket.status].forEach(value => {
        const td = document.createElement('td');
        td.textContent = value;
        tr.appendChild(td);
      });

      const actionCell = document.createElement('td');
      const select = document.createElement('select');

      ['Open','In Progress','Resolved'].forEach(status => {
        const option = document.createElement('option');
        option.value = status;
        option.textContent = status;
        option.selected = status === ticket.status;
        select.appendChild(option);
      });

      select.addEventListener('change', async () => {
        select.disabled = true;
        try {
          await api('/api/tickets/' + ticket.id,
            jsonOptions('PATCH', {status:select.value}));
          await loadDashboard();
        } catch (error) {
          alert(error.message);
          await loadDashboard();
        }
      });

      actionCell.appendChild(select);
      tr.appendChild(actionCell);
      tbody.appendChild(tr);
    });
  } catch (error) {
    document.getElementById('empty').textContent =
      'Unable to load tickets. Refresh the page and try again.';
  }
}

document.getElementById('chatForm').addEventListener('submit',
async event => {
  event.preventDefault();
  const button = event.submitter;
  const answer = document.getElementById('answer');
  button.disabled = true;
  button.textContent = 'Analysing...';
  answer.hidden = false;
  answer.textContent = 'Please wait...';

  try {
    const data = await api('/api/chat', jsonOptions('POST', {
      message:document.getElementById('message').value
    }));
    answer.textContent = data.reply;
  } catch (error) {
    answer.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = 'Analyse Issue';
  }
});

document.getElementById('ticketForm').addEventListener('submit',
async event => {
  event.preventDefault();
  const button = event.submitter;
  const message = document.getElementById('ticketMessage');
  button.disabled = true;
  button.textContent = 'Saving...';

  try {
    const data = await api('/api/tickets', jsonOptions('POST', {
      equipment:document.getElementById('equipment').value,
      issue:document.getElementById('issue').value,
      priority:document.getElementById('priority').value
    }));
    message.hidden = false;
    message.textContent = 'Ticket #' + data.id + ' created successfully.';
    event.target.reset();
    await loadDashboard();
  } catch (error) {
    message.hidden = false;
    message.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = 'Create Ticket';
  }
});

loadDashboard();
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE)


# ---------------- CHAT API ----------------

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify(error="Please enter an equipment issue."), 400
    if len(message) > 2000:
        return jsonify(error="Issue must be under 2000 characters."), 400

    return jsonify(reply=get_ai_reply(message))


# ---------------- TICKET APIs ----------------

@app.route("/api/tickets", methods=["GET"])
def list_tickets():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM tickets ORDER BY id DESC"
        ).fetchall()

    items = [dict(row) for row in rows]
    return jsonify(
        items=items,
        total=len(items),
        open=sum(t["status"] == "Open" for t in items),
        resolved=sum(t["status"] == "Resolved" for t in items)
    )


@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(silent=True) or {}

    equipment = str(data.get("equipment", "")).strip()
    issue = str(data.get("issue", "")).strip()
    priority = str(data.get("priority", "Medium")).strip().title()

    if not equipment or not issue:
        return jsonify(error="Equipment name and issue are required."), 400
    if len(equipment) > 100 or len(issue) > 2000:
        return jsonify(error="Please shorten the entered details."), 400
    if priority not in ("Low", "Medium", "High"):
        return jsonify(error="Invalid priority."), 400

    created_at = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO tickets
            (equipment, issue, priority, status, created_at)
            VALUES (?, ?, ?, 'Open', ?)
        """, (equipment, issue, priority, created_at))
        ticket_id = cursor.lastrowid

    return jsonify(id=ticket_id, status="Open"), 201


@app.route("/api/tickets/<int:ticket_id>", methods=["PATCH"])
def update_ticket(ticket_id):
    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).strip()

    if status not in ("Open", "In Progress", "Resolved"):
        return jsonify(error="Invalid ticket status."), 400

    with get_db() as db:
        cursor = db.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (status, ticket_id)
        )

        if cursor.rowcount == 0:
            return jsonify(error="Ticket not found."), 404

    return jsonify(id=ticket_id, status=status)


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    init_db()
    print("Engineering Assistant is starting...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=False, port=5000)
