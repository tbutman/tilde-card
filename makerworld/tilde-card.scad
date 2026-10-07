// Tilde card: a credit-card-sized business card you print in one go on a multi-color printer.
// The front has your name, your website and a QR code that opens your link; an optional NFC
// sticker, sealed inside during the print, lets phones tap it too. Made for Tilde, the free
// Android app that turns your phone into the same card.
//
// Click Customize and fill in the sections: the front, the back, the tap mark, colors and printing.
// The print settings and the pause for the NFC sticker are in the model's description.
//
// Full source, instructions and the developer version: https://github.com/tbutman/tilde-card
// (MIT; CC BY 4.0 on MakerWorld).

/* [Front of the card] */
// Your first name, on the first line. Example: Jane
first_name = "Jane";
// Your last name, on the second line. Leave it empty to fit your whole name on one line. Example: Doe
last_name = "Doe";
// Shown after ~/ at the top, like a folder in a terminal. Leave it empty to leave it out. Example: janedoe
handle = "janedoe";
// The link the QR code opens: up to 53 characters. Write the same one to your NFC sticker. Example: https://example.com
qr_code_link = "https://example.com";
// Your website, printed under your name. Leave it empty to leave it out. Example: example.com
website_on_card = "example.com";

/* [Back of the card] */
// What the back shows. None is plain black and prints fastest, with about half the color changes.
back_style = "terminal"; // [terminal:Terminal window (a command and your lines), plain:Plain (your lines), none:None (plain black)]
// The command shown after $ on the Terminal window back. Example: whoami
terminal_command = "whoami";
// Printed on the back, in either style. Leave a line empty to skip it. Example: jane doe
back_line_1 = "jane doe";
// Printed on the back, in either style. Leave a line empty to skip it. Example: product designer
back_line_2 = "product designer";
// Printed on the back, in either style. Leave a line empty to skip it. Example: jane@example.com
back_line_3 = "jane@example.com";

/* [Tap mark] */
// The word next to the tap waves, up to about 14 characters (17 on the 0.2 mm nozzle). Leave it empty for just the waves. Example: tap to connect
tap_label = "tap";
// Which of your colors the tap waves use, on the front and the back.
tap_waves_color = "accent"; // [accent:Accent color, light:Light color, chrome:Window bar color]
// Which of your colors the tap label uses, on the front and the back.
tap_label_color = "light"; // [light:Light color, accent:Accent color, chrome:Window bar color]
// Show the tap waves on the back too (only with an NFC sticker). Waves and label uses your tap label.
back_tap_mark = "no"; // [no:No, waves:Waves only, label:Waves and label]

/* [Colors] */
// The card, and the QR code's dark squares. Keep it dark so the code scans.
card_color = "#16181b"; // color
// The QR code's background, your name, the back's text and the tap label. Keep it light so the code scans.
light_color = "#f1efe8"; // color
// The ~/, the line under your name, your website and the tap waves.
accent_color = "#ff9f1c"; // color
// The window bar on the terminal back.
window_bar_color = "#8e9089"; // color

/* [Printing] */
// Your printer's nozzle. 0.2 mm prints the sharpest text; 0.4 mm is over three times faster.
nozzle = 0.2; // [0.2:0.2 mm nozzle (sharpest), 0.4:0.4 mm nozzle (fastest)]
// An NFC sticker sealed inside lets phones tap the card. Measure your stickers to pick thin or thick.
nfc_sticker = "thin"; // [none:No NFC sticker (QR code only), thin:Thin NFC stickers 0.10-0.20 mm (1.6 mm card), thick:Thick NFC stickers 0.20-0.40 mm (1.8 mm card)]

/* [Hidden] */
part = "preview"; // preview, body, light, accent or chrome
// Which face prints against the plate. The plate side comes out flatter and matte, so the front
// goes down. The output is in print orientation.
face_down = "front"; // front or back
qr_mask = -1; // QR mask pattern 0-7; -1 picks the one the standard scores best

// Per nozzle: layer height, the narrowest stroke (about 1.5x the nozzle), the narrowest gap
// between strokes (one line), and the smallest cap height.
fine = nozzle < 0.3;
layer_h = fine ? 0.1 : 0.2;   // slicer layer height (first layer included); thicknesses are multiples of it
min_stroke = fine ? 0.3 : 0.5;
min_gap = fine ? 0.22 : 0.34; // 0.4 nozzle: the slicer's narrowest wall, 85% of the nozzle
min_cap = fine ? 2.5 : 3;

// Card. "thick" stickers make it 0.2 mm thicker, so the same 0.2 mm of black still separates the
// tag from the white QR field.
nfc_enabled = nfc_sticker != "none";
thick_sticker = nfc_sticker == "thick";
card_w = 85.60;    // ID-1 width
card_h = 53.98;    // ID-1 height
corner_r = 3.2;
card_t = thick_sticker ? 1.8 : 1.6; // total thickness
inlay_t = 0.6;     // depth of the light and accent inlays: opaque enough over black
back_inlay_t = 0.6; // depth of the inlays on the back

// QR code: a fixed light field (quiet zone included); the modules scale to fill it, from 1.37 mm
// (version 1) to 1.2 mm (version 2) and 1.07 mm (version 3).
qr_field = 39.6;
qr_quiet = 4;           // quiet zone, in modules
qr_right_margin = 7.19; // card edge to the light field; matches the top and bottom margins
qr_field_r = 1.0;       // corner radius of the light field (inside the quiet zone)
qr_overlap = 0.02;      // grows dark modules so diagonal neighbors overlap instead of meeting at
                        // a zero-width edge, which would make both STLs non-manifold

// Front text. Sizes are cap heights in mm, and the largest used: longer text shrinks to fit the
// column left of the QR code, down to the smallest size that prints.
text_x = 6.0;                         // left edge of the text column
text_gap = 1.5;                       // text column to the QR field
mark_prefix = "~/";                   // amber, like the ~/ in a terminal prompt
mark_name = handle;                   // light
mark_font = "JetBrains Mono:style=ExtraBold";
mark_size = 4.0;
mark_bolden = fine ? 0 : 0.05;        // grows each stroke edge: the mono "a" joint is under 0.5 mm
name_lines = [for (line = [first_name, last_name]) if (line != "") line];
name_font = "Inter:style=ExtraBold";
name_size = 5.2;
name_leading = 1.45;                  // baseline-to-baseline, as a multiple of the name's size
name_baseline = 30.5;                 // baseline of the first name line, from the bottom edge
accent_w = 10.0;                      // amber rule under the name
accent_h = 0.8;
accent_gap = 3.4;                     // last name baseline to the top of the rule
// Tap marker in the strip right of the QR code, over the NFC tag: generic NFC waves (not the
// EMVCo payment symbol) and tap_label, each in its chosen color, turned to read upwards.
// The 0.2 nozzle uses Inter Bold at 2.6 mm; the 0.4 nozzle needs ExtraBold at 3 mm. A longer label
// shrinks to fit the QR code's height, down to min_cap.
tap_font = fine ? "Inter:style=Bold" : "Inter:style=ExtraBold";
tap_size = fine ? 2.6 : 3.0;
tap_dot_d = 1.1;                      // the source dot
tap_radii = [1.4, 2.55, 3.7];         // the waves, radiating towards the label; 1.15 mm apart
tap_stroke = 0.6;                     // leaves 0.55 mm of black between waves
tap_spread = 80;                      // degrees covered by each wave; sets the icon's width in the strip
tap_gap = 1.6;                        // icon to label
tap_bolden = fine ? 0 : 0.05;         // grows each stroke edge: the ExtraBold "a" joint is under 0.5 mm
// The whole marker stays within the QR code's height; the label gets what the waves leave.
tap_label_room = qr_field - (tap_dot_d / 2 + max(tap_radii) + tap_stroke / 2 + tap_gap);
domain_text = website_on_card;
domain_font = "Inter:style=ExtraBold";
domain_size = 3.2;
domain_bolden = fine ? 0 : 0.03;       // the "a" joint sits right at 0.5 mm

// Back. Terminal style: lines as [amber prompt, light text]; the last line ends in an amber cursor
// block. Plain style: the three lines in Inter, centered vertically: the first larger (light), the
// second amber, the third light.
back_enabled = back_style != "none";
back_mark_on = back_tap_mark != "no" && nfc_enabled;
back_inked = back_enabled || back_mark_on;   // anything inlaid in the back
terminal = back_style == "terminal";
plain = back_style == "plain";
plain_lines = [for (line = [[back_line_1, "light", true], [back_line_2, "accent", false], [back_line_3, "light", false]])
    if (line[0] != "") line];             // [text, color, is the first (larger) line]
plain_name_size = 4.4;
plain_size = 3.2;
plain_font = "Inter:style=ExtraBold";
plain_bolden = fine ? 0 : 0.03;       // as for the website on the front
plain_name_gap = 7.0;                 // name baseline to the next baseline
plain_gap = 5.4;                      // between the smaller lines
back_lines = [
    ["$ ", terminal_command],
    each [for (line = [back_line_1, back_line_2, back_line_3]) if (line != "") ["", line]],
    ["$ ", ""],
];
back_font = "JetBrains Mono:style=ExtraBold";
back_size = 3.6;
back_bolden = fine ? 0 : 0.05;        // grows each stroke edge: the mono "m" and "a" joints are under 0.5 mm
back_prompt_bolden = fine ? 0 : 0.15; // the mono "$" has a hairline bar
back_leading = 1.75;                  // baseline-to-baseline, as a multiple of back_size
back_x = 6.0;                         // left margin, seen from the back (matches the front)
// With the back tap mark, the strip over the tag (the front's tap strip, seen from behind) holds the
// mark, and the lines start where the front's QR field would: a text_gap past the strip.
back_shift = back_mark_on ? qr_right_margin + text_gap - back_x : 0;
back_left = back_x + back_shift;
back_room = card_w - 2 * back_x - back_shift;
// Terminal window bar at the top: three dots and a rule, in their own "chrome" part (gray).
back_bar_top = 6.0;                   // card edge to the top of the dots
back_dot_d = 2.2;
back_dot_pitch = 3.6;
back_rule_h = 0.6;
back_rule_gap = 2.4;                  // dots to rule
back_text_gap = 2.8;                  // rule to the top of the first line's capitals
back_cursor = [2.0, 3.6];             // cursor block width and height at back_size

// NFC tag
nfc_d = 25.0;            // tag diameter (25 mm round NTAG215 sticker)
nfc_clearance = 0.3;     // added to the diameter
nfc_tag_t = thick_sticker ? 0.4 : 0.2; // thickest sticker that fits; the pocket rounds this up to whole layers
nfc_floor_t = 0.6;       // plastic under the tag: at least the back inlay's 3 layers
nfc_wall = 2.0;          // plastic between the pocket and the card edge
// Against the right edge, under the QR code and the tap marker.
nfc_center = [card_w - nfc_wall - (nfc_d + nfc_clearance) / 2, card_h / 2];

// ---- Text widths ----
// Advance widths of Inter ExtraBold for U+0020 to U+00FF, per mm of cap height (from the font
// file; 0.9 for the few control characters). Kerning makes real text slightly narrower, so fitting
// to these is safe. JetBrains Mono advances are all 0.822.
INTER_EXTRABOLD_WIDTHS = [0.301, 0.493, 0.806, 0.901, 0.907, 1.415, 0.939, 0.487, 0.526, 0.526, 0.801, 0.942, 0.485, 0.648, 0.485, 0.55, 0.951, 0.607, 0.877, 0.903, 0.946, 0.871, 0.909, 0.808, 0.913, 0.909, 0.485, 0.495, 0.942, 0.942, 0.942, 0.796, 1.424, 1.058, 0.913, 1.022, 0.993, 0.838, 0.805, 1.034, 1.029, 0.393, 0.811, 1.015, 0.777, 1.297, 1.052, 1.062, 0.896, 1.074, 0.91, 0.907, 0.93, 0.999, 1.058, 1.455, 1.046, 1.034, 0.933, 0.526, 0.55, 0.526, 0.678, 0.666, 0.526, 0.809, 0.877, 0.818, 0.877, 0.826, 0.563, 0.879, 0.873, 0.389, 0.389, 0.815, 0.389, 1.274, 0.873, 0.851, 0.877, 0.877, 0.577, 0.788, 0.525, 0.873, 0.846, 1.186, 0.817, 0.85, 0.799, 0.668, 0.533, 0.668, 0.942, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.301, 0.493, 0.818, 0.893, 1.067, 0.795, 0.504, 0.781, 0.873, 1.256, 0.643, 0.95, 0.942, 0.9, 0.908, 0.582, 0.634, 0.942, 0.642, 0.663, 0.526, 0.887, 0.821, 0.485, 0.554, 0.474, 0.677, 0.95, 1.187, 1.23, 1.285, 0.796, 1.058, 1.058, 1.058, 1.058, 1.058, 1.058, 1.422, 1.022, 0.838, 0.838, 0.838, 0.838, 0.393, 0.393, 0.393, 0.393, 1.058, 1.052, 1.062, 1.062, 1.062, 1.062, 1.062, 0.942, 1.062, 0.999, 0.999, 0.999, 0.999, 1.034, 0.938, 0.927, 0.809, 0.809, 0.809, 0.809, 0.809, 0.809, 1.247, 0.818, 0.826, 0.826, 0.826, 0.826, 0.389, 0.389, 0.389, 0.389, 0.833, 0.873, 0.851, 0.851, 0.851, 0.851, 0.851, 0.942, 0.851, 0.873, 0.873, 0.873, 0.873, 0.85, 0.877, 0.85];
function inter_width(s) = let(w = [for (c = s) let(u = ord(c)) u >= 32 && u <= 255 ? INTER_EXTRABOLD_WIDTHS[u - 32] : 1.0])
    len(w) == 0 ? 0 : w * [for (x = w) 1];
function mono_width(s) = 0.822 * len(s);
// The size at which the widest of `widths` (per mm of size) fills `room`, capped at `size`.
function fit(size, widths, room) = let(widest = max(concat([0], widths))) widest == 0 ? size : min(size, room / widest);

// ---- QR encoder ----
// Turns qr_code_link into a QR code inside OpenSCAD, so the model is one file (MakerWorld's customizer
// takes a single file). Byte mode, versions 1-3 (21-29 modules, which fit the card at 1 mm or more
// per module), error correction M, or L when M can't fit the link. ISO/IEC 18004; the comments
// name the steps.

// Versions that fit the card: [version, level, data codewords, error correction codewords].
// Every one of them is a single block, so no interleaving is needed.
QR_CAPACITY = [[1, "M", 16, 10], [2, "M", 28, 16], [3, "M", 44, 26],
               [1, "L", 19, 7], [2, "L", 34, 10], [3, "L", 55, 15]];

function qr_sum(v) = len(v) == 0 ? 0 : v * [for (x = v) 1];
function qr_zeros(n) = n <= 0 ? [] : [for (i = [1 : n]) 0];
function qr_bit(n, i) = floor(n / pow(2, i)) % 2;
function qr_bits(n, width) = [for (i = [width - 1 : -1 : 0]) qr_bit(n, i)];
// OpenSCAD has no bitwise operators.
function qr_xor(a, b, width = 16) = qr_sum([for (i = [0 : width - 1]) qr_bit(a, i) != qr_bit(b, i) ? pow(2, i) : 0]);
function qr_xor_all(v, i = 0, acc = 0) = i == len(v) ? acc : qr_xor_all(v, i + 1, qr_xor(acc, v[i], 8));

// UTF-8, so links with accented letters encode the way phones decode them.
function qr_utf8_char(u) =
    u < 128 ? [u] :
    u < 2048 ? [192 + floor(u / 64), 128 + u % 64] :
    u < 65536 ? [224 + floor(u / 4096), 128 + floor(u / 64) % 64, 128 + u % 64] :
    [240 + floor(u / 262144), 128 + floor(u / 4096) % 64, 128 + floor(u / 64) % 64, 128 + u % 64];
function qr_utf8(s) = [for (c = s) each qr_utf8_char(ord(c))];

// The smallest version and level that holds n bytes: 4 bits of mode and 8 of length come first.
// QR_CAPACITY lists M before L, so this prefers M at any size the card takes.
function qr_pick(n) = [for (c = QR_CAPACITY) if (n * 8 + 12 <= c[2] * 8) c][0];

// Data codewords: mode 0100 (bytes), 8-bit length, the bytes, a terminator of up to 4 zeros,
// zeros to a whole byte, then the pad bytes 0xEC and 0x11 in turn.
function qr_data(bytes, capacity) = let(
    bits = concat(qr_bits(4, 4), qr_bits(len(bytes), 8), [for (b = bytes) each qr_bits(b, 8)]),
    term = concat(bits, qr_zeros(min(4, capacity * 8 - len(bits)))),
    whole = concat(term, qr_zeros((8 - len(term) % 8) % 8)),
    words = [for (i = [0 : 8 : len(whole) - 1]) qr_sum([for (k = [0 : 7]) whole[i + k] * pow(2, 7 - k)])]
) concat(words, qr_pad(capacity - len(words)));
function qr_pad(n) = n <= 0 ? [] : [for (i = [0 : n - 1]) i % 2 == 0 ? 236 : 17];

// Reed-Solomon over GF(256) with the polynomial x^8 + x^4 + x^3 + x^2 + 1 (0x11D).
function qr_exp_table(i = 0, x = 1, acc = []) = i == 256 ? acc
    : qr_exp_table(i + 1, x * 2 >= 256 ? qr_xor(x * 2, 285, 9) : x * 2, concat(acc, [x]));
QR_EXP = qr_exp_table();
QR_LOG = [for (v = [0 : 255]) v == 0 ? 0 : [for (i = [0 : 254]) if (QR_EXP[i] == v) i][0]];
function qr_mul(a, b) = a == 0 || b == 0 ? 0 : QR_EXP[(QR_LOG[a] + QR_LOG[b]) % 255];
function qr_poly_mul(p, q) = [for (k = [0 : len(p) + len(q) - 2])
    qr_xor_all([for (i = [0 : len(p) - 1]) let(j = k - i) if (j >= 0 && j < len(q)) qr_mul(p[i], q[j])])];
// The generator: (x - a^0)(x - a^1)...(x - a^(n-1)), highest power first.
function qr_generator(n, i = 0, p = [1]) = i == n ? p : qr_generator(n, i + 1, qr_poly_mul(p, [1, QR_EXP[i]]));
// The remainder of data * x^n divided by the generator, by long division.
function qr_ec(data, gen, n, i = 0, rem = undef) = let(r = rem == undef ? qr_zeros(n) : rem)
    i == len(data) ? r
    : let(f = qr_xor(data[i], r[0], 8), shifted = concat([for (k = [1 : n - 1]) r[k]], [0]))
      qr_ec(data, gen, n, i + 1, [for (k = [0 : n - 1]) qr_xor(shifted[k], qr_mul(gen[k + 1], f), 8)]);

// Function patterns: finders with their separators, timing lines, the format areas (with the
// dark module) and, from version 2, one alignment pattern.
function qr_in_finder(r, c, size) = (r <= 7 && c <= 7) || (r <= 7 && c >= size - 8) || (r >= size - 8 && c <= 7);
function qr_in_format(r, c, size) = (r == 8 && (c <= 8 || c >= size - 8)) || (c == 8 && (r <= 8 || r >= size - 8));
function qr_in_alignment(r, c, size) = size > 21 && abs(r - (size - 7)) <= 2 && abs(c - (size - 7)) <= 2;
function qr_is_function(r, c, size) =
    qr_in_finder(r, c, size) || r == 6 || c == 6 || qr_in_format(r, c, size) || qr_in_alignment(r, c, size);
function qr_finder_dark(dr, dc) = dr >= 0 && dr <= 6 && dc >= 0 && dc <= 6 && max(abs(dr - 3), abs(dc - 3)) != 2;
// Format: the level (L = 01, M = 00) and mask, a BCH(15,5) code, then XOR 0x5412.
function qr_bch(rem, i = 0) = i == 10 ? rem : qr_bch(rem * 2 >= 1024 ? qr_xor(rem * 2, 1335, 11) : rem * 2, i + 1);
function qr_format(level, mask) = let(data = (level == "L" ? 1 : 0) * 8 + mask)
    qr_xor(data * 1024 + qr_bch(data), 21522, 15);
// Which format bit a format-area cell holds (two copies), or -1 for the dark module.
function qr_format_index(r, c, size) =
    c == 8 && r <= 5 ? r :
    c == 8 && r == 7 ? 6 :
    c == 8 && r == 8 ? 7 :
    r == 8 && c == 7 ? 8 :
    r == 8 && c <= 5 ? 14 - c :
    r == 8 && c >= size - 8 ? size - 1 - c :
    c == 8 && r == size - 8 ? -1 :
    r - size + 15;
function qr_function_dark(r, c, size, format) =
    qr_in_finder(r, c, size) ? (qr_finder_dark(r, c) || qr_finder_dark(r, c - (size - 7)) || qr_finder_dark(r - (size - 7), c)) :
    r == 6 ? c % 2 == 0 :
    c == 6 ? r % 2 == 0 :
    qr_in_format(r, c, size) ? (let(i = qr_format_index(r, c, size)) i < 0 || qr_bit(format, i) == 1) :
    max(abs(r - (size - 7)), abs(c - (size - 7))) != 1;

// Data cells in placement order: two-column strips from the right, alternately up and down,
// skipping the vertical timing line.
function qr_order(size) = [
    for (right = concat([for (x = [size - 1 : -2 : 8]) x], [5, 3, 1]))
        for (vert = [0 : size - 1]) for (j = [0 : 1])
            let(c = right - j, up = floor((right + 1) / 2) % 2 == 0, r = up ? size - 1 - vert : vert)
            if (!qr_is_function(r, c, size)) [r, c]];
function qr_sort(v) = len(v) <= 1 ? v : let(p = v[floor(len(v) / 2)][0])
    concat(qr_sort([for (e = v) if (e[0] < p) e]), [for (e = v) if (e[0] == p) e], qr_sort([for (e = v) if (e[0] > p) e]));
function qr_mask_on(m, r, c) =
    m == 0 ? (r + c) % 2 == 0 :
    m == 1 ? r % 2 == 0 :
    m == 2 ? c % 3 == 0 :
    m == 3 ? (r + c) % 3 == 0 :
    m == 4 ? (floor(r / 2) + floor(c / 3)) % 2 == 0 :
    m == 5 ? (r * c) % 2 + (r * c) % 3 == 0 :
    m == 6 ? ((r * c) % 2 + (r * c) % 3) % 2 == 0 :
    ((r + c) % 2 + (r * c) % 3) % 2 == 0;

// The data bits as a size x size grid (function cells 0), unmasked.
function qr_data_grid(codewords, size) = let(
    bits = [for (w = codewords) each qr_bits(w, 8)],
    order = qr_order(size),
    // Version 2 and 3 have 7 remainder cells after the last codeword; they stay 0.
    cells = qr_sort([for (i = [0 : len(order) - 1]) [order[i][0] * size + order[i][1], i < len(bits) ? bits[i] : 0]])
) let(lookup = [for (e = cells) e[0]], vals = [for (e = cells) e[1]])
    [for (r = [0 : size - 1]) [for (c = [0 : size - 1])
        qr_is_function(r, c, size) ? 0 : vals[qr_find(lookup, r * size + c)]]];
// Binary search in the sorted cell keys.
function qr_find(v, key, lo = 0, hi = undef) = let(h = hi == undef ? len(v) - 1 : hi, mid = floor((lo + h) / 2))
    v[mid] == key ? mid : v[mid] < key ? qr_find(v, key, mid + 1, h) : qr_find(v, key, lo, mid - 1);

function qr_symbol(grid, size, level, mask) = let(format = qr_format(level, mask))
    [for (r = [0 : size - 1]) [for (c = [0 : size - 1])
        qr_is_function(r, c, size) ? (qr_function_dark(r, c, size, format) ? 1 : 0)
        : (grid[r][c] == 1) != qr_mask_on(mask, r, c) ? 1 : 0]];

// Mask penalty (the four rules of ISO/IEC 18004 7.8.3): long runs, 2x2 blocks, finder-like
// patterns and an uneven balance of dark and light.
function qr_runs_penalty(line) = let(n = len(line), starts = [for (i = [0 : n - 1]) if (i == 0 || line[i] != line[i - 1]) i],
    lengths = [for (k = [0 : len(starts) - 1]) (k + 1 < len(starts) ? starts[k + 1] : n) - starts[k]])
    qr_sum([for (l = lengths) if (l >= 5) l - 2]);
// Rule 3: dark-light-dark-dark-dark-light-dark with 4 light modules on either side, where the
// edge of the symbol counts as light (the quiet zone is). Scans the way reference encoders do, so
// the mask matches theirs for the same data.
QR_FINDER_LIKE = [1, 0, 1, 1, 1, 0, 1];
function qr_light(line, a, b) = a >= b || max([for (k = [a : b - 1]) line[k]]) == 0;
function qr_find_finder_like(line, start) = let(n = len(line))
    start > n - 7 ? -1 : let(hits = [for (i = [start : n - 7]) if ([for (k = [0 : 6]) line[i + k]] == QR_FINDER_LIKE) i])
    len(hits) == 0 ? -1 : hits[0];
function qr_finder_penalty(line, start = 0, acc = 0) = let(n = len(line), i = qr_find_finder_like(line, start))
    i < 0 ? acc : let(hit = i == 0 || i == n - 7 || qr_light(line, max(i - 4, 0), i) || qr_light(line, i + 7, min(i + 11, n)))
    qr_finder_penalty(line, hit ? i + 7 : i + 4, acc + (hit ? 40 : 0));
function qr_penalty(s) = let(n = len(s), cols = [for (c = [0 : n - 1]) [for (r = [0 : n - 1]) s[r][c]]],
    dark = qr_sum([for (row = s) qr_sum(row)]))
    qr_sum([for (line = concat(s, cols)) qr_runs_penalty(line) + qr_finder_penalty(line)])
    + 3 * len([for (r = [0 : n - 2]) for (c = [0 : n - 2])
        if (s[r][c] == s[r][c + 1] && s[r][c] == s[r + 1][c] && s[r][c] == s[r + 1][c + 1]) 1])
    + 10 * floor(abs(dark * 100 / (n * n) - 50) / 5);

// [size, matrix (row 0 at the top, 1 = dark), "version-level", mask], or undef if the text is too
// long for version 3-L. mask = -1 picks the one with the lowest penalty.
function qr_encode(text, mask = -1) = let(bytes = qr_utf8(text), cap = qr_pick(len(bytes)))
    cap == undef ? undef : let(
        version = cap[0], level = cap[1], size = 17 + 4 * version,
        data = qr_data(bytes, cap[2]),
        codewords = concat(data, qr_ec(data, qr_generator(cap[3]), cap[3])),
        grid = qr_data_grid(codewords, size),
        best = mask >= 0 ? mask : let(scores = [for (m = [0 : 7]) qr_penalty(qr_symbol(grid, size, level, m))])
            [for (m = [0 : 7]) if (scores[m] == min(scores)) m][0]
    ) [size, qr_symbol(grid, size, level, best), str(version, "-", level), best];

// Dark modules as horizontal runs [column, row, length], for drawing.
function qr_runs(matrix) = [for (r = [0 : len(matrix) - 1]) let(row = matrix[r], n = len(row))
    for (c = [0 : n - 1]) if (row[c] == 1 && (c == 0 || row[c - 1] == 0))
        [c, r, [for (k = [c : n - 1]) if (row[k] == 0) k][0] == undef ? n - c : [for (k = [c : n - 1]) if (row[k] == 0) k][0] - c]];

$fn = 96;

// ---- Derived values ----
qr = qr_encode(qr_code_link, qr_mask);
assert(qr != undef, str("The QR code's link is ", len(qr_utf8(qr_code_link)), " characters long, and up to 53 fit on the card. Use a shorter link."));
qr_n = qr[0];
qr_module = qr_field / (qr_n + 2 * qr_quiet);
field = qr_field;
field_x = card_w - qr_right_margin - field;
field_y = (card_h - field) / 2;

// Text sizes, shrunk where the text would otherwise run into the QR code or off the card.
text_room = field_x - text_gap - text_x;
mark_size_fit = fit(mark_size, [mark_name == "" ? 0 : mono_width(str(mark_prefix, mark_name))], text_room);
name_size_fit = fit(name_size, [for (line = name_lines) inter_width(line)], text_room);
domain_size_fit = fit(domain_size, [inter_width(domain_text)], text_room);
tap_size_fit = tap_label == "" ? tap_size : fit(tap_size, [inter_width(tap_label)], tap_label_room);
// The label's length (to the end of its ink) and the middle of its ink above the baseline, per mm
// of size. For "tap" both are measured (the p's descender to the t's top); other labels use the
// ExtraBold advance widths, slightly long for Bold, so they center a little early.
tap_label_len = tap_label == "" ? 0 : tap_label == "tap" ? (fine ? 2.14 : 2.18) * tap_size_fit : inter_width(tap_label) * tap_size_fit;
tap_label_mid = 0.328 * tap_size_fit;
// The last line also holds the cursor: one more advance, then the block. Only the terminal style
// uses these lines.
back_size_fit = !terminal ? back_size : fit(back_size, [for (i = [0 : len(back_lines) - 1])
    mono_width(str(back_lines[i][0], back_lines[i][1])) + (i == len(back_lines) - 1 ? 0.822 + back_cursor[0] / back_size : 0)],
    back_room);
plain_name_fit = fit(plain_name_size, [for (line = plain_lines) if (line[2]) inter_width(line[0])], back_room);
plain_size_fit = fit(plain_size, [for (line = plain_lines) if (!line[2]) inter_width(line[0])], back_room);

pocket_d = nfc_d + nfc_clearance;
pocket_depth = ceil(nfc_tag_t / layer_h - 1e-6) * layer_h;
pocket_top = nfc_floor_t + pocket_depth;
// The model is built front-up (z = 0 is the back). Printed front-down, heights from the plate are
// card_t - z, so the pocket's floor and ceiling swap.
print_pocket_bottom = face_down == "front" ? card_t - pocket_top : nfc_floor_t;
print_pocket_top = face_down == "front" ? card_t - nfc_floor_t : pocket_top;
cover_layers = round((card_t - print_pocket_top) / layer_h);
// Slicer layers are 1-based; the layer whose bottom is print_pocket_top is the first one over the tag.
pause_layer = round(print_pocket_top / layer_h) + 1;

// ---- Checks ----
assert(len(name_lines) > 0, "Add your name.");
// Long text can shrink to the smallest size the nozzle prints cleanly; past that, say what to do.
too_long_hint = fine ? "" : " The 0.2 mm nozzle prints smaller text, so more fits.";
assert(name_size_fit >= min_cap - 1e-6,
       str("Your name is too long to fit. Split it between first name and last name, or shorten it.", too_long_hint));
assert(mark_size_fit >= min_cap - 1e-6,
       str("The handle is too long: up to ", floor(text_room / (0.822 * min_cap)) - len(mark_prefix), " characters fit.", too_long_hint));
assert(domain_size_fit >= min_cap - 1e-6, str("The website text is too long. Shorten it, or leave out the https:// and www.", too_long_hint));
back_max_chars = floor(back_room / (0.822 * min_cap));
assert(!terminal || back_size_fit >= min_cap - 1e-6,
       str("A back line or the terminal command is too long: up to ", back_max_chars, " characters fit on a line, and ",
           back_max_chars - 2, " in the command after $. Shorten it.", too_long_hint));
assert(qr_module >= 1, "QR modules must be at least 1 mm");
assert(qr_quiet >= 4, "QR needs a 4-module quiet zone");
assert(inlay_t >= 0.4, "contrast layer must be at least 0.4 mm");
assert(!plain || min(plain_name_fit, plain_size_fit) >= min_cap - 1e-6,
       str("A back line is too long for the plain back. Shorten it, or use the Terminal window style, which fits more.", too_long_hint));
assert(back_style == "terminal" || back_style == "plain" || back_style == "none", "back_style is terminal, plain or none");
// About 0.75 mm of advance per mm of size for lowercase text with spaces.
assert(!nfc_enabled || tap_size_fit >= min_cap - 1e-6,
       str("The tap label is too long: up to about ", floor(tap_label_room / (0.75 * min_cap)),
           " characters fit. Shorten it, or leave it empty for just the waves.", too_long_hint));
assert(min(mark_size_fit, name_size_fit, domain_size_fit, tap_size_fit, back_size_fit, plain ? plain_name_fit : min_cap, plain ? plain_size_fit : min_cap) >= min_cap - 1e-6, str("cap height must be at least ", min_cap, " mm"));
assert(min(tap_stroke, tap_dot_d) >= min_stroke, str("strokes must be at least ", min_stroke, " mm"));
// Black between the dot and the first wave, and between waves, must also print.
assert(tap_radii[0] - tap_stroke / 2 - tap_dot_d / 2 >= min_stroke
       && min([for (i = [1 : len(tap_radii) - 1]) tap_radii[i] - tap_radii[i - 1]]) - tap_stroke >= min_stroke,
       str("the tap waves need at least ", min_stroke, " mm of black between them"));
assert(!back_inked || back_inlay_t >= 0.4, "contrast layer must be at least 0.4 mm");
assert(!back_inked || nfc_floor_t >= back_inlay_t, "the NFC pocket must sit above the back inlays");
assert(min(back_dot_d, back_rule_h) >= min_stroke, str("strokes must be at least ", min_stroke, " mm"));
for (t = [card_t, inlay_t, back_inlay_t, nfc_floor_t])
    assert(abs(t / layer_h - round(t / layer_h)) < 1e-6, str(t, " mm is not a whole number of ", layer_h, " mm layers"));
assert(face_down == "front" || face_down == "back", "face_down is front or back");
assert(nfc_sticker == "none" || nfc_sticker == "thin" || nfc_sticker == "thick", "nfc_sticker is none, thin or thick");
// The tag must not show through the white QR field: keep black between it and the front inlays.
assert(!nfc_enabled || card_t - inlay_t - pocket_top >= 0.2 - 1e-6, "the NFC tag needs 0.2 mm of black between it and the front inlays");
assert(!nfc_enabled || cover_layers >= 2, "the NFC tag needs at least two layers over it");
assert(!nfc_enabled || round(print_pocket_bottom / layer_h) >= 2, "the NFC tag needs at least two layers under it");
assert(!nfc_enabled || pocket_top <= card_t - inlay_t, "the NFC pocket must sit below the inlays");
assert(!nfc_enabled || nfc_center[0] - pocket_d / 2 >= nfc_wall - 1e-6 && nfc_center[0] + pocket_d / 2 <= card_w - nfc_wall + 1e-6
       && abs(nfc_center[1] - card_h / 2) + pocket_d / 2 <= card_h / 2 - nfc_wall + 1e-6,
       "the NFC pocket needs a wall to every card edge");

// A summary in the console: thickness, the nozzle's limits, the QR code, text sizes and the pause.
echo(str("CARD ", nfc_enabled ? str(nfc_sticker, " sticker") : "no NFC tag", ": ", card_t, " mm thick, ", round(card_t / layer_h), " layers"));
echo(str("PRINTER nozzle=", nozzle, " layer_h=", layer_h, " min_stroke=", min_stroke, " min_gap=", min_gap,
         " strict_gaps=", fine, " face_down=", face_down));
echo(str("QR ", qr[2], ", mask ", qr[3], ": ", qr_n, "x", qr_n, " modules, ", qr_module,
         " mm each; light field ", field, " mm"));
echo(str("Text sizes: mark ", mark_size_fit, ", name ", name_size_fit, ", website ", domain_size_fit, ", back ", back_size_fit, " mm"));
if (nfc_enabled)
    echo(str("NFC pocket: d=", pocket_d, " mm, ", print_pocket_bottom, " to ", print_pocket_top, " mm above the plate, ",
             cover_layers, " layers over it; pause before layer ", pause_layer, " (top at ", pause_layer * layer_h, " mm)"));
else
    echo("No NFC tag: no pocket, no tap marker and no pause");
down_t = face_down == "front" ? inlay_t : back_inlay_t;
up_t = face_down == "front" ? back_inlay_t : inlay_t;
if (back_inked)
    echo(str("Color layers: ", face_down, " inlays in layers 1-", round(down_t / layer_h), "; ",
             face_down == "front" ? "back" : "front", " inlays from layer ", round((card_t - up_t) / layer_h) + 1));
else
    echo(str("Color layers: front inlays from layer ", round((card_t - inlay_t) / layer_h) + 1));

// ---- 2D artwork ----
module rounded_rect(size, r) {
    offset(r) offset(-r) square(size);
}

module qr_dark_2d() {
    translate([field_x + qr_quiet * qr_module, field_y + qr_quiet * qr_module])
        for (run = qr_runs(qr[1]))
            // Row 0 is the top of the symbol.
            translate([run[0] * qr_module - qr_overlap, (qr_n - 1 - run[1]) * qr_module - qr_overlap])
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
        translate([text_x, name_baseline - i * name_size_fit * name_leading])
            text(name_lines[i], size = name_size_fit, font = name_font);
}

// The header mark is set as one string, so the ~/ and the handle keep the font's spacing, then
// split by color.
module mark_2d() {
    if (mark_name != "")
        translate([text_x, field_y + field - mark_size_fit])
            offset(delta = mark_bolden) text(str(mark_prefix, mark_name), size = mark_size_fit, font = mark_font);
}

module mark_prefix_2d() {
    if (mark_name != "")
        translate([text_x, field_y + field - mark_size_fit])
            offset(delta = mark_bolden) text(mark_prefix, size = mark_size_fit, font = mark_font);
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
    if (tap_label != "")
        translate([max(tap_radii) + tap_stroke / 2 + tap_gap, -tap_label_mid])
            offset(delta = tap_bolden) text(tap_label, size = tap_size_fit, font = tap_font);
}

// The marker is laid out left to right around the dot at the origin, then turned to read upwards
// and centered in the strip right of the QR code, or, on the back, in the
// same strip seen from behind, at x = qr_right_margin / 2. Without a label, the waves center alone.
module tap_place(x = card_w - qr_right_margin / 2, label = tap_label != "") {
    start = -tap_dot_d / 2;
    end = !label ? max(tap_radii) + tap_stroke / 2 : max(tap_radii) + tap_stroke / 2 + tap_gap + tap_label_len;
    translate([x, card_h / 2]) rotate(90) translate([-(start + end) / 2, 0]) children();
}

// The parts of the front's tap marker that go in the part `colour` names: the waves in
// tap_waves_color, the label in tap_label_color.
module front_tap_2d(colour) {
    if (nfc_enabled) tap_place() {
        if (tap_waves_color == colour) tap_icon_2d();
        if (tap_label_color == colour) tap_label_2d();
    }
}

// The same for the back tap mark, as seen from behind.
module back_tap_2d(colour) {
    with_label = back_tap_mark == "label" && tap_label != "";
    if (back_mark_on)
        tap_place(qr_right_margin / 2, with_label) {
            if (tap_waves_color == colour) tap_icon_2d();
            if (with_label && tap_label_color == colour) tap_label_2d();
        }
}

module accent_2d() {
    // The mark sits on the top edge of the QR field; the domain sits on its bottom edge.
    mark_prefix_2d();
    last_baseline = name_baseline - (len(name_lines) - 1) * name_size_fit * name_leading;
    translate([text_x, last_baseline - accent_gap - accent_h]) square([accent_w, accent_h]);
    // Without a tag the marker goes too; the QR code keeps its place, with even margins on three sides.
    front_tap_2d("accent");
    translate([text_x, field_y]) offset(delta = domain_bolden) text(domain_text, size = domain_size_fit, font = domain_font);
}

// ---- The back, drawn as seen from behind ----
back_pitch = back_size * back_leading;
back_dots_y = card_h - back_bar_top - back_dot_d / 2;
back_rule_y = back_dots_y - back_dot_d / 2 - back_rule_gap - back_rule_h;
back_top = back_rule_y - back_text_gap - back_size_fit; // first baseline, anchored under the bar

// The last line's descenders must keep at least the bar's margin from the bottom edge.
assert(!terminal || back_top - (len(back_lines) - 1) * back_pitch - 0.3 * back_size_fit >= back_bar_top,
       "the back's lines run off the bottom: shrink back_size or back_leading, or drop a line");

module back_chrome_view_2d() {
    if (terminal) for (i = [0 : 2]) translate([back_left + back_dot_d / 2 + i * back_dot_pitch, back_dots_y]) circle(d = back_dot_d, $fn = 48);
    if (terminal) translate([back_left, back_rule_y]) square([back_room, back_rule_h]);
    back_tap_2d("chrome");
}

// Plain style: each baseline measured down from the top of the first line's capitals, then the
// block centered on the card. The gap after the name scales with the name's fitted size.
function plain_step(k) = plain_lines[k - 1][2] ? plain_name_gap * plain_name_fit / plain_name_size : plain_gap;
plain_first = len(plain_lines) > 0 && plain_lines[0][2] ? plain_name_fit : plain_size_fit;
plain_baselines = [for (i = [0 : len(plain_lines) - 1])
    i == 0 ? plain_first : plain_first + qr_sum([for (k = [1 : i]) plain_step(k)])];
plain_height = len(plain_lines) == 0 ? 0 : plain_baselines[len(plain_lines) - 1] + 0.25 * plain_size_fit;
plain_top = (card_h + plain_height) / 2;

module plain_lines_2d(colour) {
    if (len(plain_lines) > 0) for (i = [0 : len(plain_lines) - 1])
        if (plain_lines[i][1] == colour)
            translate([back_left, plain_top - plain_baselines[i]])
                offset(delta = plain_bolden)
                    text(plain_lines[i][0], size = plain_lines[i][2] ? plain_name_fit : plain_size_fit, font = plain_font);
}

module back_line_2d(i, s, bolden = back_bolden) {
    translate([back_left, back_top - i * back_pitch])
        offset(delta = bolden) text(s, size = back_size_fit, font = back_font);
}

module back_accent_view_2d() {
    if (plain) plain_lines_2d("accent");
    if (terminal) terminal_accent_2d();
    back_tap_2d("accent");
}

module terminal_accent_2d() {
    for (i = [0 : len(back_lines) - 1])
        if (back_lines[i][0] != "") back_line_2d(i, back_lines[i][0], back_prompt_bolden);
    // Cursor block after the last prompt; mono advance is 0.6 em and an em is size / 0.73.
    last = len(back_lines) - 1;
    advance = 0.822 * back_size_fit;
    translate([back_left + len(str(back_lines[last][0], back_lines[last][1])) * advance, back_top - last * back_pitch - 0.3])
        square(back_cursor * back_size_fit / back_size);
}

module back_light_view_2d() {
    if (plain) plain_lines_2d("light");
    if (terminal) terminal_light_2d();
    back_tap_2d("light");
}

module terminal_light_2d() {
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
    difference() {
        mark_2d();
        mark_prefix_2d();
    }
    front_tap_2d("light");
}

// ---- 3D parts ----
// `extra` lets the cut through the body overshoot the outer face; the printed parts end flush.
module inlay(extra = 0) {
    translate([0, 0, card_t - inlay_t]) linear_extrude(inlay_t + extra) children();
}

module back_inlay(extra = 0) {
    if (back_inked) translate([0, 0, -extra]) linear_extrude(back_inlay_t + extra) from_behind() children();
}

module body() {
    difference() {
        linear_extrude(card_t) rounded_rect([card_w, card_h], corner_r);
        inlay(0.01) light_2d();
        inlay(0.01) accent_2d();
        inlay(0.01) front_tap_2d("chrome");
        back_inlay(0.01) back_light_view_2d();
        back_inlay(0.01) back_accent_view_2d();
        back_inlay(0.01) back_chrome_view_2d();
        if (nfc_enabled) translate([nfc_center[0], nfc_center[1], nfc_floor_t]) cylinder(d = pocket_d, h = pocket_depth);
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
    inlay() front_tap_2d("chrome");
    back_inlay() back_chrome_view_2d();
}

// Turned over about the card's long axis, so both faces still read correctly: a rotation, not a mirror.
module print_orientation() {
    if (face_down == "front") translate([0, card_h, card_t]) rotate([180, 0, 0]) children();
    else children();
}

print_orientation() {
    if (part == "body") body();
    else if (part == "light") light();
    else if (part == "accent") accent();
    else if (part == "chrome") chrome();
    else {
        color(card_color) body();
        color(light_color) light();
        color(accent_color) accent();
        color(window_bar_color) chrome();
    }
}
