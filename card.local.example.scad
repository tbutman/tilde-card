// Your own card, for build.sh. Copy this file to card.local.scad (git-ignored) and change the
// values: each line overrides that setting in card.scad, and build.sh builds the result into
// out/local/ (also ignored), next to the Jane Doe sample in out/. Leave out any line to keep
// card.scad's default. One `setting = value;` per line, as in card.scad.
first_name = "Jane";
last_name = "Doe";
handle = "janedoe";
qr_code_link = "https://example.com";
website_on_card = "example.com";
back_style = "terminal";
terminal_command = "whoami";
back_line_1 = "jane doe";
back_line_2 = "product designer";
back_line_3 = "jane@example.com";
