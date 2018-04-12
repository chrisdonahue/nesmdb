from collections import defaultdict
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
  p1 = pretty_midi.Instrument(program=p1_prog, name='p1', is_drum=False)
  p2 = pretty_midi.Instrument(program=p2_prog, name='p2', is_drum=False)
  tr = pretty_midi.Instrument(program=tr_prog, name='tr', is_drum=False)
  no = pretty_midi.Instrument(program=no_prog, name='no', is_drum=True)

  # Iterate through score to extract channel notes
  notes = {}
  ccs = {}
  for i, ch in enumerate(np.split(exprsco, 4, axis=1)):
    ch = ch[:, 0, :]

    # MIDI doesn't allow velocity 0 messages so set tr velocity to 1
    if i == 2:
      ch[:, 1] = 1
      last_velocity = 1
    else:
      last_velocity = 0

    last_note = 0
    last_timbre = 0
    note_starts = []
    note_ends = []
    ch_ccs = []
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
      else:
        if velocity != last_velocity:
          ch_ccs.append((s, 11, velocity))

      if timbre != last_timbre:
        ch_ccs.append((s, 12, timbre))

      last_note = note
      last_velocity = velocity
      last_timbre = timbre
    if last_note != 0:
      note_ends.append(s + 1)

    assert len(note_starts) == len(note_ends)
    notes[i] = zip(note_starts, note_ends)
    ccs[i] = ch_ccs

  # Add notes to MIDI instruments
  for i, ins in enumerate([p1, p2, tr, no]):
    for (start_samp, note, velocity), end_samp in notes[i]:
      assert end_samp > start_samp
      start_t, end_t = start_samp / 44100., end_samp / 44100.
      note = pretty_midi.Note(velocity=velocity, pitch=note, start=start_t, end=end_t)
      ins.notes.append(note)

    for samp, cc_num, arg in ccs[i]:
      cc = pretty_midi.ControlChange(cc_num, arg, samp / 44100.)
      ins.control_changes.append(cc)

  # Add instruments to MIDI file
  midi = pretty_midi.PrettyMIDI(initial_tempo=120, resolution=22050)
  midi.instruments.extend([p1, p2, tr, no])

  # Create indicator for end of song
  eos = pretty_midi.TimeSignature(1, 1, nsamps / 44100.)
  midi.time_signature_changes.append(eos)

  # Write/read MIDI file
  mf = tempfile.NamedTemporaryFile('rb')
  midi.write(mf.name)
  midi = mf.read()
  mf.close()

  return midi


def midi_to_exprsco(midi):
  import pretty_midi

  # Write/read MIDI file
  mf = tempfile.NamedTemporaryFile('wb')
  mf.write(midi)
  mf.seek(0)
  midi = pretty_midi.PrettyMIDI(mf.name)
  mf.close()

  # Recover number of samples from time signature change indicator
  assert len(midi.time_signature_changes) == 2
  nsamps = int(np.round(midi.time_signature_changes[1].time * 44100))

  # Find voices in MIDI
  exprsco = np.zeros((nsamps, 4, 3), dtype=np.uint8)
  ins_names = ['p1', 'p2', 'tr', 'no']
  for ins in midi.instruments:
    ch = ins_names.index(ins.name)

    # Process note messages
    comms = defaultdict(list)
    for note in ins.notes:
      start = int(np.round(note.start * 44100))
      end = int(np.round(note.end * 44100))
      velocity = note.velocity if ch != 2 else 0
      note = note.pitch

      comms[start].append(('note_on', note, velocity))
      comms[end].append(('note_off',))

    # Process CC messages
    for cc in ins.control_changes:
      samp = int(np.round(cc.time * 44100))
      if cc.number == 11:
        velocity = cc.value
        assert velocity > 0
        comms[samp].append(('cc_velo', velocity))
      elif cc.number == 12:
        timbre = cc.value
        comms[samp].append(('cc_timbre', timbre))
      else:
        assert False

    # Write score
    note = 0
    velocity = 0
    timbre = 0
    for i in xrange(nsamps):
      for comm in comms[i]:
        if comm[0] == 'note_on':
          note = comm[1]
          velocity = comm[2]
        elif comm[0] == 'note_off':
          note = 0
          velocity = 0
        elif comm[0] == 'cc_velo':
          velocity = comm[1]
        elif comm[0] == 'cc_timbre':
          timbre = comm[1]
        else:
          assert False

      exprsco[i, ch] = (note, velocity, timbre)

  return 44100, nsamps, exprsco
