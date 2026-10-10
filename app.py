from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re, uuid

app = Flask(__name__)

INCIDENTS = []

KEYWORDS = {
    "phishing": ["otp", "one time password", "password", "verify your account", "account will be deleted",
                 "login immediately", "credential", "bank details"],
    "scam": ["you won", "winner", "prize", "claim", "free money", "send money", "gift card", "lottery"],
    "cyberbullying": ["useless", "idiot", "stupid", "everyone hates you", "loser", "nobody likes you"],
    "harassment": ["i will hurt you", "i'll hurt you", "threat", "watch yourself", "i know where you live"],
    "privacy_risk": ["address", "phone number", "aadhar", "aadhaar", "otp", "date of birth", "personal information"]
}

def analyze_content(content, kind="message"):
    text = content.lower()
    scores = {k: 0 for k in KEYWORDS}
    reasons = []

    for category, words in KEYWORDS.items():
        for word in words:
            if word in text:
                scores[category] += 1
                reasons.append(f"Detected indicator: “{word}”")

    # URL heuristics
    urls = re.findall(r'https?://\S+|www\.\S+', text)
    if urls:
        suspicious = any(
            len(u) > 45 or
            any(x in u for x in ["verify", "login", "secure", "claim", "update"]) or
            u.count("-") >= 3
            for u in urls
        )
        if suspicious:
            scores["phishing"] += 2
            reasons.append("The URL contains patterns commonly associated with suspicious links.")

    # Deterministic risk score for MVP
    raw = max(scores.values()) * 22
    if len(reasons) >= 3:
        raw += 20
    elif len(reasons) == 2:
        raw += 10

    if "otp" in text and ("send" in text or "share" in text or "give" in text):
        raw += 25
        reasons.append("The content asks the user to share an OTP.")

    risk = min(100, max(5, raw))
    category = max(scores, key=scores.get)

    if max(scores.values()) == 0:
        category = "safe"
        risk = 8
        reasons = ["No strong threat indicators were detected by the MVP rules."]

    if risk >= 81:
        severity = "CRITICAL"
        recommendation = "Do not respond, click links, or share passwords/OTPs. Report the incident to a trusted adult or school safety team."
    elif risk >= 61:
        severity = "HIGH"
        recommendation = "Be cautious. Avoid replying or sharing personal information and consider reporting it."
    elif risk >= 31:
        severity = "MEDIUM"
        recommendation = "Review the message carefully and avoid sharing sensitive information."
    else:
        severity = "LOW"
        recommendation = "No immediate action is required, but stay alert online."

    return {
        "category": category.replace("_", " ").title(),
        "riskScore": risk,
        "severity": severity,
        "reasons": reasons[:5],
        "recommendation": recommendation
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/api/analyze")
def analyze():
    data = request.get_json(force=True)
    content = (data.get("content") or "").strip()
    kind = data.get("type", "message")

    if not content:
        return jsonify({"error": "Please enter a message or URL."}), 400

    result = analyze_content(content, kind)
    incident = {
        "incidentId": "INC-" + uuid.uuid4().hex[:8].upper(),
        "student": "Demo Student",
        "type": kind,
        "content": content,
        "category": result["category"],
        "riskScore": result["riskScore"],
        "severity": result["severity"],
        "recommendation": result["recommendation"],
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Open"
    }
    INCIDENTS.insert(0, incident)
    return jsonify(result | {"incidentId": incident["incidentId"]})

@app.get("/api/incidents")
def incidents():
    return jsonify(INCIDENTS)

@app.get("/api/dashboard")
def dashboard():
    total = len(INCIDENTS)
    critical = sum(i["severity"] == "CRITICAL" for i in INCIDENTS)
    high = sum(i["severity"] == "HIGH" for i in INCIDENTS)
    resolved = sum(i["status"] == "Resolved" for i in INCIDENTS)
    return jsonify({
        "students": 1250,
        "incidents": total,
        "critical": critical,
        "high": high,
        "resolved": resolved
    })

@app.post("/api/incidents/<incident_id>/resolve")
def resolve(incident_id):
    for incident in INCIDENTS:
        if incident["incidentId"] == incident_id:
            incident["status"] = "Resolved"
            return jsonify({"ok": True})
    return jsonify({"error": "Incident not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
