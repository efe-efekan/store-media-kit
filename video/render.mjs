// npm run render -- <locale> [--preset appstore|play]  -> out/<locale>[-play].mp4 (H.264 + AAC)
// The opening title comes from ../texts/<locale>.json ("video": line1/line2).
// appstore = 886x1920 (iPhone App Preview), play = 1080x1920 (Google Play / YouTube promo).
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";

const args = process.argv.slice(2);
const presetAt = args.indexOf("--preset");
const preset = presetAt >= 0 ? args[presetAt + 1] : undefined;
const locale = args.find((a, i) => !a.startsWith("--") && i !== presetAt + 1) ?? "en";
if (preset && !["appstore", "play"].includes(preset)) throw new Error(`unknown preset ${preset}`);
const textsFile = `../texts/${locale}.json`;
if (!existsSync(textsFile)) throw new Error(`missing ${textsFile}`);
const { video } = JSON.parse(readFileSync(textsFile, "utf8"));
if (!video?.line1) throw new Error(`${textsFile} has no "video": { "line1", "line2" }`);
mkdirSync("out", { recursive: true });
writeFileSync("out/.props.json", JSON.stringify(preset ? { video, preset } : { video }));
const out = `out/${locale}${preset === "play" ? "-play" : ""}.mp4`;
execFileSync(
  "npx",
  ["remotion", "render", "src/index.ts", "AppPreview", out, "--props=out/.props.json", "--codec=h264", "--crf=18", "--audio-codec=aac"],
  { stdio: "inherit" },
);
console.log(`wrote ${out}`);
