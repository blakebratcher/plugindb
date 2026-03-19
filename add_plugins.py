"""Temporary script to add 50 new plugins to seed.json."""
import json
import sys

with open('data/seed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

existing_slugs = {p['slug'] for p in data['plugins']}
existing_aliases = set()
for p in data['plugins']:
    for a in p.get('aliases', []):
        existing_aliases.add(a.lower())

ALL_DAWS = ['Bitwig', 'Ableton', 'Cubase', 'Studio One', 'Reaper', 'FL Studio', 'Logic', 'Pro Tools']
MOST_DAWS = ['Bitwig', 'Ableton', 'Cubase', 'Studio One', 'Reaper', 'FL Studio', 'Logic']

new_plugins = [
    # 1 - Rob Papen Blue II
    {
        'slug': 'rob-papen-blue-ii',
        'name': 'Blue II',
        'manufacturer_slug': 'rob-papen',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Cross-fusion synthesizer combining FM, subtractive, phase distortion, and waveshaping synthesis with extensive modulation.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Blue II', 'Rob Papen Blue II', 'Blue-II', 'RP-Blue II'],
        'year': 2013,
        'url': 'https://www.robpapen.com/blue-ii.html'
    },
    # 2 - Reveal Sound Spire
    {
        'slug': 'reveal-sound-spire',
        'name': 'Spire',
        'manufacturer_slug': 'reveal-sound',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Polyphonic software synthesizer combining powerful sound engine with flexible architecture and a wide variety of synthesis techniques.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Spire', 'Reveal Sound Spire', 'Spire VST'],
        'year': 2014,
        'url': 'https://www.reveal-sound.com/plug-ins/spire'
    },
    # 3 - Synapse Audio Dune 3
    {
        'slug': 'synapse-audio-dune-3',
        'name': 'Dune 3',
        'manufacturer_slug': 'synapse-audio',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'VA/wavetable hybrid synthesizer with massive unison, dual filters, 8200+ presets, and GPU-accelerated oscillators.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['DUNE 3', 'Synapse Audio DUNE 3', 'Dune3'],
        'year': 2018,
        'url': 'https://www.synapse-audio.com/dune3.html'
    },
    # 4 - Tone2 Gladiator 3
    {
        'slug': 'tone2-gladiator-3',
        'name': 'Gladiator 3',
        'manufacturer_slug': 'tone2',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Harmonic content morphing synthesizer with 38 synthesis types, built-in effects, and a resynthesis engine.',
        'formats': ['VST3', 'VST2', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Gladiator 3', 'Tone2 Gladiator 3', 'Gladiator3'],
        'year': 2021,
        'url': 'https://www.tone2.com/gladiator3.html'
    },
    # 5 - Cakewalk Z3TA+ 2
    {
        'slug': 'cakewalk-z3ta-2',
        'name': 'Z3TA+ 2',
        'manufacturer_slug': 'bandlab',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Waveshaping synthesizer with 6 oscillators, advanced modulation matrix, and built-in arpeggiator and effects.',
        'formats': ['VST3', 'VST2'],
        'daws': ['Bitwig', 'Ableton', 'Cubase', 'Studio One', 'Reaper', 'FL Studio'],
        'os': ['windows'],
        'price_type': 'paid',
        'aliases': ['Z3TA+ 2', 'z3ta+2', 'Cakewalk Z3TA+ 2', 'Z3TA 2'],
        'year': 2013,
        'url': 'https://www.bandlab.com/products/cakewalk'
    },
    # 6 - Surge XT
    {
        'slug': 'surge-xt',
        'name': 'Surge XT',
        'manufacturer_slug': 'surge-synth-team',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Free open-source hybrid synthesizer with 3 oscillators, 2 filter stages, a modulation matrix, and over 2800 factory patches.',
        'formats': ['VST3', 'AU', 'CLAP', 'LV2', 'Standalone'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'free',
        'aliases': ['Surge XT', 'SurgeXT', 'Surge Synth', 'Surge Synthesizer'],
        'year': 2022,
        'url': 'https://surge-synthesizer.github.io/'
    },
    # 7 - Cardinal
    {
        'slug': 'cardinal',
        'name': 'Cardinal',
        'manufacturer_slug': 'distrho',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Free open-source virtual modular synthesizer, a self-contained plugin port of VCV Rack with over 1300 modules.',
        'formats': ['VST3', 'AU', 'CLAP', 'LV2'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'free',
        'aliases': ['Cardinal', 'DISTRHO Cardinal', 'Cardinal Synth', 'Cardinal FX', 'CardinalMini'],
        'year': 2022,
        'url': 'https://github.com/DISTRHO/Cardinal'
    },
    # 8 - Dexed
    {
        'slug': 'dexed',
        'name': 'Dexed',
        'manufacturer_slug': 'digital-suburban',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Free open-source FM synthesizer closely modeled on the Yamaha DX7, compatible with original DX7 SysEx patches.',
        'formats': ['VST3', 'VST2', 'AU', 'CLAP', 'LV2', 'Standalone'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'free',
        'aliases': ['Dexed', 'Dexed FM', 'Dexed DX7'],
        'year': 2014,
        'url': 'https://asb2m10.github.io/dexed/'
    },
    # 9 - ZynAddSubFX
    {
        'slug': 'zynaddsubfx',
        'name': 'ZynAddSubFX',
        'manufacturer_slug': 'zynaddsubfx-team',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Free open-source software synthesizer with additive, subtractive, and pad synthesis engines plus extensive effects.',
        'formats': ['VST3', 'LV2', 'Standalone'],
        'daws': ['Bitwig', 'Cubase', 'Studio One', 'Reaper'],
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'free',
        'aliases': ['ZynAddSubFX', 'Zyn', 'ZynAddSubFX VST'],
        'year': 2002,
        'url': 'https://zynaddsubfx.sourceforge.io/'
    },
    # 10 - Klanghelm IVGI
    {
        'slug': 'klanghelm-ivgi',
        'name': 'IVGI',
        'manufacturer_slug': 'klanghelm',
        'category': 'effect',
        'subcategory': 'saturation',
        'description': 'Free saturation plugin offering smooth analog-style tube/tape warmth with asymmetric distortion and a tilt EQ.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['IVGI', 'Klanghelm IVGI'],
        'year': 2014,
        'url': 'https://klanghelm.com/contents/products/IVGI.php'
    },
    # 11 - Airwindows Consolidated
    {
        'slug': 'airwindows-consolidated',
        'name': 'Airwindows Consolidated',
        'manufacturer_slug': 'airwindows',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Massive free collection of 300+ audio effects in a single plugin, covering EQ, compression, saturation, reverb, and experimental processing.',
        'formats': ['VST3', 'AU', 'CLAP'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'free',
        'aliases': ['Airwindows Consolidated', 'Airwindows', 'Airwindows Console', 'Chris Johnson Airwindows'],
        'year': 2023,
        'url': 'https://www.airwindows.com/'
    },
    # 12 - Blue Cat Free Pack
    {
        'slug': 'blue-cat-free-pack',
        'name': 'Blue Cat Free Pack',
        'manufacturer_slug': 'blue-cat-audio',
        'category': 'utility',
        'subcategory': 'general',
        'description': 'Free bundle of audio analysis and processing plugins including a spectrum analyzer, gain suite, chorus, phaser, and frequency analyzer.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['Blue Cat Free Pack', 'Blue Cat Audio Freeware Pack', 'Blue Cat FreqAnalyst'],
        'year': 2007,
        'url': 'https://www.bluecataudio.com/Products/Bundle_FreewarePack/'
    },
    # 13 - MFreeFXBundle
    {
        'slug': 'meldaproduction-mfreefxbundle',
        'name': 'MFreeFXBundle',
        'manufacturer_slug': 'meldaproduction',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Free bundle of 37 audio plugins covering EQ, dynamics, analysis, modulation, reverb, and utility processing.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['MFreeFXBundle', 'MeldaProduction Free FX Bundle', 'Melda Free Bundle', 'MFreeEffectsBundle'],
        'year': 2010,
        'url': 'https://www.meldaproduction.com/MFreeFXBundle'
    },
    # 14 - Bertom Denoiser
    {
        'slug': 'bertom-denoiser',
        'name': 'Denoiser',
        'manufacturer_slug': 'bertom-audio',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Free noise reduction plugin with spectral processing for removing broadband noise, hiss, and hum from audio signals.',
        'formats': ['VST3', 'VST2', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['Bertom Denoiser', 'Denoiser Classic', 'Bertom Denoiser Classic'],
        'year': 2020,
        'url': 'https://www.bertomaudio.com/denoiser.html'
    },
    # 15 - Slate Digital Fresh Air
    {
        'slug': 'slate-digital-fresh-air',
        'name': 'Fresh Air',
        'manufacturer_slug': 'slate-digital',
        'category': 'effect',
        'subcategory': 'eq',
        'description': 'Free high-frequency exciter and presence enhancer with two bands for adding clarity and air to vocals and instruments.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['Fresh Air', 'Slate Digital Fresh Air', 'Slate Fresh Air'],
        'year': 2021,
        'url': 'https://slatedigital.com/fresh-air/'
    },
    # 16 - Analog Obsession BUSTERse
    {
        'slug': 'analog-obsession-buster',
        'name': 'BUSTERse',
        'manufacturer_slug': 'analog-obsession',
        'category': 'effect',
        'subcategory': 'compressor',
        'description': 'Free bus compressor modeled after classic SSL-style bus compressor topology with auto-release and sidechain HPF.',
        'formats': ['VST3', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['BUSTERse', 'Analog Obsession BUSTERse', 'BUSTER'],
        'year': 2021,
        'url': 'https://www.patreon.com/analogobsession'
    },
    # 17 - Analog Obsession TuBe
    {
        'slug': 'analog-obsession-tube',
        'name': 'TuBe',
        'manufacturer_slug': 'analog-obsession',
        'category': 'effect',
        'subcategory': 'saturation',
        'description': 'Free tube saturation plugin emulating 12AX7 tube warmth with drive control and mix blend.',
        'formats': ['VST3', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['TuBe', 'Analog Obsession TuBe'],
        'year': 2020,
        'url': 'https://www.patreon.com/analogobsession'
    },
    # 18 - Analog Obsession BritChannel
    {
        'slug': 'analog-obsession-britchannel',
        'name': 'BritChannel',
        'manufacturer_slug': 'analog-obsession',
        'category': 'effect',
        'subcategory': 'eq',
        'description': 'Free British-style console channel strip with 4-band EQ, HPF/LPF, compressor, and gate.',
        'formats': ['VST3', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['BritChannel', 'Analog Obsession BritChannel'],
        'year': 2021,
        'url': 'https://www.patreon.com/analogobsession'
    },
    # 19 - Analog Obsession CHANnev
    {
        'slug': 'analog-obsession-channev',
        'name': 'CHANnev',
        'manufacturer_slug': 'analog-obsession',
        'category': 'effect',
        'subcategory': 'eq',
        'description': 'Free Neve-style channel strip with 3-band inductor EQ, high-pass filter, and preamp drive.',
        'formats': ['VST3', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['CHANnev', 'Analog Obsession CHANnev'],
        'year': 2021,
        'url': 'https://www.patreon.com/analogobsession'
    },
    # 20 - Analog Obsession disto-X
    {
        'slug': 'analog-obsession-distox',
        'name': 'disto-X',
        'manufacturer_slug': 'analog-obsession',
        'category': 'effect',
        'subcategory': 'distortion',
        'description': 'Free multi-mode distortion plugin with 5 distortion types, tone control, and mix blend.',
        'formats': ['VST3', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['disto-X', 'Analog Obsession disto-X', 'distoX'],
        'year': 2022,
        'url': 'https://www.patreon.com/analogobsession'
    },
    # 21 - iZotope Music Production Suite
    {
        'slug': 'izotope-music-production-suite',
        'name': 'Music Production Suite',
        'manufacturer_slug': 'izotope',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Comprehensive suite bundling Ozone, Neutron, Nectar, RX, and Insight for complete mixing, mastering, and repair workflows.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Music Production Suite', 'iZotope Music Production Suite', 'iZotope MPS'],
        'year': 2017,
        'url': 'https://www.izotope.com/en/shop/music-production-suite.html'
    },
    # 22 - iZotope Insight 2
    {
        'slug': 'izotope-insight-2',
        'name': 'Insight 2',
        'manufacturer_slug': 'izotope',
        'category': 'utility',
        'subcategory': 'meter',
        'description': 'Professional metering and audio analysis suite with loudness, spectrum, stereo field, and intelligibility meters.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Insight 2', 'iZotope Insight 2', 'Insight2'],
        'year': 2018,
        'url': 'https://www.izotope.com/en/products/insight.html'
    },
    # 23 - Waves Horizon
    {
        'slug': 'waves-horizon',
        'name': 'Waves Horizon',
        'manufacturer_slug': 'waves',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Flagship Waves bundle containing 80+ plugins including compressors, EQs, reverbs, delays, and mastering tools.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Waves Horizon', 'Waves Horizon Bundle'],
        'year': 2003,
        'url': 'https://www.waves.com/bundles/horizon'
    },
    # 24 - Waves API 2500
    {
        'slug': 'waves-api-2500',
        'name': 'API 2500',
        'manufacturer_slug': 'waves',
        'category': 'effect',
        'subcategory': 'compressor',
        'description': 'Stereo bus compressor plugin modeled after the API 2500 hardware, known for punchy bus compression.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['API 2500', 'Waves API 2500', 'API2500'],
        'year': 2007,
        'url': 'https://www.waves.com/plugins/api-2500'
    },
    # 25 - Waves API 550A
    {
        'slug': 'waves-api-550a',
        'name': 'API 550A',
        'manufacturer_slug': 'waves',
        'category': 'effect',
        'subcategory': 'eq',
        'description': 'Modeled 3-band EQ based on the classic API 550A hardware with proportional-Q behavior.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['API 550A', 'Waves API 550A', 'API550A'],
        'year': 2008,
        'url': 'https://www.waves.com/plugins/api-550a'
    },
    # 26 - Waves CLA MixHub
    {
        'slug': 'waves-cla-mixhub',
        'name': 'CLA MixHub',
        'manufacturer_slug': 'waves',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Channel strip plugin modeled after the console used by Chris Lord-Alge, with EQ, compression, gating, and drive.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['CLA MixHub', 'Waves CLA MixHub', 'CLA-MixHub'],
        'year': 2021,
        'url': 'https://www.waves.com/plugins/cla-mixhub'
    },
    # 27 - Waves PuigTec EQP1A
    {
        'slug': 'waves-puigtec-eqp1a',
        'name': 'PuigTec EQP1A',
        'manufacturer_slug': 'waves',
        'category': 'effect',
        'subcategory': 'eq',
        'description': 'Modeled passive EQ based on the Pultec EQP-1A hardware, tuned by producer Jack Joseph Puig.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['PuigTec EQP1A', 'Waves PuigTec EQP1A', 'PuigTec EQP-1A'],
        'year': 2008,
        'url': 'https://www.waves.com/plugins/puigtec-eqp1a'
    },
    # 28 - Plugin Alliance Mega Bundle
    {
        'slug': 'plugin-alliance-mega-bundle',
        'name': 'Plugin Alliance Mega Bundle',
        'manufacturer_slug': 'plugin-alliance',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'All-inclusive subscription bundle containing 130+ plugins from Brainworx, SPL, Lindell, Unfiltered Audio, and more.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Plugin Alliance Mega Bundle', 'PA Mega Bundle'],
        'year': 2018,
        'url': 'https://www.plugin-alliance.com/en/products/mega-bundle.html'
    },
    # 29 - bx_subsynth
    {
        'slug': 'bx-subsynth',
        'name': 'bx_subsynth',
        'manufacturer_slug': 'plugin-alliance',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Bass enhancement plugin that synthesizes sub-harmonics from the input signal to add weight and low-end power.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['bx_subsynth', 'Brainworx bx_subsynth', 'bx subsynth'],
        'year': 2016,
        'url': 'https://www.plugin-alliance.com/en/products/bx_subsynth.html'
    },
    # 30 - bx_masterdesk
    {
        'slug': 'bx-masterdesk',
        'name': 'bx_masterdesk',
        'manufacturer_slug': 'plugin-alliance',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'All-in-one mastering plugin with chain of tone shaping, stereo width, compression, limiting, and volume control.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['bx_masterdesk', 'Brainworx bx_masterdesk', 'bx masterdesk'],
        'year': 2017,
        'url': 'https://www.plugin-alliance.com/en/products/bx_masterdesk.html'
    },
    # 31 - Boz Panipulator
    {
        'slug': 'boz-digital-panipulator',
        'name': 'Panipulator',
        'manufacturer_slug': 'boz-digital-labs',
        'category': 'utility',
        'subcategory': 'general',
        'description': 'Free utility plugin for checking mono compatibility, swapping channels, adjusting stereo width, and inverting phase.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['Panipulator', 'Boz Panipulator', 'Boz Digital Labs Panipulator'],
        'year': 2017,
        'url': 'https://www.bozdigitallabs.com/product/panipulator/'
    },
    # 32 - Audiority Limited-Z
    {
        'slug': 'audiority-limited-z',
        'name': 'Limited-Z',
        'manufacturer_slug': 'audiority',
        'category': 'effect',
        'subcategory': 'limiter',
        'description': 'Free brickwall limiter with true peak limiting, auto-release, and loudness metering for mastering and bus processing.',
        'formats': ['VST3', 'VST2', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['Limited-Z', 'LVC Audio Limited-Z', 'Audiority Limited-Z'],
        'year': 2018,
        'url': 'https://www.audiority.com/shop/limited-z/'
    },
    # 33 - Aegean Music Pitchproof
    {
        'slug': 'aegean-music-pitchproof',
        'name': 'Pitchproof',
        'manufacturer_slug': 'aegean-music',
        'category': 'effect',
        'subcategory': 'pitch',
        'description': 'Free pitch-shifting plugin that adds harmonies at fixed intervals to the input signal.',
        'formats': ['VST3', 'VST2', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['Pitchproof', 'Aegean Music Pitchproof'],
        'year': 2016,
        'url': 'https://aegeanmusic.com/pitchproof-specs'
    },
    # 34 - Variety Of Sound epicVerb
    {
        'slug': 'variety-of-sound-epicverb',
        'name': 'epicVerb',
        'manufacturer_slug': 'variety-of-sound',
        'category': 'effect',
        'subcategory': 'reverb',
        'description': 'Free algorithmic reverb with 6 room types, modulation, damping, and pre-delay controls.',
        'formats': ['VST2'],
        'daws': ['Bitwig', 'Ableton', 'Cubase', 'Studio One', 'Reaper', 'FL Studio'],
        'os': ['windows'],
        'price_type': 'free',
        'aliases': ['epicVerb', 'Variety Of Sound epicVerb', 'VoS epicVerb'],
        'year': 2011,
        'url': 'https://varietyofsound.wordpress.com/downloads/'
    },
    # 35 - Variety Of Sound FerricTDS
    {
        'slug': 'variety-of-sound-ferrictds',
        'name': 'FerricTDS',
        'manufacturer_slug': 'variety-of-sound',
        'category': 'effect',
        'subcategory': 'saturation',
        'description': 'Free tape dynamics simulator that combines tape saturation with subtle compression characteristics.',
        'formats': ['VST2'],
        'daws': ['Bitwig', 'Ableton', 'Cubase', 'Studio One', 'Reaper', 'FL Studio'],
        'os': ['windows'],
        'price_type': 'free',
        'aliases': ['FerricTDS', 'Variety Of Sound FerricTDS', 'VoS FerricTDS'],
        'year': 2012,
        'url': 'https://varietyofsound.wordpress.com/downloads/'
    },
    # 36 - ChowTapeModel
    {
        'slug': 'chowdsp-chow-tape-model',
        'name': 'ChowTapeModel',
        'manufacturer_slug': 'chowdsp',
        'category': 'effect',
        'subcategory': 'saturation',
        'description': 'Free open-source physical model of a Sony TC-260 reel-to-reel tape machine with wow, flutter, and degradation.',
        'formats': ['VST3', 'AU', 'CLAP', 'LV2'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'free',
        'aliases': ['ChowTapeModel', 'Chow Tape Model', 'CHOW Tape'],
        'year': 2020,
        'url': 'https://chowdsp.com/products.html'
    },
    # 37 - ChowCentaur
    {
        'slug': 'chowdsp-chow-centaur',
        'name': 'ChowCentaur',
        'manufacturer_slug': 'chowdsp',
        'category': 'effect',
        'subcategory': 'distortion',
        'description': 'Free open-source overdrive plugin modeled after the Klon Centaur guitar pedal using neural network emulation.',
        'formats': ['VST3', 'AU', 'CLAP', 'LV2'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'free',
        'aliases': ['ChowCentaur', 'Chow Centaur', 'ChowDSP Centaur'],
        'year': 2020,
        'url': 'https://chowdsp.com/products.html'
    },
    # 38 - A1StereoControl
    {
        'slug': 'a1audio-a1stereocontrol',
        'name': 'A1StereoControl',
        'manufacturer_slug': 'alex-hilton',
        'category': 'utility',
        'subcategory': 'general',
        'description': 'Free stereo width and mid/side control plugin with correlation meter and safe bass mono switch.',
        'formats': ['VST3', 'VST2', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['A1StereoControl', 'A1 Stereo Control', 'Alex Hilton A1StereoControl'],
        'year': 2015,
        'url': 'https://a1audio.alexhilton.net/a1stereocontrol'
    },
    # 39 - A1TriggerGate
    {
        'slug': 'a1audio-a1triggergate',
        'name': 'A1TriggerGate',
        'manufacturer_slug': 'alex-hilton',
        'category': 'effect',
        'subcategory': 'gate',
        'description': 'Free rhythmic trance gate sequencer with 16 steps, tempo sync, and adjustable gate shapes.',
        'formats': ['VST3', 'VST2', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['A1TriggerGate', 'A1 Trigger Gate', 'Alex Hilton A1TriggerGate'],
        'year': 2016,
        'url': 'https://a1audio.alexhilton.net/a1triggergate'
    },
    # 40 - Luftikus
    {
        'slug': 'lkjb-luftikus',
        'name': 'Luftikus',
        'manufacturer_slug': 'lkjb',
        'category': 'effect',
        'subcategory': 'eq',
        'description': 'Free analog-modeled semi-parametric EQ inspired by the Maag EQ4, with a fixed high-frequency air band at 2.5/5/10/20/40 kHz.',
        'formats': ['VST3', 'VST2', 'AU'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'free',
        'aliases': ['Luftikus', 'lkjb Luftikus'],
        'year': 2014,
        'url': 'https://lkjbdsp.wordpress.com/luftikus/'
    },
    # 41 - Sonic Anomaly Transpire
    {
        'slug': 'sonic-anomaly-transpire',
        'name': 'Transpire',
        'manufacturer_slug': 'sonic-anomaly',
        'category': 'effect',
        'subcategory': 'compressor',
        'description': 'Free transient shaper plugin with attack and sustain controls for punch and body adjustment.',
        'formats': ['VST2'],
        'daws': ['Bitwig', 'Ableton', 'Cubase', 'Studio One', 'Reaper', 'FL Studio'],
        'os': ['windows'],
        'price_type': 'free',
        'aliases': ['Transpire', 'Sonic Anomaly Transpire'],
        'year': 2015,
        'url': 'https://sonic.supermaailma.net/plugins'
    },
    # 42 - Acustica Audio Aquamarine
    {
        'slug': 'acustica-audio-aquamarine',
        'name': 'Aquamarine',
        'manufacturer_slug': 'acustica-audio',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Sampled channel strip based on a vintage Neve 1084 console with EQ, preamp, and compressor sections.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Aquamarine', 'Acustica Audio Aquamarine', 'Acustica Aquamarine'],
        'year': 2020,
        'url': 'https://www.acustica-audio.com/shop/products/AQUAMARINE'
    },
    # 43 - ToneLib GFX
    {
        'slug': 'tonelib-gfx',
        'name': 'ToneLib GFX',
        'manufacturer_slug': 'tonelib',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Guitar amp and effects modeling suite with 50+ amps, 70+ effects pedals, and cabinet simulation.',
        'formats': ['VST3', 'VST2', 'AU', 'Standalone'],
        'daws': MOST_DAWS,
        'os': ['windows', 'macos', 'linux'],
        'price_type': 'freemium',
        'aliases': ['ToneLib GFX', 'ToneLib-GFX', 'Tonelib Guitar FX'],
        'year': 2019,
        'url': 'https://tonelib.net/tl-gfx.html'
    },
    # 44 - NI Form
    {
        'slug': 'native-instruments-form',
        'name': 'Form',
        'manufacturer_slug': 'native-instruments',
        'category': 'instrument',
        'subcategory': 'synth',
        'description': 'Sample-based synthesizer that turns any audio into a playable instrument using granular-style scanning and modulation.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['NI Form', 'Native Instruments Form', 'Komplete Form'],
        'year': 2016,
        'url': 'https://www.native-instruments.com/en/products/komplete/synths/form/'
    },
    # 45 - Eventide SP2016 Reverb
    {
        'slug': 'eventide-sp2016-reverb',
        'name': 'SP2016 Reverb',
        'manufacturer_slug': 'eventide',
        'category': 'effect',
        'subcategory': 'reverb',
        'description': 'Plugin recreation of the Eventide SP2016 hardware reverb with 6 classic algorithms including Room, Stereo Room, and High Density Plate.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['SP2016 Reverb', 'Eventide SP2016 Reverb', 'SP2016'],
        'year': 2016,
        'url': 'https://www.eventideaudio.com/plug-ins/sp2016-reverb/'
    },
    # 46 - Eventide Physion 2
    {
        'slug': 'eventide-physion-2',
        'name': 'Physion 2',
        'manufacturer_slug': 'eventide',
        'category': 'effect',
        'subcategory': 'general',
        'description': 'Transient/tonal separation processor that splits audio into transient and body components for independent processing.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Physion 2', 'Eventide Physion 2', 'Physion2'],
        'year': 2023,
        'url': 'https://www.eventideaudio.com/plug-ins/physion-2/'
    },
    # 47 - Soundtoys Sie-Q
    {
        'slug': 'soundtoys-sie-q',
        'name': 'Sie-Q',
        'manufacturer_slug': 'soundtoys',
        'category': 'effect',
        'subcategory': 'eq',
        'description': 'Modeled parametric EQ based on the Siemens W295b, offering smooth musical curves with analog warmth.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Sie-Q', 'Soundtoys Sie-Q', 'SieQ'],
        'year': 2019,
        'url': 'https://www.soundtoys.com/product/sie-q/'
    },
    # 48 - Soundtoys Radiator
    {
        'slug': 'soundtoys-radiator',
        'name': 'Radiator',
        'manufacturer_slug': 'soundtoys',
        'category': 'effect',
        'subcategory': 'saturation',
        'description': 'Modeled tube saturation and tone shaper based on the Altec 1567A mixer, adding warmth and presence.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['Radiator', 'Soundtoys Radiator'],
        'year': 2014,
        'url': 'https://www.soundtoys.com/product/radiator/'
    },
    # 49 - FabFilter Pro-DS
    {
        'slug': 'fabfilter-pro-ds',
        'name': 'FabFilter Pro-DS',
        'manufacturer_slug': 'fabfilter',
        'category': 'effect',
        'subcategory': 'de-esser',
        'description': 'Transparent de-esser with intelligent single-voice detection, wide-band and split-band modes, and real-time display.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['FabFilter Pro-DS', 'Pro-DS', 'ProDS'],
        'year': 2014,
        'url': 'https://www.fabfilter.com/products/pro-ds-de-esser-plug-in'
    },
    # 50 - FabFilter Pro-G
    {
        'slug': 'fabfilter-pro-g',
        'name': 'FabFilter Pro-G',
        'manufacturer_slug': 'fabfilter',
        'category': 'effect',
        'subcategory': 'gate',
        'description': 'Gate/expander plugin with lookahead, sidechain, and expert controls for precise gating and expansion.',
        'formats': ['VST3', 'VST2', 'AU', 'AAX'],
        'daws': ALL_DAWS,
        'os': ['windows', 'macos'],
        'price_type': 'paid',
        'aliases': ['FabFilter Pro-G', 'Pro-G', 'ProG'],
        'year': 2014,
        'url': 'https://www.fabfilter.com/products/pro-g-gate-expander-plug-in'
    },
]

# Validate before writing
errors = []
new_alias_set = set()
all_mfr_slugs = {m['slug'] for m in data['manufacturers']}
for i, p in enumerate(new_plugins):
    slug = p['slug']
    if slug in existing_slugs:
        errors.append(f'SLUG COLLISION: {slug}')
    if p['manufacturer_slug'] not in all_mfr_slugs:
        errors.append(f'MISSING MFR: {p["manufacturer_slug"]} for {slug}')
    for a in p.get('aliases', []):
        al = a.lower()
        if al in existing_aliases:
            errors.append(f'ALIAS COLLISION: "{a}" in {slug}')
        if al in new_alias_set:
            errors.append(f'DUPLICATE NEW ALIAS: "{a}" in {slug}')
        new_alias_set.add(al)

if errors:
    print('VALIDATION ERRORS:')
    for e in errors:
        print(f'  {e}')
    sys.exit(1)

assert len(new_plugins) == 50, f'Expected 50 plugins, got {len(new_plugins)}'

data['plugins'].extend(new_plugins)

with open('data/seed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f'SUCCESS: Added 50 new plugins')
print(f'New total: {len(data["plugins"])} plugins, {len(data["manufacturers"])} manufacturers')
