// Store preview video template (any app): opening title over your key art -> gameplay /
// screen-recording shots with tap ripples, gentle camera push and optional focus zoom ->
// end card with your logo (+ optional stars). Music fades in and out.
// Sizes: "appstore" 886x1920 (6.9" iPhone App Preview) or "play" 1080x1920 (Google Play /
// YouTube Shorts promo); pick one with `npm run render -- <locale> --preset play`.
//
// Everything app-specific lives in ../../media.json ("video") and ../../texts/<locale>.json
// ("video": line1/line2). Media files go in public/ (paths in media.json are relative to it).
import { Audio, Video } from "@remotion/media";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Composition,
  continueRender,
  delayRender,
  Easing,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import media from "../../media.json";
import enTexts from "../../texts/en.json";
import { HEADLINE_FONT, loadFont } from "./fonts";

type Pt = { x: number; y: number };
type Tap = { t: number; x: number; y: number };
type Focus = { at: number; until: number; x?: number; y?: number; zoom?: number };
// A shot is a screen recording ("clip") or, when you have none yet, a still screenshot ("image")
// with a slow camera move. taps: a JSON file in public/ or the events inline.
type ShotCfg = { clip?: string; image?: string; seconds: number; push?: number[]; trim?: number; taps?: string | Tap[]; focus?: Focus; background?: string };
type VideoCfg = {
  width?: number;
  height?: number;
  fps?: number;
  transition_frames?: number;
  transitions?: "wipe" | "slide" | "fade";
  stripes?: boolean;
  opening: { image: string; seconds?: number; line1_size?: number; line2_size?: number; bottom?: number };
  shots: ShotCfg[];
  crop?: { scale: number; origin: string };
  end: { image?: string; logo?: string; logo_width?: number; stars?: boolean; seconds?: number; background?: string };
  music?: string;
  music_volume?: number;
  colors?: { headline?: string; accent?: string; shadow?: string; confetti?: string[] };
};
export type PreviewProps = { video: { line1: string; line2: string }; preset?: "appstore" | "play" };
const PRESETS = { appstore: { width: 886, height: 1920 }, play: { width: 1080, height: 1920 } } as const;

const V = (media as unknown as { video: VideoCfg }).video;
const FPS = V.fps ?? 30;
// Default canvas from media.json; the "preset" prop overrides it (Apple accepts 15-30 s).
const W0 = V.width ?? 886;
const H0 = V.height ?? 1920;
const XF = V.transition_frames ?? 12;
const OPENING = Math.round((V.opening.seconds ?? 2.4) * FPS);
const ENDING = Math.round((V.end.seconds ?? 3) * FPS);
const COLORS = {
  headline: V.colors?.headline ?? "#ffffff",
  accent: V.colors?.accent ?? "#ffd43b",
  shadow: V.colors?.shadow ?? "#0b3f9e",
  confetti: V.colors?.confetti ?? ["#ff4d5e", "#ffb020", "#ffd43b", "#3dd68c", "#3aa0ff", "#a25cff", "#ff6fb5"],
};
const shotFrames = (s: ShotCfg) => Math.round(s.seconds * FPS);
export const totalFrames = () => OPENING + V.shots.reduce((a, s) => a + shotFrames(s), 0) + ENDING - XF * (V.shots.length + 1);
const shotStarts = () => {
  const out: number[] = [];
  let at = OPENING;
  for (const s of V.shots) {
    at -= XF;
    out.push(at);
    at += shotFrames(s);
  }
  return out;
};

const headline: React.CSSProperties = {
  fontFamily: HEADLINE_FONT,
  lineHeight: 0.98,
  letterSpacing: "0.005em",
  textTransform: "uppercase",
  whiteSpace: "nowrap",
  textShadow: `0 10px 0 ${COLORS.shadow}, 0 22px 34px rgba(0,0,0,.25)`,
};

const Sparkles: React.FC<{ count?: number; speed?: number }> = ({ count = 16, speed = 1 }) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  return (
    <AbsoluteFill>
      {Array.from({ length: count }, (_, i) => {
        const tw = 0.5 + 0.5 * Math.sin(frame / 6 + i);
        const s = 10 + (i % 3) * 6;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: (i * 137) % W,
              top: 200 + ((i * 263) % (H - 600)) - frame * (0.6 + (i % 3) * 0.3) * speed,
              width: s,
              height: s,
              borderRadius: 4,
              transform: `rotate(45deg) scale(${0.6 + tw * 0.6})`,
              background: i % 2 ? "#fff" : COLORS.confetti[i % COLORS.confetti.length],
              opacity: 0.35 + tw * 0.5,
              boxShadow: "0 0 18px rgba(255,255,255,.8)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- opening: the only text in the video ----------
const Opening: React.FC<{ texts: PreviewProps["video"] }> = ({ texts }) => {
  const frame = useCurrentFrame();
  const { fps, width: W } = useVideoConfig();
  const zoom = interpolate(frame, [0, OPENING], [1.0, 1.14], { easing: Easing.inOut(Easing.cubic) });
  const drift = interpolate(frame, [0, OPENING], [0, -40], { easing: Easing.inOut(Easing.cubic) });
  const pop = (delay: number) => spring({ frame: frame - delay, fps, config: { damping: 11, stiffness: 160, mass: 0.7 } });
  const a = pop(8);
  const b = pop(15);
  // Long words shrink so they never leave the frame.
  const fit = (text: string, size: number) => Math.min(size, (W * 0.92) / Math.max(1, text.length * 0.52));
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.shadow, overflow: "hidden" }}>
      <Img src={staticFile(V.opening.image)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `translateY(${drift}px) scale(${zoom})` }} />
      <Sparkles />
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: V.opening.bottom ?? 240 }}>
        <div style={{ ...headline, color: COLORS.headline, fontSize: fit(texts.line1, V.opening.line1_size ?? 150), opacity: Math.min(1, a * 1.4), transform: `translateY(${(1 - a) * 60}px) scale(${0.7 + 0.3 * a}) rotate(${(1 - a) * -4}deg)` }}>
          {texts.line1}
        </div>
        <div style={{ ...headline, color: COLORS.accent, fontSize: fit(texts.line2, V.opening.line2_size ?? 200), opacity: Math.min(1, b * 1.4), transform: `translateY(${(1 - b) * 60}px) scale(${0.6 + 0.4 * b}) rotate(${(1 - b) * 5}deg)` }}>
          {texts.line2}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- tap ripple (where the finger touched) ----------
const at = (p: Pt): React.CSSProperties => ({ position: "absolute", left: `${p.x * 100}%`, top: `${p.y * 100}%`, width: 0, height: 0 });

const Ripple: React.FC<{ p: Pt; color: string }> = ({ p, color }) => {
  const frame = useCurrentFrame();
  const k = interpolate(frame, [0, 16], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const size = 60 + k * 150;
  return (
    <div style={at(p)}>
      <div style={{ position: "absolute", left: -size / 2, top: -size / 2, width: size, height: size, borderRadius: "50%", border: `${10 - k * 7}px solid rgba(255,255,255,${0.95 - k * 0.95})`, boxShadow: `0 0 24px rgba(255,255,255,${0.6 - k * 0.6})` }} />
      {Array.from({ length: 6 }, (_, i) => {
        const ang = (i / 6) * Math.PI * 2 + 0.3;
        const r = 40 + k * 90;
        return <div key={i} style={{ position: "absolute", left: Math.cos(ang) * r - 7, top: Math.sin(ang) * r - 7, width: 14, height: 14, borderRadius: 4, transform: `rotate(45deg) scale(${1 - k})`, background: i % 2 ? color : "#fff", opacity: 1 - k }} />;
      })}
    </div>
  );
};

// taps file: { "events": [{ "t": 1.2, "x": 0.5, "y": 0.6 }] } (t = seconds from the clip start,
// x/y = 0-1 of the frame) or a plain array of those events.
const useTaps = (source?: string | Tap[]): Tap[] => {
  const file = typeof source === "string" ? source : undefined;
  const [taps, setTaps] = useState<Tap[]>(Array.isArray(source) ? source : []);
  const [handle] = useState(() => (file ? delayRender(`taps ${file}`) : null));
  useEffect(() => {
    if (!file || handle == null) return;
    fetch(staticFile(file))
      .then((r) => r.json())
      .then((j) => {
        const ev = (Array.isArray(j) ? j : j.events ?? []) as Partial<Tap>[];
        setTaps(ev.filter((e) => e.x != null && e.y != null && e.t != null) as Tap[]);
      })
      .catch(() => setTaps([]))
      .finally(() => continueRender(handle));
  }, [file, handle]);
  return taps;
};

// ---------- one shot: slow push, optional focus zoom, tap ripples ----------
const Shot: React.FC<{ s: ShotCfg; frames: number }> = ({ s, frames }) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const trim = s.trim ?? 0;
  const taps = useTaps(s.taps).map((e) => ({ ...e, t: e.t - trim })).filter((e) => e.t >= 0);
  const push = s.push ?? [1, 1.03];
  const actionX = taps.length ? taps.reduce((a, t) => a + t.x, 0) / taps.length : 0.5;
  let scale = interpolate(frame, [0, frames], push, { easing: Easing.inOut(Easing.sin) });
  let px = Math.min(0.7, Math.max(0.3, actionX));
  let py = 0; // zooms anchored at the top edge, so top UI never leaves the frame
  if (s.focus) {
    const ramp = 16;
    const a = Math.round(s.focus.at * FPS);
    const b = Math.round(s.focus.until * FPS);
    const w = interpolate(frame, [a - ramp, a, b, b + ramp], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    scale += ((s.focus.zoom ?? 1.22) - scale) * w;
    px += ((s.focus.x ?? 0.5) - px) * w;
    py += ((s.focus.y ?? 0) - py) * w;
  }
  const tx = (1 - scale) * px * W;
  const ty = (1 - scale) * py * H;
  const crop = V.crop ?? { scale: 1, origin: "50% 50%" };
  return (
    <AbsoluteFill style={{ backgroundColor: s.background ?? "#000", overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `translate(${tx}px, ${ty}px) scale(${scale})`, transformOrigin: "0 0" }}>
        {/* crop: e.g. scale 1.062 from the bottom hides a simulator Dynamic Island */}
        <AbsoluteFill style={{ transform: `scale(${crop.scale})`, transformOrigin: crop.origin }}>
          {s.clip ? (
            <Video src={staticFile(s.clip)} trimBefore={Math.round(trim * FPS)} muted objectFit="cover" style={{ width: "100%", height: "100%", filter: "saturate(1.08) contrast(1.03)" }} />
          ) : (
            <Img src={staticFile(s.image ?? "")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          )}
          {taps.map((e, i) => (
            <Sequence key={i} from={Math.round(e.t * FPS)} durationInFrames={18} layout="none">
              <Ripple p={e} color={COLORS.confetti[(i * 3) % COLORS.confetti.length]} />
            </Sequence>
          ))}
        </AbsoluteFill>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 75% 60% at 50% 55%, rgba(0,0,0,0) 60%, rgba(10,30,80,.2) 100%)" }} />
    </AbsoluteFill>
  );
};

// Brand sweep: diagonal stripes in the brand colours on every cut.
const StripeSweep: React.FC = () => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const p = interpolate(frame, [0, XF + 4], [-1.2, 1.2], { easing: Easing.inOut(Easing.cubic) });
  return (
    <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: -W, top: -H * 0.25, width: W * 3, height: H * 1.5, transform: `translateX(${p * W * 1.3}px) rotate(-18deg)`, display: "flex" }}>
        {COLORS.confetti.map((c, i) => (
          <div key={i} style={{ width: 70, height: "100%", background: c, marginRight: 10, boxShadow: "0 0 30px rgba(0,0,0,.15)" }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ---------- end card: logo (+ stars) ----------
const Star: React.FC<{ size: number; k: number; rot: number }> = ({ size, k, rot }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{ transform: `scale(${k}) rotate(${rot}deg)`, filter: "drop-shadow(0 10px 0 #b36b00) drop-shadow(0 22px 30px rgba(0,0,0,.25))" }}>
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#fff27a" />
        <stop offset="0.55" stopColor="#ffd43b" />
        <stop offset="1" stopColor="#ffa514" />
      </linearGradient>
    </defs>
    <path d="M50 4 L62 36 L96 37 L69 58 L79 92 L50 72 L21 92 L31 58 L4 37 L38 36 Z" fill="url(#g)" stroke="#fff" strokeWidth="5" strokeLinejoin="round" />
  </svg>
);

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width: W } = useVideoConfig();
  const e = V.end;
  const bgZoom = interpolate(frame, [0, ENDING], [1.08, 1.0], { easing: Easing.out(Easing.cubic) });
  const logo = spring({ frame: frame - 4, fps, config: { damping: 10, stiffness: 140, mass: 0.8 } });
  const stars = [0, 1, 2].map((i) => spring({ frame: frame - 18 - i * 7, fps, config: { damping: 9, stiffness: 170, mass: 0.6 } }));
  return (
    <AbsoluteFill style={{ background: e.background ?? `linear-gradient(180deg,#5cc8ff 0%,#2f9bff 55%,${COLORS.shadow} 100%)`, overflow: "hidden" }}>
      {e.image && <Img src={staticFile(e.image)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${bgZoom})`, opacity: 0.95 }} />}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 22% at 50% 36%, rgba(255,255,255,.55), rgba(255,255,255,0) 70%)" }} />
      <Sparkles count={22} speed={1.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 40 }}>
        {e.logo && (
          <Img src={staticFile(e.logo)} style={{ width: e.logo_width ?? W * 0.8, transform: `scale(${0.7 + 0.3 * logo})`, opacity: Math.min(1, logo * 1.5), filter: "drop-shadow(0 16px 0 rgba(8,30,100,.3)) drop-shadow(0 30px 40px rgba(0,0,0,.25))" }} />
        )}
        {e.stars && (
          <div style={{ display: "flex", alignItems: "flex-end", gap: 10 }}>
            <Star size={170} k={stars[0]} rot={-12} />
            <div style={{ marginBottom: 50 }}>
              <Star size={215} k={stars[1]} rot={0} />
            </div>
            <Star size={170} k={stars[2]} rot={12} />
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const transition = (i: number) => {
  const kind = V.transitions ?? "wipe";
  if (i === 0 || kind === "fade") return fade();
  if (kind === "slide") return slide({ direction: i % 2 ? "from-right" : "from-left" });
  return wipe({ direction: i % 2 ? "from-left" : "from-right" });
};

export const Preview: React.FC<PreviewProps> = ({ video }) => {
  loadFont(`${video.line1} ${video.line2}`);
  const { durationInFrames } = useVideoConfig();
  const starts = shotStarts();
  const P = (p: unknown) => p as ReturnType<typeof fade>;
  return (
    <AbsoluteFill>
      <TransitionSeries name="Shots">
        <TransitionSeries.Sequence name="Opening" durationInFrames={OPENING}>
          <Opening texts={video} />
        </TransitionSeries.Sequence>
        {V.shots.flatMap((s, i) => [
          <TransitionSeries.Transition key={`t${i}`} presentation={P(transition(i))} timing={linearTiming({ durationInFrames: XF })} />,
          <TransitionSeries.Sequence key={`s${i}`} name={s.clip ?? s.image ?? `shot ${i + 1}`} durationInFrames={shotFrames(s)}>
            <Shot s={s} frames={shotFrames(s)} />
          </TransitionSeries.Sequence>,
        ])}
        <TransitionSeries.Transition presentation={P(fade())} timing={linearTiming({ durationInFrames: XF })} />
        <TransitionSeries.Sequence name="End card" durationInFrames={ENDING}>
          <EndCard />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      {(V.stripes ?? true) &&
        starts.slice(1).map((a, i) => (
          <Sequence key={i} from={a - 2} durationInFrames={XF + 6} name={`Sweep ${i + 2}`}>
            <StripeSweep />
          </Sequence>
        ))}
      {V.music && (
        <Audio
          src={staticFile(V.music)}
          volume={(f) =>
            interpolate(f, [0, 12, durationInFrames - 66, durationInFrames - 4], [0, V.music_volume ?? 0.85, V.music_volume ?? 0.85, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.inOut(Easing.sin),
            })
          }
        />
      )}
    </AbsoluteFill>
  );
};

export const AppPreviewComposition = () => (
  <Composition
    id="AppPreview"
    component={Preview}
    durationInFrames={totalFrames()}
    fps={FPS}
    width={W0}
    height={H0}
    defaultProps={{ video: (enTexts as unknown as PreviewProps).video }}
    calculateMetadata={({ props }) => (props.preset ? PRESETS[props.preset] : {})}
  />
);
