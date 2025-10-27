# Digikar Playwright automation

Quick start (Windows PowerShell)s

1) Create and activate a virtual environment:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2) Install the Python dependency:

```powershell
pip install -U pip
pip install "playwright>=1.40.0"
# Install browser binaries
python -m playwright install
```

3) Run the script (headful by default):

```powershell
python scripts/open_digikar.py
```

Run headless:

```powershell
python scripts/open_digikar.py --headless
```

The script will save a screenshot as `digikar_screenshot.png` in the current directory.

Notes
-----
- If you use Poetry or another manager, add `playwright` to your project dependencies instead of pip directly.
- If you get permissions errors on Playwright install, run PowerShell as Administrator.
 
Client certificate (mutual TLS) notes and automation
--------------------------------------------------

The digikar site in your screenshot requests a client certificate. Browsers normally show an OS-level certificate selection dialog when a server requests a client cert. That dialog can't be clicked by Playwright directly, so these approaches help automate or bypass the dialog:

1) Firefox — automatic certificate selection (recommended for easiest automation)

	- Import the client certificate into a Firefox profile (Preferences → Privacy & Security → View Certificates → Your Certificates → Import...).
	- Run the script using a persistent Firefox profile and enable automatic selection:

```powershell
# create a profile folder (optional) and run the script using it
uv run main.py --browser firefox --profile-dir ".\ff_profile" --auto-select-cert
```

	The script sets Firefox's `security.default_personal_cert` to `Select Automatically` for the launched profile so the browser will pick the certificate without showing the dialog.

2) Chromium / Chrome — use a profile where the cert is installed or configure AutoSelectCertificateForUrls policy

	- Import the client certificate into the Windows Certificate Store (Current User → Personal) or into a Chrome profile.
	- Launch Chromium with a persistent profile so Playwright reuses that profile (the script's `--profile-dir` can be used for this). Example:

```powershell
uv run main.py --browser chromium --profile-dir ".\chromium_profile" --user-data-dir 'C:\Users\baba\AppData\Local\Google\Chrome\User Data'

uv run main.py --browser chromium --user-data-dir 'C:\Users\baba\AppData\Local\Google\Chrome\User Data'
```

	- If Chrome still prompts, you can configure Chrome's `AutoSelectCertificateForUrls` policy (enterprise policy) to match the certificate issuer and URL so Chrome will select a matching certificate automatically. On Windows this requires setting a registry policy or deploying via Group Policy. See Chrome enterprise docs for details (policy name: `AutoSelectCertificateForUrls`).

3) Reuse an existing session/profile

	- Using a persistent profile (`--profile-dir`) is a good way to reuse a session (cookies, client certs). Install the certificate into that profile once (manually), then run the script repeatedly using the same `--profile-dir` so you don't need to interact with the dialog again.

Troubleshooting
---------------
- If you still see the certificate selection dialog when using Chromium, try the Firefox approach — Firefox's preference to auto-select certificates is easier to set per-profile.
- Ensure Playwright browsers are installed: `python -m playwright install`.
- If you need help converting a PKCS#12 (.p12/.pfx) certificate into a browser-installable cert, tell me and I can give commands.
