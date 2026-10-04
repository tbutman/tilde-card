// Business card for tbutman.com: QR code and NFC tag, both opening https://tbutman.com/hello.
//
// One colour body per printable part. The light and accent parts are flush inlays in the top of
// the card; the dark QR modules are the black body showing through the light field.
//
// Render one part at a time with -D part="body" | "light" | "accent"; "preview" shows them all.
// Regenerate qr_matrix.scad with scripts/gen_qr.py whenever qr_url changes.

include <qr_matrix.scad>
use <fonts/Inter-ExtraBold.ttf>
use <fonts/JetBrainsMono-ExtraBold.ttf>

/* [Output] */
part = "preview"; // [preview, body, light, accent]

/* [Card] */
card_w = 85.60;    // ID-1 width
card_h = 53.98;    // ID-1 height
corner_r = 3.2;
card_t = 1.6;      // total thickness
layer_h = 0.2;     // slicer layer height (first layer included); thicknesses below are multiples of it
inlay_t = 0.6;     // depth of the light and accent inlays (3 layers): opaque enough over black

/* [QR code] */
qr_url = "https://tbutman.com/hello";
qr_module = 1.2;        // mm per module (min 1)
qr_quiet = 4;           // quiet zone, in modules
qr_right_margin = 7.19; // card edge to the light field; matches the top and bottom margins
qr_field_r = 1.0;       // corner radius of the light field (inside the quiet zone)
qr_overlap = 0.02;      // grows dark modules so diagonal neighbours overlap instead of meeting at
                        // a zero-width edge, which would make both STLs non-manifold

/* [Text] */
text_x = 6.0;                         // left edge of the text column
mark_prefix = "~/";                   // amber, like the site header's "~/tbutman"
mark_name = "tbutman";                // light
mark_font = "JetBrains Mono:style=ExtraBold";
mark_size = 4.0;                      // in this OpenSCAD build, size = cap height in mm
mark_bolden = 0.05;                   // grows each stroke edge: the mono "a" joint is thinner than 0.5 mm
name_lines = ["Thomas", "Butman"];
name_font = "Inter:style=ExtraBold";
name_size = 5.2;
name_leading = 1.45;                  // baseline-to-baseline, as a multiple of name_size
name_baseline = 30.5;                 // baseline of the first name line, from the bottom edge
accent_w = 10.0;                      // amber rule under the name
accent_h = 0.8;
accent_gap = 3.4;                     // last name baseline to the top of the rule
domain_text = "tbutman.com";
domain_font = "Inter:style=ExtraBold";
domain_size = 3.2;

/* [NFC tag] */
nfc_d = 25.0;            // tag diameter (25 mm round NTAG215 sticker)
nfc_clearance = 0.3;     // added to the diameter
nfc_tag_t = 0.2;         // measured tag thickness; the pocket rounds this up to whole layers
nfc_floor_t = 0.4;       // plastic under the tag (2 layers)
nfc_center = [20.0, card_h / 2];

/* [Preview colours] */
body_color = "#16181b";
light_color = "#f1efe8";
accent_color = "#ff9f1c";

$fn = 96;

// ---- Derived values ----
qr_size = qr_matrix_size * qr_module;
field = (qr_matrix_size + 2 * qr_quiet) * qr_module;
field_x = card_w - qr_right_margin - field;
field_y = (card_h - field) / 2;

pocket_d = nfc_d + nfc_clearance;
pocket_depth = ceil(nfc_tag_t / layer_h - 1e-6) * layer_h;
pocket_top = nfc_floor_t + pocket_depth;
cover_layers = round((card_t - pocket_top) / layer_h);
// Slicer layers are 1-based; the layer whose bottom is pocket_top is the first one over the tag.
pause_layer = round(pocket_top / layer_h) + 1;

// ---- Checks ----
assert(qr_url == qr_matrix_url, str("qr_matrix.scad encodes ", qr_matrix_url, "; run scripts/gen_qr.py \"", qr_url, "\""));
assert(qr_module >= 1, "QR modules must be at least 1 mm");
assert(qr_quiet >= 4, "QR needs a 4-module quiet zone");
assert(inlay_t >= 0.4, "contrast layer must be at least 0.4 mm");
assert(min(mark_size, name_size, domain_size) >= 3, "cap height must be at least 3 mm");
assert(cover_layers >= 2, "the NFC tag needs at least two layers over it");
assert(pocket_top <= card_t - inlay_t, "the NFC pocket must sit below the inlays");
assert(nfc_center[0] + pocket_d / 2 <= field_x - 1, "the NFC pocket must not sit under the QR field");
assert(nfc_center[0] - pocket_d / 2 >= 2 && abs(nfc_center[1] - card_h / 2) + pocket_d / 2 <= card_h / 2 - 2,
       "the NFC pocket needs a 2 mm wall to the card edge");

echo(str("QR ", qr_matrix_designator, ": ", qr_matrix_size, "x", qr_matrix_size, " modules, ", qr_module,
         " mm each; light field ", field, " mm"));
echo(str("NFC pocket: d=", pocket_d, " mm, z ", nfc_floor_t, " to ", pocket_top, " mm, ", cover_layers,
         " layers above it; pause before layer ", pause_layer, " (top at ", pause_layer * layer_h, " mm)"));
echo(str("Colour change: inlays start at z=", card_t - inlay_t, " mm, layer ", round((card_t - inlay_t) / layer_h) + 1));

// ---- 2D artwork ----
module rounded_rect(size, r) {
    offset(r) offset(-r) square(size);
}

module qr_dark_2d() {
    translate([field_x + qr_quiet * qr_module, field_y + qr_quiet * qr_module])
        for (run = qr_matrix_runs)
            // Row 0 is the top of the symbol.
            translate([run[0] * qr_module - qr_overlap, (qr_matrix_size - 1 - run[1]) * qr_module - qr_overlap])
                square([run[2] * qr_module + 2 * qr_overlap, qr_module + 2 * qr_overlap]);
}

module qr_light_2d() {
    difference() {
        translate([field_x, field_y]) rounded_rect([field, field], qr_field_r);
        qr_dark_2d();
    }
}

module name_2d() {
    for (i = [0 : len(name_lines) - 1])
        translate([text_x, name_baseline - i * name_size * name_leading])
            text(name_lines[i], size = name_size, font = name_font);
}

// The header mark is set as one string so the spacing matches the site, then split by colour.
module mark_2d() {
    translate([text_x, field_y + field - mark_size])
        offset(delta = mark_bolden) text(str(mark_prefix, mark_name), size = mark_size, font = mark_font);
}

module mark_prefix_2d() {
    translate([text_x, field_y + field - mark_size])
        offset(delta = mark_bolden) text(mark_prefix, size = mark_size, font = mark_font);
}

module accent_2d() {
    // The mark sits on the top edge of the QR field; the domain sits on its bottom edge.
    mark_prefix_2d();
    last_baseline = name_baseline - (len(name_lines) - 1) * name_size * name_leading;
    translate([text_x, last_baseline - accent_gap - accent_h]) square([accent_w, accent_h]);
    translate([text_x, field_y]) text(domain_text, size = domain_size, font = domain_font);
}

module light_2d() {
    qr_light_2d();
    name_2d();
    difference() {
        mark_2d();
        mark_prefix_2d();
    }
}

// ---- 3D parts ----
// `extra` lets the cut through the body overshoot the top face; the printed parts end flush.
module inlay(extra = 0) {
    translate([0, 0, card_t - inlay_t]) linear_extrude(inlay_t + extra) children();
}

module body() {
    difference() {
        linear_extrude(card_t) rounded_rect([card_w, card_h], corner_r);
        inlay(0.01) light_2d();
        inlay(0.01) accent_2d();
        translate([nfc_center[0], nfc_center[1], nfc_floor_t]) cylinder(d = pocket_d, h = pocket_depth);
    }
}

module light() {
    inlay() light_2d();
}

module accent() {
    inlay() difference() {
        accent_2d();
        light_2d();
    }
}

if (part == "body") body();
else if (part == "light") light();
else if (part == "accent") accent();
else {
    color(body_color) body();
    color(light_color) light();
    color(accent_color) accent();
}
