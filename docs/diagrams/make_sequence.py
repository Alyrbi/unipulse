"""Builds the UML sequence diagram for collaborative drafting.

One spec -> two outputs (draw.io source + PNG), so they always match.
Event names follow the WebSocket event catalog in report Section 2.4 (#10).
"""
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

W = 1320
LIFELINES = [
    ("a", "Client A\n(Alice, Club Exec)", 110),
    ("b", "Client B\n(Bob, Club Exec)", 330),
    ("ws", "WS Router +\nConnectionManager", 600),
    ("svc", "PostService", 880),
    ("db", "PostgreSQL DB", 1170),
]
X = {k: x for k, _, x in LIFELINES}
TOP, BOX_W, BOX_H = 20, 170, 46
STEP = 30

# (kind, ...) rows.  kind: msg / ret / self / frame_start / frame_else / frame_end / gap
ROWS = [
    ("msg", "a", "ws", "1: WS connect /ws/collaborate/42?token=<jwt>"),
    ("ret", "ws", "a", "2: 101 Switching Protocols"),
    ("msg", "b", "ws", "3: WS connect /ws/collaborate/42?token=<jwt>"),
    ("ret", "ws", "b", "4: 101 Switching Protocols"),
    ("msg", "a", "ws", '5: presence.join {draft_id: "42"}'),
    ("msg", "b", "ws", '6: presence.join {draft_id: "42"}'),
    ("gap",),
    ("msg", "a", "ws", '7: draft.update {base_version: 3, patch: {title: "Hackathon 2026"}}'),
    ("msg", "ws", "svc", "8: apply_patch(draft=42, base_version=3, patch)"),
    ("msg", "svc", "db", "9: UPDATE drafts SET v=4 WHERE id=42 AND version=3"),
    ("ret", "db", "svc", "10: 1 row updated (version = 4)"),
    ("ret", "svc", "ws", "11: saved (version 4)"),
    ("ret", "ws", "a", "12: draft.updated {version: 4, modified_by: alice}"),
    ("ret", "ws", "b", "13: draft.updated {version: 4, modified_by: alice}"),
    ("frame_start", "alt", "[Bob edited at the same time, still on base_version 3]"),
    ("msg", "b", "ws", "14: draft.update {base_version: 3, patch: {content: ...}}"),
    ("msg", "ws", "svc", "15: apply_patch(draft=42, base_version=3, patch)"),
    ("msg", "svc", "db", "16: UPDATE ... WHERE id=42 AND version=3"),
    ("ret", "db", "svc", "17: 0 rows updated (current version is 4)"),
    ("ret", "svc", "ws", "18: VersionConflict(current_version=4)"),
    ("ret", "ws", "b", "19: VERSION_OUTDATED {current_version: 4}"),
    ("self", "b", "20: show conflict dialog, merge v4, resend with base_version 4"),
    ("frame_else", "[database write fails or times out]"),
    ("msg", "b", "ws", "21: draft.update {base_version: 4, patch: {...}}"),
    ("msg", "ws", "svc", "22: apply_patch(draft=42, base_version=4, patch)"),
    ("msg", "svc", "db", "23: UPDATE ... WHERE id=42 AND version=4"),
    ("ret", "db", "svc", "24: error / timeout -> ROLLBACK"),
    ("ret", "svc", "ws", "25: SaveFailed (version stays 4)"),
    ("ret", "ws", "b", '26: draft.save_failed {"Version not bumped."}'),
    ("frame_else", "[Bob's connection drops: no pong for 2 pings (~30 s)]"),
    ("self", "ws", "27: remove Bob's socket from room 42"),
    ("ret", "ws", "a", "28: presence.leave {user_id: bob}"),
    ("frame_end",),
]


def layout():
    y = TOP + BOX_H + 30
    items, frames, stack = [], [], []
    for r in ROWS:
        k = r[0]
        if k == "gap":
            y += 12
            continue
        if k == "frame_start":
            y += 8
            stack.append({"label": r[1], "guards": [(y, r[2])], "y0": y - 4})
            y += 32
            continue
        if k == "frame_else":
            y += 6
            stack[-1]["guards"].append((y, r[1]))
            y += 32
            continue
        if k == "frame_end":
            f = stack.pop()
            f["y1"] = y
            frames.append(f)
            y += 10
            continue
        h = 44 if k == "self" else STEP
        items.append((y + (h - STEP) * 0 + 18, r))
        y += h
    return items, frames, y + 30


def drawio(items, frames, bottom):
    cells, n = [], [2]

    def nid():
        n[0] += 1
        return f"c{n[0]}"

    font = "fontFamily=Times New Roman;fontSize=12;"
    for key, label, x in LIFELINES:
        bid = f"ll_{key}"
        cells.append(
            f'<mxCell id="{bid}" value="{escape(label.replace(chr(10), "<br>"), {chr(34): "&quot;"})}" '
            f'style="rounded=0;whiteSpace=wrap;html=1;fontStyle=1;fillColor=#f5f5f5;strokeColor=#000000;{font}" '
            f'vertex="1" parent="1"><mxGeometry x="{x - BOX_W // 2}" y="{TOP}" width="{BOX_W}" height="{BOX_H}" as="geometry"/></mxCell>'
        )
        cells.append(
            f'<mxCell id="{bid}_line" style="endArrow=none;dashed=1;html=1;strokeColor=#666666;" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x}" y="{TOP + BOX_H}" as="sourcePoint"/>'
            f'<mxPoint x="{x}" y="{bottom}" as="targetPoint"/></mxGeometry></mxCell>'
        )
    for f in frames:
        fx, fw = 40, W - 80
        cells.append(
            f'<mxCell id="{nid()}" value="{f["label"]}" style="shape=umlFrame;whiteSpace=wrap;html=1;width=50;height=22;'
            f'fillColor=none;strokeColor=#000000;fontStyle=1;{font}" vertex="1" parent="1">'
            f'<mxGeometry x="{fx}" y="{f["y0"]}" width="{fw}" height="{f["y1"] - f["y0"]}" as="geometry"/></mxCell>'
        )
        for i, (gy, g) in enumerate(f["guards"]):
            if i > 0:
                cells.append(
                    f'<mxCell id="{nid()}" style="endArrow=none;dashed=1;html=1;strokeColor=#000000;" edge="1" parent="1">'
                    f'<mxGeometry relative="1" as="geometry"><mxPoint x="{fx}" y="{gy - 4}" as="sourcePoint"/>'
                    f'<mxPoint x="{fx + fw}" y="{gy - 4}" as="targetPoint"/></mxGeometry></mxCell>'
                )
            cells.append(
                f'<mxCell id="{nid()}" value="{escape(g)}" style="text;html=1;align=left;fontStyle=2;{font}" vertex="1" parent="1">'
                f'<mxGeometry x="{fx + 60}" y="{gy}" width="600" height="20" as="geometry"/></mxCell>'
            )
    for y, r in items:
        k = r[0]
        if k == "self":
            x = X[r[1]]
            cells.append(
                f'<mxCell id="{nid()}" value="{escape(r[2])}" style="html=1;align=left;spacingLeft=4;endArrow=open;endFill=0;'
                f'verticalAlign=bottom;{font}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                f'<mxPoint x="{x}" y="{y - 8}" as="sourcePoint"/><mxPoint x="{x}" y="{y + 12}" as="targetPoint"/>'
                f'<Array as="points"><mxPoint x="{x + 30}" y="{y - 8}"/><mxPoint x="{x + 30}" y="{y + 12}"/></Array>'
                f"</mxGeometry></mxCell>"
            )
            continue
        s, t, label = X[r[1]], X[r[2]], r[3]
        style = "endArrow=block;endFill=1;" if k == "msg" else "endArrow=open;endFill=0;dashed=1;"
        cells.append(
            f'<mxCell id="{nid()}" value="{escape(label, {chr(34): "&quot;"})}" style="html=1;verticalAlign=bottom;{style}{font}" '
            f'edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{s}" y="{y}" as="sourcePoint"/>'
            f'<mxPoint x="{t}" y="{y}" as="targetPoint"/></mxGeometry></mxCell>'
        )
    body = "".join(cells)
    model = (
        f'<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
        f'fold="1" page="1" pageScale="1" pageWidth="{W}" pageHeight="{bottom + 20}"><root><mxCell id="0"/>'
        f'<mxCell id="1" parent="0"/>{body}</root></mxGraphModel>'
    )
    return model


def png(items, frames, bottom, path):
    scale = 100
    fig = plt.figure(figsize=(W / scale, (bottom + 10) / scale), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(bottom + 10, 0)
    ax.axis("off")
    fam = "DejaVu Serif"
    for _, label, x in LIFELINES:
        ax.add_patch(Rectangle((x - BOX_W / 2, TOP), BOX_W, BOX_H, fc="#f5f5f5", ec="black", lw=1))
        ax.text(x, TOP + BOX_H / 2, label, ha="center", va="center", fontsize=8.5, weight="bold", family=fam)
        ax.plot([x, x], [TOP + BOX_H, bottom], ls=(0, (4, 3)), color="#666666", lw=0.8)
    for f in frames:
        fx, fw = 40, W - 80
        ax.add_patch(Rectangle((fx, f["y0"]), fw, f["y1"] - f["y0"], fc="none", ec="black", lw=1))
        ax.add_patch(Rectangle((fx, f["y0"]), 50, 22, fc="white", ec="black", lw=1))
        ax.text(fx + 25, f["y0"] + 11, f["label"], ha="center", va="center", fontsize=8, weight="bold", family=fam)
        for i, (gy, g) in enumerate(f["guards"]):
            if i > 0:
                ax.plot([fx, fx + fw], [gy - 4, gy - 4], ls=(0, (5, 3)), color="black", lw=0.8)
            ax.text(fx + 60, gy + 10, g, ha="left", va="center", fontsize=8, style="italic", family=fam)
    for y, r in items:
        k = r[0]
        if k == "self":
            x = X[r[1]]
            ax.plot([x, x + 30, x + 30], [y - 8, y - 8, y + 12], color="black", lw=0.9)
            ax.add_patch(FancyArrowPatch((x + 30, y + 12), (x, y + 12), arrowstyle="->", mutation_scale=9, lw=0.9))
            ax.text(x + 36, y + 2, r[2], ha="left", va="center", fontsize=7.6, family=fam)
            continue
        s, t, label = X[r[1]], X[r[2]], r[3]
        if k == "msg":
            ax.add_patch(FancyArrowPatch((s, y), (t, y), arrowstyle="-|>", mutation_scale=10, lw=0.9, color="black"))
        else:
            ax.add_patch(
                FancyArrowPatch((s, y), (t, y), arrowstyle="->", mutation_scale=10, lw=0.9, color="black", ls=(0, (4, 3)))
            )
        ax.text((s + t) / 2, y - 3, label, ha="center", va="bottom", fontsize=7.6, family=fam)
    fig.savefig(path, facecolor="white")


if __name__ == "__main__":
    import sys

    out = sys.argv[1]
    items, frames, bottom = layout()
    model = drawio(items, frames, bottom)
    open(f"{out}/sequence_page.xml", "w").write(model)
    png(items, frames, bottom, f"{out}/sequence.png")
    print("height", bottom)
