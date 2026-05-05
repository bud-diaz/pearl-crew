# Pearl Crew — Discord Multi-Agent Bot

A 5-agent local AI crew running on Ollama, accessible from anywhere via Discord.

## Agents

| Agent | Role | Default Model |
|-------|------|---------------|
| Pearl | Orchestrator & Visionary | hermes3 |
| Corey | Creative & Artist | hermes3 |
| Midas | Marketing & Brand Builder | hermes3 |
| Rain  | Technical Engineer | hermes3 |
| Levy  | Monetization, Legal & Compliance | hermes3 |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Pull your Ollama model

```bash
ollama pull hermes3
# or whatever model you're using
```

### 3. Create your Discord bot

1. Go to https://discord.com/developers/applications
2. New Application → Bot → copy the token
3. Enable **Message Content Intent** under Bot → Privileged Gateway Intents
4. Invite bot to your server with these permissions:
   - Read Messages / View Channels
   - Send Messages
   - Read Message History

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env and paste your DISCORD_TOKEN
```

### 5. Create Discord channels

Create these text channels in your server (exact names):
- `#pearl`
- `#corey`
- `#midas`
- `#rain`
- `#levy`
- `#hub`

### 6. Run the bot

```bash
python bot.py
```

---

## Usage

**Direct agent channels** — talk directly to one agent:
```
#rain → Rain, how do I set up a systemd service for this bot?
#midas → What would a launch tweet thread for Paperweight look like?
```

**Hub channel** — Pearl reads your message and routes it:
```
#hub → I need help figuring out pricing for my SaaS product
→ routed to Levy (monetization question)
```

**Commands** — works in any channel:
```
!crew agents           — list all agents and current models
!crew model rain llama3.1  — hot-swap Rain's model
!crew clear            — wipe your conversation history
!crew history          — see how much history you have
!crew help             — show all commands
```

---

## Skills

Skills are plug-in capability documents that extend what an agent knows how to do. Each skill is a folder containing a `SKILL.md` file — plain text that gets injected into the agent's system prompt at the start of every response, so the agent is aware of it automatically without any tool calls.

### Directory layout

```
skills/
├── shared/          # loaded by ALL agents
│   └── my-skill/
│       └── SKILL.md
├── pearl/           # Pearl-only skills
├── corey/           # Corey-only
├── midas/           # Midas-only
├── rain/            # Rain-only
└── levy/            # Levy-only
```

### Installing from ClawhHub

Browse skills at [clawhub.ai](https://clawhub.ai). Download a skill folder and place it in the appropriate subdirectory:

```bash
# A skill for all agents
cp -r ~/Downloads/my-skill skills/shared/

# A skill only Rain should know about
cp -r ~/Downloads/shell-tricks skills/rain/
```

After dropping in a new skill, either restart the bot or ask Pearl or Rain to run the `reload_skills` tool — they'll pick it up instantly without a restart.

### Commands

```
!crew skills              — list all loaded skills across every agent
!crew skills rain         — list skills loaded for Rain specifically
```

### The reload_skills tool

Pearl and Rain both have access to a `reload_skills` tool. If you install a new skill while the bot is running, just say:

```
#pearl  → reload your skills
```

Pearl will call `reload_skills` and confirm what was loaded.

### Notes

- Skills are injected into the system prompt at the start of each response — no extra tool calls needed.
- Total injected skill content is capped at ~6000 characters to avoid context bloat.
- The bot works normally with an empty `skills/` directory.

---

## File Structure

```
pearl-crew/
├── bot.py          # Entry point, Discord event handling
├── agents.py       # Agent definitions, Ollama loop, tool execution
├── router.py       # Pearl's routing logic for hub channel
├── history.py      # Per-user conversation history (persisted to JSON)
├── tools.py        # Tool schemas + execution (search, files, shell, model switch)
├── commands.py     # !crew slash-style commands
├── workspace/      # Files agents can read/write
└── data/history/   # Persisted conversation history per user
```

---

## Swapping Models Per Agent

Edit `agents.py` and change the `model=` line for any agent, or use the live command:

```
!crew model rain llama3.1:70b
!crew model pearl mistral-small
```

---

## Recommended Models (Ollama)

For tool calling + less restriction:
- `hermes3` — NousResearch, strong tool use, less filtered
- `llama3.1` — strong tool calling natively
- `mistral-small` — fast, decent tools
- `qwen2.5` — strong tool use, fast

---

## Notes

- History is global per user — all agents share your conversation context
- History is capped at 40 messages to prevent context bloat
- File read/write is sandboxed to `./workspace/` 
- Shell commands have a basic blocklist — expand in `tools.py` as needed
- DuckDuckGo search requires no API key
