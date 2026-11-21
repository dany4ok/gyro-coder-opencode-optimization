#!/usr/bin/env python3
"""Deterministic atlas/spritesheet frame check. No AI, no guessing.

Measures, for every cell: empty or not, silhouette bounding box, pixel area and
mean colour of the largest foreground component. Then flags empty frames,
abnormal height/area differences between frames and palette drift.

Exit code 0 = PASS, 1 = FAIL (a confirmed visual defect), 2 = bad input.

Example:
  python check_atlas_frames.py sprites/atlas_player.png --cols 4 --rows 2
"""

import argparse
import json
import os
import statistics
import sys

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError as exc:
    print("LIPSA DEPENDENTA: %s (need opencv-python, numpy, Pillow)" % exc)
    sys.exit(2)


def analyse_cell(arr, row, col, cw, ch, index, color_tol):
    """Return measurement dict for one grid cell."""
    inset = 3  # drop grid lines / borders
    cc = arr[row * ch + inset: (row + 1) * ch - inset,
             col * cw + inset: (col + 1) * cw - inset]
    if cc.size == 0:
        return {"index": index, "row": row, "col": col, "empty": True,
                "reason": "cell too small after inset"}

    rgb = cc[:, :, :3].astype(np.int16)
    alpha = cc[:, :, 3]
    opaque = cc.reshape(-1, 4)
    opaque = opaque[opaque[:, 3] >= 250]
    if opaque.shape[0] == 0:
        return {"index": index, "row": row, "col": col, "empty": True,
                "reason": "no opaque pixels"}

    # Background = dominant quantised colour of the cell.
    q = (opaque[:, :3] // 16 * 16).astype(np.uint8)
    colors, counts = np.unique(q, axis=0, return_counts=True)
    bg = colors[int(np.argmax(counts))].astype(np.int16)

    diff = np.abs(rgb - bg).max(axis=2)
    fg = ((diff > color_tol) & (alpha >= 250)).astype(np.uint8)

    # Keep the largest connected component (the character). Small label text,
    # specks and loose particles are ignored on purpose.
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    if n <= 1:
        return {"index": index, "row": row, "col": col, "empty": True,
                "reason": "no foreground component"}
    sizes = stats[1:, cv2.CC_STAT_AREA]
    k = 1 + int(np.argmax(sizes))
    ys, xs = np.where(labels == k)
    if xs.size == 0:
        return {"index": index, "row": row, "col": col, "empty": True,
                "reason": "empty largest component"}

    mean_rgb = rgb[labels == k].mean(axis=0).round(1).tolist()
    return {
        "index": index,
        "row": row,
        "col": col,
        "empty": False,
        "bbox_h": int(ys.max() - ys.min() + 1),
        "bbox_w": int(xs.max() - xs.min() + 1),
        "area": int((labels == k).sum()),
        "mean_rgb": mean_rgb,
        "cell_h": int(cc.shape[0]),
        "cell_w": int(cc.shape[1]),
    }


def spread(values):
    if not values:
        return 0.0
    lo, hi = min(values), max(values)
    return float((hi - lo) / hi) if hi else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", help="atlas / spritesheet PNG")
    ap.add_argument("--cols", type=int, default=4, help="grid columns (default 4)")
    ap.add_argument("--rows", type=int, default=2, help="grid rows (default 2)")
    ap.add_argument("--max-height-spread", type=float, default=0.12,
                    help="allowed (max-min)/max of silhouette height (default 0.12)")
    ap.add_argument("--max-area-spread", type=float, default=0.45,
                    help="allowed (max-min)/max of silhouette area (default 0.45)")
    ap.add_argument("--palette-tol", type=float, default=55.0,
                    help="allowed mean-colour distance from the median frame (default 55)")
    ap.add_argument("--color-tol", type=float, default=24.0,
                    help="colour distance from background to count as foreground (default 24)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args()

    if not os.path.isfile(args.image):
        print("NU EXISTA: %s" % args.image)
        return 2
    if args.cols < 1 or args.rows < 1:
        print("--cols si --rows trebuie sa fie >= 1")
        return 2

    im = Image.open(args.image).convert("RGBA")
    W, H = im.size
    cw, ch = W // args.cols, H // args.rows
    if cw < 16 or ch < 16:
        print("Celula prea mica: %dx%d" % (cw, ch))
        return 2
    arr = np.array(im)

    cells = []
    idx = 0
    for r in range(args.rows):
        for c in range(args.cols):
            cells.append(analyse_cell(arr, r, c, cw, ch, idx, args.color_tol))
            idx += 1

    good = [c for c in cells if not c["empty"]]
    empties = [c["index"] for c in cells if c["empty"]]
    heights = [c["bbox_h"] for c in good]
    areas = [c["area"] for c in good]
    h_spread = spread(heights)
    a_spread = spread(areas)

    colors = np.array([c["mean_rgb"] for c in good], dtype=float) if good else np.zeros((0, 3))
    if len(good):
        median = np.median(colors, axis=0)
        dists = np.linalg.norm(colors - median, axis=1)
        for c, d in zip(good, dists):
            c["color_dist"] = round(float(d), 1)
        max_cd = float(max(dists))
        palette_outliers = [c["index"] for c in good if c["color_dist"] > args.palette_tol]
    else:
        max_cd = 0.0
        palette_outliers = []

    failures = []
    if empties:
        failures.append("cadre goale: %s" % empties)
    if h_spread > args.max_height_spread:
        lo_i = min(good, key=lambda c: c["bbox_h"])["index"]
        hi_i = max(good, key=lambda c: c["bbox_h"])["index"]
        failures.append("diferenta de inaltime %.0f%% > %.0f%% (celula %d=%dpx vs %d=%dpx)" % (
            h_spread * 100, args.max_height_spread * 100,
            lo_i, min(heights), hi_i, max(heights)))
    if a_spread > args.max_area_spread:
        failures.append("diferenta de arie %.0f%% > %.0f%%" % (
            a_spread * 100, args.max_area_spread * 100))
    if palette_outliers:
        failures.append("paleta diferita in cadrele: %s (distanta max %.0f)" % (
            palette_outliers, max_cd))

    result = {
        "image": args.image,
        "size": [W, H],
        "grid": [args.cols, args.rows],
        "frames": cells,
        "empty": empties,
        "height_spread": round(h_spread, 4),
        "area_spread": round(a_spread, 4),
        "max_color_dist": round(max_cd, 1),
        "palette_outliers": palette_outliers,
        "pass": not failures,
        "failures": failures,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("ATLAS: %s  %dx%d  grid %dx%d" % (args.image, W, H, args.cols, args.rows))
        print("%-4s %-6s %-8s %-8s %-9s %-18s %s" % (
            "cell", "empty", "h(px)", "w(px)", "area", "mean RGB", "color dist"))
        for c in cells:
            if c["empty"]:
                print("%-4d %-6s %-8s %-8s %-9s %-18s %s" % (
                    c["index"], "DA", "-", "-", "-", "-", c.get("reason", "")))
            else:
                print("%-4d %-6s %-8d %-8d %-9d %-18s %s" % (
                    c["index"], "nu", c["bbox_h"], c["bbox_w"], c["area"],
                    str(c["mean_rgb"]), c.get("color_dist", "-")))
        print("-" * 70)
        print("height spread: %.0f%% (limit %.0f%%) | area spread: %.0f%% (limit %.0f%%) | max colour dist: %.0f (limit %.0f)" % (
            h_spread * 100, args.max_height_spread * 100,
            a_spread * 100, args.max_area_spread * 100,
            max_cd, args.palette_tol))
        if failures:
            print("VERDICT: FAIL")
            for f in failures:
                print("  - " + f)
        else:
            print("VERDICT: PASS")

    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
