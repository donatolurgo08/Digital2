# -*- coding: utf-8 -*-
"""Genera hardware/protoboard/protoboard.html
Dos protoboards de 830 lado a lado, con las 63 columnas en vertical
(como en la foto del MB-102): buses de alimentacion a los costados.
"""
import os

PITCH = 10
ROWX = {'a': 90, 'b': 100, 'c': 110, 'd': 120, 'e': 130,
        'f': 160, 'g': 170, 'h': 180, 'i': 190, 'j': 200}
BOFF = {'A': 0, 'B': 300}
Y0 = 80
TOP = ['a', 'b', 'c', 'd', 'e']
BOT = ['f', 'g', 'h', 'i', 'j']

RAILX = {'A': {'L5': 30, 'LG': 44, 'RG': 206, 'R5': 220},
         'B': {'L3': 330, 'LG': 344, 'RG': 506, 'R5': 520}}

def hy(c):
    return Y0 + (c - 1) * PITCH

def hx(b, r):
    return BOFF[b] + ROWX[r]

def node(b, r, c):
    return "%s-%s%d" % (b, 'T' if r in TOP else 'B', c)

def ref(b, r, c):
    return "%s-%s%d" % (b, r, c)

# ---------------------------------------------------------------- pines
P = {}
for n in range(1, 21):
    P['U1.%d' % n] = ('A', 'c', 21 + n)
for n in range(21, 41):
    P['U1.%d' % n] = ('A', 'g', 62 - n)

P.update({
    'U4.1': ('A', 'a', 56), 'U4.2': ('A', 'a', 57), 'U4.3': ('A', 'a', 58),
    'C8.1': ('A', 'b', 56), 'C8.2': ('A', 'b', 58),
    'C1.1': ('A', 'b', 32), 'C1.2': ('A', 'b', 33),
    'C2.1': ('A', 'h', 30), 'C2.2': ('A', 'h', 31),
    'R23.1': ('A', 'b', 19), 'R23.2': ('A', 'b', 22),
    'R21.1': ('A', 'i', 50), 'R21.2': ('A', 'i', 53),
    'D1.A': ('A', 'i', 54), 'D1.K': ('A', 'i', 55),
    'R22.1': ('A', 'i', 56), 'R22.2': ('A', 'i', 59),
    'D2.A': ('A', 'i', 60), 'D2.K': ('A', 'i', 61),
    'BZ1.VCC': ('A', 'j', 12), 'BZ1.GND': ('A', 'j', 13), 'BZ1.IO': ('A', 'j', 14),
    'J2.1': ('A', 'j', 16), 'J2.2': ('A', 'j', 17), 'J2.3': ('A', 'j', 18),
    'J2.4': ('A', 'j', 19), 'J2.5': ('A', 'j', 20), 'J2.6': ('A', 'j', 21),
    'MOD1.5V': ('A', 'a', 2), 'MOD1.3V3': ('A', 'a', 4), 'MOD1.GND': ('A', 'a', 6),
    'MOD1.GS': ('A', 'a', 8), 'MOD1.ST': ('A', 'a', 10),
    'MOD1.X': ('A', 'f', 2), 'MOD1.Y': ('A', 'f', 4), 'MOD1.Z': ('A', 'f', 6),
    'MOD1.SLP': ('A', 'f', 8), 'MOD1.0G': ('A', 'f', 10),
    'C5.1': ('A', 'f', 3), 'C5.2': ('A', 'e', 3),
    'C6.1': ('A', 'f', 5), 'C6.2': ('A', 'e', 5),
    'C7.1': ('A', 'f', 7), 'C7.2': ('A', 'e', 7),
    # placa B
    'C9.1': ('B', 'a', 2), 'C9.2': ('B', 'a', 3),
    'C11.1': ('B', 'b', 2), 'C11.2': ('B', 'b', 3),
    'R9.1': ('A', 'e', 42), 'R9.2': ('A', 'f', 42),
    'R10.1': ('A', 'e', 43), 'R10.2': ('A', 'f', 43),
    'R11.1': ('A', 'e', 44), 'R11.2': ('A', 'f', 44),
    'R12.1': ('A', 'e', 45), 'R12.2': ('A', 'f', 45),
    'R13.1': ('A', 'e', 46), 'R13.2': ('A', 'f', 46),
    'R14.1': ('A', 'e', 47), 'R14.2': ('A', 'f', 47),
    'R15.1': ('A', 'e', 48), 'R15.2': ('A', 'f', 48),
    'R16.1': ('A', 'e', 49), 'R16.2': ('A', 'f', 49),
    'R17.1': ('B', 'i', 23), 'R17.2': ('B', 'i', 26),
    'R18.1': ('B', 'i', 31), 'R18.2': ('B', 'i', 34),
    'R19.1': ('B', 'i', 39), 'R19.2': ('B', 'i', 42),
    'Q1.C': ('B', 'j', 27), 'Q1.B': ('B', 'j', 28), 'Q1.E': ('B', 'j', 29),
    'Q2.C': ('B', 'j', 35), 'Q2.B': ('B', 'j', 36), 'Q2.E': ('B', 'j', 37),
    'Q3.C': ('B', 'j', 43), 'Q3.B': ('B', 'j', 44), 'Q3.E': ('B', 'j', 45),
    'C10.1': ('B', 'j', 47), 'C10.2': ('B', 'j', 48),
    'J1.3V3': ('B', 'j', 52), 'J1.TXD': ('B', 'j', 53), 'J1.RXD': ('B', 'j', 54),
    'J1.GND': ('B', 'j', 55), 'J1.5V': ('B', 'j', 56),
})

# displays: pin -> (row, col) sobre placa B
DS = {}
for name, c0 in (('DS1', 6), ('DS2', 12), ('DS3', 18)):
    # patas 1-5 en fila e, 6-10 en fila f (6 en la ultima columna)
    for i in range(5):
        DS['%s.p%d' % (name, i + 1)] = ('e', c0 + i)
    for i in range(5):
        DS['%s.p%d' % (name, 6 + i)] = ('f', c0 + 4 - i)
SEGNAME = {1: 'e', 2: 'd', 3: 'CC', 4: 'c', 5: 'dp',
           6: 'b', 7: 'a', 8: 'CC', 9: 'f', 10: 'g'}
for k, v in DS.items():
    P['B-' + k] = ('B', v[0], v[1])

def dspin(name, seg):
    for p in range(1, 11):
        if SEGNAME[p] == seg:
            return 'B-%s.p%d' % (name, p)
    raise KeyError(seg)

NETS = {
    '+5V': ['U1.11', 'U1.32', 'U4.1', 'BZ1.VCC', 'MOD1.5V', 'R23.1',
            'C1.1', 'C2.1', 'C8.1', 'C10.1', 'J2.2'],
    'GND': ['U1.12', 'U1.31', 'U4.3', 'C1.2', 'C2.2', 'C5.2', 'C6.2', 'C7.2',
            'C8.2', 'C9.2', 'C10.2', 'C11.2', 'D1.K', 'D2.K', 'Q1.E', 'Q2.E',
            'Q3.E', 'J1.GND', 'J2.3', 'BZ1.GND', 'MOD1.GND', 'MOD1.GS', 'MOD1.ST'],
    '+3V3': ['C9.1', 'C11.1'],
    'MOD1_3V3': ['MOD1.3V3', 'MOD1.SLP'],
    'AN0': ['U4.2', 'U1.2'],
    'X_IN': ['MOD1.X', 'C5.1', 'U1.3'],
    'Y_IN': ['MOD1.Y', 'C6.1', 'U1.8'],
    'Z_IN': ['MOD1.Z', 'C7.1', 'U1.9'],
    'MCLR': ['U1.1', 'R23.2', 'J2.1'],
    'PGD': ['U1.40', 'J2.4'],
    'PGC': ['U1.39', 'J2.5'],
    'PGM': ['U1.36', 'J2.6'],
    'TX_TTL': ['U1.25', 'J1.RXD'],
    'RX_TTL': ['U1.26', 'J1.TXD'],
    'RD0_SEG': ['U1.19', 'R9.1'],
    'RD1_SEG': ['U1.20', 'R10.1'],
    'RD2_SEG': ['U1.21', 'R11.1'],
    'RD3_SEG': ['U1.22', 'R12.1'],
    'RD4_SEG': ['U1.27', 'R13.1'],
    'RD5_SEG': ['U1.28', 'R14.1'],
    'RD6_SEG': ['U1.29', 'R15.1'],
    'RD7_SEG': ['U1.30', 'R16.1'],
    'DIG1': ['U1.15', 'R17.1'],
    'DIG2': ['U1.16', 'R18.1'],
    'DIG3': ['U1.17', 'R19.1'],
    'Q1_B': ['R17.2', 'Q1.B'],
    'Q2_B': ['R18.2', 'Q2.B'],
    'Q3_B': ['R19.2', 'Q3.B'],
    'DS1_CC': [dspin('DS1', 'CC'), 'B-DS1.p3', 'Q1.C'],
    'DS2_CC': [dspin('DS2', 'CC'), 'B-DS2.p3', 'Q2.C'],
    'DS3_CC': [dspin('DS3', 'CC'), 'B-DS3.p3', 'Q3.C'],
    'LED1': ['U1.4', 'R21.1'],
    'LED2': ['U1.7', 'R22.1'],
    'D1_A': ['R21.2', 'D1.A'],
    'D2_A': ['R22.2', 'D2.A'],
    'BZ_CTRL': ['U1.18', 'BZ1.IO'],
    'USB_TTL_3V3': ['J1.3V3'],
    'USB_TTL_5V': ['J1.5V'],
    '0G_DETECT': ['MOD1.0G'],
}
for seg, r in (('a', 9), ('b', 10), ('c', 11), ('d', 12),
               ('e', 13), ('f', 14), ('g', 15), ('dp', 16)):
    NETS['SEG_' + seg.upper()] = ['R%d.2' % r, dspin('DS1', seg),
                                  dspin('DS2', seg), dspin('DS3', seg)]

# red de cada agujero
HNET = {}
for net, pins in NETS.items():
    for p in pins:
        b, r, c = P[p]
        HNET[ref(b, r, c)] = net

FAM = {'+5V': 'p5', '+3V3': 'p3', 'GND': 'gnd'}
for k in ('AN0', 'X_IN', 'Y_IN', 'Z_IN'):
    FAM[k] = 'an'
for k in NETS:
    if k.startswith('SEG_') or k.startswith('DS') or k.startswith('Q'):
        FAM.setdefault(k, 'dg')
for k in ('DIG1', 'DIG2', 'DIG3', 'LED1', 'LED2', 'D1_A', 'D2_A', 'BZ_CTRL'):
    FAM.setdefault(k, 'dg')
for k in ('TX_TTL', 'RX_TTL', 'PGD', 'PGC', 'PGM', 'MCLR'):
    FAM.setdefault(k, 'pr')
for k in NETS:
    FAM.setdefault(k, 'an')

# ---------------------------------------------------------------- dibujo
S = []
def add(s): S.append(s)
def line(x1, y1, x2, y2, cls='lead', extra=''):
    add('<line x1="%g" y1="%g" x2="%g" y2="%g" class="%s" %s/>' % (x1, y1, x2, y2, cls, extra))
def rect(x1, y1, x2, y2, cls='body', rx=2):
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" class="%s"/>'
        % (x1, y1, x2 - x1, y2 - y1, rx, cls))
def txt(x, y, s, cls='part', anchor='middle', rot=None):
    t = ' transform="rotate(-90 %g %g)"' % (x, y) if rot else ''
    add('<text x="%g" y="%g" class="%s" text-anchor="%s"%s>%s</text>'
        % (x, y, cls, anchor, t, s))
def hole(b, r, c, cls='hole', rad=1.5):
    add('<circle cx="%g" cy="%g" r="%g" class="%s" data-node="%s" data-net="%s"/>'
        % (hx(b, r), hy(c), rad, cls, node(b, r, c), HNET.get(ref(b, r, c), '')))

def res(b, row, c1, c2, label, side=1):
    x = hx(b, row); y1, y2 = hy(c1), hy(c2)
    line(x, y1, x, y1 + 6); line(x, y2 - 6, x, y2)
    rect(x - 3, y1 + 6, x + 3, y2 - 6, 'res', 1)
    if side > 0:
        txt(x + 7, (y1 + y2) / 2 + 2, label, 'part', 'start')
    else:
        txt(x - 7, (y1 + y2) / 2 + 2, label, 'part', 'end')

def res_ch(b, col, label):
    """Resistencia cruzando el canal: fila e -> fila f, misma columna."""
    x1, x2 = hx(b, 'e'), hx(b, 'f'); y = hy(col)
    line(x1, y, x1 + 4, y); line(x2 - 4, y, x2, y)
    rect(x1 + 4, y - 3, x2 - 4, y + 3, 'res', 1)
    txt((x1 + x2) / 2, y - 5, label, 'part')

def cap(b, row, c1, c2, label, pol=False, side=1):
    x = hx(b, row); y1, y2 = hy(c1), hy(c2); m = (y1 + y2) / 2
    line(x, y1, x, m - 2); line(x, m + 2, x, y2)
    line(x - 5, m - 2, x + 5, m - 2, 'cap')
    line(x - 5, m + 2, x + 5, m + 2, 'cap')
    if pol:
        txt(x - 7, m - 4, '+', 'pol', 'middle')
    if side > 0:
        txt(x + 7, m + 2, label, 'part', 'start')
    else:
        txt(x - 7, m + 2, label, 'part', 'end')

def led(b, row, c1, c2, label):
    x = hx(b, row); y1, y2 = hy(c1), hy(c2); m = (y1 + y2) / 2
    line(x, y1, x, m - 4)
    add('<path d="M%g %g L%g %g L%g %g Z" class="diode"/>'
        % (x - 4, m - 4, x + 4, m - 4, x, m + 3))
    line(x - 5, m + 3, x + 5, m + 3, 'cap')
    line(x, m + 3, x, y2)
    txt(x + 7, m, label, 'part', 'start')

def to92(b, row, c1, label, pins, r=11):
    x = hx(b, row); yc = (hy(c1) + hy(c1 + 2)) / 2
    add('<path d="M%g %g A%g %g 0 0 1 %g %g Z" class="body"/>'
        % (x - r, yc - 8, r, r, x + r, yc - 8))
    for i in range(3):
        line(x, yc - 8, hx(b, row), hy(c1 + i), 'pin')
    for i, p in enumerate(pins):
        txt(x - 4, hy(c1 + i) + 2, p, 'pinlbl', 'end', rot=True)
    txt(x, yc - 14, label, 'part')

def hdr(b, row, c1, n, label, pins):
    x = hx(b, row); y1, y2 = hy(c1) - 4, hy(c1 + n - 1) + 4
    rect(x - 5, y1, x + 5, y2, 'hdr', 1)
    for i in range(n):
        add('<rect x="%g" y="%g" width="4" height="4" class="pinpad"/>'
            % (x - 2, hy(c1 + i) - 2))
        txt(x - 8, hy(c1 + i) + 2, pins[i], 'pinlbl', 'end', rot=True)
    txt(x + 4, y2 + 10, label, 'part', 'end')

def dip40():
    x1, x2 = hx('A', 'c'), hx('A', 'g')
    y1, y2 = hy(22) - 6, hy(41) + 6
    rect(x1 + 5, y1, x2 - 5, y2, 'chip', 2)
    add('<path d="M%g %g a4 4 0 0 1 0 8" class="notch"/>' % ((x1 + x2) / 2, y1))
    for col in range(22, 42):
        line(x1, hy(col), x1 + 5, hy(col), 'pin')
        line(x2 - 5, hy(col), x2, hy(col), 'pin')
        txt(x1 - 6, hy(col) + 2, str(col - 21), 'pinlbl', 'middle', rot=True)
        txt(x2 + 7, hy(col) + 2, str(62 - col), 'pinlbl', 'middle', rot=True)
    txt((x1 + x2) / 2, (y1 + y2) / 2 - 4, 'U1', 'chiplbl', rot=True)
    txt((x1 + x2) / 2 + 7, (y1 + y2) / 2 - 4, 'PIC16F887', 'chiplbl', rot=True)

def dip10(name, c0):
    x1, x2 = hx('B', 'e'), hx('B', 'f')
    y1, y2 = hy(c0) - 5, hy(c0 + 4) + 5
    rect(x1 + 4, y1, x2 - 4, y2, 'chip', 2)
    top = ['e', 'd', 'CC', 'c', 'dp']
    bot = ['b', 'a', 'CC', 'f', 'g']
    for i in range(5):
        line(x1, hy(c0 + i), x1 + 4, hy(c0 + i), 'pin')
        line(x2 - 4, hy(c0 + 4 - i), x2, hy(c0 + 4 - i), 'pin')
        txt(x1 - 3, hy(c0 + i) + 2, top[i], 'seglbl', 'end', rot=True)
        txt(x2 + 4, hy(c0 + 4 - i) + 2, bot[i], 'seglbl', 'start', rot=True)
    txt((x1 + x2) / 2, y1 - 7, name, 'chiplbl')

# ---------------- documento
add('<svg viewBox="0 0 560 800" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Diseno de protoboard Hand Motion, dos placas de 830 lado a lado">')

for b in ('A', 'B'):
    x0 = 18 + BOFF[b]; x1 = 232 + BOFF[b]
    rect(x0, 60, x1, 740, 'board', 4)
    # canal central
    add('<rect x="%g" y="66" width="30" height="668" class="chan"/>'
        % (hx(b, 'e') + 1))

# buses
for b in ('A', 'B'):
    for k, x in RAILX[b].items():
        cls = 'rail5' if k.endswith('5') else ('rail3' if k.endswith('3') else 'railg')
        for a, z in ((1, 31), (32, 63)):
            line(x, hy(a) - 8, x, hy(z) + 8, cls)
        for c in range(1, 64):
            add('<circle cx="%g" cy="%g" r="1.2" class="rhole"/>' % (x, hy(c)))
        lab = {'L5': '+5V', 'R5': '+5V', 'L3': '+3V3', 'LG': 'GND', 'RG': 'GND'}[k]
        txt(x + 2, 752, lab, 'raillbl', 'start', rot=True)

# agujeros
for b in ('A', 'B'):
    for r in 'abcdefghij':
        for c in range(1, 64):
            hole(b, r, c)

# letras de fila y numeros de columna
for b in ('A', 'B'):
    for r in 'abcdefghij':
        txt(hx(b, r), 56, r, 'rowlbl')
        txt(hx(b, r), 752, r, 'rowlbl')
    for c in range(1, 64, 5):
        txt(12 + BOFF[b], hy(c) + 3, str(c), 'colnum')
    txt(12 + BOFF[b], 778, 'PLACA ' + b, 'boardlbl', 'start')

# ---------------- componentes
dip40()
for nm, c0 in (('DS1', 6), ('DS2', 12), ('DS3', 18)):
    dip10(nm, c0)

to92('A', 'a', 56, 'U4 LM35', ['1', '2', '3'])
cap('A', 'b', 56, 58, 'C8', False, -1)
res('A', 'b', 19, 22, 'R23 10k', -1)
cap('A', 'b', 32, 33, 'C1', False, -1)
cap('A', 'h', 30, 31, 'C2', False, -1)
res('A', 'i', 50, 53, 'R21')
led('A', 'i', 54, 55, 'D1')
res('A', 'i', 56, 59, 'R22')
led('A', 'i', 60, 61, 'D2')
hdr('A', 'j', 12, 3, 'BZ1', ['VCC', 'GND', 'I/O'])
hdr('A', 'j', 16, 6, 'J2 ICSP', ['1', '2', '3', '4', '5', '6'])

# filtros: entre fila f y e (misma columna, distinto nodo)
for nm, c in (('C5', 3), ('C6', 5), ('C7', 7)):
    x = hx('A', 'f'); yf, ye = hy(c), hy(c)
    line(x, yf, x, yf - 4); line(x, ye, x, ye + 4)
    y = (yf + ye) / 2
    line(x - 5, y - 2, x + 5, y - 2, 'cap')
    line(x - 5, y + 2, x + 5, y + 2, 'cap')
    txt(x + 7, y + 2, nm, 'part', 'start')

cap('B', 'a', 2, 3, 'C9')
cap('B', 'b', 2, 3, 'C11', True, -1)
for i in range(8):
    res_ch('A', 42 + i, 'R%d' % (9 + i))
for i, (nm, c1) in enumerate((('R17', 23), ('R18', 31), ('R19', 39))):
    res('B', 'i', c1, c1 + 3, nm)
for i, (nm, c1) in enumerate((('Q1', 27), ('Q2', 35), ('Q3', 43))):
    to92('B', 'j', c1, nm, ['C', 'B', 'E'])
cap('B', 'j', 47, 48, 'C10', True)
hdr('B', 'j', 52, 5, 'J1 USB-TTL', ['3V3', 'TXD', 'RXD', 'GND', '+5V'])

# ---------------- MOD1 y PS1 fuera de placa
rect(20, 4, 232, 34, 'mod', 3)
txt(126, 17, 'MOD1  MMA7361L', 'chiplbl')
txt(126, 27, 'header 2x5 sobre adaptador - 10 cables', 'note')
for c in (2, 4, 6, 8, 10):
    line(hx('A', 'a'), 34, hx('A', 'a'), hy(c) - 3, 'dash')
for c in (2, 4, 6, 8, 10):
    line(hx('A', 'f') + 2, 34, hx('A', 'f') + 2, hy(c) - 3, 'dash')
for c, nm in ((2, '5V'), (4, '3V3'), (6, 'GND'), (8, 'GS'), (10, 'ST')):
    txt(hx('A', 'a') + 3, hy(c) - 5, nm, 'seglbl', 'start')
for c, nm in ((2, 'X'), (4, 'Y'), (6, 'Z'), (8, 'SLP'), (10, '0G')):
    txt(hx('A', 'f') - 4, hy(c) - 5, nm, 'seglbl', 'end')

rect(318, 4, 532, 34, 'psu', 3)
txt(425, 15, 'PS1  HW-131 / MB-102', 'chiplbl')
txt(425, 25, 'DC-IN 9 V DC  ->  +5V y +3V3', 'note')
txt(425, 33, 'USB-A es salida, no entrada', 'note')

add('</svg>')
SVG = ''.join(S)

# ---------------- cables (ocultos por defecto)
def rail_x(net, b, r):
    if net == '+5V':
        if b == 'A':
            return RAILX['A']['L5'] if r in TOP else RAILX['A']['R5']
        return RAILX['B']['R5']
    if net == '+3V3':
        return RAILX['B']['L3']
    if b == 'A':
        return RAILX['A']['LG'] if r in TOP else RAILX['A']['RG']
    return RAILX['B']['LG'] if r in TOP else RAILX['B']['RG']

segs = []
for net, pins in NETS.items():
    seen, reps = set(), []
    for p in pins:
        b, r, c = P[p]
        n = node(b, r, c)
        if n in seen:
            continue
        seen.add(n)
        reps.append((b, r, c))
    if net in ('+5V', 'GND', '+3V3'):
        continue
    else:
        reps.sort(key=lambda t: (t[0], t[2], t[1]))
        for u, v in zip(reps, reps[1:]):
            if node(*u) == node(*v):
                continue
            segs.append((net, hx(u[0], u[1]), hy(u[2]), hx(v[0], v[1]), hy(v[2])))

W = ['<g id="wires" class="wires hidden">']
for net, x1, y1, x2, y2 in segs:
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = (dx * dx + dy * dy) ** 0.5 or 1
    ox, oy = -dy / L * 7, dx / L * 7
    W.append('<path d="M%g %g Q%g %g %g %g" class="w-%s"/>'
             % (x1, y1, mx + ox, my + oy, x2, y2, FAM[net]))
W.append('</g>')
SVG = SVG.replace('</svg>', ''.join(W) + '</svg>')

# ---------------- tablas
def nodelabel(b, r, c):
    return "col %d &middot; filas %s" % (c, 'a-e' if r in TOP else 'f-j')

rows = []
for net in sorted(NETS, key=lambda n: (list(NETS).index(n))):
    fam = FAM[net]
    items = []
    for p in NETS[net]:
        b, r, c = P[p]
        items.append('<span class="pinref">%s</span> <code>%s</code> <span class="nl">%s</span>'
                     % (p, ref(b, r, c), nodelabel(b, r, c)))
    rows.append('<tr data-net="%s"><td class="nm"><b class="sw %s"></b>%s</td><td>%s</td></tr>'
                % (net, fam, net, '<br>'.join(items)))

PINF = {1: 'MCLR', 2: 'RA0/AN0', 3: 'RA1/AN1', 4: 'RA2', 5: 'RA3 (libre)', 6: 'RA4 (libre)',
        7: 'RA5', 8: 'RE0/AN5', 9: 'RE1/AN6', 10: 'RE2 (libre)', 11: 'VDD', 12: 'VSS',
        13: 'RA7 (libre)', 14: 'RA6 (libre)', 15: 'RC0', 16: 'RC1', 17: 'RC2', 18: 'RC3',
        19: 'RD0', 20: 'RD1', 21: 'RD2', 22: 'RD3', 23: 'RC4 (libre)', 24: 'RC5 (libre)',
        25: 'RC6/TX', 26: 'RC7/RX', 27: 'RD4', 28: 'RD5', 29: 'RD6', 30: 'RD7',
        31: 'VSS', 32: 'VDD', 33: 'RB0 (libre)', 34: 'RB1 (libre)', 35: 'RB2 (libre)',
        36: 'RB3/PGM', 37: 'RB4 (libre)', 38: 'RB5 (libre)', 39: 'RB6/PGC', 40: 'RB7/PGD'}
prow = []
for n in range(1, 41):
    b, r, c = P['U1.%d' % n]
    net = HNET.get(ref(b, r, c), '&mdash;')
    prow.append('<tr><td>%d</td><td>%s</td><td><code>%s</code></td><td><b class="sw %s"></b>%s</td></tr>'
                % (n, PINF[n], ref(b, r, c), FAM.get(net, 'nc'), net))

CSS = """
:root{--bg:#fff;--fg:#15181c;--mu:#66707a;--bd:#d3d8de;--board:#f4f6f8;--chan:#e6eaee;
--hole:#b3bac2;--rail:#98a1aa;--chip:#fffdf3;--edge:#2b3037;--p5:#d12c2c;--p3:#e07a00;
--an:#1c6fd1;--dg:#14895a;--pr:#a02f7f;--gnd:#4a5560;--hl:#ffd54a}
@media (prefers-color-scheme:dark){:root{--bg:#14171b;--fg:#e9ecef;--mu:#98a1aa;--bd:#333a42;
--board:#20252b;--chan:#181c21;--hole:#5c6672;--rail:#6d7883;--chip:#2a3037;--edge:#9aa4ae;
--p5:#ef5a5a;--p3:#f0a23c;--an:#5a9bf0;--dg:#3fb98a;--pr:#d268ac;--gnd:#9aa4ae;--hl:#ffd54a}}
*{box-sizing:border-box}
body{margin:0;padding:18px 20px 60px;background:var(--bg);color:var(--fg);
font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
h1{font-size:21px;margin:0 0 2px}
h2{font-size:16px;margin:30px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--bd)}
p.sub{margin:0 0 12px;color:var(--mu);font-size:13px;max-width:1100px}
.wrap{display:flex;gap:22px;align-items:flex-start;flex-wrap:wrap}
.dia{flex:0 0 auto;border:1px solid var(--bd);border-radius:10px;padding:6px;background:var(--bg)}
svg{display:block;width:560px;height:800px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12px;margin:6px 0 10px}
.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:0}
.sw.p5{background:var(--p5)}.sw.p3{background:var(--p3)}.sw.gnd{background:var(--gnd)}
.sw.an{background:var(--an)}.sw.dg{background:var(--dg)}.sw.pr{background:var(--pr)}.sw.nc{background:var(--hole)}
.board{fill:var(--board);stroke:var(--bd)}
.chan{fill:var(--chan)}
.hole{fill:var(--hole)}
.rhole{fill:var(--rail);opacity:.5}
.rail5{stroke:var(--p5);stroke-width:3.4;stroke-linecap:round}
.rail3{stroke:var(--p3);stroke-width:3.4;stroke-linecap:round}
.railg{stroke:var(--gnd);stroke-width:3.4;stroke-linecap:round;opacity:.75}
.raillbl{font:600 8px ui-monospace,monospace;fill:var(--mu)}
.rowlbl{font:700 10px ui-monospace,monospace;fill:var(--mu)}
.colnum{font:5.5px ui-monospace,monospace;fill:var(--mu)}
.boardlbl{font:700 11px ui-monospace,monospace;fill:var(--mu);letter-spacing:1px}
.chip{fill:var(--chip);stroke:var(--edge);stroke-width:1.2}
.chiplbl{font:700 7.5px ui-monospace,monospace;fill:var(--fg)}
.notch{fill:none;stroke:var(--edge);stroke-width:1.2}
.pin{stroke:var(--edge);stroke-width:1}
.pinpad{fill:var(--edge);opacity:.55}
.pinlbl{font:5.5px ui-monospace,monospace;fill:var(--mu)}
.part{font:7px ui-monospace,monospace;fill:var(--fg)}
.note{font:6px ui-monospace,monospace;fill:var(--mu)}
.seglbl{font:700 6.5px ui-monospace,monospace;fill:var(--dg)}
.lead{stroke:var(--fg);stroke-width:1}
.res{fill:none;stroke:var(--fg);stroke-width:1.1}
.cap{stroke:var(--fg);stroke-width:1.3}
.diode{fill:none;stroke:var(--dg);stroke-width:1.3}
.hdr{fill:var(--chip);stroke:var(--edge);stroke-width:1.1}
.body{fill:var(--chip);stroke:var(--edge);stroke-width:1.1}
.mod{fill:none;stroke:var(--pr);stroke-width:1.2;stroke-dasharray:4 3}
.psu{fill:none;stroke:var(--p5);stroke-width:1.2;stroke-dasharray:4 3}
.dash{stroke:var(--pr);stroke-width:.9;stroke-dasharray:3 3;opacity:.75}
.pol{font:700 6px ui-monospace,monospace;fill:var(--fg)}
.wires.hidden{display:none}
.wires path{fill:none;stroke-width:1.1;opacity:.62;stroke-linecap:round}
.w-p5{stroke:var(--p5)}.w-p3{stroke:var(--p3)}.w-gnd{stroke:var(--gnd)}
.w-an{stroke:var(--an)}.w-dg{stroke:var(--dg)}.w-pr{stroke:var(--pr)}
circle.hl{fill:var(--hl);r:3.2}
table{border-collapse:collapse;font-size:12.5px;width:100%;max-width:1100px}
th,td{border-bottom:1px solid var(--bd);padding:5px 8px;text-align:left;vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:var(--mu)}
tbody tr:hover{background:color-mix(in srgb,var(--hl) 16%,transparent)}
td.nm{white-space:nowrap;font-family:ui-monospace,monospace;font-weight:600}
code{font:11.5px ui-monospace,monospace;background:color-mix(in srgb,var(--mu) 14%,transparent);
padding:1px 4px;border-radius:3px}
.pinref{font-family:ui-monospace,monospace;font-weight:600}
.nl{color:var(--mu);font-size:11.5px}
.ctr{display:flex;gap:18px;align-items:center;font-size:13px;margin:10px 0 0;flex-wrap:wrap}
.ctr label{display:flex;gap:6px;align-items:center;cursor:pointer}
ol,ul{max-width:1100px;padding-left:22px}
li{margin:4px 0}
.warn{border-left:3px solid var(--p3);background:color-mix(in srgb,var(--p3) 8%,transparent);
padding:8px 12px;border-radius:0 6px 6px 0;margin:12px 0;max-width:1100px;font-size:13px}
.warn b{color:var(--p3)}
"""

JS = """
const holes=[...document.querySelectorAll('circle.hole')];
const rows=[...document.querySelectorAll('tr[data-net]')];
function hl(net,on){holes.forEach(h=>{if(h.dataset.net===net)h.classList.toggle('hl',on)})}
rows.forEach(tr=>{tr.addEventListener('mouseenter',()=>hl(tr.dataset.net,true));
tr.addEventListener('mouseleave',()=>hl(tr.dataset.net,false))});
document.getElementById('wchk').addEventListener('change',e=>{
document.getElementById('wires').classList.toggle('hidden',!e.target.checked)});
"""

html = """<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hand Motion - Protoboard</title><style>@@CSS@@</style></head><body>
<h1>Hand Motion &middot; protoboard de dos placas de 830</h1>
<p class="sub">Las dos placas van una al lado de la otra, con las 63 columnas en vertical y los
buses de alimentacion a los costados (orientacion del MB-102). En esta vista cada columna de
5 agujeros (a-e o f-j) es un solo nodo: por eso los componentes solo se apoyan en columnas libres.
Pasa el mouse por una red de la tabla para ver sus agujeros.</p>
<div class="legend">
<span><i style="background:var(--p5)"></i>+5V</span>
<span><i style="background:var(--gnd)"></i>GND</span>
<span><i style="background:var(--p3)"></i>+3V3</span>
<span><i style="background:var(--an)"></i>analogico</span>
<span><i style="background:var(--dg)"></i>displays / alarmas</span>
<span><i style="background:var(--pr)"></i>UART / programacion</span>
</div>
<div class="wrap"><div class="dia">@@SVG@@
<div class="ctr"><label><input type="checkbox" id="wchk"> Mostrar cables</label>
<span class="nl">Vista superior, escala 1:1 (1 agujero = 2,54 mm)</span></div></div></div>

<h2>Como leer el dibujo</h2>
<ul>
<li><b>Placa A</b> (izquierda): PIC U1, R9-R16, LM35, filtros de entrada, LEDs, buzzer e ICSP.</li>
<li><b>Placa B</b> (derecha): los tres displays, Q1-Q3 con R17-R19, reserva y USB-TTL.</li>
<li><b>Columnas:</b> los numeros 1-63 estan a la izquierda de cada placa. Cada columna tiene
5 agujeros arriba (a-e) y 5 abajo (f-j), separados por el canal central.</li>
<li><b>PIC:</b> ocupa las columnas 22-41. Las patas 1-20 van en la fila <b>c</b> y las 21-40 en la
fila <b>g</b> (0,6" entre filas). El numero de cada pata esta rotulado junto al agujero.</li>
<li><b>Displays:</b> filas <b>e</b> y <b>f</b> (0,3"), columnas 6-10, 12-16 y 18-22 de la placa B.</li>
<li><b>Buses:</b> cada bus esta partido a la altura de la columna 31/32: hay que puentearlo.</li>
</ul>

<div class="warn"><b>Antes de energizar:</b> verifica con el multimetro que el bus marcado +5V
entregue 5,0 V y el marcado +3V3 entregue 3,3 V (o 3,0 V), y que todos los GND sean comunes.
El orden real de los buses en tu placa puede estar espejado: guiate por la serigrafia y no por
este dibujo.</div>

<h2>Mapa de patas del PIC</h2>
<table><thead><tr><th>Pata</th><th>Funcion</th><th>Agujero</th><th>Red</th></tr></thead>
<tbody>@@PROW@@</tbody></table>

<h2>Redes y agujeros</h2>
<p class="sub">Cada linea es una red de la netlist. Los agujeros de una misma columna y mitad
son el mismo nodo, asi que podes usar cualquiera de los cinco.</p>
<table><thead><tr><th>Red</th><th>Pines y agujeros</th></tr></thead>
<tbody>@@ROWS@@</tbody></table>

<h2>Guia de armado</h2>
<ol>
<li><b>Fijar las dos placas</b> sobre la base, una al lado de la otra, con el canal central en
vertical y los buses hacia los costados. Dejar 2-3 cm entre ambas para pasar cables.</li>
<li><b>Puentear los buses partidos:</b> un cable corto entre la columna 31 y la 32 en cada uno de
los 8 tramos (2 por placa: +5V y GND en cada lado). Sin esto, media placa queda sin alimentacion.</li>
<li><b>Alimentacion:</b> PS1 con la fuente de 9 V DC en el DC-IN. Regular un bus a 5 V y el otro a
3,3 V. Llevar +5V y GND a los buses de la placa A y +3V3 y GND al bus izquierdo de la placa B.
Medir antes de conectar nada mas.</li>
<li><b>Zocalo DIP-40</b> en las columnas 22-41 (fila c la pata 1, fila g la pata 40). Recien
despues insertar el PIC, con la muesca hacia la columna 22.</li>
<li><b>Desacople:</b> C1 entre las columnas 32 y 33 (patas 11 y 12), C2 entre 30 y 31 (patas 32 y
31). Van pegados al zocalo.</li>
<li><b>MCLR:</b> R23 entre la columna 19 y la 22, con el extremo de la 19 al bus +5V.</li>
<li><b>LM35</b> en las columnas 56-58 (1=+VS, 2=VOUT, 3=GND) y C8 entre 56 y 58.</li>
<li><b>Filtros del sensor:</b> C5, C6 y C7 entre la fila f y la fila e de las columnas 3, 5 y 7.</li>
<li><b>MOD1</b> sobre el adaptador, con los 10 cables a las columnas 2, 4, 6, 8 y 10 de las filas
a y f. GS y ST a GND, Sleep al pin 3V3 del modulo, 0g sin conectar.</li>
<li><b>Displays</b> en la placa B: DS1 en 6-10, DS2 en 12-16, DS3 en 18-22, con la pata 1 en la
columna menor de la fila e. Unir entre si las dos patas de catodo comun (3 y 8).</li>
<li><b>R9-R16</b> en la placa A, columnas 42 a 49, cruzando el canal (una pata en la fila e
y la otra en la fila f de la misma columna). Quedan al lado de las patas RD0-RD7.</li>
<li><b>Q1-Q3</b> en la fila j (columnas 27, 35 y 43) y R17-R19 en la fila i (23, 31 y 39).</li>
<li><b>LEDs:</b> R21 y D1 en la fila i columnas 50-55; R22 y D2 en 56-61.</li>
<li><b>Buzzer e ICSP</b> en la fila j: BZ1 en 12-14 y J2 en 16-21.</li>
<li><b>USB-TTL</b> en la placa B, fila j columnas 52-56. Usar solo GND, TXD y RXD,
cruzados con el PIC; 3V3 y +5V del adaptador quedan aislados.</li>
<li><b>Continuidad:</b> antes de poner el PIC, revisar con el multimetro que +5V y GND no esten en
cortocircuito y que cada red llegue solo a donde debe.</li>
</ol>

<h2>Pendiente de verificar en banco</h2>
<ul>
<li>Polaridad y tension real de la entrada DC-IN de PS1, y que admita 9 V DC.</li>
<li>Tension real del pin 3V3 del modulo (puede ser 3,0 V) y estado del jumper del modulo.</li>
<li>Nivel logico de TXD del USB-TTL antes de conectarlo a RC7.</li>
<li>Corriente de la entrada I/O del buzzer.</li>
<li>Patillaje real de los displays (1=e, 2=d, 3=CC, 4=c, 5=dp, 6=b, 7=a, 8=CC, 9=f, 10=g).</li>
</ul>
<script>@@JS@@</script></body></html>"""
for _k, _v in (("@@CSS@@", CSS), ("@@SVG@@", SVG), ("@@PROW@@", ''.join(prow)),
               ("@@ROWS@@", ''.join(rows)), ("@@JS@@", JS)):
    html = html.replace(_k, _v)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'protoboard.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('ok', out, len(html))

