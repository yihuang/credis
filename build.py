from distutils.extension import Extension

try:
    from Cython.Build import build_ext, cythonize
except ImportError:
    def build(_):
        pass
else:
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
