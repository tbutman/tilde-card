// Inlay test strip: how deep a white inlay must be to hide the black under it. Three white squares
// inlaid flush in the top of a black base, 0.2, 0.4 and 0.6 mm deep, each labeled underneath.
// The top is the face that matters: the card's back prints on top, and its inlays are 0.4 mm deep
// on a card with an NFC sticker (0.6 mm without one). Made for a 0.4 mm nozzle at 0.2 mm layers,
// in about 10 minutes.
//
//   part = "body" (black) or "light" (white); "preview" shows both. build: test/build-inlay-test.sh

use <../fonts/Inter-ExtraBold.ttf>

part = "preview"; // preview, body or light

base = [40, 21];
base_t = 1.0;            // 5 layers of 0.2 mm
corner_r = 2;
square = 8;
gap = 4;                 // between squares
depths = [0.2, 0.4, 0.6];
margin = (base[0] - len(depths) * square - (len(depths) - 1) * gap) / 2;
square_y = base[1] - 3 - square;
label_size = 3.2;        // cap height; the label is a 0.6 mm inlay, so it reads whatever the result
label_y = 3;

module rounded_rect(size, r) {
    offset(r) offset(-r) square(size);
}

function square_x(i) = margin + i * (square + gap);

// The white: each square at its depth, and its label at the deepest.
module light() {
    for (i = [0 : len(depths) - 1]) {
        translate([square_x(i), square_y, base_t - depths[i]]) cube([square, square, depths[i]]);
        translate([square_x(i) + square / 2, label_y, base_t - max(depths)])
            linear_extrude(max(depths))
                text(str(depths[i]), size = label_size, font = "Inter:style=ExtraBold", halign = "center");
    }
}

module body() {
    difference() {
        linear_extrude(base_t) rounded_rect(base, corner_r);
        // The white's shapes, overshooting the top so the cut leaves no skin.
        for (i = [0 : len(depths) - 1])
            translate([square_x(i), square_y, base_t - depths[i]]) cube([square, square, depths[i] + 0.02]);
        for (i = [0 : len(depths) - 1])
            translate([square_x(i) + square / 2, label_y, base_t - max(depths)])
                linear_extrude(max(depths) + 0.02)
                    text(str(depths[i]), size = label_size, font = "Inter:style=ExtraBold", halign = "center");
    }
}

if (part == "body") body();
else if (part == "light") light();
else {
    color("#16181b") body();
    color("#f1efe8") light();
}
