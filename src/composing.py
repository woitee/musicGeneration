from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from enum import Enum
import numpy as np


note_seq = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


# See https://en.wikipedia.org/wiki/General_MIDI#Program_change_events
class Instrument(Enum):
    PIANO_ACOUSTIC_GRAND = 1
    PIANO_ACOUSTIC_BRIGHT = 2
    PIANO_ELECTRIC_GRAND = 3
    PIANO_HONKY_TONK = 4
    PIANO_ELECTRIC_1 = 5
    PIANO_ELECTRIC_2 = 6
    HARPSICHORD = 7
    CLAVINET = 8

    GUITAR_ACOUSTIC_NYLON = 25
    GUITAR_ACOUSTIC_STEEL = 26
    GUITAR_ELECTRIC_JAZZ = 27
    GUITAR_ELECTRIC_CLEAN = 28
    GUITAR_ELECTRIC_MUTED = 29
    GUITAR_ELECTRIC_OVERDRIVEN = 30
    GUITAR_ELECTRIC_DISTORTED = 31
    GUITAR_HARMONICS = 32
    # TODO more instruments


class Percussion(Enum):
    BASS_DRUM_ACOUSTIC = 35
    BASS_DRUM_1 = 36
    RIMSHOT = 37
    SNARE_ACOUSTIC = 38
    HAND_CLAP = 39
    SNARE_ELECTRIC = 40
    LOW_FLOOR_TOM = 41
    CLOSED_HI_HAT = 42
    HIGH_FLOOR_TOM = 43
    PEDAL_HI_HAT = 44
    LOW_TOM = 45
    OPEN_HI_HAT = 46
    LOW_MID_TOM = 47
    HI_MID_TOM = 48
    CRASH_CYMBAL_1 = 49
    HIGH_TOM = 50
    RIDE_CYMBAL_1 = 51
    CHINESE_CYMBAL = 52
    RIDE_BELL = 53
    TAMBOURINE = 54
    SPLASH_CYMBAL = 55
    COWBELL = 56
    CRASH_CYMBAL_2 = 57
    VIBRA_SLAP = 58
    RIDE_CYMBAL_2 = 59
    HIGH_BONGO = 60
    LOW_BONGO = 61
    MUTE_HIGH_CONGA = 62
    OPEN_HIGH_CONGA = 63
    LOW_CONGA = 64
    HIGH_TIMBALE = 65
    LOW_TIMBALE = 66
    HIGH_AGOGO = 67
    LOW_AGOGO = 68
    CABASA = 69
    MARACAS = 70
    SHORT_WHISTLE = 71
    LONG_WHISTLE = 72
    SHORT_GUIRO = 73
    LONG_GUIRO = 74
    CLAVES = 75
    HIGH_WOOD_BLOCK = 76
    LOW_WOOD_BLOCK = 77
    MUTE_CUICA = 78
    OPEN_CUICA = 79
    MUTE_TRIANGLE = 80
    OPEN_TRIANGLE = 81


class Scale(Enum):
    # CHROMATIC = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # random, atonal: all twelve notes
    MAJOR = [2, 2, 1, 2, 2, 2]  # classic, happy
    HARMONIC_MINOR = [2, 1, 2, 2, 1, 3]  # haunting, creepy
    MINOR_PENTATONIC = [3, 2, 2, 3]  # blues, rock
    NATURAL_MINOR = [2, 1, 2, 2, 1, 2]  # scary, epic
    MELODIC_MINOR_UP = [2, 1, 2, 2, 2, 2]  # wistful, mysterious
    # MELODIC_MINOR_DOWN = [2, 1, 2, 2, 1, 2]  # sombre, soulful, actual the same as harmonic minor
    DORIAN = [2, 1, 2, 2, 2, 1]  # cool, jazzy
    MIXOLYDIAN = [2, 2, 1, 2, 2, 1]  # progressive, complex
    AHAVA_RABA = [1, 3, 1, 2, 1, 2]  # exotic, unfamiliar
    MAJOR_PENTATONIC = [2, 2, 3, 2]  # country, gleeful
    DIATONIC = [2, 2, 2, 2, 2]  # bizarre, symmetrical


class Chord(Enum):
    MAJOR = [0, 4, 7]
    MINOR = [0, 3, 7]
    REL_MINOR_1ST_INV = [0, 4, 9]
    SUBDOMINANT_2ND_INV = [0, 5, 9]
    MAJOR_7TH = [0, 4, 7, 11]
    MINOR_7TH = [0, 3, 7, 10]
    MAJOR_9TH = [0, 4, 7, 14]
    MINOR_9TH = [0, 3, 7, 13]
    MAJOR_6TH = [0, 4, 9]
    MINOR_6TH = [0, 3, 8]
    MAJOR_7TH_9TH = [0, 4, 7, 11, 14]
    MINOR_7TH_9TH = [0, 3, 7, 10, 13]
    MAJOR_7TH_11TH = [0, 4, 7, 11, 18]
    MINOR_7TH_11TH = [0, 3, 7, 10, 17]


class Song:
    def __init__(self, bpm):
        self.bpm = bpm
        self.tracks = []

    def new_track(self, instrument=Instrument.PIANO_ACOUSTIC_GRAND):
        track = Track(self.bpm, instrument, MidiFile().ticks_per_beat)
        self.tracks.append(track)
        return track

    def save(self, filename):
        midi_file = MidiFile()
        for track in self.tracks:
            midi_file.tracks.append(track.to_midi_track())
        midi_file.save(filename)


class Track:
    # Helper class to represent "elements" of music (key press / key release)
    class MusicEvent:
        def __init__(self, type, note, tick, channel):
            self.type = type
            self.note = note
            self.tick = tick
            self.channel = channel

    def __init__(self, bpm, instrument, ticks_per_beat):
        self.bpm = bpm
        self.ticks_per_beat = ticks_per_beat
        self.instrument = instrument
        self.events = []

    # Adds a note to this track
    def add_note(self, note, beat, length, channel=0):
        note = note2number(note) if isinstance(note, str) else note

        self.events.append(Track.MusicEvent('start', note, beat * self.ticks_per_beat, channel))
        self.events.append(Track.MusicEvent('stop', note, (beat + length) * self.ticks_per_beat, channel))

    # Adds a beat (drum sound) to this track
    def add_beat(self, drum, beat, length):
        # By General MIDI standard, percussion is on track 10 (counting from one)
        self.add_note(drum.value, beat, length, 9)

    # Converts this track to MidiTrack (perhaps to later be saved)
    def to_midi_track(self):
        track = MidiTrack()
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(self.bpm)))
        # dont yet know what this does
        track.append(Message('program_change', program=self.instrument.value, time=0))

        self.events.sort(key=lambda ev: ev.tick)
        last_tick = 0
        for event in self.events:
            time_diff = event.tick - last_tick
            last_tick = event.tick

            track.append(Message(
                'note_on' if event.type == 'start' else 'note_off',
                note=event.note,
                velocity=64,
                time=time_diff,
                channel=event.channel,
            ))
        return track


# Converts string representation (e.g. G5 or F#4) to integer representation of the note
def note2number(note):
    tone = note[:-1]
    octave = int(note[-1])
    return octave * 12 + note_seq.index(tone)


def number2note(num):
    return note_seq[num % 12] + str(num // 12)


def get_scale(start_note, scale_type):
    return list(map(lambda x: start_note + x, [0] + list(np.cumsum(scale_type.value))))
