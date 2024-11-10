import random
import time
from os import system, environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from pygame import midi, font, display, Rect, event, mouse, draw, quit, init, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT

BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
GREEN = (100, 200, 100)

def init_midi_player():
    midi.init()
    player = midi.Output(0)
    player.set_instrument(0)
    return player

def play_chord(player, chord):
    for note in chord:
        player.note_on(note, 64)

def stop_chord(player, chord):
    for note in chord:
        player.note_off(note, 64)

def create_chord_guessing_game(chords, labels):
    init()
    font.init()
    random.seed(time.time())
    font1 = font.Font('assets/JetBrainsMono-Light.otf', 25)
    font2 = font.Font('assets/JetBrainsMono-Light.otf', 16)
    padding = 0
    padding2 = 20
    font_yoffset = 0
    button_width = max(font1.size(label)[0] for label in labels) + padding2
    button_height = max(font1.size(label)[1] for label in labels) + padding2//2

    cols = 7
    rows = (len(chords) + cols - 1) // cols

    width = cols * (button_width + padding) + padding
    height = rows * (button_height + padding) + padding + 150

    screen = display.set_mode((width, height-30))
    display.set_caption('midi ear training')

    buttons = []
    for i, (chord, label) in enumerate(zip(chords, labels)):
        x = padding + (i % cols) * (button_width + padding)
        y = padding + (i // cols) * (button_height + padding)
        rect = Rect(x, y, button_width, button_height)
        buttons.append((rect, chord, label))

    s_play = font1.size('play')
    s_listen = font1.size('free listen')
    play_button_width = s_play[0] + padding2
    listen_button_width = s_listen[0] + padding2
    button_height = max(s_play[1], s_listen[1]) + padding2 // 2

    total_button_width = play_button_width + listen_button_width
    margin = (width - total_button_width) // 3

    play_button = Rect(margin, height - 110, play_button_width, button_height)
    listen_button = Rect(2 * margin + play_button_width, height - 110, listen_button_width, button_height)

    midi_player = init_midi_player()

    score = 0
    total_attempts = 0
    message = ''
    current_chord = None
    current_chord_element = None
    target_chord_index = None
    button_counts = [0] * len(chords)
    voicing_counts = [[] for _ in chords]
    listen_mode = False
    listen_chord = None

    def select_random_chord():
        nonlocal target_chord_index, current_chord_element

        min_count = min(button_counts)
        available_indices = [i for i, count in enumerate(button_counts) if count == min_count]
        target_chord_index = random.choices([random.choice(available_indices),
                                             random.randint(0, len(chords)-1)], [0.75, 0.25])[0]

        button_counts[target_chord_index] += 1

        chord_list = chords[target_chord_index]
        if isinstance(chord_list, list) and len(chord_list) > 1:
            if not voicing_counts[target_chord_index]:
                voicing_counts[target_chord_index] = [0] * len(chord_list)
            min_voicing_count = min(voicing_counts[target_chord_index])
            available_voicings = [i for i, count in enumerate(voicing_counts[target_chord_index]) if count == min_voicing_count]
            voicing_index = random.choices([random.choice(available_voicings),
                                            random.randint(0, len(chord_list)-1)], [0.9, 0.1])[0]
            current_chord_element = chord_list[voicing_index]
            voicing_counts[target_chord_index][voicing_index] += 1
        else:
            current_chord_element = chord_list[0] if isinstance(chord_list, list) else chord_list

    select_random_chord()

    running = True
    while running:
        for event_ in event.get():
            if event_.type == QUIT:
                running = False
            elif event_.type == MOUSEBUTTONDOWN:
                pos = mouse.get_pos()
                if play_button.collidepoint(pos):
                    play_chord(midi_player, current_chord_element)
                    current_chord = current_chord_element
                elif listen_button.collidepoint(pos):
                    listen_mode = not listen_mode
                    if not listen_mode and listen_chord:
                        stop_chord(midi_player, listen_chord)
                        listen_chord = None
                else:
                    for i, (button, chord_list, label) in enumerate(buttons):
                        if button.collidepoint(pos):
                            if listen_mode:
                                if listen_chord:
                                    stop_chord(midi_player, listen_chord)
                                if isinstance(chord_list, list):
                                    listen_chord = random.choice(chord_list)
                                else:
                                    listen_chord = chord_list
                                play_chord(midi_player, listen_chord)
                            else:
                                if isinstance(chord_list, list):
                                    if current_chord_element in chord_list or current_chord_element == chord_list:
                                        score += 1
                                        message = f'correct! the chord was {label}.'
                                    else:
                                        message = f'wrong. the correct chord was {labels[target_chord_index]}.'

                                total_attempts += 1
                                select_random_chord()
                            break
            elif event_.type == MOUSEBUTTONUP:
                if current_chord:
                    stop_chord(midi_player, current_chord)
                    current_chord = None
                if listen_mode and listen_chord:
                    stop_chord(midi_player, listen_chord)
                    listen_chord = None

        screen.fill((255, 255, 255))
        for button, _, label in buttons:
            draw.rect(screen, LIGHT_GRAY, button)
            draw.rect(screen, BLACK, button, 1)
            text = font1.render(label, False, BLACK)
            text_rect = text.get_rect(center=(button.centerx, button.centery+font_yoffset))
            screen.blit(text, text_rect)

        draw.rect(screen, GREEN, play_button)
        draw.rect(screen, BLACK, play_button, 1)
        play_text = font1.render('play', False, BLACK)
        play_text_rect = play_text.get_rect(center=play_button.center)
        screen.blit(play_text, play_text_rect)

        listen_color = GREEN if listen_mode else LIGHT_GRAY
        draw.rect(screen, listen_color, listen_button)
        draw.rect(screen, BLACK, listen_button, 1)
        listen_text = font1.render('free listen', False, BLACK)
        listen_text_rect = listen_text.get_rect(center=listen_button.center)
        screen.blit(listen_text, listen_text_rect)

        score_text = font1.render(f'score: {score}/{total_attempts}', False, BLACK)
        screen.blit(score_text, (padding2, height - 146))
        message_text = font2.render(message, False, BLACK)
        screen.blit(message_text, (padding2, height - 60))

        display.flip()

    midi_player.close()
    midi.quit()
    quit()

if __name__ == "__main__":
    system('read_voicings.py')
    from chords import chord_data, chord_labels
    create_chord_guessing_game(chord_data, chord_labels)