# finance-monitor
Monitor all your finances in one place.
Making sure you max out your retirement plans and stay under your credit limit by 30%.

## How It Works

Drop in your statements and finance-monitor parses them locally — no bank logins, no APIs, no data leaving your machine.

- **Bank of America** — parses exported PDF statements
- **Fidelity** — parses exported CSV statements

Aggregates balances, spending, and transaction history across both.

## Display
- Terminal output by default — fast, minimal, always available
- Optional GUI dashboard with charts and summaries

## Features
- Shows current net worth
- Predicts future net worths based on historical data
- Identifies and shows repeat transactions to help detect fraud or unnecessary spending
- Provides insights into cash flow and budgeting
- Generates reports on investment performance
- Alerts for upcoming bills and reminders for financial goals

## Startup
Runs automatically on login via a systemd service or login hook so your financial snapshot is ready when you sit down.

## AI Health Check (Planned)
- Offline, local AI model analyzes your parsed data
- Flags overspending, low balances, retirement contribution gaps, high credit utilization, and other trends
- Nothing leaves your machine

## Roadmap
- [x] BofA PDF statement parser
- [x] Fidelity CSV statement parser
- [x] Balance & spending aggregation
- [x] Terminal output mode
- [ ] GUI dashboard
- [ ] Startup on login
- [ ] Local AI financial health analysis

## Todo
- Research openclaw
- Install aider and ollama in the Boxes VM, TURN OFF NETWORK CONNECTION AFTER, run parsers on the statements in the shared folders, analyze the parsed data and determine how to code the rest of the app

# Fedora VM Setup Checklist — Private AI Workspace

> Complete these steps **IN ORDER** while network is still connected.
> Disconnect network **ONLY** at the very end.

---

## Step 1 — First Boot Setup

- [ ] Complete Fedora first-boot wizard (username, password, timezone)
- [ ] Open a terminal (Activities → Terminal)

---

## Step 2 — System Update

- [ ] `sudo dnf update -y`
- [ ] `sudo dnf upgrade -y`
- [ ] Reboot after updates: `sudo reboot`

---

## Step 3 — Install Essentials

- [ ] `sudo dnf install -y curl wget git nano tree htop`

---

## Step 4 — Install Spice Agents (for file sharing with host)

- [ ] `sudo dnf install -y spice-vdagent spice-webdavd`
- [ ] `sudo systemctl enable spice-vdagentd spice-webdavd`
- [ ] `sudo systemctl start spice-vdagentd spice-webdavd`

---

## Step 5 — Install Ollama

- [ ] `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] Verify install: `ollama --version`

---

## Step 6 — Set Ollama Environment Variables (permanent)

- [ ] `echo 'export OLLAMA_API_BASE=http://localhost:11434' >> ~/.bashrc`
- [ ] `echo 'export OLLAMA_CONTEXT_LENGTH=16384' >> ~/.bashrc`
- [ ] `source ~/.bashrc`
- [ ] Verify:
```bash
echo $OLLAMA_API_BASE
echo $OLLAMA_CONTEXT_LENGTH
```

---

## Step 7 — Pull Your Model

- [ ] Start Ollama server first: `ollama serve &`
- [ ] Pull the coding model: `ollama pull qwen2.5-coder:14b`
- [ ] Verify it downloaded: `ollama list`
- [ ] *(Optional)* Pull a lightweight general model: `ollama pull llama3.2:3b`

---

## Step 8 — Install Python (if not already installed)

- [ ] `python3 --version`
- [ ] If missing: `sudo dnf install -y python3 python3-pip`

---

## Step 9 — Install Aider

- [ ] `curl -LsSf https://aider.chat/install.sh | sh`
- [ ] Add to PATH if needed:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
- [ ] Verify install: `aider --version`

---

## Step 10 — Configure Aider (permanent settings)

- [ ] `nano ~/.aider.conf.yml`
- [ ] Paste the following:
```yaml
model: ollama_chat/qwen2.5-coder:14b
ollama-api-base: http://localhost:11434
dark-mode: true
auto-commits: true
```
- [ ] Save and exit (`Ctrl+X`, `Y`, `Enter`)

---

## Step 11 — Set Up Git (required for Aider)

- [ ] `git config --global user.name "Your Name"`
- [ ] `git config --global user.email "you@example.com"`
- [ ] Verify:
```bash
git config --global user.name
git config --global user.email
```

---

## Step 12 — Test Everything Works

- [ ] Open terminal 1 — start Ollama:
```bash
ollama serve
```
- [ ] Open terminal 2 — test Aider:
```bash
mkdir ~/test-project && cd ~/test-project
git init
aider
```
- [ ] At the aider prompt type: `> create a hello world python script`
- [ ] If it works, everything is set up correctly
- [ ] Clean up test: `cd ~ && rm -rf ~/test-project`

---

## Step 13 — Optional but Recommended

- [ ] Install better terminal tools:
```bash
sudo dnf install -y fzf bat eza zoxide
```
- [ ] Install Kitty terminal:
```bash
curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh
```
- [ ] Set up case-insensitive tab completion:
```bash
echo 'set completion-ignore-case on' >> ~/.inputrc
bind -f ~/.inputrc
```

---

## Step 14 — Disconnect Network (LAST STEP)

- [ ] Confirm everything above is installed and working
- [ ] On **host machine**: GNOME Boxes → VM Settings → Network → **OFF**
- [ ] Verify no internet inside VM: `curl http://google.com` *(should fail — this is correct)*
- [ ] Your VM is now fully air-gapped and private

---

## Daily Workflow After Setup

1. Start VM from GNOME Boxes
2. Open terminal
3. **Terminal 1:** `ollama serve`
4. **Terminal 2:**
```bash
cd /your/project
aider
```

> Everything stays on your machine. Nothing leaves.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Aider can't find Ollama | `export OLLAMA_API_BASE=http://localhost:11434` |
| Model not found | `ollama list` then `ollama pull qwen2.5-coder:14b` |
| Aider command not found | `export PATH="$HOME/.local/bin:$PATH"` |
| Ollama already running | `pkill ollama` then `ollama serve` |