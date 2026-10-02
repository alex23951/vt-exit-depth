#!/bin/bash
# Open a wedge run's membrane voltage in Meshalyzer (software OpenGL for WSL).
# Usage: analysis/show_vm.sh endo    (or: epi)
cd "$(dirname "$0")/../runs" || exit 1
LIBGL_ALWAYS_SOFTWARE=1 meshalyzer meshes/2026-09-27_SqYWJrKIDE/block "2026-09-27_ext_${1:-endo}/vm.igb" ../sims/07_extracellular/view_vm.mshz
