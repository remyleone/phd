#!/bin/sh

fig_dir="figsrc"

# Make graphviz

for f in alice bob albert trie
do
    dot -T svg ${fig_dir}/${f}.dot > ${fig_dir}/${f}.svg
done

# Extract layers according to svg metadata
# Inkscape : ctrl maj d > Metadata > write the animations
#
# Example: you have 2 layers "OneCircle" and "TwoRectangles"
# You want 3 slides:
#
# OneCircle
# OneCircle;TwoRectangles
# TwoRectangles

for fig in goal
do
    echo "python exportlayers.py ${fig_dir}/${fig}.svg"
    python exportlayers.py ${fig_dir}/${fig}.svg
done

exit 0
