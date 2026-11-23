import { continueRender, delayRender, staticFile } from "remotion";

let loaded = false;

// Headline font (Anton) plus open fallbacks for other scripts: Fira Sans Extra Condensed
// (Cyrillic) and Noto Sans JP/KR/SC/TC/Thai/Devanagari/Arabic/Hebrew from public/fonts/ext
// (`python3 kit.py fonts` downloads them; `kit.py init` copies them here if present).
export const HEADLINE_FONT =
  "Anton, FiraXC, 'Noto Sans JP Variable', 'Noto Sans KR Variable', 'Noto Sans SC Variable', 'Noto Sans TC Variable', 'Noto Sans Thai Variable', 'Noto Sans Devanagari Variable', 'Noto Sans Arabic Variable', 'Noto Sans Hebrew Variable', sans-serif";

const SCRIPT_CSS = ["noto-sans-jp", "noto-sans-kr", "noto-sans-sc", "noto-sans-tc", "noto-sans-thai", "noto-sans-devanagari", "noto-sans-arabic", "noto-sans-hebrew"];

export const loadFont = (sample = "") => {
  if (loaded || typeof document === "undefined") return;
  loaded = true;
  const handle = delayRender("Loading fonts");
  const faces = [
    new FontFace("Anton", `url(${staticFile("fonts/anton-latin-400-normal.woff2")}) format("woff2")`),
    new FontFace("Anton", `url(${staticFile("fonts/anton-latin-ext-400-normal.woff2")}) format("woff2")`, { unicodeRange: "U+0100-024F, U+1E00-1EFF" }),
    new FontFace("FiraXC", `url(${staticFile("fonts/fira-sans-extra-condensed-cyrillic-900-normal.woff2")}) format("woff2")`, { weight: "900", unicodeRange: "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116" }),
    new FontFace("FiraXC", `url(${staticFile("fonts/fira-sans-extra-condensed-cyrillic-ext-900-normal.woff2")}) format("woff2")`, { weight: "900", unicodeRange: "U+0460-052F, U+1C80-1C88, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F" }),
  ];
  const links = SCRIPT_CSS.map(
    (pkg) =>
      new Promise<void>((resolve) => {
        const l = document.createElement("link");
        l.rel = "stylesheet";
        l.href = staticFile(`fonts/ext/${pkg}/package/index.css`);
        l.onload = () => resolve();
        l.onerror = () => resolve();
        document.head.appendChild(l);
      }),
  );
  Promise.all([...faces.map((f) => f.load().then((x) => document.fonts.add(x))), ...links])
    .then(() => (sample ? document.fonts.load(`900 100px ${HEADLINE_FONT}`, sample) : undefined))
    .then(() => document.fonts.ready)
    .then(() => continueRender(handle))
    .catch(() => continueRender(handle));
};
