"""One-time script to enrich seed.json with descriptions, price_type, year, and fix formats."""
import json
import sys

# Load seed.json
with open("seed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ── Description map (slug -> description) ──
DESCRIPTIONS = {
    # Ableton
    "ableton-drift": "Subtractive/wavetable hybrid synthesizer with a streamlined interface, built for Ableton Live.",
    "ableton-meld": "Two-oscillator synthesizer blending MPE support with a unique macro-driven interface for Ableton Live.",
    "operator": "FM synthesis instrument in Ableton Live with four oscillators and a flexible routing matrix.",
    "wavetable": "Ableton Live's wavetable synthesizer with dual oscillators, sub oscillator, and extensive modulation.",

    # Air Music Technology
    "hybrid-3": "Virtual analog synthesizer combining subtractive and wavetable synthesis with built-in effects.",
    "vacuum-pro": "Polyphonic vacuum tube synthesizer emulating vintage tube-driven analog hardware.",

    # Analog Obsession
    "fetish": "FET-style compressor plugin modeled after vintage solid-state hardware compressors.",
    "loaded": "Channel EQ plugin inspired by classic analog console equalizers.",
    "rare": "Vari-mu tube compressor emulation modeled after vintage broadcast limiters.",

    # Andrew Huang
    "amelia": "Experimental synthesizer designed by Andrew Huang with unique sound design capabilities.",

    # Arturia
    "analog-lab-v": "Preset browser and performance instrument providing access to sounds from Arturia's V Collection.",
    "arturia-comp-fet-76": "FET compressor emulation modeled after the classic UREI 1176 hardware.",
    "arturia-jupiter-8v": "Software emulation of the Roland Jupiter-8 analog polysynth with extended features.",
    "arturia-mini-v": "Software emulation of the Minimoog Model D monosynth with added polyphony and effects.",
    "pigments-4": "Polychrome software synthesizer with wavetable, virtual analog, granular, and harmonic engines.",
    "arturia-prophet-v": "Software emulation of the Sequential Prophet-5 analog polysynth with hybrid layering.",
    "arturia-rev-plate-140": "Plate reverb emulation modeled after the EMT 140 hardware unit.",

    # Audio Damage
    "dubstation-2": "Dub-style delay effect with tape emulation, spring reverb, and lo-fi character.",
    "quanta": "Granular synthesizer with a visual waveform display and real-time granular manipulation.",
    "ratshack-reverb": "Lo-fi spring reverb emulation inspired by cheap consumer reverb hardware.",

    # Baby Audio
    "baby-audio-comeback-kid": "Delay plugin with tape saturation, built-in ducking, and a vintage character.",
    "baby-audio-crystalline": "Algorithmic reverb with a clean, modern sound and intuitive reflection shaping controls.",
    "ihny-2": "Parallel compressor combining gentle and aggressive compression in a simple two-knob interface.",
    "parallel-aggressor": "Dual-engine parallel processor combining compression and saturation for mix glue.",
    "baby-audio-smooth-operator": "Spectral dynamics processor that smooths and balances audio using per-frequency compression.",
    "baby-audio-spaced-out": "Modulated delay and reverb effect designed for ambient and spatial textures.",
    "baby-audio-super-vhs": "Lo-fi effect emulating VHS tape degradation with wobble, noise, and saturation.",

    # Bettermaker
    "bettermaker-bus-compressor-dsp": "Bus compressor plugin modeled after the Bettermaker hardware mastering compressor.",

    # Bitwig native devices
    "bit-8": "Bitwig's built-in bitcrusher and sample rate reducer for lo-fi distortion effects.",
    "compressor": "Bitwig's built-in dynamics compressor with sidechain input and visual gain reduction.",
    "delay-4": "Bitwig's built-in stereo delay with four tap modes, feedback, and modulation.",
    "drum-machine": "Bitwig's built-in drum sampler with per-pad layering, effects, and modulation.",
    "dynamics": "Bitwig's combined compressor and expander with sidechain support and visual feedback.",
    "eq": "Bitwig's built-in parametric equalizer with up to 8 bands and spectrum analyzer.",
    "fx-grid": "Bitwig's modular patching environment for building custom audio effects from modules.",
    "fx-layer": "Bitwig container device for running multiple effect chains in parallel.",
    "gate": "Bitwig's built-in noise gate with sidechain input and adjustable hysteresis.",
    "grid": "Bitwig's modular patching environment for building custom instruments from modules.",
    "instrument-layer": "Bitwig container device for layering multiple instruments with mix and pan control.",
    "instrument-selector": "Bitwig container device for switching between multiple instruments via selection.",
    "limiter": "Bitwig's built-in brickwall limiter for peak control and loudness maximizing.",
    "multiband-fx-3": "Bitwig container that splits audio into three frequency bands for independent processing.",
    "oscilloscope": "Bitwig's built-in waveform display for real-time audio signal visualization.",
    "phase-4": "Bitwig's four-operator phase modulation synthesizer inspired by classic FM synthesis.",
    "poly-grid": "Bitwig's polyphonic modular patching environment for building custom instruments.",
    "polymer": "Bitwig's preset-based synthesizer combining multiple synthesis types with a macro interface.",
    "polysynth": "Bitwig's classic virtual analog polysynth with oscillators, filter, and envelope controls.",
    "reverb": "Bitwig's built-in algorithmic reverb with adjustable size, damping, and diffusion.",
    "sampler": "Bitwig's built-in multi-sample instrument with zones, modulation, and round-robin support.",
    "spectrum": "Bitwig's built-in FFT spectrum analyzer for frequency content visualization.",
    "tool": "Bitwig's utility device for gain, pan, phase inversion, and DC offset correction.",

    # Cableguys
    "filtershaper": "Multi-mode filter with drawable LFO curves for rhythmic and evolving filter effects.",
    "panshaper": "Auto-panner with drawable LFO waveforms for precise stereo motion and tremolo effects.",
    "shaperbox-3": "Multi-effect suite combining volume, filter, pan, width, and time shapers with drawable LFOs.",
    "timeshaper": "Time-manipulation effect using drawable curves to create glitch, stutter, and tape-stop effects.",
    "volumeshaper": "Sidechain-style volume shaping with drawable LFO curves for ducking and tremolo effects.",

    # Camel Audio
    "camelcrusher": "Free distortion plugin with two distortion modes, a compressor, and a low-pass filter.",

    # Cherry Audio
    "dreamsynth": "Polyphonic dreamlike synthesizer with wavetable and virtual analog oscillators.",
    "surrealistic-mg-1": "Software recreation of the Moog Realistic MG-1 monophonic analog synthesizer.",
    "voltage-modular": "Virtual Eurorack modular synthesizer environment with patchable modules.",

    # Cockos
    "reastream-standalone": "Network audio streaming utility for sending audio between DAWs over a LAN.",

    # Cymatics
    "cymatics-origin": "Wavetable synthesizer from Cymatics designed for modern electronic music production.",

    # D16 Group
    "decimort-2": "High-quality bitcrusher and sample rate reducer emulating vintage digital samplers.",
    "devastor-2": "Multiband distortion processor with three independent saturation stages.",
    "lush-2": "Stereo chorus and ensemble effect modeled after classic analog chorus hardware.",
    "repeater": "Delay effect with pitch shifting and reverse capabilities for creative echo effects.",

    # Denise Audio
    "perfect-room": "Algorithmic reverb focused on realistic room simulation with shape-based controls.",

    # Devious Machines
    "duck": "Volume ducking plugin that creates sidechain compression effects without a sidechain input.",
    "infiltrator": "Multi-effect processor with 54 effect modules arranged in a serial/parallel chain.",

    # discoDSP
    "ob-xd": "Free virtual analog synthesizer modeled after the Oberheim OB-X/OB-Xa hardware.",

    # DMG Audio
    "equilibrium": "Parametric equalizer with up to 32 bands, dynamic EQ, and multiple filter types.",

    # Eventide
    "blackhole": "Massive reverb inspired by the Eventide Space pedal, creating infinite ambient washes.",
    "h3000": "Multi-effects processor based on the legendary Eventide H3000 hardware harmonizer.",
    "mangledverb": "Reverb fed into distortion, creating aggressive and textural reverb effects.",
    "physion": "Transient shaping processor that splits audio into attack and sustain for independent processing.",
    "ultratap": "Multi-tap delay with up to 64 taps, rhythmic patterns, and modulation effects.",

    # FabFilter
    "fabfilter-pro-c-2": "Professional compressor with multiple compression styles, sidechain, and visual metering.",
    "fabfilter-pro-l-2": "True-peak brickwall limiter with multiple limiting algorithms and loudness metering.",
    "fabfilter-pro-mb": "Multiband dynamics processor with up to 6 bands and intelligent crossover filtering.",
    "pro-q-3": "Parametric equalizer with up to 24 bands, dynamic EQ, linear phase, and mid/side support.",
    "fabfilter-pro-r-2": "Algorithmic reverb with natural decay modeling and an intuitive visual interface.",
    "fabfilter-saturn-2": "Multiband saturation and distortion processor with modulation and multiple distortion styles.",
    "fabfilter-simplon": "Dual-filter plugin with low-pass, high-pass, band-pass, and notch filter modes.",
    "fabfilter-timeless-3": "Tape-style delay with pitch shifting, diffusion, and modulation effects.",
    "fabfilter-twin-3": "Synthesizer with three oscillators, multiple filter types, and extensive modulation routing.",
    "fabfilter-volcano-3": "Four-band filter effect with modulation, sidechain, and multiple filter slopes.",
    "harvest": "Discontinued granular synthesis instrument from FabFilter.",

    # Glitchmachines
    "fracture": "Buffer effect processor for creating glitch, stutter, and granular audio mangling.",
    "hysteresis": "Glitch delay plugin with modulated buffer effects for experimental sound design.",

    # Goodhertz
    "canopener": "Crossfeed plugin that simulates speaker playback through headphones for natural imaging.",
    "goodhertz-lossy": "Codec emulation effect simulating MP3, GSM, and other lossy compression artifacts.",
    "goodhertz-trem-control": "Tremolo effect with precise waveform shaping and stereo modulation options.",
    "goodhertz-vulf-compressor": "Characterful compressor with analog-inspired warmth and simple one-knob control.",
    "goodhertz-wow-control": "Wow and flutter effect emulating tape machine speed irregularities.",

    # IFEA
    "ifea-fusion": "Experimental audio effect combining multiple processing algorithms in a visual interface.",
    "ifea-obra": "Creative audio effect plugin with experimental sound transformation capabilities.",
    "ifea-spectral-compressor": "Spectral compressor applying per-frequency dynamic compression across the spectrum.",
    "ifea-spectral-gate": "Spectral noise gate operating on individual frequency bands for precise gating.",

    # Infected Mushroom / Polyverse
    "gatekeeper": "Volume gate sequencer with drawable envelopes for rhythmic gating and tremolo effects.",
    "i-wish": "Granular pitch-shifting effect that freezes and repitches audio in real time.",
    "manipulator": "Real-time vocal transformation plugin with pitch shifting, harmonizing, and vocoding.",

    # Initial Audio
    "heat-up-3": "Multi-format sample-based rompler covering keys, pads, basses, leads, and orchestral sounds.",
    "sektor": "Wavetable synthesizer with a visual interface and built-in effects for electronic music.",

    # iZotope
    "izotope-rx-voice-de-noise": "AI-powered noise reduction plugin for cleaning up vocal recordings in real time.",
    "izotope-nectar-4": "Vocal channel strip with AI-assisted processing, pitch correction, and harmonics.",
    "izotope-neutron-4": "AI-assisted mixing plugin with EQ, compression, gate, and transient shaping modules.",
    "ozone-11": "AI-powered mastering suite with EQ, dynamics, imager, limiter, and reference matching.",
    "ozone-11-equalizer": "Component EQ from Ozone 11 mastering suite with analog-modeled filter curves.",
    "ozone-11-exciter": "Component harmonic exciter from Ozone 11 with multiband saturation and warmth.",
    "ozone-11-imager": "Component stereo imager from Ozone 11 for multiband stereo width adjustment.",
    "ozone-11-master-rebalance": "AI-powered stem rebalancing tool from Ozone 11 for adjusting vocals, bass, and drums in a mix.",
    "izotope-ozone-9": "Previous-generation mastering suite with EQ, dynamics, imager, and maximizer modules.",
    "ozone-9-dynamics": "Component dynamics processor from Ozone 9 with multiband compression.",
    "izotope-rx-11": "Audio repair and restoration suite for noise reduction, de-click, de-hum, and spectral editing.",
    "trash-2": "Multiband distortion and saturation processor with convolution and trash algorithms.",
    "izotope-vinyl": "Free lo-fi effect emulating vinyl record noise, dust, warp, and mechanical wear.",

    # Kilohearts
    "disperser": "All-pass filter effect that smears transients and reshapes the phase of audio signals.",
    "effectrack": "Modular effect hosting rack for combining Kilohearts snapin modules in series and parallel.",
    "khs-compactor": "Simple compressor snapin module for the Kilohearts ecosystem.",
    "khs-one": "Subtractive synthesizer with a clean interface and snapin effect hosting capability.",
    "maim": "Bitcrusher and sample rate reducer snapin for digital degradation effects.",
    "multipass": "Multiband effect hosting rack that splits audio into bands for independent snapin processing.",
    "phase-plant": "Semi-modular synthesizer with analog, wavetable, sample, and granular generators plus snapin effects.",
    "snap-heap": "Modular multi-effect host with three parallel lanes for stacking Kilohearts snapin modules.",

    # Klanghelm
    "dc1a": "Simple two-knob compressor with gentle, musical compression character.",
    "mjuc": "Variable-mu tube compressor with three distinct compression modes spanning different eras.",

    # KV331 Audio
    "synthmaster-2": "Semi-modular software synthesizer with multiple synthesis methods and a large preset library.",

    # LennarDigital
    "sylenth1": "Virtual analog synthesizer known for its warm, rich sound and CPU efficiency.",

    # LHI Audio
    "st1b": "Utility plugin for stereo monitoring and channel balance analysis.",
    "st4b": "Utility plugin for multi-channel audio monitoring and signal routing.",

    # Matt Tytel
    "helm": "Free open-source polyphonic synthesizer with a visual modulation interface.",
    "vital": "Spectral warping wavetable synthesizer with visual modulation, text-to-wavetable, and built-in effects.",

    # MeldaProduction
    "mautopitch": "Free automatic pitch correction plugin for vocals and monophonic instruments.",
    "mcompressor": "Full-featured dynamics compressor with advanced sidechain and detection options.",
    "mfreeformequalizer": "Free-draw parametric equalizer allowing arbitrary EQ curve shapes.",
    "mmatcher": "Audio matching utility that analyzes and matches loudness, spectrum, and stereo width between tracks.",

    # Minimal Audio
    "current": "Hybrid synthesizer combining wavetable, sample, and granular engines with intelligent modulation.",
    "rift": "Distortion and filter plugin with feedback routing, sequencing, and modulation capabilities.",

    # MiniMeters
    "minimeters": "Compact audio metering suite with level, spectrum, stereo, and loudness displays.",
    "minimeters-loudness": "Dedicated loudness metering plugin showing LUFS, true peak, and loudness range.",

    # Native Instruments
    "absynth-5": "Semi-modular synthesizer specializing in evolving textures, pads, and atmospheric sounds.",
    "battery-4": "Drum sampler with a cell-based interface for loading, editing, and layering drum kits.",
    "fm8": "Eight-operator FM synthesizer with an advanced modulation matrix and arpeggiator.",
    "guitar-rig-7": "Guitar and bass amp/effects simulation suite with signal chain routing.",
    "kontakt": "Industry-standard sample playback engine hosting thousands of third-party instrument libraries.",
    "kontakt-7": "Updated sampler platform with new HiDPI interface, effects, and Creator Tools integration.",
    "kontakt-7-portable": "Lightweight version of Kontakt 7 for playing NKS libraries without the full sampler.",
    "kontakt-8": "Latest version of the Kontakt sampler with improved browser, effects, and performance.",
    "massive": "Classic wavetable synthesizer widely used in electronic and bass music production.",
    "massive-x": "Next-generation wavetable synthesizer with dual sequential wavetable oscillators and routing flexibility.",
    "monark": "Monophonic synthesizer modeled after the Moog Minimoog, available in Reaktor and Komplete.",
    "reaktor-6": "Visual modular synthesis environment for building custom instruments and effects from blocks.",
    "super-8": "Eight-voice virtual analog polysynth inspired by the Roland Jupiter-8.",
    "supercharger": "Tube compressor with a one-knob interface delivering punchy, characterful compression.",

    # Nembrini Audio
    "faturator": "Saturation and distortion effect originally by Softube, now by Nembrini Audio, for adding harmonic warmth.",

    # Neural DSP
    "archetype-gojira": "Guitar amp/effects suite modeled in collaboration with Gojira guitarist Joe Duplantier.",

    # Newfangled Audio
    "elevate": "Multiband limiter with adaptive algorithms and per-band transient emphasis for transparent mastering.",
    "saturate": "Spectral clipper and saturation plugin with adaptive harmonic processing.",

    # Nicky Romero
    "kickstart-2": "One-knob sidechain volume ducking tool for creating pumping effects in dance music.",

    # oeksound
    "soothe2": "Dynamic resonance suppressor that identifies and reduces harsh frequencies in real time.",
    "spiff": "Adaptive transient processor that controls transient emphasis or suppression per frequency.",

    # Output
    "chroma": "Audio effect combining distortion, filtering, and modulation for cinematic sound design.",
    "output-exhale": "Vocal-focused sample instrument built from manipulated human voice recordings.",
    "movement": "Rhythm-based effect engine applying LFO-driven modulation to any audio signal.",
    "output-portal": "Granular synthesis effect that transforms audio through grain-based processing.",
    "output-signal": "Pulse-engine synthesizer combining analog-style synthesis with built-in rhythmic modulation.",
    "thermal": "Multi-stage distortion processor with analog-modeled distortion algorithms and modulation.",
    "transit-2": "Transition and riser effects tool for creating builds, drops, and sweeps.",

    # Plogue
    "chipcrusher2": "Chiptune-style bitcrusher emulating vintage gaming console and computer audio hardware.",
    "chipsynth-sfc": "Chip music synthesizer accurately emulating the Super Nintendo (SPC700) audio hardware.",

    # plugdata
    "plugdata": "Visual patching environment based on Pure Data for building custom instruments in a DAW.",
    "plugdata-fx": "Effect version of plugdata for building custom audio effects using Pure Data patching.",

    # Plugin Alliance / Brainworx
    "bx-console": "Channel strip plugin modeled after a classic large-format analog mixing console.",
    "bx-digital-v3": "Mid/side mastering equalizer with dynamic EQ, mono-maker, and stereo width control.",
    "spl-de-esser": "De-essing plugin modeled after the SPL hardware de-esser for sibilance control.",
    "spl-iron": "Mastering compressor modeled after the SPL Iron tube compressor hardware.",

    # Plugin Boutique
    "scaler-2": "Music theory and chord progression tool that suggests chords, scales, and voicings via MIDI.",

    # Polyverse
    "comet": "Reverb plugin with shimmer, modulation, and infinite freeze for ambient sound design.",
    "wider": "Free stereo widening plugin using mid/side processing without phase issues in mono.",

    # QuantumSauce
    "melodysauce2": "AI-powered MIDI melody generator that creates melodies based on selected chords and styles.",

    # Rob Papen
    "blade-2": "Additive synthesis-based synth with XY pad control and comprehensive modulation.",
    "predator-3": "Virtual analog synth designed for leads, basses, and aggressive electronic sounds.",

    # Schaack Audio
    "transient-shaper": "Transient designer for boosting or attenuating the attack and sustain of audio signals.",

    # SIR Audio Tools
    "argentcompressor": "Clean, transparent compressor with adjustable character from gentle to aggressive.",
    "standardclip": "Soft/hard clipper and waveshaper for transparent loudness or aggressive distortion.",

    # Slate Digital
    "fg-x-2": "Mastering processor combining compression, saturation, and limiting in one interface.",
    "virtual-mix-rack": "Modular channel strip hosting interchangeable EQ, compressor, and gate modules.",
    "virtual-tape-machines": "Tape machine emulation adding warmth, saturation, and compression from analog tape.",

    # Softube
    "console-1": "Hardware-integrated channel strip providing EQ, compression, saturation, and gate per channel.",
    "saturation-knob": "Free single-knob saturation plugin with three saturation curve modes.",

    # Sonic Charge
    "bitspeek": "Real-time speech synthesizer effect using LPC vocoding for robotic vocal transformation.",
    "synplant": "Synthesizer with a genetic/evolutionary interface where sounds grow from seeds.",

    # Sonnox
    "oxford-dynamics": "Professional dynamics processor with compressor, limiter, expander, and gate sections.",
    "oxford-eq": "Parametric EQ with five fully featured bands and additional high/low-pass filters.",
    "oxford-limiter": "Brickwall limiter with enhance section for transparent loudness maximizing.",

    # Soundtoys
    "crystallizer": "Granular pitch-shifting reverse echo inspired by vintage Crystal Echoes hardware.",
    "decapitator": "Analog saturation modeler with five saturation styles from subtle warmth to heavy distortion.",
    "devil-loc": "Extreme compressor/distortion inspired by a cheap 1960s hardware leveler.",
    "echoboy": "Vintage-style delay with 30+ echo styles emulating classic tape, analog, and digital delays.",
    "filterfreak": "Analog-modeled resonant filter with LFO and envelope following for rhythmic filtering.",
    "littlealterboy": "Vocal pitch and formant shifter for real-time voice transformation effects.",
    "panman": "Auto-panning and tremolo effect with multiple waveform shapes and sync options.",
    "primaltap": "Delay and looping effect inspired by the Lexicon Prime Time hardware.",
    "soundtoys-collection": "Bundle containing all Soundtoys effect plugins in the Effect Rack hosting environment.",
    "tremolator": "Tremolo and auto-gate effect with tempo sync and envelope-following capabilities.",

    # Spectrasonics
    "keyscape": "Premium keyboard instrument with deeply sampled acoustic and electric pianos and keys.",
    "omnisphere": "Flagship synthesizer combining sample-based synthesis, wavetables, and granular processing.",
    "trilian": "Bass instrument with acoustic, electric, and synth bass sounds and arpeggiator.",

    # Spitfire Audio
    "bbc-symphony-orchestra": "Full symphonic orchestra sample library recorded at Maida Vale Studios.",
    "spitfire-labs": "Free collection of unique sample-based instruments from Spitfire Audio.",
    "spitfire-originals": "Curated single-instrument sample libraries at an accessible price point.",

    # Surreal Machines
    "modnetic": "Tape delay emulation with modulation, saturation, and degradation inspired by vintage hardware.",

    # TAL
    "tal-chorus-lx": "Free chorus effect modeled after the Roland Juno-60 built-in chorus circuit.",
    "tal-dub": "Vintage-style delay with tape saturation and a lo-fi analog character.",
    "tal-reverb-4": "Plate reverb with a modulated, lush character for ambient and retro effects.",
    "tal-u-no-lx": "Software emulation of the Roland Juno-60 analog synthesizer.",

    # Tokyo Dawn Records
    "tdr-kotelnikov": "Wideband dynamics compressor with transparent to characterful compression modes.",
    "tdr-nova": "Dynamic equalizer with up to four bands that combine EQ and compression.",
    "tdr-vos-slickeq": "Three-band mixing equalizer with analog-modeled saturation and output stage.",

    # Tone2
    "icarus-2": "Wavetable synthesizer with 3D wavetable editing, resynthesis, and HyperSaw oscillators.",

    # Toontrack
    "ezdrummer-3": "Drum production tool with a large drum library, groove browser, and song arranger.",
    "superior-drummer-3": "Premium drum sampler with deep editing, mixing, and e-drum triggering capabilities.",

    # u-he
    "ace": "Semi-modular synthesizer with patchable signal routing and a classic analog sound.",
    "diva": "Virtual analog synthesizer with component-modeled oscillators and zero-delay feedback filters.",
    "hive-2": "Streamlined wavetable synthesizer optimized for low CPU usage and fast workflow.",
    "presswerk": "Full-featured dynamics compressor with sidechain, parallel compression, and vintage character.",
    "repro-1": "Monophonic synthesizer faithfully modeling the Sequential Pro-One hardware.",
    "repro-5": "Polyphonic synthesizer faithfully modeling the Sequential Prophet-5 hardware.",
    "satin": "Tape machine emulation with recording, delay, and flanger modes from reel-to-reel modeling.",
    "zebra-2": "Modular synthesizer combining subtractive, additive, wavetable, and FM synthesis methods.",

    # Unfiltered Audio
    "sandman-pro": "Experimental delay with freeze, spectral shift, and granular buffer manipulation.",

    # Valhalla DSP
    "valhalla-dsp-collection": "Bundle containing all Valhalla DSP reverb, delay, and modulation plugins.",
    "valhalladelay": "Versatile delay with tape, BBD, digital, and pitch-shifting modes.",
    "valhallafreqecho": "Free frequency shifter and analog echo plugin for metallic and otherworldly effects.",
    "valhallaplate": "Plate reverb with lush, smooth character inspired by classic hardware plate reverbs.",
    "valhallaroom": "Algorithmic room and hall reverb with natural-sounding early reflections.",
    "valhallashimmer": "Pitch-shifting reverb creating ethereal, harmonically rich ambient textures.",
    "valhallaspacemodulator": "Free flanging and modulation effect with eleven algorithms.",
    "valhallasupermassive": "Free massive reverb and delay plugin with feedback-driven washes and long tails.",
    "valhallaubermod": "Modulation multi-effect combining chorus, flanger, and ensemble effects.",
    "valhallavintageverb": "Algorithmic reverb with vintage character inspired by hardware reverbs from the 1970s-1980s.",

    # Voxengo
    "voxengo-marvel-geq": "Free linear-phase 16-band graphic equalizer with spectrum analyzer.",
    "voxengo-msed": "Free mid/side encoding and decoding utility for stereo manipulation.",
    "span": "Free real-time FFT spectrum analyzer with customizable display and metering.",
    "span-plus": "Enhanced spectrum analyzer with sidechain comparison, metering presets, and extended features.",

    # Waves
    "abbey-road-plates": "Plate reverb emulation modeled from Abbey Road Studios' original EMT 140 hardware.",
    "cla-2a": "Optical compressor/limiter emulation modeled after the Teletronix LA-2A hardware.",
    "cla-76": "FET compressor emulation modeled after the UREI 1176 with Blacky and Bluey editions.",
    "h-delay": "Hybrid delay combining analog, tape, and digital delay flavors with modulation.",
    "waves-j37": "Tape saturation effect modeled after the Abbey Road Studios Studer J37 tape machine.",
    "waves-l1": "Classic brickwall peak limiter and loudness maximizer for mastering.",
    "waves-l2": "Brickwall limiter with look-ahead and ARC auto-release for transparent limiting.",
    "waves-rbass": "Bass enhancement processor using harmonic generation to extend low-frequency perception.",
    "waves-rcomp": "Smooth compressor with program-dependent auto-release and warm analog character.",
    "waves-req": "Parametric and graphic equalizer with six bands and vintage analog tonality.",
    "waves-rvox": "One-knob vocal compressor designed for quick, effective vocal level control.",
    "waves-scheps-omni-channel": "Channel strip designed by Andrew Scheps with compression, EQ, saturation, and de-essing.",
    "ssl-e-channel": "Channel strip modeled after the SSL 4000 E-Series console with EQ, dynamics, and filters.",
    "ssl-g-master-buss": "Bus compressor modeled after the SSL 4000 G-Series master bus compressor.",
    "waves-vitamin": "Multiband harmonic enhancer that adds energy and presence to individual frequency ranges.",
    "waveshell": "Waves plugin hosting shell that loads individual Waves plugins inside a DAW.",

    # Wavesfactory
    "spectre": "Multiband harmonic enhancer that adds saturation and harmonics per frequency band.",
    "trackspacer": "Dynamic sidechain EQ that creates space for one track by ducking conflicting frequencies in another.",

    # Xfer Records
    "cthulhu": "Chord and arpeggio MIDI effect that generates chords from single notes with pattern sequencing.",
    "lfotool": "LFO-driven volume, filter, and pan modulation tool for sidechain-style effects and tremolo.",
    "ott": "Multiband upward/downward compressor recreating the popular Ableton preset for aggressive dynamics.",
    "serum": "Advanced wavetable synthesizer with visual feedback, drag-and-drop modulation, and built-in effects.",
    "serum-2": "Next-generation wavetable synthesizer building on Serum with expanded synthesis and modulation.",

    # XLN Audio
    "addictive-drums-2": "Drum production plugin with mix-ready kits, pattern browser, and tone shaping controls.",
    "rc-20": "Lo-fi and retro effects processor with noise, wobble, distortion, and space modules.",

    # Youlean
    "youlean-loudness-meter-2": "Loudness metering plugin supporting LUFS, true peak, and various broadcast standards.",

    # Zynaptiq
    "pitchmap-colors": "Real-time polyphonic pitch remapping plugin for retuning or transposing audio material.",
}

# ── Price type map (slug -> price_type) ──
PRICE_TYPES = {
    # Free plugins
    "vital": "free",
    "helm": "free",
    "ott": "free",
    "valhallasupermassive": "free",
    "valhallafreqecho": "free",
    "valhallaspacemodulator": "free",
    "camelcrusher": "free",
    "izotope-vinyl": "free",
    "tal-chorus-lx": "free",
    "ob-xd": "free",
    "span": "free",
    "voxengo-marvel-geq": "free",
    "voxengo-msed": "free",
    "dc1a": "free",
    "wider": "free",
    "saturation-knob": "free",
    "mautopitch": "free",
    "spitfire-labs": "free",
    "fracture": "free",
    "hysteresis": "free",
    "reastream-standalone": "free",
    "tal-dub": "free",
    "tal-reverb-4": "free",
    "minimeters": "free",
    "minimeters-loudness": "free",
    "plugdata": "free",
    "plugdata-fx": "free",
    "supercharger": "free",

    # Freemium (free tier available, paid upgrades)
    "youlean-loudness-meter-2": "freemium",
    "tdr-kotelnikov": "freemium",
    "tdr-nova": "freemium",
    "tdr-vos-slickeq": "freemium",

    # Paid plugins
    "serum": "paid",
    "serum-2": "paid",
    "pro-q-3": "paid",
    "fabfilter-pro-c-2": "paid",
    "fabfilter-pro-l-2": "paid",
    "fabfilter-pro-mb": "paid",
    "fabfilter-pro-r-2": "paid",
    "fabfilter-saturn-2": "paid",
    "fabfilter-simplon": "paid",
    "fabfilter-timeless-3": "paid",
    "fabfilter-twin-3": "paid",
    "fabfilter-volcano-3": "paid",
    "ozone-11": "paid",
    "ozone-11-equalizer": "paid",
    "ozone-11-exciter": "paid",
    "ozone-11-imager": "paid",
    "ozone-11-master-rebalance": "paid",
    "izotope-ozone-9": "paid",
    "ozone-9-dynamics": "paid",
    "izotope-rx-11": "paid",
    "izotope-rx-voice-de-noise": "paid",
    "izotope-nectar-4": "paid",
    "izotope-neutron-4": "paid",
    "trash-2": "paid",
    "soothe2": "paid",
    "spiff": "paid",
    "omnisphere": "paid",
    "keyscape": "paid",
    "trilian": "paid",
    "kontakt": "paid",
    "kontakt-7": "paid",
    "kontakt-7-portable": "paid",
    "kontakt-8": "paid",
    "massive": "paid",
    "massive-x": "paid",
    "reaktor-6": "paid",
    "battery-4": "paid",
    "fm8": "paid",
    "guitar-rig-7": "paid",
    "monark": "paid",
    "super-8": "paid",
    "absynth-5": "paid",
    "phase-plant": "paid",
    "pigments-4": "paid",
    "analog-lab-v": "paid",
    "arturia-comp-fet-76": "paid",
    "arturia-jupiter-8v": "paid",
    "arturia-mini-v": "paid",
    "arturia-prophet-v": "paid",
    "arturia-rev-plate-140": "paid",
    "diva": "paid",
    "hive-2": "paid",
    "repro-1": "paid",
    "repro-5": "paid",
    "zebra-2": "paid",
    "ace": "paid",
    "presswerk": "paid",
    "satin": "paid",
    "sylenth1": "paid",
    "echoboy": "paid",
    "decapitator": "paid",
    "crystallizer": "paid",
    "devil-loc": "paid",
    "filterfreak": "paid",
    "littlealterboy": "paid",
    "panman": "paid",
    "primaltap": "paid",
    "tremolator": "paid",
    "soundtoys-collection": "paid",
    "shaperbox-3": "paid",
    "filtershaper": "paid",
    "panshaper": "paid",
    "timeshaper": "paid",
    "volumeshaper": "paid",
    "blackhole": "paid",
    "h3000": "paid",
    "mangledverb": "paid",
    "physion": "paid",
    "ultratap": "paid",
    "valhalladelay": "paid",
    "valhallaplate": "paid",
    "valhallaroom": "paid",
    "valhallashimmer": "paid",
    "valhallaubermod": "paid",
    "valhallavintageverb": "paid",
    "valhalla-dsp-collection": "paid",
    "cla-2a": "paid",
    "cla-76": "paid",
    "h-delay": "paid",
    "waves-j37": "paid",
    "waves-l1": "paid",
    "waves-l2": "paid",
    "waves-rbass": "paid",
    "waves-rcomp": "paid",
    "waves-req": "paid",
    "waves-rvox": "paid",
    "waves-scheps-omni-channel": "paid",
    "ssl-e-channel": "paid",
    "ssl-g-master-buss": "paid",
    "waves-vitamin": "paid",
    "abbey-road-plates": "paid",
    "waveshell": "paid",
    "tal-u-no-lx": "paid",
    "rc-20": "paid",
    "addictive-drums-2": "paid",
    "scaler-2": "paid",
    "cthulhu": "paid",
    "lfotool": "paid",
    "kickstart-2": "paid",
    "trackspacer": "paid",
    "spectre": "paid",
    "bbc-symphony-orchestra": "paid",
    "spitfire-originals": "paid",
    "equilibrium": "paid",
    "oxford-dynamics": "paid",
    "oxford-eq": "paid",
    "oxford-limiter": "paid",
    "ezdrummer-3": "paid",
    "superior-drummer-3": "paid",
    "console-1": "paid",
    "fg-x-2": "paid",
    "virtual-mix-rack": "paid",
    "virtual-tape-machines": "paid",
    "bx-console": "paid",
    "bx-digital-v3": "paid",
    "spl-de-esser": "paid",
    "spl-iron": "paid",
    "synplant": "paid",
    "bitspeek": "paid",
    "manipulator": "paid",
    "gatekeeper": "paid",
    "i-wish": "paid",
    "infiltrator": "paid",
    "duck": "paid",
    "disperser": "paid",
    "effectrack": "paid",
    "multipass": "paid",
    "snap-heap": "paid",
    "khs-one": "paid",
    "khs-compactor": "paid",
    "maim": "paid",
    "comet": "paid",
    "sandman-pro": "paid",
    "elevate": "paid",
    "saturate": "paid",
    "archetype-gojira": "paid",
    "faturator": "paid",
    "decimort-2": "paid",
    "devastor-2": "paid",
    "lush-2": "paid",
    "repeater": "paid",
    "perfect-room": "paid",
    "mjuc": "paid",
    "synthmaster-2": "paid",
    "heat-up-3": "paid",
    "sektor": "paid",
    "baby-audio-comeback-kid": "paid",
    "baby-audio-crystalline": "paid",
    "ihny-2": "paid",
    "parallel-aggressor": "paid",
    "baby-audio-smooth-operator": "paid",
    "baby-audio-spaced-out": "paid",
    "baby-audio-super-vhs": "paid",
    "bettermaker-bus-compressor-dsp": "paid",
    "dubstation-2": "paid",
    "quanta": "paid",
    "ratshack-reverb": "paid",
    "hybrid-3": "paid",
    "vacuum-pro": "paid",
    "dreamsynth": "paid",
    "surrealistic-mg-1": "paid",
    "voltage-modular": "paid",
    "cymatics-origin": "paid",
    "blade-2": "paid",
    "predator-3": "paid",
    "transient-shaper": "paid",
    "argentcompressor": "paid",
    "standardclip": "paid",
    "modnetic": "paid",
    "current": "paid",
    "rift": "paid",
    "output-exhale": "paid",
    "movement": "paid",
    "output-portal": "paid",
    "output-signal": "paid",
    "thermal": "paid",
    "transit-2": "paid",
    "chroma": "paid",
    "chipcrusher2": "paid",
    "chipsynth-sfc": "paid",
    "melodysauce2": "paid",
    "icarus-2": "paid",
    "span-plus": "paid",
    "pitchmap-colors": "paid",
    "amelia": "paid",
    "modnetic": "paid",
    "canopener": "paid",
    "goodhertz-lossy": "paid",
    "goodhertz-trem-control": "paid",
    "goodhertz-vulf-compressor": "paid",
    "goodhertz-wow-control": "paid",
    "ifea-fusion": "paid",
    "ifea-obra": "paid",
    "ifea-spectral-compressor": "paid",
    "ifea-spectral-gate": "paid",
}

# Bitwig native devices are included with Bitwig Studio
BITWIG_SLUGS = [
    "bit-8", "compressor", "delay-4", "drum-machine", "dynamics", "eq",
    "fx-grid", "fx-layer", "gate", "grid", "instrument-layer",
    "instrument-selector", "limiter", "multiband-fx-3", "oscilloscope",
    "phase-4", "poly-grid", "polymer", "polysynth", "reverb", "sampler",
    "spectrum", "tool",
]
for slug in BITWIG_SLUGS:
    PRICE_TYPES[slug] = "included"

# Ableton devices included with Live
for slug in ["ableton-drift", "ableton-meld", "operator", "wavetable"]:
    PRICE_TYPES[slug] = "included"

# Analog Obsession is free
for slug in ["fetish", "loaded", "rare"]:
    PRICE_TYPES[slug] = "free"

# MeldaProduction free plugins
for slug in ["mcompressor", "mfreeformequalizer", "mmatcher"]:
    PRICE_TYPES[slug] = "free"

# ── Year map (slug -> release year) ──
YEARS = {
    "serum": 2014,
    "serum-2": 2025,
    "vital": 2020,
    "helm": 2015,
    "ott": 2014,
    "pro-q-3": 2018,
    "fabfilter-pro-c-2": 2017,
    "fabfilter-pro-l-2": 2017,
    "fabfilter-pro-mb": 2013,
    "fabfilter-pro-r-2": 2023,
    "fabfilter-saturn-2": 2019,
    "fabfilter-simplon": 2009,
    "fabfilter-timeless-3": 2019,
    "fabfilter-twin-3": 2020,
    "fabfilter-volcano-3": 2020,
    "ozone-11": 2024,
    "ozone-11-equalizer": 2024,
    "ozone-11-exciter": 2024,
    "ozone-11-imager": 2024,
    "ozone-11-master-rebalance": 2024,
    "izotope-ozone-9": 2020,
    "ozone-9-dynamics": 2020,
    "izotope-rx-11": 2024,
    "izotope-nectar-4": 2024,
    "izotope-neutron-4": 2023,
    "trash-2": 2013,
    "izotope-vinyl": 2004,
    "soothe2": 2020,
    "spiff": 2021,
    "omnisphere": 2008,
    "keyscape": 2016,
    "trilian": 2009,
    "kontakt": 2002,
    "kontakt-7": 2022,
    "kontakt-7-portable": 2022,
    "kontakt-8": 2024,
    "massive": 2007,
    "massive-x": 2019,
    "reaktor-6": 2015,
    "battery-4": 2013,
    "fm8": 2007,
    "guitar-rig-7": 2023,
    "absynth-5": 2010,
    "monark": 2013,
    "super-8": 2017,
    "supercharger": 2012,
    "phase-plant": 2019,
    "pigments-4": 2023,
    "analog-lab-v": 2021,
    "arturia-jupiter-8v": 2006,
    "arturia-mini-v": 2004,
    "arturia-prophet-v": 2005,
    "arturia-rev-plate-140": 2019,
    "arturia-comp-fet-76": 2019,
    "diva": 2012,
    "hive-2": 2018,
    "repro-1": 2017,
    "repro-5": 2017,
    "zebra-2": 2006,
    "ace": 2010,
    "presswerk": 2014,
    "satin": 2013,
    "sylenth1": 2006,
    "echoboy": 2005,
    "decapitator": 2010,
    "crystallizer": 2008,
    "devil-loc": 2010,
    "filterfreak": 2005,
    "littlealterboy": 2014,
    "panman": 2008,
    "primaltap": 2015,
    "tremolator": 2006,
    "shaperbox-3": 2022,
    "filtershaper": 2009,
    "volumeshaper": 2010,
    "blackhole": 2012,
    "h3000": 2012,
    "mangledverb": 2015,
    "physion": 2017,
    "ultratap": 2016,
    "valhalladelay": 2019,
    "valhallaplate": 2014,
    "valhallaroom": 2012,
    "valhallashimmer": 2012,
    "valhallaubermod": 2016,
    "valhallavintageverb": 2012,
    "valhallafreqecho": 2012,
    "valhallaspacemodulator": 2016,
    "valhallasupermassive": 2020,
    "span": 2005,
    "span-plus": 2014,
    "voxengo-marvel-geq": 2008,
    "voxengo-msed": 2011,
    "cla-2a": 2012,
    "cla-76": 2012,
    "h-delay": 2006,
    "waves-j37": 2013,
    "waves-l1": 1997,
    "waves-l2": 2001,
    "waves-rbass": 2001,
    "waves-rcomp": 2001,
    "waves-req": 2001,
    "waves-rvox": 2010,
    "ssl-e-channel": 2005,
    "ssl-g-master-buss": 2006,
    "abbey-road-plates": 2016,
    "waves-vitamin": 2012,
    "tal-chorus-lx": 2011,
    "tal-u-no-lx": 2012,
    "tal-dub": 2010,
    "tal-reverb-4": 2010,
    "rc-20": 2017,
    "addictive-drums-2": 2013,
    "scaler-2": 2020,
    "cthulhu": 2013,
    "lfotool": 2012,
    "camelcrusher": 2012,
    "kickstart-2": 2022,
    "dc1a": 2013,
    "mjuc": 2015,
    "ob-xd": 2015,
    "saturation-knob": 2012,
    "wider": 2016,
    "trackspacer": 2016,
    "spectre": 2019,
    "bbc-symphony-orchestra": 2019,
    "spitfire-labs": 2018,
    "spitfire-originals": 2019,
    "manipulator": 2016,
    "gatekeeper": 2016,
    "i-wish": 2018,
    "disperser": 2019,
    "synplant": 2008,
    "bitspeek": 2011,
    "ezdrummer-3": 2022,
    "superior-drummer-3": 2017,
    "mautopitch": 2014,
    "oxford-dynamics": 2005,
    "oxford-eq": 2005,
    "oxford-limiter": 2007,
    "tdr-kotelnikov": 2012,
    "tdr-nova": 2015,
    "tdr-vos-slickeq": 2014,
    "equilibrium": 2012,
    "fg-x-2": 2020,
    "virtual-mix-rack": 2014,
    "virtual-tape-machines": 2012,
    "console-1": 2014,
    "bx-console": 2017,
    "bx-digital-v3": 2015,
    "comet": 2022,
    "elevate": 2017,
    "decimort-2": 2014,
    "devastor-2": 2014,
    "lush-2": 2017,
    "repeater": 2015,
    "infiltrator": 2020,
    "duck": 2019,
    "sandman-pro": 2018,
    "archetype-gojira": 2021,
    "faturator": 2022,
    "current": 2023,
    "rift": 2021,
    "icarus-2": 2021,
    "baby-audio-comeback-kid": 2021,
    "baby-audio-crystalline": 2022,
    "ihny-2": 2022,
    "parallel-aggressor": 2020,
    "baby-audio-smooth-operator": 2023,
    "baby-audio-spaced-out": 2021,
    "baby-audio-super-vhs": 2020,
    "synthmaster-2": 2011,
    "heat-up-3": 2018,
    "ableton-drift": 2022,
    "ableton-meld": 2022,
    "pitchmap-colors": 2020,
    "chipsynth-sfc": 2021,
    "movement": 2016,
    "output-portal": 2018,
    "output-signal": 2016,
    "thermal": 2019,
    "output-exhale": 2015,
    "youlean-loudness-meter-2": 2019,
    "spl-iron": 2020,
    "spl-de-esser": 2018,
}

# ── Format fix map (slug -> corrected formats) ──
FORMAT_FIXES = {
    "operator": [],      # Ableton internal device, no standard plugin format
    "wavetable": [],     # Ableton internal device, no standard plugin format
}

# ── Apply enrichments ──
for plugin in data["plugins"]:
    slug = plugin["slug"]

    # Description
    if slug in DESCRIPTIONS:
        plugin["description"] = DESCRIPTIONS[slug]
    else:
        # Generate generic description based on category/subcategory
        cat = plugin.get("category", "")
        sub = plugin.get("subcategory", "")
        name = plugin.get("name", "")
        mfg = plugin.get("manufacturer_slug", "")

        desc_map = {
            ("instrument", "synth"): f"Software synthesizer plugin.",
            ("instrument", "sampler"): f"Sample-based instrument plugin.",
            ("instrument", "rompler"): f"Preset-based sample playback instrument.",
            ("instrument", "drum-machine"): f"Drum machine and beat production instrument.",
            ("instrument", "piano"): f"Piano instrument plugin.",
            ("instrument", "general"): f"Virtual instrument plugin.",
            ("effect", "compressor"): f"Dynamics compressor effect plugin.",
            ("effect", "eq"): f"Equalizer effect plugin.",
            ("effect", "reverb"): f"Reverb effect plugin.",
            ("effect", "delay"): f"Delay effect plugin.",
            ("effect", "distortion"): f"Distortion effect plugin.",
            ("effect", "saturation"): f"Saturation effect plugin.",
            ("effect", "filter"): f"Filter effect plugin.",
            ("effect", "limiter"): f"Limiter effect plugin.",
            ("effect", "modulation"): f"Modulation effect plugin.",
            ("effect", "chorus"): f"Chorus effect plugin.",
            ("effect", "gate"): f"Noise gate effect plugin.",
            ("effect", "multiband"): f"Multiband dynamics processor plugin.",
            ("effect", "pitch"): f"Pitch processing effect plugin.",
            ("effect", "vocoder"): f"Vocoder effect plugin.",
            ("effect", "de-esser"): f"De-esser effect plugin.",
            ("effect", "general"): f"Audio effect plugin.",
            ("utility", "analyzer"): f"Audio analysis and metering utility plugin.",
            ("utility", "meter"): f"Audio metering utility plugin.",
            ("utility", "general"): f"Audio utility plugin.",
            ("utility", "routing"): f"Audio routing utility plugin.",
            ("container", "general"): f"Device container for hosting other plugins.",
            ("midi", "general"): f"MIDI processing utility plugin.",
        }
        plugin["description"] = desc_map.get((cat, sub), "Audio plugin.")

    # Price type
    if slug in PRICE_TYPES:
        plugin["price_type"] = PRICE_TYPES[slug]

    # Year
    if slug in YEARS:
        plugin["year"] = YEARS[slug]

    # Format fixes
    if slug in FORMAT_FIXES:
        plugin["formats"] = FORMAT_FIXES[slug]

# ── Validate no invalid formats remain ──
valid_formats = {"VST2", "VST3", "CLAP", "AU", "AAX"}
for plugin in data["plugins"]:
    for fmt in plugin.get("formats", []):
        if fmt not in valid_formats:
            print(f"WARNING: Invalid format still present: {plugin['slug']} -> {fmt}")

# ── Write back ──
with open("seed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ── Report ──
plugins = data["plugins"]
has_desc = sum(1 for x in plugins if x.get("description"))
has_year = sum(1 for x in plugins if x.get("year"))
has_price = sum(1 for x in plugins if x.get("price_type"))
print(f"Total: {len(plugins)}")
print(f"Descriptions: {has_desc} ({has_desc*100//len(plugins)}%)")
print(f"Years: {has_year} ({has_year*100//len(plugins)}%)")
print(f"Price types: {has_price} ({has_price*100//len(plugins)}%)")
print("Done!")
