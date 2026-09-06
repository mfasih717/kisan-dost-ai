Kisan Dost - Final Responsive Frontend

Replace these files in your existing project:

1. web_app.py
2. templates/index.html
3. static/style.css
4. static/script.js

Project structure:

kisan dost/
│
├── main.py
├── config.py
├── web_app.py
│
├── kisan_agents/
├── tools/
├── guardrails/
├── models/
├── database/
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js

Run:

pip install flask
python web_app.py

Then open:

http://127.0.0.1:5000

After replacing files, use Ctrl + F5 in browser.

Fixes included:
- Only chat messages area scrolls on desktop/laptop
- Sidebar no longer shows unwanted desktop scrollbar
- Composer/input stays visible at bottom
- Better mobile/laptop/desktop resizing
- Mobile browser viewport/keyboard height handling
- Duplicate agent response cleanup
- Per-browser SQLite conversation memory
- Casual conversation memory preserved
- Off-domain guardrail returns friendly message instead of 500 error
- Prevents accidental duplicate sends while response is loading
