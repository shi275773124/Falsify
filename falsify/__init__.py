"""falsify: adversarial review for AI-era work.

Public package surface. The CLI lives in ``falsify.cli`` — re-exported here so
``from falsify import X`` keeps working for existing tests, web server, and the
console-script entry point. ``falsify.cli`` is pure stdlib (no numpy), so eager
import keeps ``import falsify`` quant-free. The quant gate lives in
``falsify.quant`` / ``falsify.quant_gate`` and requires the ``[quant]`` extra.
"""

VERSION = "0.6.0"

from falsify.cli import *  # noqa: F401,F403 — re-export CLI public API (pure stdlib, numpy-free)
from falsify.cli import main  # explicit, for console-script entry point
