from distutils.extension import Extension

from Cython.Build import build_ext, cythonize


def build(setup_kwargs):
    """Build extension modules."""
    setup_kwargs.update({
        'ext_modules': cythonize(
            [
                Extension("credis.base", ["credis/base.pyx"]),
                Extension("credis.geventpool", ["credis/geventpool.pyx"]),
            ],
        ),
        'cmdclass': {'build_ext': build_ext}
    })
