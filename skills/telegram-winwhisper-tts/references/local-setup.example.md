# Local setup reference (machine-specific)
# Copy this file to local-setup.md and fill in your paths.

Last verified from this machine/session.

## Active local paths

- Hermes Telegram audio cache (WSL): `/home/USER/.hermes/audio_cache`
- Windows faster-whisper root (WSL mount): `/mnt/c/faster-whisper`
- Windows faster-whisper root (Windows): `C:\faster-whisper`
- Windows STT wrapper (WSL mount): `/mnt/c/faster-whisper/stt_run.bat`
- Windows STT wrapper (Windows): `C:\faster-whisper\stt_run.bat`
- Windows venv Python (WSL mount): `/mnt/c/faster-whisper/.venv/Scripts/python.exe`
- Windows venv Python (Windows): `C:\faster-whisper\.venv\Scripts\python.exe`
- Windows ffmpeg (WSL mount): `/mnt/c/FFMPEG/bin/ffmpeg.exe`
- Windows ffmpeg (Windows): `C:\FFMPEG\bin\ffmpeg.exe`

## Active command wiring

- `HERMES_WINDOWS_STT_COMMAND = C:\faster-whisper\stt_run.bat {input_path} {language}`

## Current behavior notes

- Telegram voice files are cached locally before transcription.
- Prefer the cached `.ogg` file as the recovery/debugging source.
- Default Hermes TTS provider is Edge in WSL, with Chinese voice `zh-CN-XiaoxiaoNeural`.
- Prefer passing a shared `/mnt/c/...` path converted into `C:\...` for Windows-side transcription.
- Windows CPU transcription is the safe fallback.

## WSL ↔ Windows path / shell conversion notes

Use these conventions when launching Windows-side tools from WSL:

- Prefer explicit shell paths when invoking Windows from WSL:
  - CMD: `/mnt/c/Windows/System32/cmd.exe`
  - PowerShell: `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
- Prefer shared paths under `/mnt/c/...` instead of `/home/...` for any file that Windows batch tools must actually open.
- If a file starts in WSL home, first copy it into a shared `/mnt/c/...` location, then convert that shared path with `wslpath -w`.
