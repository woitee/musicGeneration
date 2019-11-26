from composing import Song, Percussion, Instrument, Scale, Chord, note2number, number2note, get_scale
import numpy as np


def second_pcg():
    seed = np.random.randint(1000000)
    print("seed = {}".format(seed))
    song_name = name_from_seed(seed)
    print("name = {}".format(song_name))
    np.random.seed(seed)

    song = Song(240)

    # Generate beat
    drum_track = song.new_track()
    base_percussion = [Percussion.BASS_DRUM_1, None, None, None, None, None, None, None]

    drumprob = [0, 0, 0.5, 0, 0.5, 0, 0.5, 0.5]
    for beat, prob in enumerate(drumprob):
        if np.random.uniform() < prob:
            base_percussion[beat] = np.random.choice([
                Percussion.BASS_DRUM_1,
                Percussion.SNARE_ACOUSTIC,
                Percussion.RIMSHOT,
                Percussion.SNARE_ELECTRIC,
                Percussion.HIGH_WOOD_BLOCK,
                Percussion.LOW_WOOD_BLOCK
            ])

    percussion = [None] * 8 + base_percussion * 8

    for i, beat in enumerate(percussion):
        if beat is not None:
            drum_track.add_beat(beat, i, 1)

    # Generate basic melody
    melody_track = song.new_track(Instrument.PIANO_ACOUSTIC_GRAND)
    start_note = note2number('C4') + np.random.randint(12)

    usable_scales = [
        Scale.MAJOR, Scale.HARMONIC_MINOR, Scale.MINOR_PENTATONIC, Scale.NATURAL_MINOR, Scale.DORIAN, Scale.AHAVA_RABA
    ]
    scale = np.random.choice(usable_scales)
    print('scale = {}'.format(scale.name))
    print('start_note = {} {}'.format(start_note, number2note(start_note)))
    full_scale = get_scale(start_note - 12, scale) + get_scale(start_note, scale)

    note_prob = [0, 0.4, 0.7, 0.4, 0.7, 0.4, 0.7, 0.4, 0.5, 0.4, 0.7, 0.4, 0.7, 0.4, 0.7, 0.4]
    melody = [start_note] + [None] * 16
    current_note_relative = full_scale.index(start_note)
    for beat, prob in enumerate(note_prob):
        if np.random.uniform() < prob:
            step = np.random.choice([-2, -1, 0, 1, 2])
            current_note_relative += step
            current_note_relative = np.clip(current_note_relative, 0, len(full_scale) - 1)

            melody[beat] = full_scale[current_note_relative]

    melody = [None] * 16 + melody * 2
    for i, note in enumerate(melody):
        if note is not None:
            melody_track.add_note(note, i, 1)

    # Generate varation of melody
    # Put together to form verse
    # Generate chorus
    # Generate underlying bass for everything
    # Generate
    # Harmonize
    # Generate ending

    song.save('out/{}.mid'.format(song_name.replace(' ', '_')))


def name_from_seed(seed):
    with open('src/nouns.txt') as f:
        nouns = [s.strip() for s in f.readlines()]
    with open('src/adjectives.txt') as f:
        adjectives = [s.strip() for s in f.readlines()]
    noun = nouns[seed % 1000]
    adjective = adjectives[seed // 1000]
    return '{} {}'.format(adjective, noun)


if __name__ == '__main__':
    second_pcg()