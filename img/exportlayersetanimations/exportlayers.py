#!/usr/bin/env python

"""
Export selected layers from Inkscape SVG.
"""

import sys, codecs
from xml.dom import minidom


def export_layers(src):
    """
    Export selected layers of SVG in the file `src` to the file `dest`.

    :arg  str    src:  path of the source SVG file.
    :arg  str   dest:  path to export SVG file.
    :arg  list  hide:  layers to hide. each element is a string.
    :arg  list  show:  layers to show. each element is a string.

    """
    svg = minidom.parse(open(src))
    g_hide = []
    g_show = []
    all_frames, = svg.getElementsByTagName("dc:description")
    frames = all_frames.firstChild.data.split('\n')
    for i, frame in enumerate(frames):
        layers = frame.split(";")
        
        for g in svg.getElementsByTagName("g"):
            if g.attributes.has_key("inkscape:label"):
                label = g.attributes["inkscape:label"].value
                if label in layers:
                    g.attributes['style'] = 'display:inline'
                else:
                    g.attributes['style'] = 'display:none'
        export = svg.toxml()
        
        dest = "%s-%d.svg" % (src[:-4], i)
        
        codecs.open(dest, "w", encoding="utf8").write(export)


def main():
    export_layers(sys.argv[1])


if __name__ == '__main__':
    main()
