import subprocess
from random import choices, choice, randint, sample, shuffle
from mido import MidiFile, MidiTrack, Message, MetaMessage

def create_midi_file(chords, beats_per_chord, note_lengths, filename='output.mid'):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    ticks_per_beat = mid.ticks_per_beat
    chord_ticks = int(0.5 * beats_per_chord * ticks_per_beat)
    note_ticks = int(chord_ticks * note_lengths)
    rest_ticks = chord_ticks - note_ticks

    track.append(MetaMessage('set_tempo', tempo=500000))
    track.append(Message('program_change', program=7, time=0, channel=0))

    for chord in chords:
        for note in chord:
            track.append(Message('note_on', note=note, velocity=64, time=0))
        for i, note in enumerate(chord):
            if i == 0:
                track.append(Message('note_off', note=note, velocity=64, time=note_ticks))
            else:
                track.append(Message('note_off', note=note, velocity=64, time=0))
        if rest_ticks > 0:
            track.append(Message('note_off', note=0, velocity=0, time=rest_ticks))

    mid.save(filename)
    # print(f"'{filename}' generated successfully.")

def read_binary_strings(binary_filename, n, density):
    with open(binary_filename, 'rb') as f:
        data = f.read()
    binary_strings = []
    bits_read = 0
    current_value = 0
    mask = (1 << n) - 1
    for byte in data:
        current_value = (current_value << 8) | byte
        bits_read += 8
        while bits_read >= n:
            bits_read -= n
            binary_strings.append(format((current_value >> bits_read) & mask, f'0{n}b')[::-1])
    if density != 0:
        while binary_strings and all(bit == '0' for bit in binary_strings[-1]):
            binary_strings.pop()
    else:
        while len(binary_strings) > 1 and all(bit == '0' for bit in binary_strings[-1]):
            binary_strings.pop()
    return binary_strings

def run_necklaces_exe(type, edo, density=None, forbidden_sequence=None):
    command = ['./necklaces.exe', str(type), str(edo)]
    if type == 2 and density is not None:
        command.append(str(density))
    elif type == 3 and forbidden_sequence is not None:
        command.append(forbidden_sequence)
    subprocess.run(command)

from itertools import permutations

def binary_string_permutations(binary_string):
    indices = [i for i, char in enumerate(binary_string) if char == '1']
    if not indices:
        return [()]
    orderings = list(permutations(indices))
    return orderings

def generate_binary_strings(binary_str, ordering):
    if not ordering:
        return '0' * len(binary_str)
    result = []
    prev_index = -1
    for index in ordering:
        if not result or index <= prev_index:
            new_str = ['0'] * len(binary_str)
            new_str[index] = '1'
            result.append(''.join(new_str))
        else:
            result[-1] = result[-1][:index] + '1' + result[-1][index+1:]
        prev_index = index
    return ''.join(result)

CHARACTERS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
def binary_to_gap_lengths(binary, simplify=False):
    gaps = []
    gap_count = 0 if simplify else 1
    binary += binary[0]
    for bit in binary:
        if bit == '0':
            gap_count += 1
        else:
            gaps.append(gap_count)
            gap_count = 0 if simplify else 1

    if binary[0] != '0':
        gaps = gaps[1:]
    return ''.join(CHARACTERS[gap] for gap in gaps)

def write_chords_to_file(chord_data, chord_labels, filename='chords.py'):
    with open(filename, 'w') as f:
        f.write("chord_data = [\n")
        for chord in chord_data:
            # Check if the chord is a list (i.e., list of lists)
            if isinstance(chord, list):
                # Write the list of chords
                f.write(f"    {chord},\n")
            else:
                # Write the single chord element in a list format
                f.write(f"    [{chord}],\n")
        f.write("]\n\n")
        
        f.write("chord_labels = [\n")
        for label in chord_labels:
            f.write(f"    '{label}',\n")
        f.write("]\n")

def main():
    # if len(sys.argv) < 3:
    #     print("  1. all necklaces:         1 <EDO>")
    #     print("  2. fixed-density:         2 <EDO> <density>")
    #     print("  3. forbidden substring:   3 <EDO> <substring>")
    #     exit(1)

    type = 2  # int(sys.argv[1])


    edo = 12  # int(sys.argv[2])
    # number_of_voicings = 100
    root_note = 48
    density = 3
    forbidden_sequence = None

    
    # if type == 2:
    #     density = 3  # int(sys.argv[3])
    # elif type == 3:
    #     forbidden_sequence = sys.argv[3]

    run_necklaces_exe(type, edo, density, forbidden_sequence)
    # print('done writing.')
    
    with open('info.txt') as f:
        total = int(f.read().strip())
    print(f"total = {total}")

    if total <= 10000:
        binary_strings = read_binary_strings('binaries.bin', edo, density)
        print('done reading.')
        # if total <= 1000:
        #     print("\n".join(binary_strings))


    ## all chord shapes in a random order, each with a random voicing and root note
    # # binary_strings = choices(binary_strings, k=number_of_voicings)
    # binary_strings = sample(binary_strings, min(number_of_voicings, total))
    # if isinstance(binary_strings, str):
    #     binary_strings = [binary_strings]
    # midi_data = []
    # print()
    # for b in binary_strings:
    #     ordering = choice(binary_string_permutations(b))
    #     key = randint(0,edo-1)
    #     binary_string = generate_binary_strings(b, ordering)
    #     binary_string = binary_string.lstrip('0').rstrip('0')
    #     binary_string = binary_string[::-1]
    #     symbol = f'{CHARACTERS[key]}.{binary_to_gap_lengths(binary_string, True)[:-1]}'
    #     binary_string = key*'0'+binary_string

    #     midi_data.append(tuple([i+root_note for i, char in enumerate(binary_string) if char == '1']))

    #     print(f'{symbol} {binary_string}')

    ## all voicings and keys for each chord shape
    all_shapes_voicings = []

    for b in binary_strings:
        orderings = binary_string_permutations(b)
        # zero_pad = int(ceil(log10(len(orderings))))
        for i,o in enumerate(orderings):
            binary_string = generate_binary_strings(b, o)
            binary_string = binary_string.lstrip('0').rstrip('0')
            orderings[i] = binary_string
        voicings = sorted(set(orderings), key=lambda x: int(x[::-1], 2))
        all_shapes_voicings.append(voicings)
    
    # keys = [randint(0,edo-1) for _ in  range(total)]
    # shuffle(all_shapes_voicings)
    # button_chords = [choice(all_shapes_voicings[i]) for i in range(total)]

    chord_data = [[] for _ in range(total)]
    chord_labels = []
    for i,vs in enumerate(all_shapes_voicings):
        for v in vs:
            for key in range(edo):
                chord_data[i].append(tuple([x+root_note for x, char in enumerate(key*'0'+v) if char == '1']))
        chord_labels.append(f'{binary_to_gap_lengths(all_shapes_voicings[i][0], True)[:-1]}')

    # print(*[f'{a} {b}' for a,b in zip(chord_data, chord_labels)], sep='\n')
    write_chords_to_file(chord_data, chord_labels)



        # for i,o in enumerate(voicings):
        #     for key in range(edo):
        #         symbol = f'{str(i).zfill(zero_pad)}  {CHARACTERS[key]}.{binary_to_gap_lengths(o, True)[:-1]}  {key*'0'+o}'
        #         print(symbol)
        # print()


    # beats_per_chord = 2
    # note_lengths = 0.8
    # create_midi_file(midi_data, beats_per_chord, note_lengths)
        

if __name__ == "__main__":
    main()