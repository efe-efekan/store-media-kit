# Prompts — copy, paste, done

These prompts work with any assistant that can read files and run commands in your project
(Claude Code, ChatGPT Codex / ChatGPT desktop with code, Gemini CLI, Cursor, GitHub Copilot agent,
Aider, Windsurf…). The assistant reads [`AGENTS.md`](../AGENTS.md) and does the rest.

**Before you start:** put this repo next to your app (`git clone https://github.com/efe-efekan/store-media-kit.git`),
then open **your app's folder** in the assistant. Replace the words in `<angle brackets>`.

---

## 1. First set of screenshots (start here)

```text
Use store-media-kit (../store-media-kit — read its AGENTS.md first) to make App Store screenshots
for this app. My app: <name>, <one line about what it does>. Stores: <App Store / Google Play / both>.
The 5 things to show, in order: <1>, <2>, <3>, <4>, <5>. Brand colours: <#hex or "take them from the app icon">.
Logo: <path to logo.png>.
Set up the project in ./store-media, capture clean screenshots from the simulator, write
keyword-driven English captions, render them and show me the review sheet. Don't upload anything.
```

## 2. Captions in many languages

```text
Using store-media-kit, write the screenshot captions for these languages: <de, fr, es, ja, ko, pt-BR, tr, ...>.
Write each one for that market (the words people search for there), not a literal translation.
Keep "<feature names>" exactly as the app shows them. Two short lines + a pill per slide, no numbers
that can change. Run kit.py check, render, and show me one sheet per device.
```

## 3. iPad and Android

```text
Using store-media-kit, add iPad 13" and Android phone (and 10" tablet) screenshots for ./store-media.
Capture the same 5 moments on the iPad simulator and an Android emulator (1080x1920), render all
languages for each device and show me the sheets.
```

## 4. Preview video

```text
Using store-media-kit, make a 20–25 second preview video for ./store-media: opening title
"<LINE 1> / <LINE 2>", then the real app — <describe 3–4 short moments> — then the logo end card.
Record the shots on the simulator (or use the screenshots with a slow camera move), add tap
ripples where I tap, keep the camera calm. Render the App Store version and the Google Play version.
```

## 5. Banners

```text
Using store-media-kit, make the App Store product page header (3840x1646) and the Google Play
feature graphic (1024x500) for ./store-media with just our logo on the brand colours. Show me both.
```

## 6. Fix one thing

```text
In store-media slide <N>: <make the phone bigger / tilt it less / move the coin decoration to the
bottom-left / the German headline is too small, shorten it / use a different capture>. Render only
that slide for <en, de> and show me before/after.
```

## 7. Upload (when you are happy)

```text
Upload the approved screenshots with store-media-kit: copy them into fastlane's folders for
<iPhone, iPad / Android phone, tablets>, run the upload lane, upload the App Preview video for
<en-US, en-GB> and set its poster frame on the opening title. My Apple ID is in $FASTLANE_USER
<and the Play key in $SUPPLY_JSON_KEY>. Then verify every locale and give me a table of counts.
```

## 8. No coding assistant? Use a web chat (ChatGPT, Gemini, Claude.ai)

A web chat cannot run commands, but it can write everything for you to paste:

```text
I'm using the open-source tool store-media-kit (https://github.com/efe-efekan/store-media-kit).
Here are its instructions: <paste the contents of llms.txt>.
My app: <name, what it does, 5 features, colours, languages>.
Write my media.json and texts/<lang>.json files, then give me the exact terminal commands to run,
one step at a time. I'll paste back any errors.
```

Then run the commands it gives you in a terminal inside the `store-media-kit` folder.

---

### Tips that make the AI do better work

- Give it **your store keywords** (or your current App Store / Play listing link) — captions get much stronger.
- Say what **must not** appear (beta features, prices, personal data, a competitor's name).
- Ask it to confirm **no status bar** (clock, battery, signal) is visible in any image or video frame.
- Ask it to **show the sheet** after every change; judge on the sheet, not on single files.
- Approve uploads one store at a time.
