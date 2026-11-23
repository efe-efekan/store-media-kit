# Contributing

Thanks for helping! store-media-kit should stay **small, dependency-light and easy for AI assistants to drive**.

## Run it locally

```bash
pip install -r requirements.txt
python3 kit.py doctor
python3 examples/make_examples.py            # regenerates the demo captures and art
python3 kit.py check examples/tiles
python3 kit.py shots examples/tiles --locale en
python3 kit.py shots examples/habits --locale ar --device android_phone   # right-to-left + Android
```

Before a pull request:

- `python3 -m py_compile kit.py kit/*.py examples/*.py docs/*.py`
- render both examples on `iphone69`, `ipad13` and `android_phone` and look at `kit.py sheet`
- video changes: `python3 kit.py video examples/tiles && cd examples/tiles/video && npm install && npx tsc --noEmit -p . && npm run render -- en`
- if a README image changed: `python3 docs/make_readme_images.py`

## Ideas that would help

- more device presets (Apple Watch, Apple TV, Mac, Chromebook, Wear OS)
- more layout styles (two phones per slide, landscape games)
- a capture helper for XCUITest / Espresso / Maestro
- more caption examples per market in `docs/`

## Rules

- Never commit real people's data, credentials, store keys or another company's artwork.
- Example apps stay fictional and their art is generated (see `examples/make_examples.py`).
- Keep `AGENTS.md` in sync when you change commands or config keys.
