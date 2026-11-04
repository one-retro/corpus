# Croc: power-on to the SAVE GAME choice on the 1-1 map. Both cores show
# PRESS START BUTTON from about frame 2400 to 3300.
wait 2700
press start          # title -> START GAME / OPTIONS
wait 400
press start          # START GAME -> map 1-1: START LEVEL / OPTIONS / SAVE GAME / QUIT GAME
wait 900
press down
wait 30
press down
wait 30
shot map             # cursor on SAVE GAME
press b              # A
wait 400
