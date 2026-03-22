#!/usr/bin/env python3
"""Add 2026 plugin releases to seed.json."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plugindb.seed import slugify

data = json.load(open("data/seed.json", encoding="utf-8"))
existing_slugs = {p["slug"] for p in data["plugins"]}
existing_mfr = {m["slug"] for m in data["manufacturers"]}

NEW = [
    ("Grainferno", "Baby Audio", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2026,
     ["granular", "synthesizer", "sound-design", "creative", "morphing"],
     "Granular synthesizer with audio-rate grain engine that turns any sample into a playable synth voice.",
     "https://babyaud.io/grainferno"),
    ("Nox", "Acustica Audio", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2026,
     ["synthesizer", "edm", "techno", "hybrid", "melodic"],
     "Hybrid synthesizer designed for EDM and melodic techno, built on the Alice-9 architecture.",
     "https://www.acustica-audio.com/shop/products/NOX"),
    ("Evolve Air", "Excite Audio", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2026,
     ["synthesizer", "sample-based", "texture", "morphing", "ambient"],
     "Sample-based synth with quad-engine for blending and morphing between four sources.",
     "https://www.excite-audio.com"),
    ("Efx AMBIENT", "Arturia", "effect", "reverb", ["VST3", "AU", "AAX"], "paid", 2026,
     ["reverb", "ambient", "spectral", "creative", "delay"],
     "Spectral processing and feedback-based delay plugin from the Arturia FX Collection.",
     "https://www.arturia.com/products/software-effects/efx-ambient/overview"),
    ("Pitch SHIFTER-910", "Arturia", "effect", "pitch", ["VST3", "AU", "AAX"], "paid", 2026,
     ["pitch-shift", "formant", "creative", "harmonizer"],
     "Pitch and formant shifting tool inspired by classic hardware pitch shifters.",
     "https://www.arturia.com/products/software-effects/pitch-shifter-910/overview"),
    ("Oxford Drum Gate 2", "Sonnox", "effect", "gate", ["VST3", "AU", "AAX"], "paid", 2026,
     ["gate", "drums", "transient", "mixing", "intelligent"],
     "Intelligent drum gate with advanced transient detection for precise gating.",
     "https://www.sonnox.com"),
    ("Falcon 2026", "UVI", "instrument", "synth", ["VST3", "AU", "AAX", "Standalone"], "paid", 2026,
     ["synthesizer", "hybrid", "sampler", "modular", "sound-design"],
     "Major update to UVI Falcon with new oscillators, effects, and modulators.",
     "https://www.uvi.net/falcon.html"),
    ("Corte Fino EQ", "Cotorro Audio", "effect", "eq", ["VST3", "AU"], "free", 2026,
     ["equalizer", "free", "subtractive", "mixing", "clean"],
     "Free subtractive equalizer with clean, transparent character.",
     "https://cotorroaudio.com"),
    ("Pianology", "Rhodes Music", "instrument", "piano", ["VST3", "AU", "AAX", "Standalone"], "paid", 2026,
     ["piano", "rhodes", "electric-piano", "keys", "realistic"],
     "Acoustic and electric piano collection from Rhodes Music.",
     "https://www.rhodesmusic.com"),
    ("GRN Granular FX", "FRCTL Audio", "effect", "general", ["VST3", "AU"], "paid", 2026,
     ["granular", "creative", "sound-design", "textural", "ambient"],
     "Granular effects processor for creative sound manipulation.",
     "https://frctlaudio.com"),
    ("Echo Cube", "AudioThing", "effect", "delay", ["VST3", "AU", "AAX"], "paid", 2026,
     ["delay", "acoustic", "dual", "creative", "spatial"],
     "Dual acoustic delay effect with spatial processing capabilities.",
     "https://www.audiothing.net/plugins/echo-cube/"),
    ("Dime[mb]", "Time Off Audio", "utility", "routing", ["VST3", "AU"], "paid", 2026,
     ["multiband", "routing", "utility", "mixing", "creative"],
     "Adds multiband processing to any plugin by splitting signal into five frequency bands.",
     "https://timeoffaudio.com"),
    ("Cascade", "Mixing Night Audio", "effect", "delay", ["VST3", "AU", "AAX"], "paid", 2026,
     ["delay", "creative", "mixing", "rhythmic"],
     "Creative delay plugin for mixing and sound design.",
     "https://mixingnightaudio.com"),
    ("Tape Vibe", "Three-Body Technology", "effect", "saturation", ["VST3", "AU", "AAX", "CLAP"], "paid", 2026,
     ["saturation", "tape", "vintage", "warm", "analog-modeling"],
     "Tape saturator plugin with vintage analog character.",
     "https://www.threebodytech.com"),
    ("Mortamer", "Gooey", "effect", "general", ["VST3", "AU"], "paid", 2026,
     ["lofi", "creative", "degradation", "vintage", "fx"],
     "Lo-fi effects processor for creative audio degradation.",
     "https://gooeyaudio.com"),
    ("Scepter", "Mercurial Tones", "utility", "analyzer", ["VST3", "AU", "AAX"], "paid", 2026,
     ["analyzer", "reference", "mastering", "mixing", "metering"],
     "Referencing and analysis workstation for mixing and mastering.",
     "https://mercurialtones.com"),
    ("Outland III", "The Very Loud Indeed Co.", "instrument", "sampler", ["VST3", "AU", "AAX"], "paid", 2026,
     ["cinematic", "dark", "scoring", "texture", "atmospheric"],
     "Dark scoring textures instrument for cinematic composition.",
     "https://theveryloudindeedco.com"),
    ("Concert Vibraphone", "Soundiron", "instrument", "sampler", ["VST3", "AU", "AAX"], "paid", 2026,
     ["vibraphone", "percussion", "orchestral", "mallet", "cinematic"],
     "Deeply sampled concert vibraphone with multiple articulations.",
     "https://soundiron.com"),
    ("Pro-Q 4", "FabFilter", "effect", "eq", ["VST3", "AU", "AAX", "CLAP"], "paid", 2025,
     ["equalizer", "mixing", "mastering", "dynamic-eq", "precise"],
     "Industry-standard parametric EQ with dynamic EQ, surround support, and spectrum analysis.",
     "https://www.fabfilter.com/products/pro-q-4-equalizer-plug-in"),
]

added = 0
new_mfrs = 0
for name, mfr_name, cat, subcat, formats, price, year, tags, desc, url in NEW:
    slug = slugify(name)
    mfr_slug = slugify(mfr_name)

    if slug in existing_slugs:
        print(f"  Skip (exists): {name}")
        continue

    if mfr_slug not in existing_mfr:
        data["manufacturers"].append({"slug": mfr_slug, "name": mfr_name, "website": url})
        existing_mfr.add(mfr_slug)
        new_mfrs += 1

    data["plugins"].append({
        "slug": slug, "name": name, "manufacturer_slug": mfr_slug,
        "category": cat, "subcategory": subcat, "formats": formats,
        "aliases": [name, f"{mfr_name} {name}"],
        "daws": ["Ableton", "Bitwig", "Cubase", "Studio One", "Reaper", "FL Studio", "Logic", "Pro Tools"],
        "os": ["windows", "macos"], "description": desc,
        "price_type": price, "url": url, "year": year, "tags": tags,
    })
    existing_slugs.add(slug)
    added += 1
    print(f"  Added: {name} ({mfr_name})")

data["manufacturers"].sort(key=lambda m: m["slug"])

with open("data/seed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nAdded {added} plugins, {new_mfrs} new manufacturers")
print(f"Total: {len(data['plugins'])} plugins")
