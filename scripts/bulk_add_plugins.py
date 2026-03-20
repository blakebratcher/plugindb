#!/usr/bin/env python3
"""Bulk add popular plugins to seed.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plugindb.seed import slugify

# Each tuple: (name, manufacturer_name, category, subcategory, formats, price_type, year, tags, description, url)
# Formats shorthand: A=all(VST3,AU,AAX), V=VST3+AU, C=VST3+AU+CLAP
NEW_MANUFACTURERS = [
    ("Spectrasonics", "https://www.spectrasonics.net"),
    ("East West", "https://www.soundsonline.com"),
    ("Toontrack", "https://www.toontrack.com"),
    ("IK Multimedia", "https://www.ikmultimedia.com"),
    ("Slate Digital", "https://www.slatedigital.com"),
    ("Soundtoys", "https://www.soundtoys.com"),
    ("Plugin Alliance", "https://www.plugin-alliance.com"),
    ("Universal Audio", "https://www.uaudio.com"),
    ("Voxengo", "https://www.voxengo.com"),
    ("TDR", "https://www.tokyodawn.net"),
    ("Analog Obsession", "https://www.patreon.com/analogobsession"),
    ("Klanghelm", "https://klanghelm.com"),
    ("Melda Production", "https://www.meldaproduction.com"),
    ("Cakewalk", "https://www.cakewalk.com"),
    ("Tone2", "https://www.tone2.com"),
    ("Synapse Audio", "https://www.synapse-audio.com"),
    ("Reveal Sound", "https://www.reveal-sound.com"),
    ("LennarDigital", "https://www.lennardigital.com"),
    ("Xln Audio", "https://www.xlnaudio.com"),
    ("Brainworx", "https://www.brainworx.audio"),
    ("Sonnox", "https://www.sonnox.com"),
    ("Acustica Audio", "https://www.acustica-audio.com"),
    ("AIR Music Technology", "https://www.airmusictech.com"),
    ("Harrison", "https://harrisonconsoles.com"),
    ("PSP Audioware", "https://www.pspaudioware.com"),
    ("Audiority", "https://www.audiority.com"),
    ("Auburn Sounds", "https://www.auburnsounds.com"),
    ("Oversampled", "https://oversampled.com"),
    ("Unfiltered Audio", "https://www.unfilteredaudio.com"),
    ("Spitfire Audio", "https://www.spitfireaudio.com"),
    ("Sample Logic", "https://www.samplelogic.com"),
    ("Output", "https://output.com"),
    ("Heavyocity", "https://heavyocity.com"),
    ("Ujam", "https://www.ujam.com"),
    ("UVI", "https://www.uvi.net"),
    ("TAL Software", "https://tal-software.com"),
    ("Dada Life", "https://www.dadalifetools.com"),
    ("Devious Machines", "https://deviousmachines.com"),
    ("Infected Mushroom", "https://polyversemusic.com"),
    ("Polyverse", "https://polyversemusic.com"),
    ("Minimal Audio", "https://www.minimal.audio"),
    ("Artistry Audio", "https://artistryaudio.com"),
    ("Initial Audio", "https://initialaudio.com"),
    ("Cherry Audio", "https://cherryaudio.com"),
    ("Kilohearts", "https://kilohearts.com"),
    ("Klevgrand", "https://klevgrand.com"),
    ("AudioThing", "https://www.audiothing.net"),
    ("Goodhertz", "https://goodhertz.com"),
    ("Sinevibes", "https://www.sinevibes.com"),
    ("Wavesfactory", "https://www.wavesfactory.com"),
    ("Black Rooster Audio", "https://blackroosteraudio.com"),
    ("Acon Digital", "https://acondigital.com"),
    ("DMG Audio", "https://dmgaudio.com"),
    ("Zynaptiq", "https://zynaptiq.com"),
    ("DDMF", "https://ddmf.eu"),
    ("Venn Audio", "https://www.vennaudio.com"),
    ("SocaLabs", "https://socalabs.com"),
    ("Full Bucket Music", "https://www.fullbucket.de"),
    ("HY-Plugins", "https://hy-plugins.com"),
    ("Analog Obsession", "https://www.patreon.com/analogobsession"),
]

# Massive list of plugins to add
NEW_PLUGINS = [
    # === INSTRUMENTS - Synths ===
    ("Omnisphere 2", "Spectrasonics", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2015, ["synthesizer", "hybrid", "sound-design", "creative", "pads"], "Flagship hybrid synthesizer with massive sound library and deep synthesis engine.", "https://www.spectrasonics.net/products/omnisphere/"),
    ("Phase Plant", "Kilohearts", "instrument", "synth", ["VST3", "AU", "CLAP"], "paid", 2019, ["synthesizer", "modular", "sound-design", "wavetable", "electronic"], "Modular synthesizer with snap-in effects and flexible routing.", "https://kilohearts.com/products/phase_plant"),
    ("Surge XT", "Surge Synth Team", "instrument", "synth", ["VST3", "AU", "CLAP", "LV2", "Standalone"], "free", 2022, ["synthesizer", "open-source", "free", "wavetable", "subtractive"], "Free open-source hybrid synthesizer with extensive modulation.", "https://surge-synthesizer.github.io/"),
    ("Helm", "Matt Tytel", "instrument", "synth", ["VST3", "AU", "LV2", "Standalone"], "free", 2015, ["synthesizer", "free", "open-source", "subtractive", "polyphonic"], "Free polyphonic synthesizer with flexible modulation routing.", "https://tytel.org/helm/"),
    ("Synth1", "Ichiro Toda", "instrument", "synth", ["VST2"], "free", 2004, ["synthesizer", "free", "virtual-analog", "classic"], "One of the most downloaded free VST synthesizers ever made.", "https://www.kvraudio.com/product/synth1-by-ichiro-toda"),
    ("Spire", "Reveal Sound", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2014, ["synthesizer", "trance", "edm", "polyphonic", "warm"], "Polyphonic synthesizer with powerful sound engine for EDM production.", "https://www.reveal-sound.com/"),
    ("Sylenth1", "LennarDigital", "instrument", "synth", ["VST3", "AU"], "paid", 2006, ["synthesizer", "virtual-analog", "warm", "classic", "edm"], "Classic virtual analog synthesizer known for warm, fat sounds.", "https://www.lennardigital.com/sylenth1/"),
    ("Hive 2", "u-he", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2020, ["synthesizer", "wavetable", "fast", "electronic", "versatile"], "Fast and versatile wavetable synthesizer with streamlined workflow.", "https://u-he.com/products/hive/"),
    ("Zebra2", "u-he", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2007, ["synthesizer", "modular", "sound-design", "creative", "versatile"], "Deep modular synthesizer used by film composers and sound designers.", "https://u-he.com/products/zebra2/"),
    ("Repro", "u-he", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2017, ["synthesizer", "analog-modeling", "vintage", "warm", "classic"], "Painstaking emulation of the Prophet-5 and Pro-One analog synths.", "https://u-he.com/products/repro/"),
    ("Bazille", "u-he", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2014, ["synthesizer", "modular", "digital", "fm", "experimental"], "Digital modular synthesizer with FM, phase distortion, and fractal resonance.", "https://u-he.com/products/bazille/"),
    ("ANA 2", "Slate Digital", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2019, ["synthesizer", "edm", "wavetable", "modern", "electronic"], "Modern synthesizer designed for electronic music production.", "https://www.slatedigital.com/ana-2/"),
    ("Electra2", "Tone2", "instrument", "synth", ["VST3", "AU"], "paid", 2014, ["synthesizer", "multi-synthesis", "versatile", "electronic"], "Multi-synthesis workstation with 9 different synthesis methods.", "https://www.tone2.com/electra2.html"),
    ("Icarus", "Tone2", "instrument", "synth", ["VST3", "AU"], "paid", 2017, ["synthesizer", "wavetable", "3d-wavetable", "modern"], "3D wavetable synthesizer with resynthesis capabilities.", "https://www.tone2.com/icarus.html"),
    ("Dune 3", "Synapse Audio", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2018, ["synthesizer", "virtual-analog", "wavetable", "polyphonic"], "VA/wavetable hybrid synth with dual arpeggiators.", "https://www.synapse-audio.com/dune3.html"),
    ("TAL-U-NO-LX", "TAL Software", "instrument", "synth", ["VST3", "AU", "AAX", "LV2"], "paid", 2012, ["synthesizer", "vintage", "juno", "analog-modeling", "warm"], "Emulation of the Roland Juno-60 with exact component modeling.", "https://tal-software.com/products/tal-u-no-lx"),
    ("TAL-Noisemaker", "TAL Software", "instrument", "synth", ["VST3", "AU", "LV2"], "free", 2009, ["synthesizer", "free", "virtual-analog", "versatile"], "Free virtual analog synthesizer with built-in effects.", "https://tal-software.com/products/tal-noisemaker"),
    ("Odin 2", "The Wave Warden", "instrument", "synth", ["VST3", "AU", "LV2", "Standalone"], "free", 2020, ["synthesizer", "free", "open-source", "semi-modular", "versatile"], "Free semi-modular synthesizer with 2400+ factory presets.", "https://www.thewavewarden.com/odin2"),
    ("ZebraHZ", "u-he", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2009, ["synthesizer", "film-scoring", "modular", "atmospheric"], "Extended Zebra2 for Hans Zimmer — expanded modular capabilities.", "https://u-he.com/products/zebrahz/"),
    ("Podolski", "u-he", "instrument", "synth", ["VST3", "AU", "AAX", "LV2"], "free", 2005, ["synthesizer", "free", "virtual-analog", "simple", "warm"], "Free simple virtual analog synth from u-he with great sound quality.", "https://u-he.com/products/podolski/"),
    ("Triple Cheese", "u-he", "instrument", "synth", ["VST3", "AU", "AAX", "LV2"], "free", 2006, ["synthesizer", "free", "creative", "unusual", "experimental"], "Free experimental synth using comb filter synthesis.", "https://u-he.com/products/triplecheese/"),
    ("Tyrell N6", "u-he", "instrument", "synth", ["VST3", "AU", "LV2"], "free", 2012, ["synthesizer", "free", "virtual-analog", "subtractive"], "Free virtual analog synth designed with Amazona magazine.", "https://u-he.com/products/tyrelln6/"),
    ("Sektor", "Initial Audio", "instrument", "synth", ["VST3", "AU"], "paid", 2018, ["synthesizer", "wavetable", "modern", "edm"], "Wavetable synthesizer with easy-to-use interface.", "https://initialaudio.com/product/sektor-wavetable-synthesizer/"),
    ("Synthmaster 2", "KV331 Audio", "instrument", "synth", ["VST3", "AU", "AAX"], "paid", 2012, ["synthesizer", "multi-synthesis", "versatile", "edm"], "All-around synthesizer with multiple synthesis methods.", "https://www.kv331audio.com/synthmaster.aspx"),
    ("Voltage Modular", "Cherry Audio", "instrument", "synth", ["VST3", "AU", "AAX", "Standalone"], "freemium", 2019, ["synthesizer", "modular", "eurorack", "virtual-modular"], "Virtual Eurorack modular synthesizer environment.", "https://cherryaudio.com/products/voltage-modular"),
    ("CA2600", "Cherry Audio", "instrument", "synth", ["VST3", "AU", "AAX", "Standalone"], "paid", 2020, ["synthesizer", "vintage", "arp-2600", "analog-modeling", "semi-modular"], "Faithful recreation of the ARP 2600 analog synthesizer.", "https://cherryaudio.com/products/ca2600"),
    ("Memorymode", "Cherry Audio", "instrument", "synth", ["VST3", "AU", "AAX", "Standalone"], "paid", 2021, ["synthesizer", "vintage", "memorymoog", "analog-modeling", "polyphonic"], "Recreation of the Memorymoog polyphonic analog synthesizer.", "https://cherryaudio.com/products/memorymode"),
    ("Dreamsynth", "Cherry Audio", "instrument", "synth", ["VST3", "AU", "AAX", "Standalone"], "paid", 2023, ["synthesizer", "modern", "wavetable", "creative"], "Modern wavetable synthesizer with intuitive interface.", "https://cherryaudio.com/products/dreamsynth"),
    ("Monique", "Thomas Neuhaus", "instrument", "synth", ["VST3", "AU", "Standalone"], "free", 2018, ["synthesizer", "free", "monophonic", "bass", "lead"], "Free monophonic synthesizer optimized for bass and lead sounds.", "https://github.com/surge-synthesizer/monique-monosynth"),
    ("Ample Guitar", "Ample Sound", "instrument", "guitar", ["VST3", "AU", "AAX"], "freemium", 2015, ["guitar", "acoustic", "sample-based", "realistic"], "Realistic acoustic and electric guitar virtual instruments.", "https://www.amplesound.net/en/pro-pd.asp?id=7"),
    ("Addictive Keys", "Xln Audio", "instrument", "piano", ["VST3", "AU", "AAX"], "paid", 2012, ["piano", "keyboard", "sample-based", "realistic"], "Studio grand, electric grand, and modern upright piano instruments.", "https://www.xlnaudio.com/products/addictive-keys"),

    # === INSTRUMENTS - Samplers/Romplers ===
    ("LABS", "Spitfire Audio", "instrument", "sampler", ["VST3", "AU", "AAX", "Standalone"], "free", 2017, ["sampler", "free", "orchestral", "cinematic", "strings"], "Free curated sample library from Spitfire Audio.", "https://www.spitfireaudio.com/labs"),
    ("Decent Sampler", "Decent Samples", "instrument", "sampler", ["VST3", "AU", "AAX", "Standalone"], "free", 2020, ["sampler", "free", "open-format", "versatile"], "Free sample player that plays .dspreset format samples.", "https://www.decentsamples.com/product/decent-sampler-plugin/"),
    ("EZdrummer 3", "Toontrack", "instrument", "drum-machine", ["VST3", "AU", "AAX"], "paid", 2022, ["drums", "drum-machine", "realistic", "mixing"], "Drum production studio with realistic drum sounds and song creation.", "https://www.toontrack.com/product/ezdrummer-3/"),
    ("Superior Drummer 3", "Toontrack", "instrument", "drum-machine", ["VST3", "AU", "AAX"], "paid", 2017, ["drums", "drum-machine", "professional", "mixing", "realistic"], "Professional drum production with immersive sound library.", "https://www.toontrack.com/product/superior-drummer-3/"),
    ("Addictive Drums 2", "Xln Audio", "instrument", "drum-machine", ["VST3", "AU", "AAX"], "paid", 2014, ["drums", "drum-machine", "realistic", "mixing"], "Complete drum production studio with mix-ready sounds.", "https://www.xlnaudio.com/products/addictive-drums-2"),
    ("SampleTank 4", "IK Multimedia", "instrument", "rompler", ["VST3", "AU", "AAX", "Standalone"], "paid", 2019, ["rompler", "workstation", "sample-based", "multi-timbral"], "Sound and groove workstation with thousands of instruments.", "https://www.ikmultimedia.com/products/sampletank4/"),
    ("Falcon 3", "UVI", "instrument", "sampler", ["VST3", "AU", "AAX", "Standalone"], "paid", 2023, ["sampler", "synthesizer", "hybrid", "sound-design"], "Hybrid instrument combining sampling, synthesis, and effects.", "https://www.uvi.net/falcon.html"),
    ("Grace", "One Small Clue", "instrument", "sampler", ["VST3"], "free", 2015, ["sampler", "free", "sfz-player", "lightweight"], "Free SFZ sample player with low CPU usage.", "https://www.onesmallclue.com/plugin/grace/"),
    ("Sforzando", "Plogue", "instrument", "sampler", ["VST3", "AU", "AAX", "Standalone"], "free", 2012, ["sampler", "free", "sfz-player", "versatile"], "Free high-quality SFZ player from Plogue.", "https://www.plogue.com/products/sforzando.html"),

    # === EFFECTS - EQs ===
    ("Pro-Q 4", "FabFilter", "effect", "eq", ["VST3", "AU", "AAX", "CLAP"], "paid", 2024, ["equalizer", "mixing", "mastering", "dynamic-eq", "precise"], "Industry-standard parametric EQ with dynamic EQ and spectrum analysis.", "https://www.fabfilter.com/products/pro-q-4-equalizer-plug-in"),
    ("Equilibrium", "DMG Audio", "effect", "eq", ["VST3", "AU", "AAX"], "paid", 2016, ["equalizer", "mixing", "mastering", "precise", "linear-phase"], "Precision parametric EQ with linear-phase and minimum-phase modes.", "https://dmgaudio.com/equilibrium"),
    ("SlickEQ", "TDR", "effect", "eq", ["VST3", "AU", "AAX"], "free", 2015, ["equalizer", "free", "mixing", "analog-modeling", "musical"], "Free mixing and mastering EQ with analog-modeled character.", "https://www.tokyodawn.net/tdr-slickeq/"),
    ("Nova GE", "TDR", "effect", "eq", ["VST3", "AU", "AAX"], "paid", 2016, ["equalizer", "dynamic-eq", "mixing", "mastering", "precise"], "Parallel dynamic equalizer for precision mixing.", "https://www.tokyodawn.net/tdr-nova-ge/"),
    ("Kirchhoff EQ", "Three-Body Technology", "effect", "eq", ["VST3", "AU", "AAX", "CLAP"], "paid", 2022, ["equalizer", "mixing", "mastering", "analog-modeling", "modern"], "Modern equalizer with analog circuit modeling and AI-assisted features.", "https://www.threebodytech.com/kirchhoff-eq/"),
    ("Toned", "AudioThing", "effect", "eq", ["VST3", "AU", "AAX"], "free", 2023, ["equalizer", "free", "simple", "mixing", "tone-shaping"], "Free Baxandall EQ with warm analog character.", "https://www.audiothing.net/plugins/toned/"),
    ("Marvel GEQ", "Voxengo", "effect", "eq", ["VST3", "AU", "AAX"], "free", 2006, ["equalizer", "free", "graphic-eq", "linear-phase", "mixing"], "Free linear-phase 16-band graphic equalizer.", "https://www.voxengo.com/product/marvelgeq/"),
    ("SPAN", "Voxengo", "effect", "analyzer", ["VST3", "AU", "AAX"], "free", 2006, ["analyzer", "free", "spectrum", "metering", "mixing"], "Free real-time FFT spectrum analyzer for mixing.", "https://www.voxengo.com/product/span/"),
    ("Ozone Equalizer", "iZotope", "effect", "eq", ["VST3", "AU", "AAX"], "paid", 2023, ["equalizer", "mastering", "mixing", "dynamic-eq"], "Mastering-grade equalizer from the Ozone suite.", "https://www.izotope.com/en/products/ozone.html"),
    ("MEqualizer", "Melda Production", "effect", "eq", ["VST3", "AU", "AAX"], "free", 2010, ["equalizer", "free", "parametric", "mixing", "versatile"], "Free 6-band parametric EQ with analyzer.", "https://www.meldaproduction.com/MEqualizer"),

    # === EFFECTS - Compressors ===
    ("Pro-C 2", "FabFilter", "effect", "compressor", ["VST3", "AU", "AAX", "CLAP"], "paid", 2017, ["compressor", "mixing", "mastering", "versatile", "precise"], "Professional compressor with 8 compression styles.", "https://www.fabfilter.com/products/pro-c-2-compressor-plug-in"),
    ("Kotelnikov GE", "TDR", "effect", "compressor", ["VST3", "AU", "AAX"], "paid", 2017, ["compressor", "mastering", "transparent", "precise", "bus-compressor"], "Gentlemen's Edition mastering compressor with surgical precision.", "https://www.tokyodawn.net/tdr-kotelnikov-ge/"),
    ("Kotelnikov", "TDR", "effect", "compressor", ["VST3", "AU", "AAX"], "free", 2014, ["compressor", "free", "mastering", "transparent", "bus-compressor"], "Free wideband dynamics processor for mastering.", "https://www.tokyodawn.net/tdr-kotelnikov/"),
    ("Molotok", "TDR", "effect", "compressor", ["VST3", "AU", "AAX"], "free", 2019, ["compressor", "free", "character", "drums", "aggressive"], "Free character compressor with aggressive sound.", "https://www.tokyodawn.net/tdr-molotok/"),
    ("DC1A", "Klanghelm", "effect", "compressor", ["VST3", "AU"], "free", 2013, ["compressor", "free", "simple", "character", "mixing"], "Free character compressor with just two knobs.", "https://klanghelm.com/contents/products/DC1A.php"),
    ("MJUC jr.", "Klanghelm", "effect", "compressor", ["VST3", "AU"], "free", 2016, ["compressor", "free", "variable-mu", "vintage", "warm"], "Free variable-mu compressor with vintage character.", "https://klanghelm.com/contents/products/MJUCjr.php"),
    ("Rough Rider 3", "Audio Damage", "effect", "compressor", ["VST3", "AU", "CLAP"], "free", 2020, ["compressor", "free", "aggressive", "character", "drums"], "Free modern compressor with aggressive character.", "https://www.audiodamage.com/pages/ad056-roughrider3"),
    ("MCompressor", "Melda Production", "effect", "compressor", ["VST3", "AU", "AAX"], "free", 2010, ["compressor", "free", "versatile", "mixing", "transparent"], "Free compressor with advanced sidechain options.", "https://www.meldaproduction.com/MCompressor"),
    ("LA-2A", "Universal Audio", "effect", "compressor", ["VST3", "AU", "AAX"], "paid", 2011, ["compressor", "optical", "vintage", "warm", "vocals"], "Classic optical compressor emulation for smooth compression.", "https://www.uaudio.com/uad-plugins/compressors-limiters/teletronix-la-2a.html"),
    ("1176", "Universal Audio", "effect", "compressor", ["VST3", "AU", "AAX"], "paid", 2011, ["compressor", "fet", "vintage", "punchy", "drums"], "FET compressor emulation — the legendary 1176 hardware.", "https://www.uaudio.com/uad-plugins/compressors-limiters/1176-compressor-collection.html"),

    # === EFFECTS - Reverbs ===
    ("Pro-R 2", "FabFilter", "effect", "reverb", ["VST3", "AU", "AAX", "CLAP"], "paid", 2023, ["reverb", "mixing", "mastering", "natural", "algorithmic"], "Natural sounding reverb with intuitive decay rate EQ.", "https://www.fabfilter.com/products/pro-r-2-reverb-plug-in"),
    ("Valhalla Room", "Valhalla DSP", "effect", "reverb", ["VST3", "AU", "AAX"], "paid", 2012, ["reverb", "algorithmic", "versatile", "natural", "ambient"], "Versatile algorithmic reverb for natural and ambient spaces.", "https://valhalladsp.com/shop/reverb/valhalla-room/"),
    ("Valhalla Shimmer", "Valhalla DSP", "effect", "reverb", ["VST3", "AU", "AAX"], "paid", 2012, ["reverb", "shimmer", "ambient", "creative", "ethereal"], "Reverb with pitch-shifted feedback for ethereal textures.", "https://valhalladsp.com/shop/reverb/valhalla-shimmer/"),
    ("Valhalla Supermassive", "Valhalla DSP", "effect", "reverb", ["VST3", "AU", "AAX"], "free", 2020, ["reverb", "delay", "free", "ambient", "massive", "creative"], "Free massive reverb and delay plugin for lush ambient textures.", "https://valhalladsp.com/shop/reverb/valhalla-supermassive/"),
    ("Valhalla Delay", "Valhalla DSP", "effect", "delay", ["VST3", "AU", "AAX"], "paid", 2018, ["delay", "tape", "vintage", "versatile", "creative"], "Versatile delay with tape, BBD, digital, and pitch modes.", "https://valhalladsp.com/shop/delay/valhalla-delay/"),
    ("Valhalla Freq Echo", "Valhalla DSP", "effect", "delay", ["VST3", "AU", "AAX"], "free", 2013, ["delay", "frequency-shifter", "free", "psychedelic", "creative"], "Free frequency shifter and analog echo plugin.", "https://valhalladsp.com/shop/delay/valhalla-freq-echo/"),
    ("Tai Chi", "Valhalla DSP", "effect", "reverb", ["VST3", "AU", "AAX"], "paid", 2024, ["reverb", "creative", "modulated", "ambient", "textural"], "Creative modulated reverb for evolving textures.", "https://valhalladsp.com/shop/reverb/valhalla-tai-chi/"),
    ("Raum", "Native Instruments", "effect", "reverb", ["VST3", "AU", "AAX"], "free", 2019, ["reverb", "free", "creative", "ambient", "textural"], "Free creative reverb with three distinct algorithms.", "https://www.native-instruments.com/en/products/komplete/effects/raum/"),
    ("CloudSeed", "Ghost Note Audio", "effect", "reverb", ["VST3", "AU", "CLAP"], "free", 2022, ["reverb", "free", "algorithmic", "ambient", "lush"], "Free algorithmic reverb inspired by classic hardware.", "https://github.com/ghostnoteaudio/cloudseed"),
    ("MConvolutionEZ", "Melda Production", "effect", "reverb", ["VST3", "AU", "AAX"], "free", 2010, ["reverb", "free", "convolution", "realistic", "mixing"], "Free convolution reverb with zero-latency processing.", "https://www.meldaproduction.com/MConvolutionEZ"),
    ("TAL-Reverb-4", "TAL Software", "effect", "reverb", ["VST3", "AU", "LV2"], "free", 2010, ["reverb", "free", "plate", "vintage", "warm"], "Free plate reverb with warm vintage character.", "https://tal-software.com/products/tal-reverb-4"),

    # === EFFECTS - Delays ===
    ("EchoBoy", "Soundtoys", "effect", "delay", ["VST3", "AU", "AAX"], "paid", 2007, ["delay", "tape", "analog", "vintage", "creative"], "Analog-style echo plugin with 30+ echo styles.", "https://www.soundtoys.com/product/echoboy/"),
    ("Timeless 3", "FabFilter", "effect", "delay", ["VST3", "AU", "AAX", "CLAP"], "paid", 2023, ["delay", "tape", "creative", "modulation", "modern"], "Creative delay with drag-and-drop modulation system.", "https://www.fabfilter.com/products/timeless-3-delay-plug-in"),
    ("H-Delay", "Waves", "effect", "delay", ["VST3", "AU", "AAX"], "paid", 2007, ["delay", "hybrid", "analog", "versatile", "mixing"], "Versatile hybrid delay with analog and digital modes.", "https://www.waves.com/plugins/h-delay-hybrid-delay"),
    ("MFreeFXBundle", "Melda Production", "effect", "general", ["VST3", "AU", "AAX"], "free", 2010, ["bundle", "free", "effects", "mixing", "versatile"], "Free bundle of 37 audio effects plugins for mixing.", "https://www.meldaproduction.com/MFreeFXBundle"),
    ("TAL-Dub-3", "TAL Software", "effect", "delay", ["VST3", "AU", "LV2"], "free", 2010, ["delay", "free", "dub", "vintage", "tape"], "Free vintage-style dub delay with character.", "https://tal-software.com/products/tal-dub-3"),

    # === EFFECTS - Distortion/Saturation ===
    ("Decapitator", "Soundtoys", "effect", "saturation", ["VST3", "AU", "AAX"], "paid", 2010, ["saturation", "distortion", "analog", "warm", "character"], "Analog saturation modeler with 5 hardware models.", "https://www.soundtoys.com/product/decapitator/"),
    ("Saturn 2", "FabFilter", "effect", "saturation", ["VST3", "AU", "AAX", "CLAP"], "paid", 2020, ["saturation", "distortion", "multiband", "creative", "mixing"], "Multiband distortion and saturation processor.", "https://www.fabfilter.com/products/saturn-2-multiband-distortion-saturation-plug-in"),
    ("Trash 2", "iZotope", "effect", "distortion", ["VST3", "AU", "AAX"], "paid", 2012, ["distortion", "creative", "multiband", "sound-design", "aggressive"], "Multiband distortion system with convolution and dynamics.", "https://www.izotope.com/en/products/trash.html"),
    ("Camel Crusher", "Camel Audio", "effect", "distortion", ["VST2"], "free", 2012, ["distortion", "free", "compression", "warm", "aggressive"], "Free distortion plugin with compression and filter.", "https://www.kvraudio.com/product/camelcrusher-by-camel-audio"),
    ("Softube Saturation Knob", "Softube", "effect", "saturation", ["VST3", "AU", "AAX"], "free", 2016, ["saturation", "free", "simple", "warm", "mixing"], "Free one-knob saturation plugin from Softube.", "https://www.softube.com/saturation-knob"),
    ("FreeClip", "Venn Audio", "effect", "saturation", ["VST3", "AU", "CLAP"], "free", 2021, ["clipper", "free", "saturation", "mastering", "loudness"], "Free soft clipper for adding warmth and loudness.", "https://www.vennaudio.com/freeclip/"),

    # === EFFECTS - Limiters ===
    ("Pro-L 2", "FabFilter", "effect", "limiter", ["VST3", "AU", "AAX", "CLAP"], "paid", 2017, ["limiter", "mastering", "loudness", "transparent", "precise"], "Mastering limiter with 8 limiting algorithms.", "https://www.fabfilter.com/products/pro-l-2-limiter-plug-in"),
    ("Invisible Limiter G2", "AOM", "effect", "limiter", ["VST3", "AU", "AAX"], "paid", 2019, ["limiter", "mastering", "transparent", "precise", "loudness"], "Ultra-transparent mastering limiter.", "https://aom-factory.jp/en/products/invisible-limiter-g2/"),
    ("Youlean Loudness Meter 2", "Youlean", "effect", "analyzer", ["VST3", "AU", "AAX"], "freemium", 2018, ["metering", "loudness", "lufs", "free", "mixing", "mastering"], "Industry-standard loudness meter supporting LUFS standards.", "https://youlean.co/youlean-loudness-meter/"),
    ("Limiter No6", "Vladg Sound", "effect", "limiter", ["VST3", "AU"], "free", 2012, ["limiter", "free", "mastering", "multiband", "versatile"], "Free mastering limiter with 5 processing modules.", "https://vladgsound.wordpress.com/plugins/limiter6/"),

    # === EFFECTS - Modulation ===
    ("PhaseMistress", "Soundtoys", "effect", "modulation", ["VST3", "AU", "AAX"], "paid", 2016, ["phaser", "modulation", "analog", "vintage", "creative"], "Analog phaser with extreme modulation options.", "https://www.soundtoys.com/product/phasemistress/"),
    ("Tremolator", "Soundtoys", "effect", "modulation", ["VST3", "AU", "AAX"], "paid", 2007, ["tremolo", "modulation", "rhythmic", "creative", "vintage"], "Rhythmic tremolo and auto-gating effect.", "https://www.soundtoys.com/product/tremolator/"),
    ("Crystallizer", "Soundtoys", "effect", "delay", ["VST3", "AU", "AAX"], "paid", 2006, ["delay", "granular", "pitch-shift", "creative", "ambient"], "Granular reverse echo with pitch-shifting.", "https://www.soundtoys.com/product/crystallizer/"),
    ("Little AlterBoy", "Soundtoys", "effect", "pitch", ["VST3", "AU", "AAX"], "paid", 2014, ["pitch", "formant", "vocal", "creative", "sound-design"], "Vocal character and pitch manipulation.", "https://www.soundtoys.com/product/little-alterboy/"),
    ("MFlanger", "Melda Production", "effect", "modulation", ["VST3", "AU", "AAX"], "free", 2010, ["flanger", "free", "modulation", "creative", "mixing"], "Free classic flanger effect with modern features.", "https://www.meldaproduction.com/MFlanger"),
    ("Chorus CE-2W", "Roland", "effect", "chorus", ["VST3", "AU", "AAX"], "paid", 2019, ["chorus", "vintage", "warm", "modulation", "classic"], "Software version of the legendary Boss CE-2W chorus.", "https://www.roland.com/global/products/rc_ce-2w/"),

    # === EFFECTS - Filters ===
    ("FilterFreak", "Soundtoys", "effect", "filter", ["VST3", "AU", "AAX"], "paid", 2007, ["filter", "analog", "resonant", "creative", "modulation"], "Analog filter plugin with rhythm sync and modulation.", "https://www.soundtoys.com/product/filterfreak/"),
    ("IVGI", "Klanghelm", "effect", "saturation", ["VST3", "AU"], "free", 2013, ["saturation", "free", "analog-modeling", "warm", "mixing"], "Free analog saturation plugin for subtle warmth.", "https://klanghelm.com/contents/products/IVGI.php"),

    # === EFFECTS - Multi-effects ===
    ("Effectrix", "Sugar Bytes", "effect", "general", ["VST3", "AU", "AAX"], "paid", 2009, ["multi-effect", "sequencer", "creative", "glitch", "performance"], "14 effects in a sequencer grid for creative processing.", "https://sugar-bytes.de/effectrix"),
    ("Turnado", "Sugar Bytes", "effect", "general", ["VST3", "AU", "AAX"], "paid", 2012, ["multi-effect", "performance", "creative", "live", "dj"], "Real-time multi-effect processor for live performance.", "https://sugar-bytes.de/turnado"),
    ("Portal", "Output", "effect", "general", ["VST3", "AU", "AAX"], "paid", 2019, ["granular", "creative", "sound-design", "ambient", "textural"], "Granular effects processor for creative sound design.", "https://output.com/products/portal"),

    # === UTILITIES ===
    ("Soothe2", "Oeksound", "utility", "analyzer", ["VST3", "AU", "AAX"], "paid", 2020, ["resonance-suppression", "mixing", "mastering", "de-harsh", "dynamic"], "Dynamic resonance suppressor for taming harsh frequencies.", "https://oeksound.com/plugins/soothe2/"),
    ("SPAN Plus", "Voxengo", "utility", "analyzer", ["VST3", "AU", "AAX"], "paid", 2012, ["analyzer", "spectrum", "metering", "mixing", "mastering"], "Advanced real-time FFT spectrum analyzer.", "https://www.voxengo.com/product/spanplus/"),
    ("Reference", "Mastering The Mix", "utility", "analyzer", ["VST3", "AU", "AAX"], "paid", 2018, ["reference", "mixing", "mastering", "analysis", "comparison"], "Reference track comparison tool for mixing and mastering.", "https://www.masteringthemix.com/products/reference"),
    ("LEVELS", "Mastering The Mix", "utility", "meter", ["VST3", "AU", "AAX"], "paid", 2017, ["metering", "mixing", "mastering", "lufs", "analysis"], "Multi-metric metering tool for mix and master analysis.", "https://www.masteringthemix.com/products/levels"),
    ("Expose 2", "Mastering The Mix", "utility", "analyzer", ["VST3", "AU", "AAX", "Standalone"], "paid", 2021, ["analysis", "mastering", "quality-control", "metering"], "Audio quality control and analysis tool.", "https://www.masteringthemix.com/products/expose"),
    ("bx_meter", "Brainworx", "utility", "meter", ["VST3", "AU", "AAX"], "free", 2012, ["metering", "free", "loudness", "lufs", "mixing"], "Free loudness metering plugin with LUFS support.", "https://www.plugin-alliance.com/en/products/bx_meter.html"),
    ("Correlometer", "Voxengo", "utility", "meter", ["VST3", "AU", "AAX"], "free", 2006, ["metering", "free", "correlation", "phase", "stereo"], "Free stereo correlation meter for phase analysis.", "https://www.voxengo.com/product/correlometer/"),
    ("dpMeter5", "TBProAudio", "utility", "meter", ["VST3", "AU", "AAX"], "free", 2020, ["metering", "free", "loudness", "lufs", "mastering"], "Free loudness meter supporting all broadcast standards.", "https://www.tbproaudio.de/products/dpmeter"),
    ("Plugin Doctor", "DDMF", "utility", "analyzer", ["VST3", "AU", "AAX", "Standalone"], "paid", 2015, ["analyzer", "testing", "plugin-analysis", "frequency-response"], "Plugin analysis tool for examining frequency response and distortion.", "https://ddmf.eu/plugindoctor/"),
    ("MSED", "Voxengo", "utility", "routing", ["VST3", "AU", "AAX"], "free", 2006, ["mid-side", "free", "encoding", "decoding", "stereo"], "Free mid-side encoding and decoding utility.", "https://www.voxengo.com/product/msed/"),
    ("Panagement", "Auburn Sounds", "utility", "routing", ["VST3", "AU", "AAX", "CLAP"], "free", 2019, ["panning", "free", "spatial", "stereo", "imaging"], "Free spatial audio plugin for natural 3D panning.", "https://www.auburnsounds.com/products/Panagement.html"),
    ("Blue Cat Gain Suite", "Blue Cat Audio", "utility", "general", ["VST3", "AU", "AAX"], "free", 2005, ["gain", "free", "utility", "metering", "basic"], "Free gain, stereo, and channel utilities.", "https://www.bluecataudio.com/Products/Bundle_FreePack/"),
    ("MAnalyzer", "Melda Production", "utility", "analyzer", ["VST3", "AU", "AAX"], "free", 2010, ["analyzer", "free", "spectrum", "mixing", "dual-channel"], "Free dual-channel spectrum analyzer.", "https://www.meldaproduction.com/MAnalyzer"),
    ("Torpedo Wall of Sound", "Two Notes", "utility", "general", ["VST3", "AU", "AAX", "Standalone"], "freemium", 2016, ["cab-sim", "guitar", "amp", "impulse-response", "mixing"], "Guitar and bass cabinet simulator with IR loading.", "https://www.two-notes.com/wall-of-sound"),

    # === EFFECTS - More compressors ===
    ("SSL Native Bus Compressor 2", "SSL", "effect", "compressor", ["VST3", "AU", "AAX"], "paid", 2022, ["compressor", "bus-compressor", "ssl", "glue", "mixing"], "The legendary SSL bus compressor — official native plugin.", "https://www.solidstatelogic.com/products/native-bus-compressor-2"),
    ("Compassion", "DMG Audio", "effect", "compressor", ["VST3", "AU", "AAX"], "paid", 2018, ["compressor", "versatile", "mixing", "mastering", "precise"], "Advanced compressor with multiple detection and processing modes.", "https://dmgaudio.com/compassion"),
    ("EQuick", "DMG Audio", "effect", "eq", ["VST3", "AU", "AAX"], "free", 2017, ["equalizer", "free", "fast", "mixing", "lightweight"], "Free lightning-fast equalizer for quick mixing.", "https://dmgaudio.com/equick"),

    # === EFFECTS - More effects ===
    ("Devil-Loc", "Soundtoys", "effect", "compressor", ["VST3", "AU", "AAX"], "paid", 2010, ["compressor", "distortion", "character", "lo-fi", "drums"], "Audio level destroyer for extreme compression and distortion.", "https://www.soundtoys.com/product/devil-loc/"),
    ("Little Plate", "Soundtoys", "effect", "reverb", ["VST3", "AU", "AAX"], "paid", 2017, ["reverb", "plate", "vintage", "simple", "warm"], "Vintage plate reverb with simple two-knob interface.", "https://www.soundtoys.com/product/little-plate/"),
    ("Sie-Q", "Soundtoys", "effect", "eq", ["VST3", "AU", "AAX"], "free", 2022, ["equalizer", "free", "analog", "vintage", "simple"], "Free vintage German broadcast EQ plugin.", "https://www.soundtoys.com/product/sie-q/"),
    ("Radiator", "Soundtoys", "effect", "saturation", ["VST3", "AU", "AAX"], "free", 2017, ["saturation", "free", "tube", "warm", "lo-fi"], "Free lo-fi tube saturation from vintage hardware.", "https://www.soundtoys.com/product/radiator/"),
    ("VU Meter", "Klanghelm", "utility", "meter", ["VST3", "AU"], "free", 2015, ["metering", "free", "vu", "vintage", "mixing"], "Free VU meter with vintage styling.", "https://klanghelm.com/contents/products/VUMeter.php"),
    ("GClip", "GVST", "effect", "saturation", ["VST3"], "free", 2010, ["clipper", "free", "saturation", "simple", "mastering"], "Free waveshaping clipper for subtle saturation.", "https://www.gvst.co.uk/gclip.htm"),
    ("OTT", "Xfer Records", "effect", "compressor", ["VST3", "AU"], "free", 2012, ["compressor", "multiband", "free", "edm", "aggressive"], "Free multiband upward/downward compressor. An EDM staple.", "https://xferrecords.com/freeware"),
]


def main():
    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_slugs = {p["slug"] for p in data["plugins"]}
    existing_mfr_slugs = {m["slug"] for m in data["manufacturers"]}

    # Add new manufacturers
    mfr_added = 0
    for name, website in NEW_MANUFACTURERS:
        slug = slugify(name)
        if slug not in existing_mfr_slugs:
            data["manufacturers"].append({"slug": slug, "name": name, "website": website})
            existing_mfr_slugs.add(slug)
            mfr_added += 1

    # Sort manufacturers
    data["manufacturers"].sort(key=lambda m: m["slug"])

    # Add new plugins
    plugins_added = 0
    skipped = 0
    for name, mfr_name, category, subcategory, formats, price_type, year, tags, description, url in NEW_PLUGINS:
        plugin_slug = slugify(name)
        mfr_slug = slugify(mfr_name)

        if plugin_slug in existing_slugs:
            skipped += 1
            continue

        if mfr_slug not in existing_mfr_slugs:
            print(f"  WARNING: manufacturer '{mfr_name}' ({mfr_slug}) not found, adding...")
            data["manufacturers"].append({"slug": mfr_slug, "name": mfr_name})
            existing_mfr_slugs.add(mfr_slug)

        plugin = {
            "slug": plugin_slug,
            "name": name,
            "manufacturer_slug": mfr_slug,
            "category": category,
            "subcategory": subcategory,
            "formats": formats,
            "aliases": [name, f"{mfr_name} {name}"],
            "daws": ["Ableton", "Bitwig", "Cubase", "Studio One", "Reaper", "FL Studio", "Logic", "Pro Tools"],
            "os": ["windows", "macos"],
            "description": description,
            "price_type": price_type,
            "url": url,
            "year": year,
            "tags": tags,
        }
        data["plugins"].append(plugin)
        existing_slugs.add(plugin_slug)
        plugins_added += 1

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Added {plugins_added} plugins, {mfr_added} manufacturers ({skipped} skipped as duplicates)")
    print(f"Total: {len(data['plugins'])} plugins, {len(data['manufacturers'])} manufacturers")


if __name__ == "__main__":
    main()
