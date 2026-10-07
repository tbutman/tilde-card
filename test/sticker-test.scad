// Sticker test tile: card-sized and printed like the card (front on the plate), with two NFC
// pockets that differ only in how much black sits between the sticker and the front's white:
//
//   z from the plate   pocket B                     pocket 2
//   0.0-0.6            white inlay (the front)      white inlay (the front)
//   0.6-0.8            black                        black
//   0.8-1.0            pocket (0.2 mm)              black
//   1.0-1.2            lid                          pocket (0.2 mm)
//   1.2-1.4            lid                          lid
//   1.4-1.8            white inlays (the back)      white inlays (the back)
//
// So B has 0.2 mm of black in front of the sticker and a 0.4 mm lid behind it; 2 has 0.4 mm and
// 0.2 mm. The back has terminal-style letters over each pocket and a strip of white squares
// inlaid 0.2, 0.4 and 0.6 mm deep. Two colors: body (black) and light (white).
//
// Modeled in print orientation: z = 0 is the front face, on the plate. Seen from the front, the
// tile is mirrored left to right, so the front's labels are mirrored here to read correctly.
//
//   part = "body" or "light"; "preview" shows both. Export: test/build-sticker-test.sh

use <../fonts/Inter-ExtraBold.ttf>
use <../fonts/JetBrainsMono-ExtraBold.ttf>

part = "preview"; // preview, body or light

card = [85.60, 53.98];
card_t = 1.8;
corner_r = 3.2;
front_inlay = 0.6;
back_inlay = 0.4;
pocket_d = 25.8;           // as the card: 25 mm stickers plus 0.8 mm clearance
pocket_depth = 0.2;        // thin stickers
// [name, x of the center, bottom of the pocket]
pockets = [["B", 21.4, 0.8], ["2", 64.2, 1.0]];
pocket_y = 33;
patch = 32;                // the QR-like white field over each pocket, on the front
squares = [0.2, 0.4, 0.6]; // depths of the back's test squares
square = 8;
square_y = 4;
eps = 0.01;

module rounded_rect(size, r) {
    offset(r) offset(-r) square(size);
}

// The front's QR-like patch: white, with finder-like corners and a few dark modules, kept clear
// over the middle so the sticker would show there if it shows at all.
module patch_2d() {
    module finder() {
        difference() { square(7); translate([1, 1]) square(5); }
        translate([2, 2]) square(3);
    }
    difference() {
        square(patch);
        translate([1.5, patch - 8.5]) finder();
        translate([patch - 8.5, patch - 8.5]) finder();
        translate([1.5, 1.5]) finder();
        for (p = [[11, 2], [14, 2], [patch - 4, 11], [patch - 4, 14], [2, 13], [patch - 7, 2], [patch - 4, 2]])
            translate(p) square(2);
    }
}

module label_2d(s, size = 4) {
    text(s, size = size, font = "Inter:style=ExtraBold", halign = "center", valign = "center");
}

// Everything white, each piece as a 2D shape and the z range it fills.
module white(extra = 0) {
    for (p = pockets) {
        cx = p[1];
        // Front: the patch over the pocket and its label under it, both mirrored to read from the front.
        translate([cx + patch / 2, pocket_y - patch / 2, -extra]) linear_extrude(front_inlay + extra) mirror([1, 0]) patch_2d();
        translate([cx, pocket_y - patch / 2 - 6, -extra]) linear_extrude(front_inlay + extra) mirror([1, 0]) label_2d(p[0]);
        // Back: terminal-style lines right over the pocket, and the label above it.
        translate([0, 0, card_t - back_inlay]) linear_extrude(back_inlay + extra) {
            translate([cx - 11.8, pocket_y + 1.4]) text("$ whoami", size = 3.6, font = "JetBrains Mono:style=ExtraBold");
            translate([cx - 11.8, pocket_y - 4.9]) text("jane doe", size = 3.6, font = "JetBrains Mono:style=ExtraBold");
            translate([cx, pocket_y + pocket_d / 2 + 3.4]) label_2d(p[0]);
        }
    }
    // Back: the squares, each with its depth beside it.
    for (i = [0 : len(squares) - 1]) {
        x = 12 + i * 25;
        translate([x, square_y, card_t - squares[i]]) cube([square, square, squares[i] + extra]);
        translate([0, 0, card_t - back_inlay]) linear_extrude(back_inlay + extra)
            translate([x + square + 1.5, square_y + square / 2]) text(str(squares[i]), size = 3, font = "Inter:style=ExtraBold", valign = "center");
    }
}

module body() {
    difference() {
        linear_extrude(card_t) rounded_rect(card, corner_r);
        white(eps);
        for (p = pockets) translate([p[1], pocket_y, p[2]]) cylinder(d = pocket_d, h = pocket_depth, $fn = 128);
    }
}

if (part == "body") body();
else if (part == "light") white();
else {
    color("#16181b") body();
    color("#f1efe8") white();
}
