# pyrealpro-format

Modern reference implementation of the iReap Pro lead sheet format.

## Semi-formal technical documentation

There's an informal description of the [iReal Pro custom chord chart protocol](https://www.irealpro.com/ireal-pro-custom-chord-chart-protocol) on the app's website. [Old version from the web archive](https://web.archive.org/web/20240621162423/https://www.irealpro.com/ireal-pro-file-format).

## Big-ass corpus of standards in iReal Pro format

https://www.irealpro.com/main-playlists/

Parts of this corpus are used for roundtrip tests of this library. The corpus is delivered as `iealb://` urls which contain copyrighted music data. That's why it is not saved in the repository but can be loaded dynamically using the [Makefile](Makefile).

## Previous projects

These previous projects have made valuable contributions by making the intriguing format of the wonderful iReal Pro app more accessible to developers and musicians:

- [drs251/**pyRealParser**](https://github.com/drs251/pyRealParser)  
  A minimal, older Python library that parses iReal Pro URLs and chord progressions into basic Python objects. It primarily reads metadata and simple chord strings, but lacks support for the full current specification and hasn’t been actively maintained.
- [splendidtoad/**pyrealpro**](https://github.com/splendidtoad/pyrealpro) ([PyPI](https://pypi.org/project/pyrealpro/))  
  A Python library focused on creating and serializing iReal Pro songs into importable URLs, providing a clear object model for Songs, Measures, and Chords. It does not parse existing songs and only supports exporting, with limited coverage of advanced iReal Pro syntax, but offers a clean foundation for programmatic song generation.

## Author and license

(c) 2026 [Mirko Westermeier](https://github.com/memowe)

Released under the MIT license. See [LICENSE](LICENSE) for details.
