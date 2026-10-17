#!/usr/bin/env python3
"""
EnglishTube 3B1B Explainer - ElevenLabs Voiceover Generator
===========================================================
This turnkey script generates high-fidelity AI voiceovers for the EnglishTube
3Blue1Brown-style architectural explainer video using the official ElevenLabs API.

Usage:
  # Method 1: Set environment variable
  export ELEVENLABS_API_KEY="sk_..."
  python3 generate_elevenlabs_voice.py

  # Method 2: Pass API key via argument
  python3 generate_elevenlabs_voice.py --api-key "sk_..."

  # Options:
  --voice-id <id>     (Default: Adam - 'pNInz6obpgDQGcFmaJgB')
                      Recommended voices:
                        - Adam (Deep, analytical, 3B1B-like): 'pNInz6obpgDQGcFmaJgB'
                        - George (Warm British academic):      'JBFqnCBsd6RMkjVDRZzb'
                        - Charlie (Conversational Australian): 'IKne3meq5aSn9XLyUdCD'
  --model <id>        (Default: 'eleven_multilingual_v2')
  --remux             (Automatically remux final MP4 video after generating audio)
  --rerender          (Rerender Manim animations with updated exact timestamps)
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import subprocess

SCRIPT_SECTIONS = [
    {
        "id": "scene1_bottleneck",
        "title": "Act 1: The Subtitle Desynchrony Problem",
        "text": (
            "When acquiring a foreign language through media, timing is everything. "
            "Traditional video players suffer from temporal desynchronization: "
            "audio streams and visual text drift apart. "
            "This creates a cognitive bottleneck, forcing the brain to decode subtitles "
            "rather than absorbing acoustic patterns."
        )
    },
    {
        "id": "scene2_clock_engine",
        "title": "Act 2: 60 FPS Continuous Clock Engine",
        "text": (
            "EnglishTube eliminates this barrier with a custom sixty frames-per-second continuous time clock. "
            "Instead of jittery two-hundred-and-fifty millisecond polling, "
            "our mathematical interpolation predicts and tracks vocal phonemes with sub-millisecond precision. "
            "Every subtitle cue aligns synchronously with the soundwave."
        )
    },
    {
        "id": "scene3_interactive_studio",
        "title": "Act 3: Interactive Studio & Word Anatomy",
        "text": (
            "Inside the VoiceTube Studio, learning becomes interactive. "
            "Words illuminate in real time like karaoke. "
            "Touch any unfamiliar word to instantly reveal its phonetic IPA, part of speech, "
            "and neural speech pronunciation."
        )
    },
    {
        "id": "scene4_conclusion",
        "title": "Act 4: Brand Reveal & Conclusion",
        "text": (
            "EnglishTube. "
            "Where language acquisition meets acoustic precision. "
            "Explore over five hundred lessons and master English with complete clarity."
        )
    }
]

def get_audio_duration(file_path):
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return round(float(res.stdout.strip()), 3)
    except Exception as e:
        print(f"Warning: Could not measure duration with ffprobe for {file_path}: {e}")
        return 0.0

def generate_voiceover(api_key, voice_id, model_id, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    durations = {}

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    print(f"\n🎙️  Connecting to ElevenLabs API (Voice ID: {voice_id}, Model: {model_id})...\n")

    generated_files = []

    for section in SCRIPT_SECTIONS:
        sid = section["id"]
        out_file = os.path.join(output_dir, f"{sid}.mp3")
        payload = {
            "text": section["text"],
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.80,
                "style": 0.15,
                "use_speaker_boost": True
            }
        }

        print(f"  • Generating '{section['title']}'...")
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                with open(out_file, "wb") as f:
                    f.write(data)
                
            dur = get_audio_duration(out_file)
            durations[sid] = dur
            generated_files.append(out_file)
            print(f"    ✓ Saved {out_file} ({dur:.2f}s)")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"\n❌ ElevenLabs API Error ({e.code}): {err_body}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Request failed: {e}")
            sys.exit(1)

    # Save durations
    dur_file = os.path.join(output_dir, "durations.json")
    with open(dur_file, "w") as f:
        json.dump(durations, f, indent=2)
    print(f"\n📊 Updated voiceover timestamps written to {dur_file}")

    # Concatenate audio tracks
    concat_list_file = os.path.join(output_dir, "concat.txt")
    with open(concat_list_file, "w") as f:
        for gf in generated_files:
            f.write(f"file '{os.path.abspath(gf)}'\n")

    master_audio = os.path.join(output_dir, "master_narration_elevenlabs.mp3")
    print(f"  • Merging all tracks into {master_audio}...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_file, "-c", "copy", master_audio
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_dur = get_audio_duration(master_audio)
    print(f"🎉 Complete master ElevenLabs narration ready! Total length: {total_dur:.2f}s")
    return master_audio, durations

def main():
    parser = argparse.ArgumentParser(description="Generate ElevenLabs voiceover for EnglishTube 3B1B explainer")
    parser.add_argument("--api-key", default=os.environ.get("ELEVENLABS_API_KEY", ""), help="ElevenLabs API key")
    parser.add_argument("--voice-id", default="pNInz6obpgDQGcFmaJgB", help="Voice ID (Default: Adam 'pNInz6obpgDQGcFmaJgB')")
    parser.add_argument("--model", default="eleven_multilingual_v2", help="ElevenLabs model ID")
    parser.add_argument("--output-dir", default="media/audio/elevenlabs", help="Output directory")
    parser.add_argument("--remux", action="store_true", default=True, help="Remux final video with the new voiceover")
    parser.add_argument("--rerender", action="store_true", help="Rerender Manim scene to calibrate to new durations")
    args = parser.parse_args()

    if not args.api_key:
        print("=" * 70)
        print("⚠️  ELEVENLABS_API_KEY NOT FOUND")
        print("=" * 70)
        print("Please provide your ElevenLabs API key using one of the following:")
        print("  1. export ELEVENLABS_API_KEY=\"your_api_key_here\"")
        print("     python3 generate_elevenlabs_voice.py")
        print("\n  2. python3 generate_elevenlabs_voice.py --api-key \"your_api_key_here\"")
        print("\nNote: You can get your free API key at: https://elevenlabs.io")
        print("Current production video 'englishtube_3b1b_explainer.mp4' is currently voiced")
        print("by Microsoft Neural Voice (Christopher - Academic Tone).")
        print("=" * 70)
        sys.exit(1)

    master_audio, durations = generate_voiceover(args.api_key, args.voice_id, args.model, args.output_dir)

    if args.rerender:
        print("\n🎨 Rerendering Manim video to adapt to ElevenLabs pacing...")
        # Copy durations.json to media/audio/durations.json so Manim reads it
        with open("media/audio/durations.json", "w") as f:
            json.dump(durations, f, indent=2)
        subprocess.run([
            ".manim-env/bin/python3", "-m", "manim", "-qh", "englishtube_3b1b.py", "FullExplainer"
        ], check=True)

    if args.remux:
        base_video = "media/videos/englishtube_3b1b/1080p30/FullExplainer.mp4"
        final_video = "englishtube_3b1b_explainer_elevenlabs.mp4"
        if os.path.exists(base_video):
            print(f"\n🎬 Multiplexing final video to '{final_video}'...")
            subprocess.run([
                "ffmpeg", "-y", "-i", base_video, "-i", master_audio,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                final_video
            ], check=True)
            print(f"✨ SUCCESS! Final ElevenLabs-voiced 3B1B explainer generated:")
            print(f"   👉 {os.path.abspath(final_video)}")
        else:
            print(f"⚠️  Base video {base_video} not found. Please render the Manim scene first.")

if __name__ == "__main__":
    main()
