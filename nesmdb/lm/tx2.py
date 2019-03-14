from collections import defaultdict
import tempfile

def midi_to_tx2(midi):
  import pretty_midi
  pretty_midi.pretty_midi.MAX_TICK = 1e16

  # Load MIDI file
  with tempfile.NamedTemporaryFile('wb') as mf:
    mf.write(midi)
    mf.seek(0)
    midi = pretty_midi.PrettyMIDI(mf.name)

  ins_names = ['p1', 'p2', 'tr', 'no']
  instruments = sorted(midi.instruments, key=lambda x: ins_names.index(x.name))
  samp_to_events = defaultdict(list)
  for ins in instruments:
    instag = ins.name.upper()

    last_start = -1
    last_end = -1
    last_pitch = -1
    for note in ins.notes:
      start = (note.start * 44100) + 1e-6
      end = (note.end * 44100) + 1e-6

      assert start - int(start) < 1e-3
      assert end - int(end) < 1e-3

      start = int(start)
      end = int(end)

      assert start > last_start
      assert start >= last_end

      pitch = note.pitch
      velocity = note.velocity

      if last_end >= 0 and last_end != start:
        samp_to_events[last_end].append('{}_NOTEOFF'.format(instag))
      samp_to_events[start].append('{}_NOTEON_{}'.format(instag, pitch))
      if instag != 'TR':
        samp_to_events[start].append('{}_VELOCITY_{}'.format(instag, velocity))

      last_start = start
      last_end = end
      last_pitch = pitch

    if last_pitch != -1:
      samp_to_events[last_end].append('{}_NOTEOFF'.format(instag))

    for cc in ins.control_changes:
      samp = (cc.time * 44100) + 1e-6
      assert samp - int(samp) < 1e-3
      samp = int(samp)

      if cc.number == 11:
        velocity = cc.value
        assert velocity > 0
        samp_to_events[samp].append('{}_VELOCITY_{}'.format(instag, velocity))
      elif cc.number == 12:
        samp_to_events[samp].append('{}_TIMBRE_{}'.format(instag, cc.value))
      else:
        assert False

  """
  for ins in midi.instruments:
    print('-' * 80)
    print(ins.name)
    for note in ins.notes[:4]:
      print(note)
    for cc in ins.control_changes[:4]:
      print(cc)
  """

  tx2 = []
  last_samp = 0
  for samp, events in sorted(samp_to_events.items(), key=lambda x: x[0]):
    wt = samp - last_samp
    assert last_samp == 0 or wt > 0
    if wt > 0:
      tx2.append('WT_{}'.format(wt))
    tx2.extend(events)
    last_samp = samp

  nsamps = int((midi.time_signature_changes[-1].time * 44100) + 1e-6)
  if nsamps > last_samp:
    tx2.append('WT_{}'.format(nsamps - last_samp))

  tx2 = '\n'.join(tx2)
  return tx2


def tx2_to_midi(tx2):
  import pretty_midi

  tx2 = tx2.strip().splitlines()
  nsamps = sum([int(x.split('_')[1]) for x in tx2 if x[:2] == 'WT'])

  # Create MIDI instruments
  p1_prog = pretty_midi.instrument_name_to_program('Lead 1 (square)')
  p2_prog = pretty_midi.instrument_name_to_program('Lead 2 (sawtooth)')
  tr_prog = pretty_midi.instrument_name_to_program('Synth Bass 1')
  no_prog = pretty_midi.instrument_name_to_program('Breath Noise')
  p1 = pretty_midi.Instrument(program=p1_prog, name='p1', is_drum=False)
  p2 = pretty_midi.Instrument(program=p2_prog, name='p2', is_drum=False)
  tr = pretty_midi.Instrument(program=tr_prog, name='tr', is_drum=False)
  no = pretty_midi.Instrument(program=no_prog, name='no', is_drum=True)

  name_to_ins = {'P1': p1, 'P2': p2, 'TR': tr, 'NO': no}
  name_to_pitch = {'P1': None, 'P2': None, 'TR': None, 'NO': None}
  name_to_start = {'P1': None, 'P2': None, 'TR': None, 'NO': None}
  name_to_max_velocity = {'P1': 15, 'P2': 15, 'TR': 1, 'NO': 15}

  samp = 0
  for event in tx2:
    if event[:2] == 'WT':
      samp += int(event[3:])
    else:
      tokens = event.split('_')
      name = tokens[0]
      ins = name_to_ins[tokens[0]]

      old_pitch = name_to_pitch[name]
      if tokens[1] == 'NOTEON':
        if old_pitch is not None:
          ins.notes.append(pretty_midi.Note(
              velocity=name_to_max_velocity[name],
              pitch=old_pitch,
              start=name_to_start[name] / 44100.,
              end=samp / 44100.))
        name_to_pitch[name] = int(tokens[2])
        name_to_start[name] = samp
      elif tokens[1] == 'NOTEOFF':
        if old_pitch is not None:
          ins.notes.append(pretty_midi.Note(
              velocity=name_to_max_velocity[name],
              pitch=name_to_pitch[name],
              start=name_to_start[name] / 44100.,
              end=samp / 44100.))

        name_to_pitch[name] = None
        name_to_start[name] = None
      elif tokens[1] == 'VELOCITY':
        ins.control_changes.append(pretty_midi.ControlChange(
          11,
          int(tokens[2]),
          samp / 44100.))
      elif tokens[1] == 'TIMBRE':
        ins.control_changes.append(pretty_midi.ControlChange(
          12,
          int(tokens[2]),
          samp / 44100.))
      else:
        raise ValueError()

  # Deactivating this for generated files
  #for name, pitch in name_to_pitch.items():
  #  assert pitch is None

  # Create MIDI and add instruments
  midi = pretty_midi.PrettyMIDI(initial_tempo=120, resolution=22050)
  midi.instruments.extend([p1, p2, tr, no])

  # Create indicator for end of song
  eos = pretty_midi.TimeSignature(1, 1, nsamps / 44100.)
  midi.time_signature_changes.append(eos)

  """
  for ins in midi.instruments:
    print('-' * 80)
    print(ins.name)
    for note in ins.notes[:4]:
      print(note)
    for cc in ins.control_changes[:4]:
      print(cc)
  """

  with tempfile.NamedTemporaryFile('rb') as mf:
    midi.write(mf.name)
    midi = mf.read()

  return midi
