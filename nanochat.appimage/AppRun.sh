#!/bin/bash
set -e

export APPDIR="${APPDIR:-$(dirname "$(readlink -f "${BASH_SOURCE[0]}")}"
export PATH="${APPDIR}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${APPDIR}/opt/nanogpt-chat:${APPDIR}:${PYTHONPATH}"
exec python3 -m nanogpt_chat.main "$@"
