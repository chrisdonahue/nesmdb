def nd_to_txt(nd):
  txt = filter(lambda c: c[0] != 'ram', nd)
  txt = [','.join([str(f) for f in c]) for c in txt]
  txt = '\n'.join(txt)

  return txt


def txt_to_nd(txt):
  txt = [l.strip() for l in txt.splitlines()]

  nd = []
  for l in txt:
    if len(l) == 0 or l.startswith('//'):
      continue

    comm = l.split(',')
    if comm[0] == 'clock':
      nd.append(('clock', int(comm[1])))
    elif comm[0] == 'wait':
      nd.append(('wait', int(comm[1])))
    elif comm[0] == 'apu':
      if len(comm) == 3:
        # NDR
        nd.append(('apu', comm[1], comm[2]))
      else:
        # NDF
        nd.append(('apu', comm[1], comm[2], int(comm[3]), int(comm[4]), int(comm[5])))
    else:
      raise NotImplementedError('Invalid command: {}'.format(comm))

  return nd
