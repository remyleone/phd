#!/bin/sh

(cd arbre_high_calibration_10; make TARGET=wismote run)
(cd arbre_high_calibration_25; make TARGET=wismote run)
(cd arbre_high_calibration_50; make TARGET=wismote run)
(cd arbre_high_calibration_75; make TARGET=wismote run)
(cd arbre_high_calibration_100; make TARGET=wismote run)

# (cd arbre_low_calibration_10; make TARGET=wismote run)
# (cd arbre_low_calibration_25; make TARGET=wismote run)
# (cd arbre_low_calibration_50; make TARGET=wismote run)
# (cd arbre_low_calibration_75; make TARGET=wismote run)
# (cd arbre_low_calibration_100; make TARGET=wismote run)


# (cd arbre_high_calibration; make run)
# (cd arbre_medium_calibration; make run)
# (cd arbre_low_calibration; make run)
# (cd arbre_high; make run)
# (cd arbre_medium; make run)
# (cd arbre_low; make run)
