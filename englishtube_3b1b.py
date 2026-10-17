from manim import *
import json, os

# 3Blue1Brown Signature Aesthetics
config.background_color = "#0c0d14"
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30

DURATIONS = {
    "scene1_bottleneck": 15.74,
    "scene2_clock_engine": 16.46,
    "scene3_interactive_studio": 10.87,
    "scene4_conclusion": 6.05
}

if os.path.exists("media/audio/durations.json"):
    try:
        with open("media/audio/durations.json", "r") as f:
            DURATIONS = json.load(f)
    except Exception:
        pass

class FullExplainer(Scene):
    def construct(self):
        # ─────────────────────────────────────────────────────────────
        # ACT 1: THE BOTTLENECK (15.74s)
        # ─────────────────────────────────────────────────────────────
        title1 = Text("The Subtitle Desynchrony Problem", font="Helvetica", weight=BOLD, font_size=40)
        title1.set_color_by_gradient("#818cf8", "#c084fc")
        title1.to_edge(UP, buff=0.8)

        self.play(Write(title1), run_time=1.5)

        # Draw audio waveform
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 2, 1],
            x_length=8,
            y_length=2.5,
            axis_config={"color": "#334155", "stroke_width": 2}
        ).shift(UP * 0.5)

        wave = axes.plot(lambda x: 1.2 * np.sin(3 * x) * np.cos(0.5 * x), color="#4cd6a0", stroke_width=3)
        wave_label = Text("Continuous Vocal Audio Stream", font="Helvetica", font_size=20, color="#4cd6a0").next_to(axes, UP, buff=0.2)

        self.play(Create(axes), Create(wave), FadeIn(wave_label), run_time=2.0)

        # Desynced subtitle block
        sub_box = RoundedRectangle(corner_radius=0.2, width=6.5, height=1.0, color="#ef4444", fill_color="#1e1e38", fill_opacity=0.8)
        sub_box.shift(DOWN * 1.8)
        sub_text = Text('"Loving can hurt, loving can hurt..."', font="Helvetica", font_size=22, color="#f87171")
        sub_text.move_to(sub_box)

        offset_label = Text("Phase Error: Δt = +1.8s (Out of Sync)", font="Helvetica", font_size=18, color="#ef4444")
        offset_label.next_to(sub_box, DOWN, buff=0.25)

        self.play(FadeIn(sub_box), Write(sub_text), FadeIn(offset_label), run_time=1.8)
        self.play(sub_box.animate.shift(RIGHT * 0.8), run_time=1.0)
        self.play(sub_box.animate.shift(LEFT * 1.6), run_time=1.2)
        self.play(sub_box.animate.shift(RIGHT * 0.8), run_time=0.8)

        # Cognitive Bottleneck indicator
        bottleneck_text = Text("Cognitive Working Memory Overload", font="Helvetica", font_size=22, color="#fbbf24")
        bottleneck_text.shift(DOWN * 2.8)
        self.play(Write(bottleneck_text), run_time=1.5)

        # Wait to match exact audio duration of scene 1 (accounting for 1.2s fadeout)
        rem1 = max(0.1, DURATIONS["scene1_bottleneck"] - 9.8 - 1.2)
        self.wait(rem1)

        # Transition to Act 2
        self.play(
            FadeOut(title1), FadeOut(axes), FadeOut(wave), FadeOut(wave_label),
            FadeOut(sub_box), FadeOut(sub_text), FadeOut(offset_label), FadeOut(bottleneck_text),
            run_time=1.2
        )

        # ─────────────────────────────────────────────────────────────
        # ACT 2: THE 60 FPS CONTINUOUS CLOCK ENGINE (16.46s)
        # ─────────────────────────────────────────────────────────────
        title2 = Text("60 FPS Continuous Clock Engine", font="Helvetica", weight=BOLD, font_size=40)
        title2.set_color_by_gradient("#38bdf8", "#818cf8")
        title2.to_edge(UP, buff=0.8)

        self.play(Write(title2), run_time=1.2)

        # Compare 250ms Iframe Staircase vs 60fps Interpolated Curve
        axes2 = Axes(
            x_range=[0, 6, 1],
            y_range=[0, 4, 1],
            x_length=9,
            y_length=4,
            axis_config={"color": "#475569"}
        ).shift(DOWN * 0.4)

        # Stair step (old 250ms polling)
        stair_points = []
        for step in range(6):
            stair_points.extend([[step, step * 0.65], [step + 1, step * 0.65]])
        
        stair_lines = VGroup()
        for i in range(0, len(stair_points) - 1):
            p1 = axes2.c2p(stair_points[i][0], stair_points[i][1])
            p2 = axes2.c2p(stair_points[i+1][0], stair_points[i+1][1])
            stair_lines.add(Line(p1, p2, color="#f43f5e", stroke_width=3))

        stair_label = Text("Traditional: 250ms Stair-Step Polling (Jittery)", font="Helvetica", font_size=20, color="#f43f5e")
        stair_label.next_to(axes2, UP, buff=0.2).shift(LEFT * 1.5)

        self.play(Create(axes2), Create(stair_lines), FadeIn(stair_label), run_time=2.2)

        # Continuous 60fps Line
        smooth_line = axes2.plot(lambda x: 0.65 * x, x_range=[0, 6], color="#8b7cff", stroke_width=5)
        smooth_label = Text("EnglishTube: 60 FPS Continuous Time Clock (Sub-millisecond)", font="Helvetica", font_size=20, color="#a5b4fc")
        smooth_label.next_to(axes2, UP, buff=0.2).shift(RIGHT * 0.5)

        self.play(
            ReplacementTransform(stair_lines, smooth_line),
            ReplacementTransform(stair_label, smooth_label),
            run_time=2.5
        )

        # Scanning Dot & Ripple
        tracker = ValueTracker(0)
        dot = always_redraw(lambda: Dot(axes2.c2p(tracker.get_value(), 0.65 * tracker.get_value()), color="#38bdf8", radius=0.15))
        pulse_circle = always_redraw(lambda: Circle(radius=0.35, color="#38bdf8", stroke_width=2).move_to(dot.get_center()))

        self.add(dot, pulse_circle)
        self.play(tracker.animate.set_value(5.5), run_time=4.5, rate_func=linear)

        rem2 = max(0.1, DURATIONS["scene2_clock_engine"] - 10.4 - 1.2)
        self.wait(rem2)

        self.play(
            FadeOut(title2), FadeOut(axes2), FadeOut(smooth_line), FadeOut(smooth_label),
            FadeOut(dot), FadeOut(pulse_circle),
            run_time=1.2
        )

        # ─────────────────────────────────────────────────────────────
        # ACT 3: INTERACTIVE STUDIO & ON-DEMAND STREAMING (10.87s)
        # ─────────────────────────────────────────────────────────────
        title3 = Text("Interactive Studio & Instant Word Anatomy", font="Helvetica", weight=BOLD, font_size=38)
        title3.set_color_by_gradient("#34d399", "#38bdf8")
        title3.to_edge(UP, buff=0.8)

        self.play(Write(title3), run_time=1.2)

        # Subtitle Row
        cue_bg = RoundedRectangle(corner_radius=0.25, width=10.5, height=1.6, color="#2e2e4a", fill_color="#131326", fill_opacity=0.95)
        cue_bg.shift(UP * 0.8)

        # Individual Words in Sentence
        words_en = ["Loving", "can", "heal,", "loving", "can", "mend", "your", "soul"]
        word_mobs = VGroup(*[Text(w, font="Helvetica", font_size=26, color="#cbd5e1") for w in words_en])
        word_mobs.arrange(RIGHT, buff=0.22)
        word_mobs.move_to(cue_bg).shift(UP * 0.25)

        cue_zh = Text("愛能撫平傷痕，愛能治癒你的靈魂", font="Heiti TC", font_size=20, color="#94a3b8")
        cue_zh.next_to(word_mobs, DOWN, buff=0.25)

        self.play(FadeIn(cue_bg), FadeIn(word_mobs), FadeIn(cue_zh), run_time=1.5)

        # Karaoke Sweep
        for i in range(3):
            self.play(
                word_mobs[i].animate.set_color("#8b7cff").scale(1.15),
                run_time=0.45
            )
            self.play(
                word_mobs[i].animate.scale(1/1.15),
                run_time=0.15
            )

        # Click on "heal" -> Popover Card
        heal_word = word_mobs[2]
        click_ring = Circle(radius=0.4, color="#38bdf8", stroke_width=3).move_to(heal_word.get_center())
        self.play(Create(click_ring), run_time=0.4)
        self.play(FadeOut(click_ring), run_time=0.2)

        dict_card = RoundedRectangle(corner_radius=0.2, width=6.5, height=2.2, color="#6366f1", fill_color="#18182f", fill_opacity=0.98)
        dict_card.shift(DOWN * 1.6)

        dict_w = Text("heal", font="Helvetica", weight=BOLD, font_size=28, color="#ffffff").shift(DOWN * 0.9 + LEFT * 1.8)
        dict_ipa = Text("/hiːl/", font="Helvetica", font_size=22, color="#38bdf8").next_to(dict_w, RIGHT, buff=0.3)
        dict_pos = Text("v.", font="Helvetica", slant=ITALIC, font_size=20, color="#a5b4fc").next_to(dict_ipa, RIGHT, buff=0.2)
        dict_def = Text("治癒，撫平；使康復痊癒", font="Heiti TC", font_size=20, color="#e2e8f0").shift(DOWN * 1.6 + LEFT * 0.5)
        dict_btn = Text("🔊 真人發音  ·  ＋ 收藏單字", font="Heiti TC", font_size=16, color="#4cd6a0").shift(DOWN * 2.2)

        dict_group = VGroup(dict_card, dict_w, dict_ipa, dict_pos, dict_def, dict_btn)
        self.play(FadeIn(dict_group, shift=UP * 0.3), run_time=1.2)

        rem3 = max(0.1, DURATIONS["scene3_interactive_studio"] - 6.3 - 1.0)
        self.wait(rem3)

        self.play(
            FadeOut(title3), FadeOut(cue_bg), FadeOut(word_mobs), FadeOut(cue_zh),
            FadeOut(dict_group),
            run_time=1.0
        )

        # ─────────────────────────────────────────────────────────────
        # ACT 4: CONCLUSION & BRAND REVEAL (6.05s)
        # ─────────────────────────────────────────────────────────────
        logo_bg = RoundedRectangle(corner_radius=0.35, width=4.0, height=1.6, color="#8b7cff", fill_color="#8b7cff", fill_opacity=1.0)
        tube_text = Text("TUBE", font="Helvetica", weight=BOLD, font_size=60, color="#ffffff")
        tube_text.move_to(logo_bg)
        tube_group = VGroup(logo_bg, tube_text).shift(RIGHT * 1.8)

        eng_text = Text("ENGLISH", font="Helvetica", weight=BOLD, font_size=60, color="#ffffff")
        eng_text.next_to(tube_group, LEFT, buff=0.3)

        full_logo = VGroup(eng_text, tube_group).center().shift(UP * 0.3)

        tagline = Text("Where Language Acquisition Meets Acoustic Precision", font="Helvetica", font_size=24)
        tagline.set_color_by_gradient("#94a3b8", "#e2e8f0")
        tagline.next_to(full_logo, DOWN, buff=0.8)

        sub_stats = Text("500 Curated Video Lessons & Classic Songs · 60 FPS Sub-Millisecond Sync", font="Helvetica", font_size=18, color="#6366f1")
        sub_stats.next_to(tagline, DOWN, buff=0.3)

        self.play(
            FadeIn(eng_text, shift=RIGHT * 0.5),
            FadeIn(tube_group, shift=LEFT * 0.5),
            run_time=1.5
        )
        self.play(Write(tagline), FadeIn(sub_stats), run_time=1.8)

        # Glowing ripple around logo
        ripple = Circle(radius=3.2, color="#8b7cff", stroke_width=3).move_to(full_logo.get_center())
        self.play(ripple.animate.scale(1.4).set_opacity(0), run_time=1.5)

        rem4 = max(0.1, DURATIONS["scene4_conclusion"] - 4.8 - 0.8)
        self.wait(rem4)

        self.play(FadeOut(full_logo), FadeOut(tagline), FadeOut(sub_stats), run_time=0.8)
