# 🤖 Telegram Userbot with Human-like Auto-reply

A powerful Telegram userbot that automatically replies to private messages with human-like behavior, featuring typing indicators, random delays, and customizable reply rules.

## ✨ Features

- **Human-like Responses**: Typing indicators and random delays for realistic interactions
- **Customizable Rules**: Define triggers and responses for different messages
- **REST API**: Manage rules and blacklist via API endpoints
- **Persistent Storage**: MongoDB integration for storing rules and blacklist
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Vercel Compatible**: Deploy API endpoints to Vercel serverless platform

## 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd telegram-userbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file with your credentials:
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   PHONE=+1234567890
   MONGODB_URL=your_mongodb_connection_string
   PORT=8000
   ```

4. **Generate session**:
   ```bash
   python generate_session.py
   ```

5. **Export session string for Vercel**:
   ```bash
   python export_session_string.py
   ```

6. **Run the userbot**:
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
telegram-userbot/
├── main.py              # Main userbot application
├── api_server.py        # Vercel-compatible API server
├── generate_session.py  # Session generation script
├── export_session_string.py  # Session string exporter for Vercel
├── config.py            # Configuration loader
├── database.py          # MongoDB integration
├── api/
│   └── routes.py        # API endpoints
└── utils/
    └── humanize.py      # Human-like behavior utilities
```

## 🔧 Deployment Strategy

### For Full Functionality (Recommended)
Use a hybrid approach:

1. **Telegram Bot**: Deploy `main.py` on Railway/Render/VPS (persistent connection required)
2. **API Server**: Deploy `api_server.py` on Vercel (serverless endpoints)
3. **Shared Database**: Both connect to the same MongoDB instance

### Environment Variables
Both deployments need these variables:
```env
SESSION_STRING=your_exported_session_string
API_ID=your_api_id
API_HASH=your_api_hash
MONGODB_URL=your_mongodb_connection_string
PORT=8000
```

### Why This Approach?
- **Vercel Limitations**: Serverless functions timeout after ~15 seconds
- **Telegram Requirements**: Bots need persistent connections to receive messages
- **Best of Both Worlds**: API on Vercel for scalability, bot on persistent platform for reliability

## 🌐 API Endpoints

All endpoints are available at `/api/*`:

- `GET /api/health` - Health check
- `GET /api/rules` - List all reply rules
- `POST /api/rules` - Create a new rule
- `PUT /api/rules/{id}` - Update a rule
- `DELETE /api/rules/{id}` - Delete a rule
- `GET /api/blacklist` - List blacklisted users
- `POST /api/blacklist` - Add user to blacklist
- `DELETE /api/blacklist/{user_id}` - Remove user from blacklist

## ⚙️ Configuration

### Reply Rules
Create rules with triggers and responses:
```json
{
  "trigger": "hello",
  "response": "Hi there! How can I help you?",
  "enabled": true
}
```

Special trigger `"any"` serves as a fallback for unmatched messages.

### Blacklist
Block specific users from receiving auto-replies by adding their user IDs to the blacklist.

## 🛠️ Troubleshooting

### Session Issues
If you encounter authentication problems:
1. Delete the `userbot.session` file
2. Run `python generate_session.py` again
3. Verify your credentials in `.env`

### Vercel Deployment
Remember:
- Only deploy `api_server.py` to Vercel
- Don't try to run the full bot on Vercel
- Use the session string exported by `export_session_string.py`

### Network Issues
Ensure your hosting platform allows outbound connections to Telegram servers (ports 443, 80).

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
