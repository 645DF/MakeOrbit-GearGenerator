"""Autodesk Fusion entry point for MakeOrbit GearGenerator."""

try:
    from . import addin
except ImportError:
    import addin


def run(context):
    addin.run(context)


def stop(context):
    addin.stop(context)
