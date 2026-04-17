---
name: telegram-winwhisper-tts
description: Build and troubleshoot a Hermes Telegram voice pipeline that uses cached Telegram audio, Windows-side faster-whisper for STT, optional Edge TTS for Chinese output, and Telegram voice replies.
version: 1.0.2
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, hermes, stt, tts, faster-whisper, windows, wsl, voice]
    related_skills: [hermes-agent, systematic-debugging]
---

# telegram-winwhisper-tts

Use this skill when working on a Hermes Telegram voice workflow where Telegram voice arrives in WSL/Linux, STT should run on Windows-side faster-whisper, and replies may be sent back as Telegram voice messages.

## Goals

- Recover from Telegram voice transcription failures quickly.
- Route STT to Windows faster-whisper instead of WSL Whisper when that is the preferred setup.
- Preserve a reliable WSL-to-Windows handoff pattern.
- Generate Chinese TTS replies correctly when needed.

## Core principles

1. Do not assume Telegram failed to provide the voice file just because transcription failed.
2. First inspect Hermes audio cache for the newly cached `.ogg` file.
3. Prefer a shared `/mnt/<drive>/...` path for WSL-to-Windows handoff.
4. Avoid passing Linux-home paths directly into Windows tooling.
5. If Windows GPU inference fails, continue with Windows CPU fallback instead of bouncing back to WSL Whisper.

## Expected flow

1. Telegram voice message arrives.
2. Hermes caches the incoming voice as an `.ogg` file.
3. The cached audio becomes the recovery/debugging source of truth.
4. Copy that audio into a WSL path that maps cleanly to a Windows drive path.
5. Convert the shared WSL path to a Windows path.
6. Invoke Windows-side faster-whisper through a configured command wrapper.
7. If needed, generate reply audio with Edge TTS using a Chinese voice.
8. Convert reply audio to Telegram-friendly OGG/Opus.
9. Send it back with Telegram `sendVoice` or the platform's equivalent voice-send path.

## Path handoff rules

Preferred handoff pattern:
- Use a shared path under `/mnt/c/...` or another mounted Windows drive.
- Convert that path into a Windows `C:\...` style path before invoking Windows tools.

Avoid:
- Passing `/home/...` Linux paths directly to Windows STT.
- Relying on UNC paths like `\\wsl.localhost\...` for this workflow.

Why:
- `/mnt/c/...` maps predictably into a normal Windows drive path.
- Windows batch wrappers and `cmd.exe` are much more reliable with a drive-letter path than with a UNC path.

## Telegram cache investigation

What is now verified in Hermes:
- `gateway/platforms/telegram.py` downloads inbound Telegram `voice`
- then calls `cache_audio_from_bytes(..., ext='.ogg')`
- and writes the cached file under `/home/lin/.hermes/audio_cache/`

Operational rule:
1. Treat the cached `.ogg` in Hermes audio cache as the source of truth for downstream STT.
2. If automatic transcription fails, do not assume Telegram failed to deliver audio.
3. Inspect the cache, identify the newest `.ogg`, and hand that file to the Windows-side STT path.
4. Do not bounce back to WSL GPU Whisper as the first recovery path; stay on the Windows faster-whisper path, with Windows CPU fallback if needed.

Typical validation approach:
- list recent cached `.ogg` files
- pick the newest one
- run a direct transcription test against it

## Telegram adapter boundary

When touching `gateway/platforms/telegram.py`, keep the boundary narrow:
- `telegram.py` should download Telegram voice/audio, cache it locally, and attach that cached path to `event.media_urls`
- `tools/transcription_tools.py` should handle WSL↔Windows path conversion, shared temp copies, and Windows command invocation

Do not move Windows STT plumbing into `telegram.py`.

Current cleanup/source-of-truth note:
- `/home/lin/.hermes/hermes-agent/docs/plans/2026-04-16-telegram-py-voice-cache-purpose-and-plan.md`

Important local conclusion from that review:
- `cache_audio_from_bytes()` already returns the real cached file path
- so `telegram.py` should usually pass that direct returned path downstream
- do not add extra cache-directory rescans or “pick newest cached file” logic in `telegram.py` unless you first reproduce a real failure mode showing the direct returned path is unusable

## Windows STT expectations

Recommended setup pattern:
- Configure Hermes STT provider to use a Windows-oriented provider or wrapper.
- Keep the actual Windows command in an environment variable such as `HERMES_WINDOWS_STT_COMMAND`.
- Have the wrapper accept at least an input path and language.
- Use `cmd.exe /c` and `shell=True` if a Windows batch wrapper requires it.

Implementation guidance:
- The Windows-side wrapper should read the shared audio path.
- It should write transcript output to a predictable file or return channel.
- It should clean up temporary files after completion.

## GPU/CPU fallback rule

If faster-whisper on Windows fails because CUDA libraries do not match the installed runtime:
- do not block the workflow waiting for GPU repair
- switch or stay on Windows CPU mode
- verify correctness first, optimize later

## Chinese TTS rule

For Chinese replies, explicitly use an appropriate Chinese Edge TTS voice such as:
- `zh-CN-XiaoxiaoNeural`

Do not assume the default English voice will work for Chinese text.

## Audio conversion rule

Before sending a Telegram voice reply:
- convert the generated audio to Telegram-friendly OGG/Opus
- verify the output file exists and is non-empty

Typical ffmpeg pattern:
- input: generated mp3/wav
- output codec: `libopus`
- container: `.ogg`

## Troubleshooting checklist

### A. Telegram voice did not transcribe
1. Confirm the `.ogg` file exists in Hermes audio cache.
2. Confirm STT is resolving to the intended Windows provider.
3. Confirm the Windows STT command is present in the running environment.
4. Run a direct transcription test on the cached file.
5. If GPU fails, retry with CPU mode.

### B. Windows wrapper cannot read the file
1. Confirm the audio was copied into a `/mnt/c/...` style shared directory.
2. Convert it to a Windows drive path before invocation.
3. Avoid Linux-home and UNC paths.
4. If WSL reports `cmd.exe: not found`, do not assume Windows interop is unavailable; verify whether `cmd.exe` is simply missing from WSL `PATH` and use the explicit path `/mnt/c/Windows/System32/cmd.exe` instead.
5. When invoking a batch wrapper from WSL, prefer an explicit Windows shell call such as `cmd.exe /d /c ...` and avoid adding an extra layer of quoting around the already-converted `C:\...` input path if the batch file already wraps `%~1` in quotes.
6. A practical symptom of over-quoting is a Windows-side path that reaches Python as a literal quoted string like `'"C:\\Users\\...\\file.ogg"'`, which can make PyAV/faster-whisper fail with `Invalid argument`.

### C. Chinese TTS failed
1. Use an explicit Chinese Edge voice.
2. Regenerate the audio.
3. Re-convert to OGG/Opus.
4. Retry sendVoice.
5. If Hermes' built-in `text_to_speech` tool returns an Edge-style error such as `No audio was received`, fall back to invoking the local `edge-tts` CLI directly from the Hermes venv, for example:
   - `/home/lin/.hermes/hermes-agent/venv/bin/edge-tts --voice zh-CN-XiaoxiaoNeural --text '...Chinese text...' --write-media /home/lin/.hermes/audio_cache/reply.mp3`
6. After direct CLI generation succeeds, convert the mp3 to Telegram voice format with ffmpeg, for example:
   - `ffmpeg -y -i /home/lin/.hermes/audio_cache/reply.mp3 -c:a libopus -b:a 48k /home/lin/.hermes/audio_cache/reply.ogg`
7. Verify the `.ogg` file exists and is non-empty before sending.

### D. Direct manual verification from WSL fails unexpectedly
1. If the current WSL working directory appears to Windows as a `\\wsl.localhost\...` UNC path, `cmd.exe` may warn about UNC current directories before running the command.
2. To reduce noise, explicitly switch to a normal Windows drive first, for example with `cmd.exe /d /c "cd /d C:\ && ..."`.
3. If the wrapper then succeeds and writes the transcript `.txt`, treat the remaining issue as command-launch/path-handling rather than a model or audio-decoding failure.

## Minimal verification sequence

1. Verify a new Telegram voice file is cached.
2. Verify direct STT on that cached file succeeds.
3. Verify the reported provider is the intended Windows provider.
4. Verify TTS output is generated for Chinese text.
5. Verify ffmpeg conversion produces a valid `.ogg` file.
6. Verify Telegram accepts the final voice reply.

## Success criteria

This workflow is healthy when:
- incoming Telegram voice is cached successfully
- direct STT on cached audio succeeds through the Windows path
- CPU fallback works if GPU is unavailable
- Chinese TTS succeeds with an explicit Chinese voice
- final `.ogg` reply is accepted as a Telegram voice message

## Local reference file

For this machine's currently verified concrete paths and command wiring, also check:
- `references/local-setup.md`

## Notes for future maintenance

- Keep machine-specific absolute paths out of persistent memory when possible.
- Store stable local conventions in tool memory or local references, not bloated global memory.
- If the local environment changes, patch this skill with updated discovery and troubleshooting steps rather than stuffing more details into permanent memory.
