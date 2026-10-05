// Business card for tbutman.com: QR code and NFC tag, both opening https://tbutman.com/hello.
//
// One colour body per printable part (body, light, accent, and chrome for the back's window bar). The light and accent parts are flush inlays in the top of
// the card (the front) and in the bottom (the back, which prints against the plate, mirrored so
// it reads correctly when the card is turned over). The dark QR modules are the black body
// showing through the light field.
//
// Render one part at a time with -D part="body" | "light" | "accent"; "preview" shows them all.
// Regenerate qr_matrix.scad with scripts/gen_qr.py whenever qr_url changes.

include <qr_matrix.scad>
use <fonts/Inter-ExtraBold.ttf>
use <fonts/Inter-Bold.ttf>
use <fonts/JetBrainsMono-ExtraBold.ttf>

/* [Output] */
part = "preview"; // [preview, body, light, accent, chrome]

/* [Printer] */
nozzle = 0.2;      // [0.2, 0.4] build.sh exports both versions; the settings below follow it
// Per nozzle: layer height, the narrowest stroke (about 1.5x the nozzle), the narrowest gap
// between strokes (one line), and the smallest cap height.
fine = nozzle < 0.3;
layer_h = fine ? 0.1 : 0.2;   // slicer layer height (first layer included); thicknesses are multiples of it
min_stroke = fine ? 0.3 : 0.5;
min_gap = fine ? 0.22 : 0.34; // 0.4 nozzle: the slicer's narrowest wall, 85% of the nozzle
min_cap = fine ? 2.5 : 3;

/* [Card] */
card_w = 85.60;    // ID-1 width
card_h = 53.98;    // ID-1 height
corner_r = 3.2;
card_t = 1.6;      // total thickness
inlay_t = 0.6;     // depth of the light and accent inlays: opaque enough over black
back_inlay_t = 0.6; // depth of the inlays on the back

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
mark_bolden = fine ? 0 : 0.05;        // grows each stroke edge: the mono "a" joint is under 0.5 mm
name_lines = ["Thomas", "Butman"];
name_font = "Inter:style=ExtraBold";
name_size = 5.2;
name_leading = 1.45;                  // baseline-to-baseline, as a multiple of name_size
name_baseline = 30.5;                 // baseline of the first name line, from the bottom edge
accent_w = 10.0;                      // amber rule under the name
accent_h = 0.8;
accent_gap = 3.4;                     // last name baseline to the top of the rule
// "tap" marker in the strip right of the QR code, over the NFC tag: generic NFC waves (not the
// EMVCo payment symbol) in amber and a light label, turned to read upwards.
// The 0.2 nozzle fits the full phrase; with a 0.4 nozzle its strokes and gaps are too fine.
tap_label = fine ? "tap to connect" : "tap";
tap_font = fine ? "Inter:style=Bold" : "Inter:style=ExtraBold"; // ExtraBold closes the c and e at 2.6 mm
tap_size = fine ? 2.6 : 3.0;
// Measured per mm of size: the label's length ("tap to connect" in Bold, "tap" in ExtraBold), and
// the middle of its ink (the p's descender to the t's top) above the baseline. Re-measure if a
// label changes.
tap_label_len = (fine ? 9.72 : 2.18) * tap_size;
tap_label_mid = 0.328 * tap_size;
tap_dot_d = 1.1;                      // the source dot
tap_radii = [1.4, 2.55, 3.7];         // the waves, radiating towards the label; 1.15 mm apart
tap_stroke = 0.6;                     // leaves 0.55 mm of black between waves
tap_spread = 80;                      // degrees covered by each wave; sets the icon's width in the strip
tap_gap = 1.6;                        // icon to label
tap_bolden = fine ? 0 : 0.05;         // grows each stroke edge: the ExtraBold "a" joint is under 0.5 mm
domain_text = "tbutman.com";
domain_font = "Inter:style=ExtraBold";
domain_size = 3.2;

/* [Back] */
back_enabled = true;
back_email = "tbutman@gmail.com";
// Terminal lines: [amber prompt, light text]. The last line ends in an amber cursor block.
back_lines = [
    ["$ ", "whoami"],
    ["", "thomas butman"],
    ["", "senior product engineer"],
    ["", back_email],
    ["$ ", ""],
];
back_font = "JetBrains Mono:style=ExtraBold";
back_size = 3.6;
back_bolden = fine ? 0 : 0.05;        // grows each stroke edge: the mono "m" and "a" joints are under 0.5 mm
back_prompt_bolden = fine ? 0 : 0.15; // the mono "$" has a hairline bar
back_leading = 1.75;                  // baseline-to-baseline, as a multiple of back_size
back_x = 6.0;                         // left margin, seen from the back (matches the front)
// Terminal window bar at the top: three dots and a rule, in their own "chrome" part (gray).
back_bar_top = 6.0;                   // card edge to the top of the dots
back_dot_d = 2.2;
back_dot_pitch = 3.6;
back_rule_h = 0.6;
back_rule_gap = 2.4;                  // dots to rule
back_text_gap = 2.8;                  // rule to the top of the first line's capitals
back_cursor = [2.0, 3.6];             // cursor block width and height

/* [NFC tag] */
nfc_d = 25.0;            // tag diameter (25 mm round NTAG215 sticker)
nfc_clearance = 0.3;     // added to the diameter
nfc_tag_t = 0.2;         // measured tag thickness; the pocket rounds this up to whole layers
nfc_floor_t = 0.6;       // plastic under the tag: at least the back inlay's 3 layers
nfc_wall = 2.0;          // plastic between the pocket and the card edge
// Against the right edge, under the QR code and the tap marker.
nfc_center = [card_w - nfc_wall - (nfc_d + nfc_clearance) / 2, card_h / 2];

/* [Preview colours] */
body_color = "#16181b";
light_color = "#f1efe8";
accent_color = "#ff9f1c";
chrome_color = "#8e9089";

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
assert(min(mark_size, name_size, domain_size, tap_size, back_size) >= min_cap, str("cap height must be at least ", min_cap, " mm"));
assert(min(tap_stroke, tap_dot_d) >= min_stroke, str("strokes must be at least ", min_stroke, " mm"));
// Black between the dot and the first wave, and between waves, must also print.
assert(tap_radii[0] - tap_stroke / 2 - tap_dot_d / 2 >= min_stroke
       && min([for (i = [1 : len(tap_radii) - 1]) tap_radii[i] - tap_radii[i - 1]]) - tap_stroke >= min_stroke,
       str("the tap waves need at least ", min_stroke, " mm of black between them"));
assert(!back_enabled || back_inlay_t >= 0.4, "contrast layer must be at least 0.4 mm");
assert(!back_enabled || nfc_floor_t >= back_inlay_t, "the NFC pocket must sit above the back inlays");
assert(min(back_dot_d, back_rule_h) >= min_stroke, str("strokes must be at least ", min_stroke, " mm"));
for (t = [card_t, inlay_t, back_inlay_t, nfc_floor_t])
    assert(abs(t / layer_h - round(t / layer_h)) < 1e-6, str(t, " mm is not a whole number of ", layer_h, " mm layers"));
assert(cover_layers >= 2, "the NFC tag needs at least two layers over it");
assert(pocket_top <= card_t - inlay_t, "the NFC pocket must sit below the inlays");
assert(nfc_center[0] - pocket_d / 2 >= nfc_wall - 1e-6 && nfc_center[0] + pocket_d / 2 <= card_w - nfc_wall + 1e-6
       && abs(nfc_center[1] - card_h / 2) + pocket_d / 2 <= card_h / 2 - nfc_wall + 1e-6,
       "the NFC pocket needs a wall to every card edge");

// build.sh reads this line to give verify.py the same limits.
// The 0.4 version's small type has gaps narrower than its nozzle can print (the 0.2 version exists
// for that), so its gap check reports rather than fails.
echo(str("PRINTER nozzle=", nozzle, " layer_h=", layer_h, " min_stroke=", min_stroke, " min_gap=", min_gap,
         " strict_gaps=", fine));
echo(str("QR ", qr_matrix_designator, ": ", qr_matrix_size, "x", qr_matrix_size, " modules, ", qr_module,
         " mm each; light field ", field, " mm"));
echo(str("NFC pocket: d=", pocket_d, " mm, z ", nfc_floor_t, " to ", pocket_top, " mm, ", cover_layers,
         " layers above it; pause before layer ", pause_layer, " (top at ", pause_layer * layer_h, " mm)"));
if (back_enabled)
    echo(str("Colour layers: back inlays in layers 1-", round(back_inlay_t / layer_h), "; front inlays from layer ",
             round((card_t - inlay_t) / layer_h) + 1));
else
    echo(str("Colour layers: front inlays from layer ", round((card_t - inlay_t) / layer_h) + 1));

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

// A stroke with round ends through `points`, as a chain of hulls.
module stroke_2d(points, width) {
    for (i = [0 : len(points) - 2])
        hull() {
            translate(points[i]) circle(d = width, $fn = 24);
            translate(points[i + 1]) circle(d = width, $fn = 24);
        }
}

module tap_icon_2d() {
    circle(d = tap_dot_d, $fn = 32);
    for (r = tap_radii)
        stroke_2d([for (a = [-tap_spread / 2 : 5 : tap_spread / 2]) r * [cos(a), sin(a)]], tap_stroke);
}

module tap_label_2d() {
    translate([max(tap_radii) + tap_stroke / 2 + tap_gap, -tap_label_mid])
        offset(delta = tap_bolden) text(tap_label, size = tap_size, font = tap_font);
}

// The marker is laid out left to right around the dot at the origin, then turned to read upwards
// and centred in the strip right of the QR code. The icon is amber and the label light.
module tap_place() {
    start = -tap_dot_d / 2;
    end = max(tap_radii) + tap_stroke / 2 + tap_gap + tap_label_len;
    translate([card_w - qr_right_margin / 2, card_h / 2]) rotate(90) translate([-(start + end) / 2, 0]) children();
}

module accent_2d() {
    // The mark sits on the top edge of the QR field; the domain sits on its bottom edge.
    mark_prefix_2d();
    last_baseline = name_baseline - (len(name_lines) - 1) * name_size * name_leading;
    translate([text_x, last_baseline - accent_gap - accent_h]) square([accent_w, accent_h]);
    tap_place() tap_icon_2d();
    translate([text_x, field_y]) text(domain_text, size = domain_size, font = domain_font);
}

// ---- The back, drawn as seen from behind ----
back_pitch = back_size * back_leading;
back_dots_y = card_h - back_bar_top - back_dot_d / 2;
back_rule_y = back_dots_y - back_dot_d / 2 - back_rule_gap - back_rule_h;
back_top = back_rule_y - back_text_gap - back_size; // first baseline, anchored under the bar

// The last line's descenders must keep at least the bar's margin from the bottom edge.
assert(!back_enabled || back_top - (len(back_lines) - 1) * back_pitch - 0.3 * back_size >= back_bar_top,
       "the back's lines run off the bottom: shrink back_size or back_leading, or drop a line");

module back_chrome_view_2d() {
    for (i = [0 : 2]) translate([back_x + back_dot_d / 2 + i * back_dot_pitch, back_dots_y]) circle(d = back_dot_d, $fn = 48);
    translate([back_x, back_rule_y]) square([card_w - 2 * back_x, back_rule_h]);
}

module back_line_2d(i, s, bolden = back_bolden) {
    translate([back_x, back_top - i * back_pitch])
        offset(delta = bolden) text(s, size = back_size, font = back_font);
}

module back_accent_view_2d() {
    for (i = [0 : len(back_lines) - 1])
        if (back_lines[i][0] != "") back_line_2d(i, back_lines[i][0], back_prompt_bolden);
    // Cursor block after the last prompt; mono advance is 0.6 em and an em is size / 0.73.
    last = len(back_lines) - 1;
    advance = 0.6 * back_size / 0.73;
    translate([back_x + len(str(back_lines[last][0], back_lines[last][1])) * advance, back_top - last * back_pitch - 0.3])
        square(back_cursor);
}

module back_light_view_2d() {
    for (i = [0 : len(back_lines) - 1])
        if (back_lines[i][1] != "")
            difference() {
                back_line_2d(i, str(back_lines[i][0], back_lines[i][1]));
                if (back_lines[i][0] != "") back_line_2d(i, back_lines[i][0], back_prompt_bolden);
            }
}

// Turning the card over swaps left and right.
module from_behind() {
    translate([card_w, 0]) mirror([1, 0]) children();
}

module light_2d() {
    qr_light_2d();
    name_2d();
    tap_place() tap_label_2d();
    difference() {
        mark_2d();
        mark_prefix_2d();
    }
}

// ---- 3D parts ----
// `extra` lets the cut through the body overshoot the outer face; the printed parts end flush.
module inlay(extra = 0) {
    translate([0, 0, card_t - inlay_t]) linear_extrude(inlay_t + extra) children();
}

module back_inlay(extra = 0) {
    if (back_enabled) translate([0, 0, -extra]) linear_extrude(back_inlay_t + extra) from_behind() children();
}

module body() {
    difference() {
        linear_extrude(card_t) rounded_rect([card_w, card_h], corner_r);
        inlay(0.01) light_2d();
        inlay(0.01) accent_2d();
        back_inlay(0.01) back_light_view_2d();
        back_inlay(0.01) back_accent_view_2d();
        back_inlay(0.01) back_chrome_view_2d();
        translate([nfc_center[0], nfc_center[1], nfc_floor_t]) cylinder(d = pocket_d, h = pocket_depth);
    }
}

module light() {
    inlay() light_2d();
    back_inlay() back_light_view_2d();
}

module accent() {
    inlay() difference() {
        accent_2d();
        light_2d();
    }
    back_inlay() difference() {
        back_accent_view_2d();
        back_light_view_2d();
    }
}

module chrome() {
    back_inlay() back_chrome_view_2d();
}

if (part == "body") body();
else if (part == "light") light();
else if (part == "accent") accent();
else if (part == "chrome") chrome();
else {
    color(body_color) body();
    color(light_color) light();
    color(accent_color) accent();
    color(chrome_color) chrome();
}
