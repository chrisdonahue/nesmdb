import numpy as np
import tempfile


def exprsco_to_midi(exprsco):
  import pretty_midi

  rate, nsamps, exprsco = exprsco

  # Create MIDI instruments
  p1_prog = pretty_midi.instrument_name_to_program('Lead 1 (square)')
  p2_prog = pretty_midi.instrument_name_to_program('Lead 2 (sawtooth)')
  tr_prog = pretty_midi.instrument_name_to_program('Synth Bass 1')
  no_prog = pretty_midi.instrument_name_to_program('Breath Noise')
  p1 = pretty_midi.Instrument(program=p1_prog)
  p2 = pretty_midi.Instrument(program=p2_prog)
  tr = pretty_midi.Instrument(program=tr_prog)
  no = pretty_midi.Instrument(program=no_prog)
  # TODO: is_drum=True for no??

  # Iterate through score to extract channel notes
  notes = {}
  for i, ch in enumerate(np.split(exprsco, 4, axis=1)):
    ch = ch[:, 0, :]
    if i == 2:
      ch[:, 1] = 1

    last_note = 0
    note_starts = []
    note_ends = []
    for s, (note, velocity, timbre) in enumerate(ch):
      if note != last_note:
        if note == 0:
          note_ends.append(s)
        else:
          if last_note == 0:
            note_starts.append((s, note, velocity))
          else:
            note_ends.append(s)
            note_starts.append((s, note, velocity))
        last_note = note
    if last_note != 0:
      note_ends.append(s)

    assert len(note_starts) == len(note_ends)
    notes[i] = zip(note_starts, note_ends)

  # Add notes to MIDI instruments
  for i, ins in enumerate([p1, p2, tr, no]):
    ch_notes = notes[i]
    for (start_samp, note, velocity), end_samp in ch_notes:
      assert end_samp > start_samp
      start_t, end_t = start_samp / 44100., end_samp / 44100.
      note = pretty_midi.Note(velocity=velocity, pitch=note, start=start_t, end=end_t)
      ins.notes.append(note)

  # Add instruments to MIDI file
  midi = pretty_midi.PrettyMIDI()
  midi.instruments.extend([p1, p2, tr, no])

  # Write/read MIDI file
  mf = tempfile.NamedTemporaryFile('rb')
  midi.write(mf.name)
  midi = mf.read()
  mf.close()

  return rate, nsamps, midi


def midi_to_exprsco(midi):
  import pretty_midi

  rate, nsamps, midi = midi

  assert rate == 44100

  # Write/read MIDI file
  mf = tempfile.NamedTemporaryFile('wb')
  mf.write(midi)
  mf.seek(0)
  midi = pretty_midi.PrettyMIDI(mf.name)
  mf.close()

  # Reconstruct expressive score
  exprsco = np.zeros((nsamps, 4, 3), dtype=np.uint8)
  for i, ins in enumerate(midi.instruments):
    for note in ins.notes:
      start = int(np.round(note.start * 44100))
      end = int(np.round(note.end * 44100))
      velocity = note.velocity
      note = note.pitch

      exprsco[start:end, i] = (note, velocity, 0)

  return rate, nsamps, exprsco
