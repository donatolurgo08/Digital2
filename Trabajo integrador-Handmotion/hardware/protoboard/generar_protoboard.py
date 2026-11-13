# -*- coding: utf-8 -*-
"""Genera hardware/protoboard/protoboard.html
Dos protoboards de 830 lado a lado, con las 63 columnas en vertical
(como en la foto del MB-102): buses de alimentacion a los costados.
"""
import os

PITCH = 10
ROWX = {'a': 75, 'b': 85, 'c': 95, 'd': 105, 'e': 115,
        'f': 145, 'g': 155, 'h': 165, 'i': 175, 'j': 185}
BOFF = {'A': 0, 'B': 224}
Y0 = 90
TOP = ['a', 'b', 'c', 'd', 'e']
BOT = ['f', 'g', 'h', 'i', 'j']

# Rieles simetricos dentro de cada placa de 224 px de ancho.
# Exterior = +, interior = GND (segun la serigrafia de la placa real).
RAILX = {'A': {'L5': 37, 'LG': 51, 'RG': 209, 'R5': 223},
         'B': {'L3': 261, 'LG': 275, 'RG': 433, 'R5': 447}}

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
    'C8.1': ('A', 'c', 56), 'C8.2': ('A', 'c', 58),
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
    'MOD1.5V': ('A', 'e', 2), 'MOD1.3V3': ('A', 'e', 3), 'MOD1.GND': ('A', 'e', 4),
    'MOD1.GS': ('A', 'e', 5), 'MOD1.ST': ('A', 'e', 6),
    'MOD1.X': ('A', 'f', 2), 'MOD1.Y': ('A', 'f', 3), 'MOD1.Z': ('A', 'f', 4),
    'MOD1.SLP': ('A', 'f', 5), 'MOD1.0G': ('A', 'f', 6),
    'C5.1': ('A', 'f', 9), 'C5.2': ('A', 'e', 9),
    'C6.1': ('A', 'f', 10), 'C6.2': ('A', 'e', 10),
    'C7.1': ('A', 'f', 11), 'C7.2': ('A', 'e', 11),
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
    'R17.1': ('B', 'i', 30), 'R17.2': ('B', 'i', 33),
    'R18.1': ('B', 'i', 38), 'R18.2': ('B', 'i', 41),
    'R19.1': ('B', 'i', 46), 'R19.2': ('B', 'i', 49),
    'Q1.C': ('B', 'j', 27), 'Q1.B': ('B', 'j', 28), 'Q1.E': ('B', 'j', 29),
    'Q2.C': ('B', 'j', 35), 'Q2.B': ('B', 'j', 36), 'Q2.E': ('B', 'j', 37),
    'Q3.C': ('B', 'j', 43), 'Q3.B': ('B', 'j', 44), 'Q3.E': ('B', 'j', 45),
    'C10.1': ('B', 'j', 50), 'C10.2': ('B', 'j', 51),
    'J1.3V3': ('B', 'j', 52), 'J1.TXD': ('B', 'j', 53), 'J1.RXD': ('B', 'j', 54),
    'J1.GND': ('B', 'j', 55), 'J1.5V': ('B', 'j', 56),
})

# displays: pin -> (row, col) sobre placa B
DS = {}
for name, c0 in (('DS1', 6), ('DS2', 14), ('DS3', 22)):
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
def hole(b, r, c):
    x, y = hx(b, r), hy(c)
    add('<circle cx="%g" cy="%g" r="2.2" class="hole" data-node="%s" data-net="%s"/>'
        % (x, y, node(b, r, c), HNET.get(ref(b, r, c), '')))
    add('<circle cx="%g" cy="%g" r="1.3" class="holein"/>' % (x, y))

BANDS = {
    '220': ['#d12c2c', '#d12c2c', '#8a5a2b', '#c9a227'],
    '330': ['#e07a00', '#e07a00', '#8a5a2b', '#c9a227'],
    '10k': ['#8a5a2b', '#1a1a1a', '#e07a00', '#c9a227'],
}

def res_v(b, row, c1, c2, label, colors, side=1):
    x = hx(b, row); y1, y2 = hy(c1), hy(c2)
    line(x, y1, x, y1 + 6)
    line(x, y2 - 6, x, y2)
    add('<rect x="%g" y="%g" width="6" height="%g" rx="2" class="res"/>'
        % (x - 3, y1 + 6, y2 - y1 - 12))
    span = y2 - y1 - 12
    for i, col in enumerate(colors):
        p = y1 + 6 + span * (0.18 + 0.18 * i)
        add('<rect x="%g" y="%g" width="6" height="2" fill="%s"/>' % (x - 3, p, col))
    if side > 0:
        txt(x + 6, (y1 + y2) / 2, label, 'part', 'middle', rot=True)
    else:
        txt(x - 6, (y1 + y2) / 2, label, 'part', 'middle', rot=True)

def res_h(b, col, label, colors):
    x1, x2 = hx(b, 'e'), hx(b, 'f'); y = hy(col)
    line(x1, y, x1 + 6, y)
    line(x2 - 6, y, x2, y)
    add('<rect x="%g" y="%g" width="%g" height="6" rx="2" class="res"/>'
        % (x1 + 6, y - 3, x2 - x1 - 12))
    span = x2 - x1 - 12
    for i, colr in enumerate(colors):
        p = x1 + 6 + span * (0.18 + 0.18 * i)
        add('<rect x="%g" y="%g" width="2" height="6" fill="%s"/>' % (p, y - 3, colr))
    if label:
        txt(x1 - 5, y, label, 'part', 'middle', rot=True)

def cap_v(b, row, c1, c2, label, kind='ceramic', side=1):
    x = hx(b, row); y1, y2 = hy(c1), hy(c2); m = (y1 + y2) / 2
    line(x, y1, x, m - 3)
    line(x, m + 3, x, y2)
    if kind == 'ecap':
        add('<circle cx="%g" cy="%g" r="7" class="ecap"/>' % (x, m))
        add('<path d="M%g %g a6 6 0 0 1 0 12" fill="none" stroke="#e8ecef" '
            'stroke-width="1.6" opacity="0.8"/>' % (x - 2.5, m - 6))
        txt(x - 2.5, m - 3.5, '+', 'pol', 'middle')
    else:
        add('<ellipse cx="%g" cy="%g" rx="5.5" ry="4" class="capdisc"/>' % (x, m))
        add('<path d="M%g %g q4 -2 7 0" class="capplate" fill="none"/>' % (x - 3, m - 2))
    if side > 0:
        txt(x + 7, m + 2, label, 'part', 'start')
    else:
        txt(x - 7, m + 2, label, 'part', 'end')

def cap_h(b, col, label):
    x1, x2 = hx(b, 'e'), hx(b, 'f'); y = hy(col); m = (x1 + x2) / 2
    line(x1, y, m - 4, y)
    line(m + 4, y, x2, y)
    add('<ellipse cx="%g" cy="%g" rx="4" ry="5.5" class="capdisc"/>' % (m, y))
    if label:
        txt(x1 - 5, y, label, 'part', 'middle', rot=True)

def led_v(b, row, c1, c2, label):
    x = hx(b, row); y1, y2 = hy(c1), hy(c2); m = (y1 + y2) / 2
    line(x, y1, x, m - 5)
    line(x, m + 5, x, y2)
    add('<circle cx="%g" cy="%g" r="6" class="ledbody"/>' % (x, m))
    add('<ellipse cx="%g" cy="%g" rx="2" ry="1.4" class="ledhi"/>' % (x - 2, m - 2))
    add('<line x1="%g" y1="%g" x2="%g" y2="%g" class="lead"/>' % (x - 5, m + 4, x + 5, m + 4))
    txt(x + 7, m + 2, label, 'part', 'start')

def to92(b, row, c1, label, pins, side=-1):
    """TO-92 visto de frente: cuerpo acostado a un lado de sus tres patas."""
    x = hx(b, row)
    ys = [hy(c1 + i) for i in range(3)]
    yc = (ys[0] + ys[2]) / 2
    bw, bh = 9, 11
    bx = x + side * (bw + 2)
    for i, y in enumerate(ys):
        line(x, y, bx, y, 'pin')
        add('<circle cx="%g" cy="%g" r="1.7" class="gold"/>' % (x, y))
        txt(x + (4 if side < 0 else -4), y + 2, pins[i], 'pinlbl', 'middle', rot=True)
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" class="to92"/>'
        % (bx - bw, yc - bh, 2 * bw, 2 * bh, bw))
    add('<rect x="%g" y="%g" width="4" height="%g" rx="2" class="to92face"/>'
        % (bx + side * (bw - 5) - 2, yc - bh + 4, 2 * bh - 8))
    txt(bx - 4 if side < 0 else bx + 4, yc + 2, label, 'chiplbl', 'middle', rot=True)

def hdr(b, row, c1, n, label, pins, side=1):
    x = hx(b, row); y1, y2 = hy(c1) - 5, hy(c1 + n - 1) + 5
    add('<rect x="%g" y="%g" width="10" height="%g" rx="2" class="hdr"/>'
        % (x - 5, y1, y2 - y1))
    for i in range(n):
        add('<rect x="%g" y="%g" width="4" height="4" class="gold"/>'
            % (x - 2, hy(c1 + i) - 2))
        if side > 0:
            txt(x + 7, hy(c1 + i) + 2, pins[i], 'pinlbl', 'start', rot=True)
        else:
            txt(x - 7, hy(c1 + i) + 2, pins[i], 'pinlbl', 'end', rot=True)
    txt(x, y2 + 10, label, 'part', 'middle')

def dip40():
    x1, x2 = hx('A', 'c'), hx('A', 'g')
    y1, y2 = hy(22) - 6, hy(41) + 6
    bx1, bx2 = x1 + 5, x2 - 5
    by1, by2 = y1 + 2, y2 - 2
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="3" class="chip"/>'
        % (bx1, by1, bx2 - bx1, by2 - by1))
    cx = (bx1 + bx2) / 2
    add('<path d="M%g %g a5 5 0 0 1 10 0 Z" class="notch"/>' % (cx - 5, by1))
    add('<circle cx="%g" cy="%g" r="2" class="pinpad"/>' % (bx1 + 8, by1 + 8))
    for col in range(22, 42):
        line(x1, hy(col), bx1, hy(col), 'pin')
        line(bx2, hy(col), x2, hy(col), 'pin')
        txt(x1 - 5, hy(col) + 2, str(col - 21), 'pinlbl', 'middle', rot=True)
        txt(x2 + 6, hy(col) + 2, str(62 - col), 'pinlbl', 'middle', rot=True)
    txt(cx, (by1 + by2) / 2, 'PIC16F887', 'chiplbl', 'middle', rot=True)
    txt(cx + 8, (by1 + by2) / 2, 'U1', 'chiplbl', 'middle', rot=True)

def display(name, c0):
    x1, x2 = hx('B', 'e'), hx('B', 'f')
    bx1, bx2 = x1 - 10, x2 + 10
    by1, by2 = hy(c0) - 17.5, hy(c0 + 4) + 17.5
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="3" class="disp"/>'
        % (bx1, by1, bx2 - bx1, by2 - by1))
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="2" class="dispface"/>'
        % (bx1 + 3, by1 + 3, bx2 - bx1 - 6, by2 - by1 - 6))
    add('<path d="M%g %g L%g %g L%g %g Z" fill="#fff" opacity="0.06"/>'
        % (bx1 + 4, by1 + 4, bx2 - 8, by1 + 4, bx1 + 4, by2 - 10))
    cx = (bx1 + bx2) / 2 - 2
    cy = (by1 + by2) / 2
    w2, h2, t = 11, 18, 2.8
    segs = ((cx - w2, cy - h2, 2 * w2, t),
            (cx - w2, cy - t / 2, 2 * w2, t),
            (cx - w2, cy + h2 - t, 2 * w2, t),
            (cx - w2, cy - h2, t, h2),
            (cx + w2 - t, cy - h2, t, h2),
            (cx - w2, cy, t, h2),
            (cx + w2 - t, cy, t, h2))
    for sx, sy, w, h in segs:
        add('<rect x="%g" y="%g" width="%g" height="%g" rx="1.2" class="seg"/>'
            % (sx, sy, w, h))
    add('<circle cx="%g" cy="%g" r="2" class="seg"/>' % (cx + w2 + 4, cy + h2 - 2))
    top = ['e', 'd', 'CC', 'c', 'dp']
    bot = ['b', 'a', 'CC', 'f', 'g']
    for i in range(5):
        y = hy(c0 + i)
        add('<line x1="%g" y1="%g" x2="%g" y2="%g" class="pin"/>' % (bx1, y, x1, y))
        add('<circle cx="%g" cy="%g" r="1.5" class="gold"/>' % (x1, y))
        txt(bx1 + 4, y + 2, top[i], 'seglbl', 'middle', rot=True)
    for i in range(5):
        y = hy(c0 + 4 - i)
        add('<line x1="%g" y1="%g" x2="%g" y2="%g" class="pin"/>' % (x2, y, bx2, y))
        add('<circle cx="%g" cy="%g" r="1.5" class="gold"/>' % (x2, y))
        txt(bx2 - 4, y + 2, bot[i], 'seglbl', 'middle', rot=True)
    txt((bx1 + bx2) / 2, by1 - 4, name, 'part')

def buzzer():
    """Modulo buzzer activo MDU1095: PCB chico de 3 terminales."""
    x = hx('A', 'j')
    y1, y2 = hy(12) - 7, hy(14) + 7
    add('<rect x="%g" y="%g" width="15" height="%g" rx="2" class="mod"/>'
        % (x - 7.5, y1, y2 - y1))
    for i in range(3):
        add('<circle cx="%g" cy="%g" r="1.9" class="gold"/>' % (x, hy(12 + i)))
    txt(x - 10, (y1 + y2) / 2, 'BZ1 MDU1095', 'part', 'middle', rot=True)

def module():
    """Modulo MMA7361L sobre adaptador 2x5 que cruza el canal (filas e/f)."""
    x1, x2 = hx('A', 'e'), hx('A', 'f')
    bx1, bx2 = x1 - 8, x2 + 8
    by1, by2 = hy(2) - 7, hy(6) + 7
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="2.5" class="mod"/>'
        % (bx1, by1, bx2 - bx1, by2 - by1))
    add('<rect x="%g" y="%g" width="%g" height="7" rx="1.5" class="modpart"/>'
        % (bx1 + 3, (by1 + by2) / 2 - 3.5, bx2 - bx1 - 6))
    top = ['5V', '3V3', 'GND', 'GS', 'ST']
    bot = ['X', 'Y', 'Z', 'SLP', '0G']
    for i in range(5):
        y = hy(2 + i)
        add('<circle cx="%g" cy="%g" r="1.9" class="gold"/>' % (x1, y))
        txt(x1 - 4, y, top[i], 'modlbl', 'end', rot=True)
        add('<circle cx="%g" cy="%g" r="1.9" class="gold"/>' % (x2, y))
        txt(x2 + 4, y, bot[i], 'modlbl', 'start', rot=True)
    txt((bx1 + bx2) / 2, by1 - 4, 'MOD1 MMA7361L', 'part')
    txt((bx1 + bx2) / 2, by2 + 8, 'J1 abierto', 'note')

def psu_inset():
    """PS1 fuera de las placas: modulo de protoboard HW-131 / MB-102."""
    x1, y1, x2, y2 = 300, 2, 478, 46
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="3" class="psu"/>'
        % (x1, y1, x2 - x1, y2 - y1))
    add('<rect x="%g" y="%g" width="30" height="12" rx="1.5" class="modpart"/>'
        % (x1 + 6, y1 + 5))
    txt(x1 + 42, y1 + 13, 'PS1  HW-131 / MB-102', 'psulbl', 'start')
    txt(x1 + 6, y1 + 26, 'DC-IN 9 V DC  ->  +5V y +3V3', 'psunote', 'start')
    txt(x1 + 6, y1 + 34, 'USB-A: salida 5 V, no entrada', 'psunote', 'start')
    txt(x1 + 6, y1 + 42, 'fuera de las placas', 'psunote', 'start')

# ---------------- documento
add('<svg viewBox="0 0 490 800" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Diseno de protoboard Hand Motion, dos placas de 830 unidas">')
add('<defs><filter id="bs" x="-4%" y="-4%" width="108%" height="108%">'
    '<feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity="0.16"/>'
    '</filter></defs>')

# sombra unica: las dos placas se leen como una sola pieza unida
add('<rect x="18" y="60" width="448" height="680" rx="6" class="shadow"/>')
for b in ('A', 'B'):
    x0 = 18 + BOFF[b]
    add('<rect x="%g" y="60" width="224" height="680" rx="6" class="board"/>' % x0)
    # canal central
    add('<rect x="%g" y="68" width="%g" height="664" rx="4" class="chan"/>'
        % (hx(b, 'e') + 2, ROWX['f'] - ROWX['e'] - 4))

# buses: linea azul partida, banda y 25 agujeros por mitad
RAIL_LAB = {'L5': '+5V', 'R5': '+5V', 'L3': '+3V3', 'LG': 'GND', 'RG': 'GND'}
for b in ('A', 'B'):
    for k, x in RAILX[b].items():
        if k.endswith('5'):
            cls, band = 'rail5', 'band5'
        elif k.endswith('3'):
            cls, band = 'rail3', 'band3'
        else:
            cls, band = 'railg', 'bandg'
        for a, z in ((80, hy(31) + 4), (hy(32) - 4, 720)):
            add('<rect x="%g" y="%g" width="8" height="%g" class="%s"/>'
                % (x - 4, a, z - a, band))
            line(x, a, x, z, cls)
        for c in list(range(7, 32)) + list(range(33, 58)):
            add('<circle cx="%g" cy="%g" r="1.8" class="rhole"/>' % (x, hy(c)))
            add('<circle cx="%g" cy="%g" r="1" class="rholein"/>' % (x, hy(c)))
        txt(x + 3, 96, RAIL_LAB[k], 'raillbl', 'start', rot=True)

# agujeros
for b in ('A', 'B'):
    for r in 'abcdefghij':
        for c in range(1, 64):
            hole(b, r, c)

# letras de fila (arriba/abajo) y numeros de columna (borde exterior)
for b in ('A', 'B'):
    for r in 'abcdefghij':
        txt(hx(b, r), 56, r, 'rowlbl')
        txt(hx(b, r), 752, r, 'rowlbl')
    xn = 10 if b == 'A' else 474
    for c in range(1, 64, 5):
        txt(xn, hy(c) + 2.5, str(c), 'colnum')
    txt(18 + BOFF[b], 780, 'PLACA ' + b, 'boardlbl', 'start')

# ---------------- componentes
dip40()
for nm, c0 in (('DS1', 6), ('DS2', 14), ('DS3', 22)):
    display(nm, c0)

module()
psu_inset()

# --- placa A: sensores, LEDs, buzzer y programacion
to92('A', 'a', 56, 'U4', ['V', 'OUT', 'GND'])
txt(hx('A', 'a') - 7, hy(57) + 2, 'LM35', 'chiplbl', 'middle', rot=True)
cap_v('A', 'c', 56, 58, 'C8')
res_v('A', 'b', 19, 22, 'R23 10k', BANDS['10k'], side=-1)
cap_v('A', 'b', 32, 33, 'C1', side=-1)
cap_v('A', 'h', 30, 31, 'C2', side=-1)
res_v('A', 'i', 50, 53, 'R21 220', BANDS['220'], side=-1)
led_v('A', 'i', 54, 55, 'D1')
res_v('A', 'i', 56, 59, 'R22 220', BANDS['220'], side=-1)
led_v('A', 'i', 60, 61, 'D2')
buzzer()
hdr('A', 'j', 16, 6, 'J2 ICSP', ['1', '2', '3', '4', '5', '6'], side=-1)

# R9-R16: de RD0..RD7 al bus de segmentos (cruzan el canal)
for i in range(8):
    res_h('A', 42 + i, None, BANDS['220'])
txt(hx('A', 'e') + 15, hy(50) + 4, 'R9-R16', 'note')
txt(hx('A', 'e') + 15, hy(51) + 4, '8 x 220', 'note')
# C5-C7: filtros de las salidas X/Y/Z
for nm, c in (('C5', 9), ('C6', 10), ('C7', 11)):
    cap_h('A', c, nm)

# --- placa B: displays, drivers, desacople y USB-TTL
cap_v('B', 'a', 2, 3, 'C9', side=-1)
cap_v('B', 'b', 2, 3, 'C11', 'ecap')
for nm, c1 in (('R17', 30), ('R18', 38), ('R19', 46)):
    res_v('B', 'i', c1, c1 + 3, nm + ' 330', BANDS['330'])
for nm, c1 in (('Q1', 27), ('Q2', 35), ('Q3', 43)):
    to92('B', 'j', c1, nm, ['C', 'B', 'E'])
cap_v('B', 'j', 50, 51, 'C10', 'ecap')
hdr('B', 'j', 52, 5, 'J1 USB-TTL', ['3V3', 'TXD', 'RXD', 'GND', '+5V'])

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
:root{--bg:#fff;--fg:#15181c;--mu:#66707a;--bd:#d3d8de;
--board:#f3f5f1;--chan:#d6dbd4;--hole:#b9bfb9;--holein:#3a3f44;
--railp:#1c6fd1;--railp2:#3d8fe0;--railg:#123f6b;
--chip:#2b2f33;--chiptext:#e8ecef;--edge:#0e1012;
--p5:#1c6fd1;--p3:#3d8fe0;--an:#0e7c86;--dg:#14895a;--pr:#a02f7f;--gnd:#123f6b;
--hl:#ffd54a;--warn:#c47a00}
@media (prefers-color-scheme:dark){:root{--bg:#14171b;--fg:#e9ecef;--mu:#98a1aa;--bd:#333a42;
--board:#20252b;--chan:#181c21;--hole:#5c6672;--holein:#0b0d0f;
--railp:#4a9bf0;--railp2:#7bb8f5;--railg:#2b6fb5;
--chip:#1b1e21;--chiptext:#e9ecef;--edge:#8b949c;
--p5:#4a9bf0;--p3:#7bb8f5;--an:#3fb8c4;--dg:#3fb98a;--pr:#d268ac;--gnd:#2b6fb5;
--hl:#ffd54a;--warn:#f0a23c}}
*{box-sizing:border-box}
body{margin:0;padding:18px 20px 60px;background:var(--bg);color:var(--fg);
font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
h1{font-size:21px;margin:0 0 2px}
h2{font-size:16px;margin:30px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--bd)}
p.sub{margin:0 0 12px;color:var(--mu);font-size:13px;max-width:1100px}
.wrap{display:flex;gap:22px;align-items:flex-start;flex-wrap:wrap}
.dia{flex:0 0 auto;border:1px solid var(--bd);border-radius:10px;padding:6px;background:var(--bg)}
svg{display:block;width:490px;height:800px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12px;margin:6px 0 10px}
.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:0}
.sw.p5{background:var(--p5)}.sw.p3{background:var(--p3)}.sw.gnd{background:var(--gnd)}
.sw.an{background:var(--an)}.sw.dg{background:var(--dg)}.sw.pr{background:var(--pr)}.sw.nc{background:var(--hole)}
.board{fill:var(--board);stroke:#c3c9c3;stroke-width:1}
.shadow{fill:#000;opacity:.18;filter:url(#bs)}
.chan{fill:var(--chan)}
.hole{fill:var(--hole)}
.holein{fill:var(--holein)}
.rhole{fill:#d8ddd8;stroke:#9aa29a;stroke-width:.4}
.rholein{fill:var(--holein)}
.band5{fill:var(--railp);opacity:.14}
.band3{fill:var(--railp2);opacity:.14}
.bandg{fill:var(--railg);opacity:.14}
.rail5{stroke:var(--railp);stroke-width:2.6;stroke-linecap:round}
.rail3{stroke:var(--railp2);stroke-width:2.6;stroke-linecap:round}
.railg{stroke:var(--railg);stroke-width:2.6;stroke-linecap:round}
.raillbl{font:700 7px ui-monospace,monospace;fill:var(--fg)}
.rowlbl{font:700 9px ui-monospace,monospace;fill:#59636c}
.colnum{font:5px ui-monospace,monospace;fill:#59636c}
.boardlbl{font:700 10px ui-monospace,monospace;fill:#59636c;letter-spacing:1px}
.chip{fill:var(--chip);stroke:var(--edge);stroke-width:1}
.chiplbl{font:700 7px ui-monospace,monospace;fill:var(--chiptext)}
.notch{fill:var(--board);stroke:var(--edge);stroke-width:1}
.pin{stroke:#a6adb2;stroke-width:1.2}
.pinpad{fill:#c9a227;opacity:.9}
.pinlbl{font:5px ui-monospace,monospace;fill:#59636c}
.part{font:6.5px ui-monospace,monospace;fill:var(--fg)}
.note{font:5.5px ui-monospace,monospace;fill:var(--mu)}
.seglbl{font:700 4.5px ui-monospace,monospace;fill:#d8e6f5}
.lead{stroke:#8a9298;stroke-width:1}
.res{fill:#e6d8b8;stroke:#8a7a5a;stroke-width:.8}
.band{}
.capdisc{fill:#d98a3a;stroke:#8a4a1a;stroke-width:.8}
.capplate{stroke:#8a4a1a;stroke-width:1.2}
.ecap{fill:#2a4d8a;stroke:#15305a;stroke-width:.8}
.ecapstripe{fill:#e8ecef;opacity:.9}
.ledbody{fill:#d93a3a;stroke:#8a1a1a;stroke-width:.8}
.ledhi{fill:#fff;opacity:.45}
.hdr{fill:#1a1c1f;stroke:#0b0c0e;stroke-width:.8}
.gold{fill:#c9a227}
.to92{fill:#2a2d31;stroke:#0e1012;stroke-width:.8}
.to92face{fill:#3a3e42}
.disp{fill:#1a1c1f;stroke:#0b0c0e;stroke-width:.8}
.dispface{fill:#140b0b}
.displbl{font:700 6.5px ui-monospace,monospace;fill:#e8ecef}
.seg{fill:#4a1212;stroke:#7a2020;stroke-width:.4}
.mod{fill:#1f5fa8;stroke:#123f6b;stroke-width:1}
.modlbl{font:700 4.5px ui-monospace,monospace;fill:#eaf2ff}
.modpart{fill:#15181c;stroke:#000;stroke-width:.5}
.psu{fill:#1f5fa8;stroke:#123f6b;stroke-width:1}
.psulbl{font:700 6.5px ui-monospace,monospace;fill:#eaf2ff}
.psunote{font:5px ui-monospace,monospace;fill:#cfe2ff}
.dash{stroke:var(--pr);stroke-width:.9;stroke-dasharray:3 3;opacity:.75}
.pol{font:700 6px ui-monospace,monospace;fill:#fff}
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
.warn{border-left:3px solid var(--warn);background:color-mix(in srgb,var(--warn) 8%,transparent);
padding:8px 12px;border-radius:0 6px 6px 0;margin:12px 0;max-width:1100px;font-size:13px}
.warn b{color:var(--warn)}
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
<li><b>Placa A</b> (izquierda): PIC U1, MOD1 (MMA7361), R9-R16, LM35, filtros de entrada, LEDs, buzzer e ICSP.</li>
<li><b>Placa B</b> (derecha): los tres displays, Q1-Q3 con R17-R19, desacople y USB-TTL.</li>
<li><b>Las dos placas van pegadas</b>: se encastran por el borde y forman una sola superficie de trabajo.</li>
<li><b>Columnas:</b> los numeros 1-63 estan a la izquierda de cada placa. Cada columna tiene
5 agujeros arriba (a-e) y 5 abajo (f-j), separados por el canal central.</li>
<li><b>PIC:</b> ocupa las columnas 22-41. Las patas 1-20 van en la fila <b>c</b> y las 21-40 en la
fila <b>g</b> (0,6" entre filas). El numero de cada pata esta rotulado junto al agujero.</li>
<li><b>Displays:</b> filas <b>e</b> y <b>f</b> (0,3"), columnas 6-10, 14-18 y 22-26 de la placa B.</li>
<li><b>MMA7361:</b> adaptador 2x5 sobre las filas e y f, columnas 2-6, cruzando el canal.</li>
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
<li><b>Fijar las dos placas</b> encastradas entre si, con el canal central en vertical y los buses
hacia los costados. Quedan como una sola superficie de trabajo.</li>
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
<li><b>LM35</b> en las columnas 56-58 (1=+VS, 2=VOUT, 3=GND) y C8 entre las columnas 56 y 58 de
la fila c.</li>
<li><b>Filtros del sensor:</b> C5, C6 y C7 entre la fila f y la fila e de las columnas 9, 10 y 11.</li>
<li><b>MOD1</b> sobre el adaptador 2x5, con los 10 pines en las filas e y f de las columnas 2 a 6
(cruza el canal). GS y ST a GND, Sleep al pin 3V3 del modulo, 0g sin conectar.</li>
<li><b>Displays</b> en la placa B: DS1 en 6-10, DS2 en 14-18, DS3 en 22-26, con la pata 1 en la
columna menor de la fila e. Unir entre si las dos patas de catodo comun (3 y 8).</li>
<li><b>R9-R16</b> en la placa A, columnas 42 a 49, cruzando el canal (una pata en la fila e
y la otra en la fila f de la misma columna). Quedan al lado de las patas RD0-RD7.</li>
<li><b>Q1-Q3</b> en la fila j (columnas 27, 35 y 43) y R17-R19 en la fila i (30, 38 y 46).</li>
<li><b>LEDs:</b> R21 y D1 en la fila i columnas 50-55; R22 y D2 en 56-61.</li>
<li><b>Buzzer e ICSP</b> en la fila j: BZ1 en 12-14 y J2 en 16-21.</li>
<li><b>Desacople de la placa B:</b> C9 entre las columnas 2 y 3 de la fila a; C11 (10 uF) entre
las columnas 2 y 3 de la fila b; C10 (220 uF) entre las columnas 50 y 51 de la fila j.</li>
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

