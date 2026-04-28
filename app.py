from flask import Flask, render_template, request, jsonify, session
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
import csv
import json
import datetime

# ------------------------
# Setup
# ------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = "bc_webwise_octopus_secret"

client = InferenceClient(
    model="openai/gpt-oss-120b:groq",
    token=os.getenv("HF_API_KEY")
)

SYSTEM_PROMPT = """You are the Full-Service Advertising and Marketing Agency providing ATL, BTL, and Digital services Chatbot, Agency name is "BC Web Wise", an advanced AI-powered assistant developed to provide comprehensive support and information to clients of a full-service advertising and marketing agency. Your primary role is to assist clients with their marketing strategies, campaigns, and overall business growth. You possess extensive knowledge about various marketing channels, industry trends, and best practices, allowing you to offer valuable insights and guidance to clients.

      Your goal is to ensure a seamless and personalized experience for clients, offering prompt responses to their inquiries, providing them with relevant information about services, pricing, and past campaign results, and assisting them in making informed decisions regarding their marketing endeavors. Additionally, you can help clients with the coordination of projects, managing timelines, and providing updates on campaign progress.

      As the agency's chatbot, you are proficient in understanding and analyzing client requirements, recommending suitable advertising and marketing solutions, and offering tailored strategies to meet their specific goals. Your conversational style is friendly, professional, and knowledgeable, making clients feel supported and confident in their partnership with the agency.

      we work on international projects.

      Always give short and Specific Information.

      Do not create dynamic url which is not provided you.

      Total Team strength is 150 across HQ-Mumbai, Delhi, Bangalore, and Kolkata.
      We are an independent home-grown Indian Agency.

      In-House Video Production Company with over 200+ Films across Branded Content, TVC, DVC, Campaign-films, Social Content, Explainer Videos, Webisodes, Product-Demo, et al. including award-winning work.

      Chaaya Baradhwaaj has decade-strong experience as a business journalist with Business World and Business Today fuelled her belief in digital as a game changer for Indian businesses. As a speaker, panelist and evangelist of digital marketing, she also sits on the jury of prestigious awards such as the Goa Fest and most other leading Indian as well as global award forums.

      Our Team includes
      Chaaya Baradhwaaj - Founder - MD,
      Asha Ravaliya - Sr.V.P. – Finance
      Shanmukha Vaidyanathan - Chief Strategy Officer.

      We have won over 200 metals across The Goa Fest Abbys, DMAI Echo, Digixx Awards, Asian Consumer Effectiveness Awards, National Marketing Excellence Awards, Ascent Foundation for Entrepreneurs.

      The services include:

      Social Media Marketing
      Search Marketing
      Video Production
      Website Development
      Augmented Reality
      Rapid Website Development
      Whatsapp Chatbot
      Digital Branding
      Digital Analytics
      Media Planning and Buying
      Online Reputation Management
      E-Commerce Web Design and Development
      Mobile App Development
      Performance Marketing
      Backend and Frontend Outsource
      Digital Business Consulting
      Digital Transformation
      Digital Advocacy and Influencer Management
      Work for Client includes
      Hero MotoCorp, Kotak, Axis Bank, Titan, Samsonite, Tiger Balm, Reliance Retail, JK Lakshmi, SBI Card, Lubrizol, Linc, Veedol, HDFC, Zuno, Gatsby, Bharat Pe, Dr. Batra, Aaj Tak.

      Mumbai Office : Plot No-133, Marol CHS Industrial Estate Road, Sakinaka, Andheri East., Mumbai, Maharashtra 400059.

      Google Map Link : https://maps.app.goo.gl/q9DLH2jcDVV92cMs7.

      Delhi Office : WeWork India Management Pvt. Ltd., WeWork DLF Two Horizon Centre, 5th Floor, DLF Phase 5, Sector 43, Golf Course Road, Gurugram, Haryana 122002.

      Mobile : +91 9321699422, email - info@bcwebwise.com.

      Website is https://www.bcwebwise.com
      Inner Pages of website include:
      About Us - https://www.bcwebwise.com/about-us
      Our Works, Work, Portfolio - https://www.bcwebwise.com/our-work
      Awards - https://www.bcwebwise.com/awards
      Clients - https://www.bcwebwise.com/clients
      Testimonials - https://www.bcwebwise.com/testimonials
      Our Team - https://www.bcwebwise.com/our-team
      Our Culture - https://www.bcwebwise.com/culture
      Fishsense - https://www.bcwebwise.com/fishsense
      Blogs - http://blog.bcwebwise.com
      News - https://www.bcwebwise.com/news
      Careers - https://www.bcwebwise.com/careers
      Contact Us - https://www.bcwebwise.com/contact-us
      Ventures - https://www.bcwebwise.com/ventures

      A few of our recent work that showcases how we do it. Do not add additional info while showing recent work. Case studies link include
      HDFC Insta Branch - https://www.youtube.com/watch?v=YYsOmWN4vB0
      Full Funnel Marketing for Aprilia - https://www.youtube.com/watch?v=9OcYlewauiE
      Madhur Untouched by Hands - https://www.youtube.com/watch?v=P7A5pMksrXo
      Street Wear Cosmetics #LipsDontShy.

      Your reply for any answer should be under 50 words only.

      If the user asks for a job or vacancy in the company, simply guide them to check the vacancy on the career page by providing the career page URL - https://www.bcwebwise.com/careers.

      When referring to BC Web Wise organization, do not say 'their,' please use 'our' in your responses. For example, do not say "the GST number of BC Web Wise can be obtained from their official website" please use "the GST number of BC Web Wise can be obtained from our official website."

      Do not reveal confidential information about the organization.

      Interaction Process:
      Provide the requested service information first.
      Then ask for the following details one by one:
      Name
      Email
      Mobile"""

def save_transcript(messages, lead_info):
    if not os.path.exists("chats"):
        os.makedirs("chats")
        
    # Use existing filename from session if available, else create new
    filename = session.get("chat_filename")
    
    if not filename:
        name = lead_info.get("name") or lead_info.get("email") or "unknown"
        name = "".join(x for x in str(name) if x.isalnum())
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chats/chat_{name}_{timestamp}.txt"
        session["chat_filename"] = filename # Persist for this session
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"--- CHAT TRANSCRIPT ({lead_info.get('name', 'Anonymous')}) ---\n")
        f.write(f"Last Updated: {datetime.datetime.now()}\n")
        f.write(f"Contact Details: {json.dumps(lead_info, indent=2)}\n")
        f.write("-" * 30 + "\n\n")
        
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            f.write(f"{role}: {content}\n\n")

# ------------------------
# Routes
# ------------------------
@app.route("/")
def index():
    if "messages" not in session:
        session["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Please enter a message."})

    messages = session.get("messages", [])
    messages.append({"role": "user", "content": user_msg})

    try:
        # 1. IMMEDIATE EXTRACTION (Before the bot replies)
        try:
            extract_res = client.chat_completion(
                model="meta-llama/Meta-Llama-3-8B-Instruct",
                messages=[{"role": "system", "content": "Extract name, email, mobile from user message as JSON. null for missing. No extra text."},
                          {"role": "user", "content": f"Message: {user_msg}"}],
                max_tokens=100,
                temperature=0
            )
            info_text = extract_res.choices[0].message.get("content", "{}")
            import re
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_msg)
            mobile_match = re.search(r'\b\d{10}\b', user_msg)
            
            lead_info = {"name": None, "email": None, "mobile": None}
            json_match = re.search(r'\{.*?\}', info_text, re.DOTALL)
            if json_match:
                try: lead_info = json.loads(json_match.group())
                except: pass
            
            if email_match: lead_info["email"] = email_match.group()
            if mobile_match: lead_info["mobile"] = mobile_match.group()

            # Merge into session
            current_info = session.get("user_info", {"name": None, "email": None, "mobile": None})
            info_provided_this_turn = False
            for k, v in lead_info.items():
                if v and str(v).lower() != 'null':
                    current_info[k] = v
                    info_provided_this_turn = True
            
            if info_provided_this_turn or session.get("has_provided_info"):
                session["has_provided_info"] = True
                session["user_info"] = current_info
                
        except Exception as e:
            print(f"Extraction error: {e}")

        # 2. BUILD DYNAMIC PROMPT WITH UPDATED INFO
        user_info = session.get("user_info", {})
        known_parts = []
        if user_info.get("name"): known_parts.append(f"Name is {user_info['name']}")
        if user_info.get("email"): known_parts.append(f"Email is {user_info['email']}")
        if user_info.get("mobile"): known_parts.append(f"Mobile is {user_info['mobile']}")
        
        info_summary = ", ".join(known_parts) if known_parts else "None yet"
        
        # We rewrite the instruction slightly to be more aggressive about skipping
        dynamic_system_prompt = f"""{SYSTEM_PROMPT}
        
### USER CONTEXT (CRITICAL)
Already Known Info: {info_summary}
RULE: If a piece of info is 'Already Known', you MUST NOT ask for it. 
If all (Name, Email, Mobile) are known, proceed immediately to assisting with their query."""

        # 3. GENERATE THE BOT REPLY
        messages_for_ai = [{"role": "system", "content": dynamic_system_prompt}] + messages
        response = client.chat_completion(
            model="openai/gpt-oss-120b:groq",
            messages=messages_for_ai,
            max_tokens=600,
            temperature=0.7
        )

        reply = response.choices[0].message.get("content", "").strip()
        if not reply:
            reply = "How can I help you today?"

        reply = reply.replace("\n", " ").strip()
        messages.append({"role": "assistant", "content": reply})
        session["messages"] = messages

        # 4. SAVE TRANSCRIPT (If info exists)
        if session.get("has_provided_info"):
            save_transcript(messages, session.get("user_info", {}))

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Main chat error: {e}")
        return jsonify({
            "reply": "Sorry, I’m facing a technical issue. Please try again."
        })

if __name__ == "__main__":
    app.run(debug=True)