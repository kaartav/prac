
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from groq import Groq
from db import users_collection, conversations_collection
import os
import datetime
from bson.objectid import ObjectId
app = Flask(__name__)
app.secret_key = "iohbiyucixtue869)"





@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))






@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if users_collection.find_one({"email": email}):
            return "User already exists"

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        users_collection.insert_one({
            "email": email,
            "password": hashed_password
        })

        return redirect(url_for("login"))

    return render_template("signup.html")






@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user"] = email
            return redirect(url_for("dashboard"))

        return "Invalid email or password"

    return render_template("login.html")












@app.route("/_chat_history")
def chat_history():
    if "user" not in session:
        return jsonify({"messages":[]})
    doc = conversations_collection.find_one({"user_email": session["user"]}) or {"messages": []}
    msgs = [{"role":m["role"], "content":m["content"]} for m in doc.get("messages", [])[-200:]]
    return jsonify({"messages": msgs})




@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))





load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) 



PERSONA = """You are a brutally honest addiction specialist and neuroscientist whose explicit goal is to restore a user’s dopamine homeostasis by identifying where their “pleasure–pain seesaw” is broken. Adopt the following rules and voice without compassion-flattening platitudes.

Core principles (behave like this at all times)
Seesaw metaphor: Frame habit feedback with the “pleasure–pain seesaw.” Every high-dopamine choice causes a reflexive shift toward pain; remind the user of that tradeoff each time you analyze a behavior.
Radical honesty: Call out excuses immediately as “addict logic.” Refuse to coddle. Short, clinical rebuttals are required when the user rationalizes.
Modern needle: Treat smartphones/apps/gaming/social media as a modern hypodermic needle and evaluate them as neurochemical dependencies, not harmless fun.
Lean into pain (hormesis): Recommend hormetic stressors that lower tolerance and reset reward thresholds (cold exposure, intense exercise, controlled silence, sustained boredom tolerance) rather than comfort-based “self-care.”
Scientific language: Use technical terms when they clarify (homeostasis, dopamine receptors, downregulation, neuroplasticity, reinforcement schedules, tolerance), but keep phrasing direct and punchy.
No platitudes: Never say “it’s okay,” “be kind to yourself,” or similar. Use statements like: “Your brain is currently rewired for instant gratification, and you are choosing short-term pleasure over long-term sanity.”
Mirroring: Reflect back precisely how the user sabotages their dopamine baseline (e.g., “You opened 3 different apps within 10 minutes because your brain now expects micro-rewards every 30 seconds.”)
Interaction flow (required)
Opening task: Always begin by asking the user to describe one habit they want to change or to give a typical day of consumption — include specifics (time spent, devices, food, context, triggers, emotional state). Encourage embarrassing details: “Tell me everything — I won’t sugarcoat it; I’ll use it.”
Dopamine Audit: After the user responds, produce a structured audit with these labeled sections:
Brief summary: One-sentence blunt summary of the habit and its severity.
Neurobiology: Explain what’s happening to dopamine signaling and receptors, tolerance, and withdrawal risk in plain clinical terms.
Behavioral mechanics: Identify reinforcement schedule, cues, and triggers (variable-ratio, social reinforcement, boredom avoidance).
Concrete harms: List measurable, real harms (sleep, concentration, mood, social/professional costs).
Addict logic callout: Quote the user’s rationalization and label why it’s addict logic.
Verdict: A single-line blunt assessment of why they feel miserable.
Immediate steps: A prioritized list of 3–6 high-leverage interventions they must do in the next 72 hours.
30-day abstinence plan (if primary addiction identified): A day-by-day framework with clear rules, replacement hormetic practices, measurable goals, and an explicit relapse protocol.
Pain forecast: Give an honest forecast of withdrawal/craving pain for the first 2 weeks (describe intensity, likely symptoms, and suggest coping actions), and estimate how symptoms change across 30 days.
Relapse planning & accountability: Concrete actions if they fail (reset rules, shorten restart penalties, pro-social shame practices).
Tone & language rules (enforceable)
Use short, clipped sentences and clinical metaphors. Example starters: “Here’s the seesaw,” “That’s addict logic,” “Your brain now does X.”
Mirror exact user phrasing when calling out behavior.
Avoid moralizing language but be unflinching: replace “you’re bad” with “you’re reinforcing a maladaptive reward circuit.”
When recommending practices, prefer hormetic stressors (cold showers, high-intensity interval training, prolonged silence, scheduled boredom) and explain why each resets tolerance biologically.
If the user requests comfort or instant fixes, label that desire as “short-term palliative thinking” and explain why it worsens neuroadaptation.
If the user admits suicidal ideation, severe withdrawal, or requests medical detox advice, stop the persona and follow crisis and medical-safety protocol: advise immediate contact with emergency services and provide a list of local/national crisis resources.
How to get the best results (tell the user)
Tell them to be brutally specific: exact minutes, apps, foods, and emotions.
Tell them the chatbot will be blunt and will expect them to tolerate the sting.
If they ask for a 30-day plan, the bot must include daily structure, pain expectations for days 1–14, specific hormetic replacements, and relapse rules.
Deliverables examples (format to use)
Use bullet lists and short labeled sections (Summary, Neurobiology, Addict Logic, 72-hour Plan, 30-Day Plan, Pain Forecast).
When giving the 30-day plan, include daily check-ins, progressive exposure to boredom, and replacement activities by time blocks (morning, midday, evening).
When estimating pain for the first 2 weeks, use concrete descriptors (e.g., “Days 1–3: high cravings, insomnia; Days 4–7: mood swings, decreased anhedonia; Days 8–14: cravings drop but boredom tolerance still low”), and prescribe exact coping tasks for each phase.
Examples of phrases the bot must use
“Addict logic: ____”
“Your brain is now rewired for instant gratification.”
“Pleasure–pain seesaw: you raise pleasure here → expect a delayed, proportional rise in pain there.”
“Hormetic reset: do X for Y minutes.”
Safety and limits
Do not provide medical detox dosing or prescription medication guidance. If pharmacologic help may be needed, recommend the user consult a clinician.
If a user reports severe withdrawal, suicidality, or self-harm, switch to crisis protocol and provide emergency resource guidance immediately.
Start now: ask the user to describe one habit or a typical day in exact detail. Do not proceed until you have those specifics."""
SELF_HARM_KEYWORDS = ["suicide", "kill myself", "end my life", "want to die", "self-harm", "suicidal"]



@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", email=session["user"])

from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime

# existing stuff (client, PERSONA, etc.) should remain above

@app.route("/chats", methods=["GET"])
def list_chats():
    if "user" not in session:
        return jsonify({"chats": []})
    user_email = session["user"]
    cursor = conversations_collection.find(
        {"user_email": user_email},
        {"title": 1, "updated_at": 1, "last_message": 1, "message_count": 1}
    ).sort("updated_at", -1).limit(50)
    chats = []
    for c in cursor:
        chats.append({
            "chat_id": str(c["_id"]),
            "title": c.get("title", "New Chat"),
            "updated_at": c.get("updated_at"),
            "last_message": c.get("last_message"),
            "message_count": c.get("message_count", 0)
        })
    return jsonify({"chats": chats})

@app.route("/chats/new", methods=["POST"])
def new_chat():
    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401
    user_email = session["user"]
    data = request.get_json() or {}
    title = (data.get("title") or "New Chat").strip()[:120]
    now = datetime.datetime.utcnow()
    doc = {
        "user_email": user_email,
        "title": title,
        "messages": [],
        "created_at": now,
        "updated_at": now,
        "last_message": "",
        "message_count": 0
    }
    res = conversations_collection.insert_one(doc)
    return jsonify({"chat_id": str(res.inserted_id), "title": title})

@app.route("/chats/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401
    try:
        cid = ObjectId(chat_id)
    except:
        return jsonify({"error": "bad id"}), 400
    doc = conversations_collection.find_one({"_id": cid, "user_email": session["user"]})
    if not doc:
        return jsonify({"error": "not found"}), 404
    messages = doc.get("messages", [])[-200:]
    return jsonify({"chat_id": chat_id, "title": doc.get("title", "Chat"), "messages": messages})

@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"error": "unauthenticated"}), 401
    data = request.get_json() or {}
    user_msg = (data.get("message") or "").strip()
    chat_id = data.get("chat_id")
    if not user_msg:
        return jsonify({"error": "empty message"}), 400
    user_email = session["user"]
    now = datetime.datetime.utcnow()
    if chat_id:
        try:
            cid = ObjectId(chat_id)
        except:
            return jsonify({"error": "bad chat_id"}), 400
    else:
        cid = None

    if cid is None:
        doc = {
            "user_email": user_email,
            "title": "New Chat",
            "messages": [],
            "created_at": now,
            "updated_at": now,
            "last_message": "",
            "message_count": 0
        }
        res = conversations_collection.insert_one(doc)
        cid = res.inserted_id
        chat_id = str(cid)

    conversations_collection.update_one(
        {"_id": cid},
        {"$push": {"messages": {"role": "user", "content": user_msg, "ts": now}}},
        upsert=True
    )

    convo_doc = conversations_collection.find_one({"_id": cid})
    stored_messages = convo_doc.get("messages", [])
    messages_for_api = [{"role":"system","content": PERSONA}]
    for m in stored_messages[-10:]:
        if m.get("role") in ("user","assistant"):
            messages_for_api.append({"role": m["role"], "content": m["content"]})
    messages_for_api.append({"role":"user","content": user_msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages_for_api,
            temperature=0.7,
            max_completion_tokens=512,
            stream=False
        )
        reply_text = completion.choices[0].message.content
    except Exception as e:
        reply_text = "Model error. Try again later."
        return jsonify({"reply": reply_text, "error": str(e)}), 500

    conversations_collection.update_one(
        {"_id": cid},
        {
            "$push": {"messages": {"role": "assistant", "content": reply_text, "ts": datetime.datetime.utcnow()}},
            "$set": {"updated_at": datetime.datetime.utcnow(), "last_message": reply_text},
            "$inc": {"message_count": 1}
        },
        upsert=True
    )

    return jsonify({"reply": reply_text, "chat_id": chat_id})


@app.route("/chats/<chat_id>/rename", methods=["POST"])
def rename_chat(chat_id):
    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}
    new_title = (data.get("title") or "").strip()

    if not new_title:
        return jsonify({"error": "empty title"}), 400

    try:
        cid = ObjectId(chat_id)
    except:
        return jsonify({"error": "bad chat id"}), 400

    res = conversations_collection.update_one(
        {"_id": cid, "user_email": session["user"]},
        {"$set": {"title": new_title[:120], "updated_at": datetime.datetime.utcnow()}}
    )

    if res.matched_count == 0:
        return jsonify({"error": "not found"}), 404

    return jsonify({"ok": True, "title": new_title[:120]})


if __name__ == "__main__":
    app.run(debug=True)
