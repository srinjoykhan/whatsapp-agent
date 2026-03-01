# 🤖 WhatsApp AI Bot with LangChain & Hugging Face

This project is a fully functional, AI-powered WhatsApp chatbot. It uses the official Meta WhatsApp Cloud API to receive and send messages, and a LangChain Agent powered by a free Hugging Face open-source LLM (like Qwen) to generate intelligent, context-aware responses.

Best of all, this setup is designed to be hosted **100% for free** using Render.

---

## 📋 Prerequisites

Before you begin, make sure you have the following accounts created:

1. **[Meta for Developers](https://developers.facebook.com/)**: To access the WhatsApp API.
2. **[Hugging Face](https://huggingface.co/)**: To get a free API token for the AI model.
3. **[GitHub](https://github.com/)**: To store your code for deployment.
4. **[Render](https://render.com/)**: To host your bot 24/7 for free.
5. **Python 3.9+** installed on your computer.

---

## 🚀 Step 1: Meta WhatsApp API Setup

1. Go to [Meta for Developers](https://developers.facebook.com/) and click **My Apps** -> **Create App**.
2. Select **Connect with customers through WhatsApp** (under the "Business messaging" use case) and click Next.
3. Link or create a Meta Business Portfolio and finish creating the app.
4. In your App Dashboard, navigate to **WhatsApp** -> **API Setup** (you may need to click "Customize" on your use case first).
5. Copy the following credentials:
* **Temporary Access Token**
* **Phone Number ID**


6. Scroll down to the **To** field, select **Manage phone number list**, and add your personal WhatsApp number to verify it. *(You can only send test messages to verified numbers).*

## 🧠 Step 2: Hugging Face Setup

1. Log in to [Hugging Face](https://huggingface.co/).
2. Go to your **Settings** -> **Access Tokens**.
3. Create a new token (a **Read** token is sufficient) and copy it.

---

## 💻 Step 3: Local Setup (Optional but Recommended)

To test the bot on your computer before putting it on the internet:

**1. Clone the repository and install dependencies:**

```bash
git clone <your-repository-url>
cd <your-repository-folder>
pip install -r requirements.txt

```

**2. Create a `.env` file in the root folder and add your keys:**

```env
WHATSAPP_ACCESS_TOKEN=your_meta_access_token
PHONE_NUMBER_ID=your_meta_phone_number_id
WEBHOOK_VERIFY_TOKEN=my_secret_token_123
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token

```

**3. Run the local server:**

```bash
python agent_bot.py

```

**4. Expose your local server to the internet using ngrok (in a new terminal):**

```bash
ngrok http 5000

```

*(Copy the `https` forwarding URL ngrok gives you, e.g., `https://xxxx.ngrok-free.app`)*

---

## ☁️ Step 4: Cloud Deployment (Render)

To keep the bot running 24/7 when your computer is off, we deploy it to Render.

1. Ensure your code is pushed to a **private** GitHub repository. Do NOT upload your `.env` file.
2. Go to [Render.com](https://render.com/) and create a **New Web Service**.
3. Connect your GitHub account and select your repository.
4. Configure the deployment:
* **Runtime:** Python 3
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn agent_bot:app`
* **Instance Type:** Free


5. Scroll down to **Environment Variables** and add all four variables from your `.env` file.
6. Click **Create Web Service**.
7. Once the build finishes and says "Live", copy your new Render URL (e.g., `https://my-bot.onrender.com`).

---

## 🔌 Step 5: Connect Meta to Your Webhook

The final step is telling Meta where to send incoming WhatsApp messages.

1. Go back to your Meta App Dashboard -> **WhatsApp** -> **Configuration**.
2. Click **Edit** under the Webhook section.
3. **Callback URL:** Paste your Render URL (or ngrok URL if testing locally) and **add `/webhook` to the end** (e.g., `https://my-bot.onrender.com/webhook`).
4. **Verify Token:** Type `my_secret_token_123` (or whatever you set in your environment variables).
5. Click **Verify and save**.
6. Under **Webhook fields**, click **Manage**, find **`messages`**, check the **Subscribe** box, and save.

🎉 **You are done! Send a WhatsApp message to your test number and watch the AI reply!**

---

### ⚠️ Important Notes

* **Meta's 24-Hour Rule:** You can only send free-form AI text replies to a user if they have sent a message to your bot within the last 24 hours.
* **Temporary Tokens:** The Meta access token expires every 24 hours. For a permanent bot, you must generate a **System User Token** in your Meta Business Settings.
* **Render Free Tier Sleep:** Render spins down free web services after 15 minutes of inactivity. The first message you send to a "sleeping" bot may take 45-60 seconds to get a reply while the server wakes up. Subsequent messages will be fast.