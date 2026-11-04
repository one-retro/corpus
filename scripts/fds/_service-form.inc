# The Nintendo Disk Writer service form (ナマエ トウロク), shared by several
# games: type アイウ in the name field and go to the bottom row. The script
# that includes this then moves right to the "save" cell (10 cells in F1
# Race, 11 in the Golf games) and presses A.
press a 6           # ア (cursor starts on ア)
wait 30
press right 6
wait 20
press a 6           # イ
wait 30
press right 6
wait 20
press a 6           # ウ
wait 30
press up 6          # bottom row (ヒ)
wait 20
