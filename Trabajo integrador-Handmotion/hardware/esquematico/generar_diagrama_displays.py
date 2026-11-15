"""Genera diagrama-displays.html con el conexionado pin por pin de DS1-DS3.

Mismo formato que hardware/protoboard/protoboard.html: HTML autocontenido,
tema claro/oscuro, SVG interactivo, leyenda de redes y tablas con resaltado.

Fuente de verdad: hardware/esquematico/conexiones.txt (redes y patillaje) y
firmware/src/modules/display.inc (RD0-RD7 segmentos activos en alto; RC0-RC2
seleccionan el digito).
"""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).with_name("diagrama-displays.html")

# (segmento, pata fisica, resistencia, pin PIC, numero de pin PIC)
SEGMENTS = [
    ("a", 7, "R9", "RD0", 19),
    ("b", 6, "R10", "RD1", 20),
    ("c", 4, "R11", "RD2", 21),
    ("d", 2, "R12", "RD3", 22),
    ("e", 1, "R13", "RD4", 27),
    ("f", 9, "R14", "RD5", 28),
    ("g", 10, "R15", "RD6", 29),
    ("dp", 5, "R16", "RD7", 30),
]

# (display, funcion, transistor, resistencia de base, pin PIC, numero)
DISPLAYS = [
    ("DS1", "decenas", "Q1", "R17", "RC0", 15),
    ("DS2", "unidades", "Q2", "R18", "RC1", 16),
    ("DS3", "C", "Q3", "R19", "RC2", 17),
]

NET_CLASS = {
    "SEG_A": "n-a",
    "SEG_B": "n-b",
    "SEG_C": "n-c",
    "SEG_D": "n-d",
    "SEG_E": "n-e",
    "SEG_F": "n-f",
    "SEG_G": "n-g",
    "SEG_DP": "n-dp",
    "CC": "n-cc",
    "DIG": "n-dig",
}


def net_for(segment: str) -> str:
    return "SEG_DP" if segment == "dp" else f"SEG_{segment.upper()}"


def net_class(net: str) -> str:
    if net.endswith("_CC"):
        return NET_CLASS["CC"]
    if net.startswith("DIG"):
        return NET_CLASS["DIG"]
    return NET_CLASS[net]


def display_svg(ds: str, cc_net: str) -> str:
    xs = [160, 212, 264, 316, 368]
    top = [(1, "e"), (2, "d"), (3, "CC"), (4, "c"), (5, "dp")]
    bottom = [(6, "b"), (7, "a"), (8, "CC"), (9, "f"), (10, "g")]

    p: list[str] = [
        f'<svg viewBox="0 0 560 360" role="img" '
        f'aria-label="Conexionado pin por pin de {ds}">'
    ]
    p.append('<rect x="150" y="80" width="260" height="170" rx="10" class="disp"/>')
    p.append('<rect x="158" y="88" width="244" height="154" rx="7" class="dispface"/>')

    segments = [
        (190, 100, 370, 100),
        (175, 115, 175, 160),
        (385, 115, 385, 160),
        (190, 168, 370, 168),
        (175, 180, 175, 225),
        (385, 180, 385, 225),
        (190, 235, 370, 235),
    ]
    for x1, y1, x2, y2 in segments:
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="seg"/>')
    p.append('<circle cx="400" cy="235" r="5" class="segdot"/>')

    p.append('<g class="wires">')
    for index, (number, segment) in enumerate(top):
        x = xs[index]
        net = cc_net if segment == "CC" else net_for(segment)
        p.append(
            f'<line x1="{x}" y1="30" x2="{x}" y2="54" '
            f'class="wire {net_class(net)}" data-net="{net}"/>'
        )
    for index, (number, segment) in enumerate(bottom):
        x = xs[index]
        net = cc_net if segment == "CC" else net_for(segment)
        p.append(
            f'<line x1="{x}" y1="276" x2="{x}" y2="304" '
            f'class="wire {net_class(net)}" data-net="{net}"/>'
        )
    p.append("</g>")

    for index, (number, segment) in enumerate(top):
        x = xs[index]
        net = cc_net if segment == "CC" else net_for(segment)
        cls = net_class(net)
        p.append(f'<rect x="{x - 6}" y="54" width="12" height="26" class="pin"/>')
        p.append(f'<circle cx="{x}" cy="80" r="1.8" class="gold"/>')
        p.append(
            f'<text x="{x + 10}" y="68" class="pinlbl">{number}&middot;{segment}</text>'
        )
        p.append(
            f'<rect x="{x - 25}" y="6" width="50" height="24" rx="5" '
            f'class="netchip {cls}" data-net="{net}"/>'
        )
        p.append(
            f'<text x="{x}" y="22" class="nettxt {cls}" data-net="{net}">{net}</text>'
        )

    for index, (number, segment) in enumerate(bottom):
        x = xs[index]
        net = cc_net if segment == "CC" else net_for(segment)
        cls = net_class(net)
        p.append(f'<rect x="{x - 6}" y="250" width="12" height="26" class="pin"/>')
        p.append(f'<circle cx="{x}" cy="250" r="1.8" class="gold"/>')
        p.append(
            f'<text x="{x + 10}" y="292" class="pinlbl">{number}&middot;{segment}</text>'
        )
        p.append(
            f'<rect x="{x - 25}" y="304" width="50" height="24" rx="5" '
            f'class="netchip {cls}" data-net="{net}"/>'
        )
        p.append(
            f'<text x="{x}" y="320" class="nettxt {cls}" data-net="{net}">{net}</text>'
        )

    p.append("</svg>")
    return "".join(p)


def display_table(ds: str, q: str) -> str:
    cc_net = f"{ds}_CC"
    by_pin = {item[1]: item for item in SEGMENTS}
    rows = []
    for number in range(1, 11):
        if number in (3, 8):
            rows.append(
                f'<tr data-net="{cc_net}"><td class="nm">{number}</td><td>CC</td>'
                f"<td><code>{cc_net}</code></td><td>&mdash;</td>"
                f"<td>{q} colector (pata 1)</td></tr>"
            )
            continue
        segment, _, resistor, pic, pic_pin = by_pin[number]
        net = net_for(segment)
        rows.append(
            f'<tr data-net="{net}"><td class="nm">{number}</td><td>{segment}</td>'
            f"<td><code>{net}</code></td><td>{resistor} &middot; 220 &Omega;</td>"
            f"<td>{pic} (pin {pic_pin})</td></tr>"
        )
    body = "\n".join(rows)
    return (
        "<table><thead><tr><th>Pata</th><th>Segmento</th><th>Red</th>"
        "<th>Resistencia</th><th>Pin PIC</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def transistor_table(ds: str, q: str, rb: str, rcx: str, rcx_pin: int) -> str:
    dig = f"DIG{ds[-1]}"
    return (
        "<table><thead><tr><th>Elemento</th><th>Conexion</th></tr></thead><tbody>"
        f'<tr data-net="{dig}"><td>{rcx} (pin {rcx_pin})</td>'
        f"<td>{rb}.1 &mdash; extremo de entrada</td></tr>"
        f'<tr data-net="{dig}"><td>{rb} &middot; 330 &Omega;</td>'
        f"<td>{rcx} (pin {rcx_pin}) &rarr; base {q}</td></tr>"
        f'<tr data-net="{dig}"><td>{q} base (pata 2)</td><td>{rb}.2</td></tr>'
        f'<tr data-net="{ds}_CC"><td>{q} colector (pata 1)</td>'
        f"<td>{ds} patas 3 y 8 (catodo comun)</td></tr>"
        f"<tr><td>{q} emisor (pata 3)</td><td>GND</td></tr>"
        "</tbody></table>"
    )


def bc337_svg() -> str:
    return """
<svg viewBox="0 0 240 210" role="img" aria-label="Patillaje fisico del BC337">
  <text x="120" y="16" class="note" text-anchor="middle">Cara plana al observador</text>
  <rect x="80" y="34" width="80" height="98" rx="8" class="to92"/>
  <rect x="86" y="40" width="68" height="6" rx="2" class="to92face"/>
  <text x="120" y="92" class="modlbl" text-anchor="middle">BC337</text>
  <line x1="100" y1="132" x2="100" y2="172" class="pin"/>
  <line x1="120" y1="132" x2="120" y2="172" class="pin"/>
  <line x1="140" y1="132" x2="140" y2="172" class="pin"/>
  <circle cx="100" cy="172" r="1.8" class="gold"/>
  <circle cx="120" cy="172" r="1.8" class="gold"/>
  <circle cx="140" cy="172" r="1.8" class="gold"/>
  <text x="100" y="192" class="pinlbl" text-anchor="middle">1 &middot; C</text>
  <text x="120" y="192" class="pinlbl" text-anchor="middle">2 &middot; B</text>
  <text x="140" y="192" class="pinlbl" text-anchor="middle">3 &middot; E</text>
</svg>"""


def overview_svg() -> str:
    p = [
        '<svg viewBox="0 0 1200 500" role="img" '
        'aria-label="Vista general del conexionado de displays">'
    ]

    # PIC
    p.append('<rect x="30" y="50" width="160" height="360" rx="8" class="chipbox"/>')
    p.append('<text x="110" y="70" class="tlabel" text-anchor="middle">U1</text>')
    p.append('<text x="110" y="84" class="sublabel" text-anchor="middle">PIC16F887</text>')
    rd = [
        (19, "RD0", 120), (20, "RD1", 140), (21, "RD2", 160), (22, "RD3", 180),
        (27, "RD4", 200), (28, "RD5", 220), (29, "RD6", 240), (30, "RD7", 260),
    ]
    rc = [(15, "RC0", 330), (16, "RC1", 350), (17, "RC2", 370)]
    for pin, name, y in rd + rc:
        p.append(f'<text x="180" y="{y + 3}" class="sublabel" text-anchor="end">{name} {pin}</text>')
        p.append(f'<line x1="190" y1="{y}" x2="220" y2="{y}" class="rail"/>')
    p.append('<text x="180" y="403" class="sublabel" text-anchor="end">GND 12/31</text>')

    # Resistencias de segmento y de base
    for index, (segment, _, resistor, _, _) in enumerate(SEGMENTS):
        y = 120 + index * 20
        p.append(f'<rect x="220" y="{y - 5}" width="50" height="10" rx="2" class="res"/>')
        p.append(f'<text x="245" y="{y + 2.5}" class="reslbl" text-anchor="middle">{resistor} 220</text>')
    for index, (ds, _, q, rb, _, _) in enumerate(DISPLAYS):
        y = 330 + index * 20
        p.append(f'<rect x="220" y="{y - 5}" width="50" height="10" rx="2" class="res"/>')
        p.append(f'<text x="245" y="{y + 2.5}" class="reslbl" text-anchor="middle">{rb} 330</text>')

    # Chips de red del lado PIC
    for index, (segment, _, _, _, _) in enumerate(SEGMENTS):
        y = 120 + index * 20
        net = net_for(segment)
        p.append(f'<line x1="270" y1="{y}" x2="290" y2="{y}" class="rail"/>')
        p.append(
            f'<rect x="290" y="{y - 9}" width="80" height="18" rx="4" '
            f'class="netchip {net_class(net)}" data-net="{net}"/>'
        )
        p.append(
            f'<text x="330" y="{y + 3.5}" class="nettxt {net_class(net)}" '
            f'data-net="{net}">{net}</text>'
        )
    for index, (ds, _, _, _, _, _) in enumerate(DISPLAYS):
        y = 330 + index * 20
        net = f"DIG{ds[-1]}"
        p.append(f'<line x1="270" y1="{y}" x2="290" y2="{y}" class="rail"/>')
        p.append(
            f'<rect x="290" y="{y - 9}" width="80" height="18" rx="4" '
            f'class="netchip {net_class(net)}" data-net="{net}"/>'
        )
        p.append(
            f'<text x="330" y="{y + 3.5}" class="nettxt {net_class(net)}" '
            f'data-net="{net}">{net}</text>'
        )

    # Bus de segmentos
    p.append('<rect x="400" y="110" width="60" height="160" rx="8" class="bus"/>')
    p.append('<text x="430" y="190" class="buslbl" text-anchor="middle" '
             'transform="rotate(-90 430 190)">BUS 8 LINEAS</text>')
    for index in range(8):
        y = 120 + index * 20
        p.append(f'<line x1="370" y1="{y}" x2="400" y2="{y}" class="rail"/>')

    # Reparto del bus a los tres displays
    p.append('<path d="M430 110 L430 40 L1040 40" class="rail"/>')
    p.append('<circle cx="430" cy="40" r="2.5" class="dot"/>')
    for x in (600, 820, 1040):
        p.append(f'<path d="M{x} 40 L{x} 80" class="rail"/>')
        p.append(f'<circle cx="{x}" cy="40" r="2.5" class="dot"/>')
    p.append('<text x="700" y="32" class="sublabel" text-anchor="middle">'
             '8 segmentos compartidos por los tres displays</text>')

    # Displays y transistores
    for index, (ds, role, q, rb, rcx, rcx_pin) in enumerate(DISPLAYS):
        x = 520 + index * 220
        p.append(f'<rect x="{x}" y="80" width="160" height="180" rx="8" class="block"/>')
        p.append(f'<rect x="{x + 10}" y="95" width="50" height="60" rx="4" class="disp"/>')
        p.append(f'<text x="{x + 35}" y="140" class="digit8">8</text>')
        p.append(f'<text x="{x + 70}" y="110" class="tlabel">{ds}</text>')
        p.append(f'<text x="{x + 70}" y="124" class="sublabel">{role}</text>')
        p.append(f'<text x="{x + 70}" y="145" class="sublabel">8 segmentos</text>')
        p.append(f'<text x="{x + 70}" y="159" class="sublabel">CC: patas 3+8</text>')

        p.append(f'<line x1="{x + 80}" y1="260" x2="{x + 80}" y2="320" class="rail"/>')
        p.append(f'<text x="{x + 86}" y="294" class="sublabel">CC</text>')

        p.append(f'<rect x="{x}" y="320" width="160" height="120" rx="8" class="block"/>')
        p.append(f'<text x="{x + 10}" y="340" class="tlabel">{q} &middot; BC337</text>')
        p.append(f'<text x="{x + 10}" y="360" class="sublabel">'
                 f'B &larr; {rb} 330 &Omega; &larr; {rcx} {rcx_pin}</text>')
        p.append(f'<text x="{x + 10}" y="378" class="sublabel">'
                 f'C &rarr; {ds} patas 3+8</text>')
        p.append(f'<text x="{x + 10}" y="396" class="sublabel">E &rarr; GND</text>')
        net = f"DIG{ds[-1]}"
        p.append(
            f'<rect x="{x + 10}" y="405" width="70" height="18" rx="4" '
            f'class="netchip {net_class(net)}" data-net="{net}"/>'
        )
        p.append(
            f'<text x="{x + 45}" y="418.5" class="nettxt {net_class(net)}" '
            f'data-net="{net}">{net}</text>'
        )

    p.append("</svg>")
    return "".join(p)


CSS = """
:root{--bg:#f6f7f9;--fg:#1b1e21;--mu:#5b6570;--bd:#d7dce2;--card:#ffffff;
--disp:#1a1c1f;--dispface:#140b0b;--edge:#8b949c;--pin:#a6adb2;--gold:#c9a227;
--hl:#ffb300;--warn:#b06a00;--sel:#fff2cc;
--seg-a:#d92d3a;--seg-b:#d97a1a;--seg-c:#a98600;--seg-d:#1f8a5b;
--seg-e:#1a8fa0;--seg-f:#2f6fd0;--seg-g:#7a5bd6;--seg-dp:#c24a86;
--cc:#6b7480;--dig:#b04f8e;--seg:#8e1f1f;--segline:#c23a3a}
@media (prefers-color-scheme:dark){:root{--bg:#14171b;--fg:#e9ecef;--mu:#98a1aa;
--bd:#333a42;--card:#1b1f24;--hl:#ffd54a;--warn:#f0a23c;--sel:#3a3520;
--seg-a:#ff6b6b;--seg-b:#ffa94d;--seg-c:#ffd43b;--seg-d:#51cf66;
--seg-e:#3bc9db;--seg-f:#74a8ff;--seg-g:#b197fc;--seg-dp:#f783ac;
--cc:#9aa4ae;--dig:#e07ab8;--seg:#8e1f1f;--segline:#d9534f}}
*{box-sizing:border-box}
body{margin:0;padding:18px 20px 60px;background:var(--bg);color:var(--fg);
font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
h1{font-size:21px;margin:0 0 2px}
h2{font-size:16px;margin:30px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--bd)}
p.sub{margin:0 0 12px;color:var(--mu);font-size:13px;max-width:1100px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12px;margin:6px 0 12px}
.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.wrap{display:flex;gap:22px;align-items:flex-start;flex-wrap:wrap}
.dia{flex:0 0 auto;border:1px solid var(--bd);border-radius:10px;padding:10px;background:var(--card)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:18px}
.card{border:1px solid var(--bd);border-radius:10px;padding:14px;background:var(--card)}
.card h3{margin:0 0 2px;font-size:15px}
.card .sub{margin:0 0 8px}
.disp{fill:var(--disp);stroke:#0b0c0e;stroke-width:1.4}
.dispface{fill:var(--dispface)}
.seg{stroke:var(--segline);stroke-width:6;stroke-linecap:round;opacity:.95}
.segdot{fill:var(--segline)}
.pin{fill:var(--pin);stroke:#475569;stroke-width:.8}
.gold{fill:var(--gold)}
.pinlbl{font:600 10px ui-monospace,monospace;fill:var(--fg)}
.note{font:11px ui-monospace,monospace;fill:var(--mu)}
.modlbl{font:700 12px ui-monospace,monospace;fill:#eaf2ff}
.to92{fill:#2a2d31;stroke:#0e1012;stroke-width:.8}
.to92face{fill:#3a3e42}
.chipbox{fill:var(--card);stroke:var(--bd);stroke-width:1.2}
.tlabel{font:700 10px ui-monospace,monospace;fill:var(--fg)}
.sublabel{font:8.5px ui-monospace,monospace;fill:var(--mu)}
.res{fill:#e6d8b8;stroke:#8a7a5a;stroke-width:.8}
.reslbl{font:700 7px ui-monospace,monospace;fill:#3a2f1a}
.bus{fill:var(--mu);fill-opacity:.12;stroke:var(--mu);stroke-width:1}
.buslbl{font:700 9px ui-monospace,monospace;fill:var(--mu)}
.rail{stroke:var(--mu);stroke-width:1.4;fill:none}
.dot{fill:var(--mu)}
.digit8{font:700 34px ui-monospace,monospace;fill:var(--segline);text-anchor:middle}
.block{fill:var(--card);stroke:var(--bd);stroke-width:1.2}
.netchip{fill:var(--net);fill-opacity:.16;stroke:var(--net);stroke-width:1}
.nettxt{font:700 9px ui-monospace,monospace;fill:var(--net);text-anchor:middle}
.n-a{--net:var(--seg-a)}.n-b{--net:var(--seg-b)}.n-c{--net:var(--seg-c)}
.n-d{--net:var(--seg-d)}.n-e{--net:var(--seg-e)}.n-f{--net:var(--seg-f)}
.n-g{--net:var(--seg-g)}.n-dp{--net:var(--seg-dp)}.n-cc{--net:var(--cc)}
.n-dig{--net:var(--dig)}
.wire{stroke:var(--net,var(--mu));stroke-width:1.3;stroke-linecap:round}
.wires.hidden{display:none}
[data-net]{cursor:pointer}
.netchip.hl{fill-opacity:.55;stroke-width:2.4}
.nettxt.hl{font-weight:800}
.wire.hl{stroke:var(--hl);stroke-width:3}
table{border-collapse:collapse;font-size:12.5px;width:100%}
th,td{border-bottom:1px solid var(--bd);padding:5px 8px;text-align:left;vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:var(--mu)}
tbody tr[data-net]:hover{background:color-mix(in srgb,var(--hl) 18%,transparent)}
td.nm{white-space:nowrap;font-family:ui-monospace,monospace;font-weight:600}
code{font:11.5px ui-monospace,monospace;background:color-mix(in srgb,var(--mu) 14%,transparent);
padding:1px 4px;border-radius:3px}
.ctr{display:flex;gap:16px;align-items:center;font-size:13px;margin:10px 0 0;flex-wrap:wrap}
.ctr label{display:flex;gap:6px;align-items:center;cursor:pointer}
.selinfo{font:600 12px ui-monospace,monospace;color:var(--fg);
background:color-mix(in srgb,var(--hl) 35%,transparent);padding:2px 8px;border-radius:4px}
.selinfo:empty{display:none}
ol,ul{max-width:1100px;padding-left:22px}
li{margin:4px 0}
.warn{border-left:3px solid var(--warn);background:color-mix(in srgb,var(--warn) 8%,transparent);
padding:8px 12px;border-radius:0 6px 6px 0;margin:12px 0;max-width:1100px;font-size:13px}
.warn b{color:var(--warn)}
.flow{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0 4px;font-size:12.5px}
.flow .b{border:1px solid var(--bd);border-radius:8px;padding:6px 10px;background:var(--card)}
.flow .b b{display:block;font-size:12.5px}
.flow .a{color:var(--mu);font-size:17px}
footer{color:var(--mu);font-size:12px;margin-top:34px;border-top:1px solid var(--bd);padding-top:10px}
"""

JS = """
const all=[...document.querySelectorAll('[data-net]')];
const info=document.getElementById('selinfo');
let pinned=null;
function apply(net,on){all.forEach(e=>{if(e.dataset.net===net)e.classList.toggle('hl',on)})}
all.forEach(e=>{
 e.addEventListener('mouseenter',()=>apply(e.dataset.net,true));
 e.addEventListener('mouseleave',()=>{if(pinned!==e.dataset.net)apply(e.dataset.net,false)});
 e.addEventListener('click',ev=>{
  ev.stopPropagation();
  if(pinned===e.dataset.net){pinned=null;apply(e.dataset.net,false);info.textContent='';return}
  all.forEach(x=>x.classList.remove('hl'));
  pinned=e.dataset.net;apply(pinned,true);
  info.textContent='Red '+pinned;
 });
});
document.addEventListener('click',()=>{if(pinned){apply(pinned,false);pinned=null;info.textContent=''}});
document.querySelectorAll('.wchk').forEach(chk=>{
 const card=chk.closest('.card');
 const wires=card.querySelectorAll('.wires');
 chk.addEventListener('change',()=>wires.forEach(g=>g.classList.toggle('hidden',!chk.checked)));
});
"""

HTML = """<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hand Motion - Conexionado de displays</title><style>@@CSS@@</style></head><body>
<h1>Hand Motion &middot; conexionado de displays</h1>
<p class="sub">DS1, DS2 y DS3 son displays de 7 segmentos de catodo comun. Los segmentos
salen de RD0-RD7 por R9-R16 (220 &Omega;) y son compartidos por los tres displays.
RC0-RC2 seleccionan el digito con Q1-Q3 (BC337) por R17-R19 (330 &Omega;).
Pasa el mouse por una red o por una fila de la tabla para resaltarla; un clic la fija.</p>

<div class="legend">
<span><i style="background:var(--seg-a)"></i>SEG_A</span>
<span><i style="background:var(--seg-b)"></i>SEG_B</span>
<span><i style="background:var(--seg-c)"></i>SEG_C</span>
<span><i style="background:var(--seg-d)"></i>SEG_D</span>
<span><i style="background:var(--seg-e)"></i>SEG_E</span>
<span><i style="background:var(--seg-f)"></i>SEG_F</span>
<span><i style="background:var(--seg-g)"></i>SEG_G</span>
<span><i style="background:var(--seg-dp)"></i>SEG_DP</span>
<span><i style="background:var(--cc)"></i>catodo comun</span>
<span><i style="background:var(--dig)"></i>seleccion de digito</span>
<span id="selinfo" class="selinfo"></span>
</div>

<h2>Vista general</h2>
<div class="dia" style="display:block;max-width:1200px">@@OVERVIEW@@</div>

<div class="warn"><b>Antes de soldar:</b> el patillaje de los displays es el
<b>adoptado por documento</b> (1 e, 2 d, 3 CC, 4 c, 5 dp, 6 b, 7 a, 8 CC, 9 f, 10 g).
Contrastalo con el datasheet del display o con el multimetro en modo diodo. Proba
primero un solo display y un solo segmento. Las patas 3 y 8 son el mismo nodo.</div>

<h2>Detalle pin por pin</h2>
<div class="grid">
@@CARDS@@
</div>

<h2>Tabla maestra de redes</h2>
<div class="dia" style="display:block;max-width:1100px">
<table><thead><tr><th>Red</th><th>Resistencia</th><th>Origen</th><th>Destino</th></tr></thead>
<tbody>@@MASTER@@</tbody></table>
<p class="sub" style="margin:8px 0 0">Cada salida de R9-R16 alimenta el mismo segmento
en los tres displays: es un nodo compartido de tres patas. No hay resistencia en el
catodo comun; la corriente la maneja el transistor.</p>
</div>

<h2>Orden de armado</h2>
<div class="card">
<ol>
<li>Identifica en cada display las patas 3 y 8 (catodo comun) y verifica cada segmento
con el multimetro en modo diodo.</li>
<li>Une las patas 3 y 8 de DS1 entre si; lo mismo en DS2 y DS3. No las unas entre
displays distintos.</li>
<li>Monta R9-R16 (220 &Omega;) desde RD0-RD7 del PIC.</li>
<li>Lleva la salida de cada resistencia al mismo segmento de los tres displays
(redes SEG_A &hellip; SEG_DP).</li>
<li>Monta Q1-Q3 con R17-R19 (330 &Omega;) en la base.</li>
<li>Colector de Q1 &rarr; patas 3+8 de DS1; Q2 &rarr; DS2; Q3 &rarr; DS3.</li>
<li>Emisores de Q1-Q3 &rarr; GND comun.</li>
<li>Verifica continuidad y que no haya cortos entre segmentos vecinos.</li>
<li>Alimenta y prueba: DS1 decenas, DS2 unidades, DS3 letra C.</li>
</ol>
</div>

<h2>Verificacion</h2>
<div class="card">
<ul>
<li><b>Sin alimentacion:</b> continuidad entre pata 3 y pata 8 de cada display.</li>
<li><b>Sin alimentacion:</b> cada pata de segmento debe llegar a una sola resistencia
y a las tres patas equivalentes de los displays.</li>
<li><b>Con alimentacion:</b> RCx en alto debe encender el display correspondiente;
RCx en bajo lo apaga.</li>
<li><b>BC337:</b> cara plana al observador y patas hacia abajo = 1 C, 2 B, 3 E.
No invertir colector y emisor.</li>
<li><b>Corriente:</b> 220 &Omega; y 330 &Omega; son valores adoptados, no medidos.
Confirma Vf, VOH, brillo y saturacion en banco.</li>
</ul>
</div>

<footer>Fuente: <code>hardware/esquematico/conexiones.txt</code> (redes y patillaje) y
<code>firmware/src/modules/display.inc</code> (segmentos activos en alto, RC0-RC2
seleccionan el digito). Generado por
<code>hardware/esquematico/generar_diagrama_displays.py</code>.</footer>
<script>@@JS@@</script></body></html>"""


def build() -> str:
    cards = []
    for ds, role, q, rb, rcx, rcx_pin in DISPLAYS:
        cc_net = f"{ds}_CC"
        cards.append(
            f"""<section class="card">
  <h3>{ds} &middot; {role}</h3>
  <p class="sub">Patas 3 y 8 = catodo comun; se unen entre si y van al colector de {q}.</p>
  <div class="dia" style="padding:6px">{display_svg(ds, cc_net)}
    <div class="ctr"><label><input type="checkbox" class="wchk" checked> Mostrar conexiones</label>
    </div>
  </div>
  {display_table(ds, q)}
  <h3 style="margin-top:14px">{q} &middot; selector de {ds}</h3>
  <div style="display:grid;grid-template-columns:minmax(0,1fr) 200px;gap:12px;align-items:start">
    <div>{transistor_table(ds, q, rb, rcx, rcx_pin)}</div>
    <div>{bc337_svg()}</div>
  </div>
</section>"""
        )

    master_rows = []
    for segment, pin, resistor, pic, pic_pin in SEGMENTS:
        net = net_for(segment)
        master_rows.append(
            f'<tr data-net="{net}"><td class="nm">{net}</td>'
            f"<td>{resistor} &middot; 220 &Omega;</td>"
            f"<td>{pic} (pin {pic_pin})</td>"
            f"<td>DS1.{pin} &middot; DS2.{pin} &middot; DS3.{pin}</td></tr>"
        )
    for ds, _, q, rb, rcx, rcx_pin in DISPLAYS:
        master_rows.append(
            f'<tr data-net="{ds}_CC"><td class="nm">{ds}_CC</td><td>&mdash;</td>'
            f"<td>{q} colector (pata 1)</td><td>{ds} patas 3 y 8</td></tr>"
        )
        master_rows.append(
            f'<tr data-net="DIG{ds[-1]}"><td class="nm">DIG{ds[-1]}</td>'
            f"<td>{rb} &middot; 330 &Omega;</td>"
            f"<td>{rcx} (pin {rcx_pin})</td><td>{q} base (pata 2)</td></tr>"
        )

    html = HTML.replace("@@CSS@@", CSS)
    html = html.replace("@@OVERVIEW@@", overview_svg())
    html = html.replace("@@CARDS@@", "".join(cards))
    html = html.replace("@@MASTER@@", "".join(master_rows))
    html = html.replace("@@JS@@", JS)
    return html


def main() -> None:
    OUT.write_text(build(), encoding="utf-8")
    print(f"Escrito: {OUT}")


if __name__ == "__main__":
    main()
