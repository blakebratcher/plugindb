"""Add missing Native Instruments plugins to seed.json."""

import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed.json"

NI_DAWS = ["Ableton", "Cubase", "Studio One", "Reaper", "FL Studio", "Logic", "Pro Tools"]
NI_FORMATS = ["VST3", "AU", "AAX"]
NI_OS = ["windows", "macos"]
MFR = "native-instruments"


def ni(slug, name, category, subcategory, description, price_type, url, year, tags, aliases):
    return {
        "slug": slug,
        "name": name,
        "manufacturer_slug": MFR,
        "category": category,
        "subcategory": subcategory,
        "formats": NI_FORMATS,
        "aliases": aliases,
        "daws": NI_DAWS,
        "os": NI_OS,
        "description": description,
        "price_type": price_type,
        "url": url,
        "year": year,
        "tags": tags,
        "image_url": "",
    }


NI_PLUGINS = [
    # ── Play Series ──────────────────────────────────────────────────────
    ni("ni-analog-dreams", "Analog Dreams", "instrument", "synth",
       "Play Series instrument featuring lush analog-style synth sounds including rich pads, warm basses, and retro leads with intuitive macro controls.",
       "paid", "https://www.native-instruments.com/en/products/komplete/play-series/analog-dreams/", 2019,
       ["synthesizer", "analog", "pads", "retro", "sample-based", "play-series"],
       ["Analog Dreams", "NI Analog Dreams"]),

    ni("ni-ethereal-earth", "Ethereal Earth", "instrument", "synth",
       "Play Series instrument creating atmospheric and otherworldly sounds by combining organic recordings with hybrid synthesis.",
       "paid", "https://www.native-instruments.com/en/products/komplete/play-series/ethereal-earth/", 2019,
       ["synthesizer", "atmospheric", "organic", "ambient", "hybrid", "play-series"],
       ["Ethereal Earth", "NI Ethereal Earth"]),

    ni("ni-hybrid-keys", "Hybrid Keys", "instrument", "piano",
       "Play Series instrument combining sampled acoustic and electronic keys with an advanced arpeggiator, from realistic pianos to futuristic synth textures.",
       "paid", "https://www.native-instruments.com/en/products/komplete/play-series/hybrid-keys/", 2019,
       ["piano", "keys", "hybrid", "arpeggiator", "sample-based", "play-series"],
       ["Hybrid Keys", "NI Hybrid Keys"]),

    ni("ni-lo-fi-glow", "Lo-Fi Glow", "instrument", "synth",
       "Play Series instrument delivering hazy keys, synths, guitars, and bass processed for lo-fi warmth with over 150 tweakable presets.",
       "paid", "https://www.native-instruments.com/en/products/komplete/play-series/lo-fi-glow/", 2020,
       ["lo-fi", "vintage", "warm", "keys", "synth", "play-series", "hip-hop"],
       ["Lo-Fi Glow", "NI Lo-Fi Glow", "LoFi Glow"]),

    ni("ni-modular-icons", "Modular Icons", "instrument", "synth",
       "Play Series instrument inspired by legendary modular synthesizers, delivering bold basses, searing leads, and evolving textures with macro controls.",
       "paid", "https://www.native-instruments.com/en/products/komplete/play-series/modular-icons/", 2019,
       ["synthesizer", "modular", "bass", "leads", "sample-based", "play-series"],
       ["Modular Icons", "NI Modular Icons"]),

    # ── Keys & Pianos ────────────────────────────────────────────────────
    ni("ni-noire", "Noire", "instrument", "piano",
       "Nils Frahm's signature Yamaha CFX concert grand piano with Pure and Felt modes plus an innovative Particles engine for generative harmonic textures.",
       "paid", "https://www.native-instruments.com/en/products/komplete/keys/noire/", 2019,
       ["piano", "concert-grand", "cinematic", "ambient", "sample-based"],
       ["Noire", "NI Noire"]),

    ni("ni-una-corda", "Una Corda", "instrument", "piano",
       "Custom David Klavins one-string-per-key upright piano with pure, cotton, and felt preparations, created in collaboration with Nils Frahm.",
       "paid", "https://www.native-instruments.com/en/products/komplete/keys/una-corda/", 2015,
       ["piano", "upright", "intimate", "felt", "ambient", "cinematic", "sample-based"],
       ["Una Corda", "NI Una Corda"]),

    ni("ni-the-giant", "The Giant", "instrument", "piano",
       "Sampled Klavins Piano Model 370i — a super-sized upright standing over three meters high, delivering a colossal sonic spectrum for cinematic scoring.",
       "paid", "https://www.native-instruments.com/en/products/komplete/keys/the-giant/", 2012,
       ["piano", "upright", "cinematic", "massive", "sample-based"],
       ["The Giant", "NI The Giant"]),

    ni("ni-retro-machines-mk2", "Retro Machines MK2", "instrument", "synth",
       "Collection of 16 definitive analog synthesizers and keyboards from the '70s and '80s lovingly re-created for Kontakt, with arpeggiator and chord player.",
       "paid", "https://www.native-instruments.com/en/products/komplete/synths/retro-machines-mk2/", 2011,
       ["synthesizer", "analog", "vintage", "retro", "keys", "sample-based"],
       ["Retro Machines MK2", "NI Retro Machines MK2", "Retro Machines Mk II"]),

    ni("ni-electric-keys", "Electric Keys Collection", "instrument", "piano",
       "Two meticulously sampled electric pianos — Phoenix (Fender Rhodes 73) and Diamond (suitcase 88) — with detailed tonal controls for Kontakt.",
       "paid", "https://www.native-instruments.com/en/products/komplete/keys/electric-keys-collection/", 2024,
       ["electric-piano", "rhodes", "keys", "vintage", "sample-based"],
       ["Electric Keys", "Tines Duo", "NI Electric Keys"]),

    # ── Cinematic & Orchestral ───────────────────────────────────────────
    ni("ni-damage", "Damage", "instrument", "drum-machine",
       "Cinematic percussion powerhouse by Heavyocity combining orchestral and industrial percussion with 25,000+ samples, 700 loops, and 58 kits.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/damage/", 2011,
       ["cinematic", "percussion", "drums", "orchestral", "sound-design", "film-scoring"],
       ["Damage", "NI Damage", "Heavyocity Damage"]),

    ni("ni-action-strings-2", "Action Strings 2", "instrument", "rompler",
       "Epic orchestral string phrases for cinematic scoring with live-recorded articulations in collaboration with Sonuscore.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/action-strings-2/", 2021,
       ["cinematic", "strings", "orchestral", "film-scoring", "phrases", "sample-based"],
       ["Action Strings 2", "NI Action Strings 2"]),

    ni("ni-symphony-series-string-ensemble", "Symphony Series - String Ensemble", "instrument", "rompler",
       "60-piece string section recorded at Studio 22 Budapest with 38 articulations, four mic mixes, and on-board effects.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/symphony-series-string-ensemble/", 2016,
       ["orchestral", "strings", "cinematic", "ensemble", "film-scoring", "sample-based"],
       ["Symphony Series String Ensemble", "NI Symphony Series Strings"]),

    ni("ni-symphony-series-brass", "Symphony Series - Brass", "instrument", "rompler",
       "Comprehensive brass library offering ensemble and solo instruments with extensive articulations for orchestral and cinematic brass scoring.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/symphony-series-brass/", 2015,
       ["orchestral", "brass", "cinematic", "ensemble", "film-scoring", "sample-based"],
       ["Symphony Series Brass", "NI Symphony Series Brass"]),

    ni("ni-symphony-series-woodwind", "Symphony Series - Woodwind", "instrument", "rompler",
       "Detailed woodwind collection by Soundiron with ensemble and solo instruments for expressive orchestral scoring.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/symphony-series-woodwind-collection/", 2017,
       ["orchestral", "woodwinds", "cinematic", "ensemble", "film-scoring", "sample-based"],
       ["Symphony Series Woodwind", "NI Symphony Series Woodwind"]),

    ni("ni-symphony-series-percussion", "Symphony Series - Percussion", "instrument", "rompler",
       "Orchestral percussion library with a wide range of tuned and untuned instruments for film, game, and orchestral scoring.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/symphony-series-percussion/", 2017,
       ["orchestral", "percussion", "cinematic", "drums", "film-scoring", "sample-based"],
       ["Symphony Series Percussion", "NI Symphony Series Percussion"]),

    ni("ni-mysteria", "Mysteria", "instrument", "synth",
       "Cinematic vocal instrument with over 350 presets from 800 sound sources, using X-Y morphing for epic emotional voice-based textures.",
       "paid", "https://www.native-instruments.com/en/products/komplete/vocal/mysteria/", 2020,
       ["cinematic", "vocal", "atmospheric", "sound-design", "film-scoring", "texture"],
       ["Mysteria", "NI Mysteria"]),

    ni("ni-thrill", "Thrill", "instrument", "synth",
       "Cinematic scoring instrument combining orchestral power with expert sound design via X-Y performance control for suspenseful builds and scores.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/thrill/", 2017,
       ["cinematic", "orchestral", "sound-design", "film-scoring", "horror", "suspense"],
       ["Thrill", "NI Thrill"]),

    ni("ni-rise-and-hit", "Rise & Hit", "instrument", "synth",
       "The first instrument designed for expressive cinematic build-ups, with 700+ single-layer and 250 multi-layer sounds by Galaxy Instruments.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/rise-hit/", 2014,
       ["cinematic", "build-up", "riser", "impact", "film-scoring", "sound-design"],
       ["Rise & Hit", "Rise and Hit", "NI Rise & Hit"]),

    ni("ni-ashlight", "Ashlight", "instrument", "synth",
       "Dark granular synthesis instrument exploring unconventional sound sources like bowed metals, carbon, and glass with 300 presets for cinematic scoring.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/ashlight/", 2021,
       ["granular", "cinematic", "dark", "atmospheric", "sound-design", "experimental"],
       ["Ashlight", "NI Ashlight"]),

    ni("ni-emotive-strings", "Emotive Strings", "instrument", "rompler",
       "Live-recorded legato string phrases from a 44-piece ensemble by Sonuscore for quickly creating cinematic and emotional string arrangements.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/emotive-strings/", 2018,
       ["cinematic", "strings", "orchestral", "legato", "phrases", "film-scoring"],
       ["Emotive Strings", "NI Emotive Strings"]),

    ni("ni-kinetic-metal", "Kinetic Metal", "instrument", "synth",
       "Cinematic instrument featuring 211 patches from unconventional metallic sound sources with X-Y morphing for ethereal textures and tonal percussion.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/kinetic-metal/", 2013,
       ["cinematic", "metallic", "texture", "sound-design", "experimental", "percussion"],
       ["Kinetic Metal", "NI Kinetic Metal"]),

    ni("ni-kinetic-toys", "Kinetic Toys", "instrument", "synth",
       "Creative Kontakt instrument morphing 200+ recordings of vintage children's toys with synthesized layers via X-Y modulation.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/kinetic-toys/", 2016,
       ["cinematic", "creative", "sound-design", "experimental", "texture"],
       ["Kinetic Toys", "NI Kinetic Toys"]),

    ni("ni-stradivari-violin", "Stradivari Violin", "instrument", "rompler",
       "Deeply sampled 1727 Stradivari 'Vesuvius' violin with 20 articulations and multiple mic positions recorded in Cremona's Auditorium.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/stradivari-violin/", 2020,
       ["violin", "strings", "solo", "orchestral", "cinematic", "classical", "sample-based"],
       ["Stradivari Violin", "NI Stradivari Violin"]),

    ni("ni-stradivari-cello", "Stradivari Cello", "instrument", "rompler",
       "Deeply sampled 1700 Stradivari 'Stauffer' cello with extensive articulations and multiple mic positions recorded in Cremona's Auditorium.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/stradivari-cello/", 2021,
       ["cello", "strings", "solo", "orchestral", "cinematic", "classical", "sample-based"],
       ["Stradivari Cello", "NI Stradivari Cello"]),

    ni("ni-cremona-quartet", "Cremona Quartet", "instrument", "rompler",
       "Four legendary stringed instruments (Stradivari Violin, Guarneri Violin, Amati Viola, Stradivari Cello) as a unified ensemble with auto divisi.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/cremona-quartet/", 2022,
       ["strings", "quartet", "orchestral", "cinematic", "classical", "sample-based", "ensemble"],
       ["Cremona Quartet", "NI Cremona Quartet"]),

    ni("ni-choir-omnia", "Choir: Omnia", "instrument", "rompler",
       "40-piece symphonic choir with soprano, alto, tenor, and bass sections featuring Syllabuilder engine, polyphonic true legato, and 189 presets.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/choir-omnia/", 2022,
       ["choir", "vocal", "orchestral", "cinematic", "classical", "film-scoring", "ensemble"],
       ["Choir Omnia", "NI Choir Omnia"]),

    ni("ni-vocal-colors", "Vocal Colors", "instrument", "synth",
       "Expressive vocal instrument combining male and female voices with hybrid synthesis, morphing vocals into evolving pads, basses, and grooves.",
       "paid", "https://www.native-instruments.com/en/products/komplete/vocal/vocal-colors/", 2023,
       ["vocal", "sound-design", "hybrid", "cinematic", "expressive", "creative"],
       ["Vocal Colors", "NI Vocal Colors"]),

    ni("ni-valves", "Valves", "instrument", "rompler",
       "Emotive brass ensemble featuring flugelhorn, French horn, trombone, euphonium, and tuba with phrase engine and Moments slider for intimate textures.",
       "paid", "https://www.native-instruments.com/en/products/komplete/cinematic/valves/", 2023,
       ["brass", "cinematic", "ensemble", "phrases", "orchestral", "intimate", "film-scoring"],
       ["Valves", "NI Valves"]),

    # ── Effects ──────────────────────────────────────────────────────────
    ni("ni-solid-bus-comp", "Solid Bus Comp", "effect", "compressor",
       "Powerful bus compressor for finishing mixes with unmistakable high-end sound, part of the Solid Mix Series.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/solid-bus-comp/", 2012,
       ["compressor", "bus", "mixing", "mastering", "dynamics", "analog-modeling"],
       ["Solid Bus Comp", "NI Solid Bus Comp"]),

    ni("ni-solid-eq", "Solid EQ", "effect", "eq",
       "Precise 6-band equalizer with two switchable curve models for subtle shading to aggressive shaping, part of the Solid Mix Series.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/solid-eq/", 2012,
       ["eq", "equalizer", "mixing", "mastering", "analog-modeling"],
       ["Solid EQ", "NI Solid EQ"]),

    ni("ni-solid-dynamics", "Solid Dynamics", "effect", "dynamics",
       "Combined compressor and gate/expander for versatile dynamics control on individual tracks, part of the Solid Mix Series.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/solid-dynamics/", 2012,
       ["compressor", "gate", "dynamics", "mixing", "analog-modeling"],
       ["Solid Dynamics", "NI Solid Dynamics"]),

    ni("ni-passive-eq", "Passive EQ", "effect", "eq",
       "4-band passive equalizer by Softube modeling classic tube hardware, offering warm and musical tonal shaping for the Premium Tube Series.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/premium-tube-series/", 2012,
       ["eq", "tube", "analog-modeling", "warm", "vintage", "mastering"],
       ["Passive EQ", "NI Passive EQ"]),

    ni("ni-vari-comp", "Vari Comp", "effect", "compressor",
       "Two-channel tube compressor by Softube delivering natural, musical compression modeled after classic Vari-Mu hardware.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/premium-tube-series/", 2012,
       ["compressor", "tube", "analog-modeling", "warm", "vintage", "mastering"],
       ["Vari Comp", "NI Vari Comp"]),

    ni("ni-enhanced-eq", "Enhanced EQ", "effect", "eq",
       "Tube equalizer by Softube focused on filling out the low end and adding clarity to midrange with musical tonal shaping.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/premium-tube-series/", 2012,
       ["eq", "tube", "analog-modeling", "warm", "vintage"],
       ["Enhanced EQ", "NI Enhanced EQ"]),

    ni("ni-rc-24", "RC 24", "effect", "reverb",
       "Classic algorithmic reverb by Softube modeled after the legendary Lexicon 224, with intuitive visual display and lush harmonic character.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/rc-24/", 2013,
       ["reverb", "algorithmic", "vintage", "classic", "mixing"],
       ["RC 24", "RC24", "NI RC 24"]),

    ni("ni-rc-48", "RC 48", "effect", "reverb",
       "Classic algorithmic reverb by Softube modeled after the legendary Lexicon 480L, delivering deep dimensional reverb with visual feedback.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/rc-48/", 2013,
       ["reverb", "algorithmic", "vintage", "classic", "mixing"],
       ["RC 48", "RC48", "NI RC 48"]),

    ni("ni-transient-master", "Transient Master", "effect", "dynamics",
       "Essential dynamics effect with just three knobs (Attack, Sustain, Gain) for reshaping transients — simple, powerful, and extremely useful.",
       "paid", "https://www.native-instruments.com/en/products/komplete/effects/transient-master/", 2012,
       ["transient", "dynamics", "envelope", "drums", "mixing", "shaping"],
       ["Transient Master", "NI Transient Master"]),

    ni("ni-replika", "Replika", "effect", "delay",
       "Streamlined delay plugin with Modern, Vintage Digital, and Diffusion algorithms, plus resonant filter and classic phaser with stereo modes.",
       "free", "https://www.native-instruments.com/en/products/komplete/effects/replika/", 2014,
       ["delay", "free", "vintage", "diffusion", "creative"],
       ["Replika", "NI Replika"]),

    # ── Session Guitarist / Bassist ──────────────────────────────────────
    ni("ni-strummed-acoustic", "Session Guitarist - Strummed Acoustic", "instrument", "guitar",
       "Realistic strummed acoustic guitar for Kontakt with pattern-based playback engine and studio-quality recordings.",
       "paid", "https://www.native-instruments.com/en/products/komplete/guitar/session-guitarist-strummed-acoustic/", 2015,
       ["guitar", "acoustic", "strumming", "patterns", "sample-based"],
       ["Strummed Acoustic", "NI Strummed Acoustic", "Session Guitarist Strummed Acoustic"]),

    ni("ni-electric-sunburst-deluxe", "Session Guitarist - Electric Sunburst Deluxe", "instrument", "guitar",
       "Expanded electric guitar with 237 patterns including riffs, arpeggios, and chords, plus a melodic instrument for lead playing.",
       "paid", "https://www.native-instruments.com/en/products/komplete/guitar/session-guitarist-electric-sunburst-deluxe/", 2019,
       ["guitar", "electric", "patterns", "riffs", "sample-based"],
       ["Electric Sunburst Deluxe", "NI Electric Sunburst Deluxe"]),

    ni("ni-picked-acoustic", "Session Guitarist - Picked Acoustic", "instrument", "guitar",
       "Vintage acoustic guitar with 194 fingerpicking patterns recorded by a session pro, plus a melodic instrument with multiple articulations.",
       "paid", "https://www.native-instruments.com/en/products/komplete/guitar/session-guitarist-picked-acoustic/", 2019,
       ["guitar", "acoustic", "fingerpicking", "patterns", "sample-based"],
       ["Picked Acoustic", "NI Picked Acoustic", "Session Guitarist Picked Acoustic"]),

    ni("ni-picked-nylon", "Session Guitarist - Picked Nylon", "instrument", "guitar",
       "Classical nylon-string guitar for Kontakt by Drumasonic with pattern-based performance engine and melodic playing capabilities.",
       "paid", "https://www.native-instruments.com/en/products/komplete/guitar/session-guitarist-picked-nylon/", 2021,
       ["guitar", "nylon", "classical", "fingerpicking", "patterns", "sample-based"],
       ["Picked Nylon", "NI Picked Nylon", "Session Guitarist Picked Nylon"]),

    ni("ni-acoustic-sunburst-deluxe", "Session Guitarist - Acoustic Sunburst Deluxe", "instrument", "guitar",
       "Premium acoustic guitar library with 254 picked and strummed patterns played by session professionals.",
       "paid", "https://www.native-instruments.com/en/products/komplete/guitar/session-guitarist-acoustic-sunburst-deluxe/", 2024,
       ["guitar", "acoustic", "strumming", "fingerpicking", "patterns", "sample-based"],
       ["Acoustic Sunburst Deluxe", "NI Acoustic Sunburst Deluxe"]),

    ni("ni-prime-bass", "Session Bassist - Prime Bass", "instrument", "general",
       "Kontakt electric bass instrument by Drumasonic with pattern-based engine delivering authentic bass guitar performances.",
       "paid", "https://www.native-instruments.com/en/products/komplete/guitar/session-bassist-prime-bass/", 2022,
       ["bass", "electric", "patterns", "sample-based"],
       ["Prime Bass", "Session Bassist Prime Bass", "NI Prime Bass"]),

    # ── Discovery / Spotlight Series ─────────────────────────────────────
    ni("ni-discovery-india", "Discovery Series: India", "instrument", "rompler",
       "Comprehensive library of playable North and South Indian instruments with nine percussion and six melodic instruments and 96 raga scales.",
       "paid", "https://www.native-instruments.com/en/products/komplete/spotlight-collection/spotlight-collection/", 2014,
       ["world", "indian", "percussion", "melodic", "ethnic", "sample-based"],
       ["Discovery Series India", "NI India"]),

    ni("ni-discovery-west-africa", "Discovery Series: West Africa", "instrument", "rompler",
       "West African instrument collection for creating traditional polyrhythmic ensemble textures with one-touch playback.",
       "paid", "https://www.native-instruments.com/en/products/komplete/spotlight-collection/spotlight-collection/", 2014,
       ["world", "african", "percussion", "ensemble", "ethnic", "sample-based"],
       ["Discovery Series West Africa", "NI West Africa"]),

    ni("ni-discovery-middle-east", "Discovery Series: Middle East", "instrument", "rompler",
       "25 characteristic Arabic, Turkish, and Persian instruments including oud, ney, zurna, kanun, tanbur, and saz.",
       "paid", "https://www.native-instruments.com/en/products/komplete/spotlight-collection/spotlight-collection/", 2018,
       ["world", "middle-eastern", "ethnic", "arabic", "turkish", "sample-based"],
       ["Discovery Series Middle East", "NI Middle East"]),

    ni("ni-discovery-cuba", "Discovery Series: Cuba", "instrument", "rompler",
       "Meticulously sampled Cuban instruments with eight melodic and nine percussive ensembles reflecting Cuba's musical landscape.",
       "paid", "https://www.native-instruments.com/en/products/komplete/spotlight-collection/spotlight-collection/", 2016,
       ["world", "cuban", "latin", "percussion", "ensemble", "ethnic", "sample-based"],
       ["Discovery Series Cuba", "NI Cuba"]),
]


def main():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_slugs = {p["slug"] for p in data["plugins"]}
    added = 0
    skipped = 0

    for plugin in NI_PLUGINS:
        if plugin["slug"] in existing_slugs:
            print(f"  SKIP: {plugin['slug']}")
            skipped += 1
            continue
        data["plugins"].append(plugin)
        existing_slugs.add(plugin["slug"])
        added += 1

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    ni_total = len([p for p in data["plugins"] if p["manufacturer_slug"] == MFR])
    print(f"\nDone: +{added} NI plugins ({skipped} skipped)")
    print(f"Native Instruments total: {ni_total} plugins")
    print(f"Database total: {len(data['plugins'])} plugins")


if __name__ == "__main__":
    main()
