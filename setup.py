from setuptools import setup
import os.path

# Get the version:
version = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.py')) as f: exec(f.read(), version)

setup(
    name = 'qstools',
    version = version['__version__'],
    description = 'SGE Job & Log Summarisation scripts',
    author = 'Alastair Droop',
    author_email = 'alastair.droop@gmail.com',
    url = 'https://github.com/alastair.droop/qstools',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Pre-processors',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3'
    ],
    py_modules = ['qsjobs', 'qslogs', 'version'],
    install_requires = [
    ],
    python_requires = '>=3',
    entry_points = {
        'console_scripts': [
            'qsjobs=qsjobs:main',
            'qslogs=qslogs:main'
        ]
    }
)
