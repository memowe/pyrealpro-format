"""
iReal Pro format data model.

This module defines the complete, immutable data model for the iReal Pro URL
format (``irealb://``).  All types are frozen dataclasses or enums so they are
hashable and safe to use as dictionary keys or in sets.

Protocol reference:
    https://www.irealpro.com/ireal-pro-custom-chord-chart-protocol

URL structure (after URL-decoding)::

    irealb://title=composer==style=key==<scrambled-chords>=feel=bpm=flag
             \\__________________________song 1__________________________/
             ===
             \\__________________________song 2__________________________/
             ...

Songs are separated by ``===``.  A playlist is a collection of songs obtained
from one ``.irealb`` file.

Chord-progression notation examples (unscrambled)::

    T44*A{C^7 |A-7 |D-9 |G7#5 }
    *B[Bh7 |Bb7(A7b9) |sEh,A7,|Y|lD-/C ]
    N1D-/F Z
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

# ── Notes & accidentals ───────────────────────────────────────────────────────


class NoteName(StrEnum):
    """The seven diatonic note names, as they appear in the format."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


class Accidental(StrEnum):
    """Sharp (``#``) or flat (``b``) modifier for a note or chord root."""

    SHARP = "#"
    FLAT = "b"


# ── Chord quality ─────────────────────────────────────────────────────────────


class Quality(StrEnum):
    """
    The triad quality – describes the **third** of the chord, not the seventh.

    The ``^`` symbol in the wire format (e.g. ``C^7``, ``C-^7``) is *not* a
    quality: it indicates that the seventh is major rather than minor.  It is
    encoded separately as :attr:`Chord.major_seventh`.

    Examples (quality token only, before any seventh modifier):
        - ``MAJOR``    → ``C``, ``C7``, ``C^7``   (large third, major scale)
        - ``MINOR``    → ``C-``, ``C-7``, ``C-^7`` (small third, minor scale)
        - ``HALF_DIM`` → ``Ch7``   (m7♭5, half-diminished / ø; wire token is ``h``)
        - ``DIM``      → ``Co7``   (fully diminished)
        - ``AUG``      → ``C+``, ``C+7``  (augmented fifth)
        - ``SUS4``     → ``Csus``, ``G7sus``  (third replaced by perfect 4th)
        - ``SUS2``     → ``C2``, ``Csus2``   (third replaced by major 2nd)
    """

    MAJOR = ""
    MINOR = "-"
    HALF_DIM = "h"  # ø in standard notation; iReal Pro wire token is "h"
    DIM = "o"
    AUG = "+"
    SUS4 = "sus"
    SUS2 = "2"


# ── Chord alterations ─────────────────────────────────────────────────────────


class Alteration(StrEnum):
    """
    Individual tension alterations that can appear after the chord extension.

    Multiple alterations may appear on a single chord.  In the format they
    follow the extension number directly, e.g. ``G7b9#11``.

    Note: suspended-second (``sus2``/``C2``) is modelled as
    :attr:`Quality.SUS2`, not as an alteration, because it replaces the
    third entirely – just like :attr:`Quality.SUS4`.
    """

    FLAT_5 = "b5"
    SHARP_5 = "#5"
    FLAT_9 = "b9"
    SHARP_9 = "#9"
    SHARP_11 = "#11"
    FLAT_13 = "b13"
    ALT = "alt"
    ADD_9 = "add9"
    ADD_11 = "add11"


# ── Chord display size ────────────────────────────────────────────────────────


class ChordSize(StrEnum):
    """
    Display-size hint preceding a chord in the progression string.

    - ``NORMAL`` – no prefix
    - ``SMALL``  – prefix ``s`` (renders chord smaller on the chart)
    - ``LARGE``  – prefix ``l`` (renders chord larger on the chart)
    """

    NORMAL = ""
    SMALL = "s"
    LARGE = "l"


# ── Chord ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Chord:
    """
    A single chord symbol, fully parsed.

    Attributes:
        root:            The root note name (e.g. ``NoteName.C``).
        accidental:      Optional sharp or flat on the root.
        quality:         The chord quality (major, minor, half-dim, …).
        extension:       Numeric extension: 4, 5, 6, 7, 9, 11, 13, or
                         ``None`` for a plain triad.
        major_seventh:   When ``True``, the seventh (if any) is major rather
                         than minor.  Serialises to ``^`` between the quality
                         token and the extension, e.g. ``C^7``, ``C-^7``.
                         Has no effect without an extension (unless the chart
                         uses bare ``^`` to indicate open voicing).
        alterations:     Tuple of applied tension alterations in the order
                         they appear in the format string.
        sub_chord:       A substitution chord written in parentheses after
                         this chord, e.g. ``Bb7(A7b9)`` → sub_chord is
                         the ``A7b9`` :class:`Chord`.
        bass_note:       Root of the bass note in a slash chord.
        bass_accidental: Optional accidental on the bass note.
        size:            Display-size rendering hint.

    Examples::

        Chord(NoteName.C)                                           # C
        Chord(NoteName.C, extension=7)                             # C7  (dominant)
        Chord(NoteName.C, major_seventh=True, extension=7)         # C^7 (major 7th)
        Chord(NoteName.A, quality=Quality.MINOR, extension=7)      # A-7
        Chord(NoteName.A, quality=Quality.MINOR,
              major_seventh=True, extension=7)                     # A-^7 (minor-major 7th)
        Chord(NoteName.G, extension=7,
              alterations=(Alteration.SHARP_5,))                   # G7#5
        Chord(NoteName.B, accidental=Accidental.FLAT,
              quality=Quality.HALF_DIM, extension=7)               # Bbh7
        Chord(NoteName.D, quality=Quality.MINOR,
              bass_note=NoteName.C)                                # D-/C
        Chord(NoteName.C, quality=Quality.SUS4)                    # Csus
        Chord(NoteName.C, quality=Quality.SUS2)                    # C2 (Csus2)
    """

    root: NoteName
    accidental: Accidental | None = None
    quality: Quality = Quality.MAJOR
    major_seventh: bool = False
    extension: int | None = None
    alterations: tuple[Alteration, ...] = ()
    sub_chord: Chord | None = None
    bass_note: NoteName | None = None
    bass_accidental: Accidental | None = None
    size: ChordSize = ChordSize.NORMAL


# ── Bar lines ─────────────────────────────────────────────────────────────────


class BarlineKind(StrEnum):
    """
    The kind of bar line / bracket as it appears in the format.

    ============= ======= ================================================
    Member        Symbol  Meaning
    ============= ======= ================================================
    ``SINGLE``    ``|``   Regular bar line
    ``DOUBLE``    ``||``  Thin–thin double bar line
    ``FINAL``     ``Z``   Final (thin–thick) double bar line
    ``REPEAT_OPEN``  ``{``  Begin-repeat sign (𝄆)
    ``REPEAT_CLOSE`` ``}``  End-repeat sign (𝄇)
    ``SECTION_OPEN`` ``[``  Open section bracket
    ``SECTION_CLOSE`` ``]`` Close section bracket
    ============= ======= ================================================
    """

    SINGLE = "|"
    DOUBLE = "||"
    FINAL = "Z"
    REPEAT_OPEN = "{"
    REPEAT_CLOSE = "}"
    SECTION_OPEN = "["
    SECTION_CLOSE = "]"


@dataclass(frozen=True)
class Barline:
    """
    A bar line or bracket symbol.

    Using a single :class:`Barline` node with a :class:`BarlineKind` field
    instead of seven separate classes makes exhaustive ``match`` / ``case``
    dispatch over the full progression much more readable::

        match cell:
            case Barline(kind=BarlineKind.REPEAT_OPEN):  ...
            case Barline(kind=BarlineKind.REPEAT_CLOSE): ...
            case Barline():                              ...  # any other

    Attributes:
        kind: Which kind of bar line or bracket this is.
    """

    kind: BarlineKind


# ── Section / rehearsal marks ─────────────────────────────────────────────────


class SectionKind(StrEnum):
    """
    The letter label used in a rehearsal-mark / section header.

    - ``A``–``D`` are the standard sections.
    - ``V`` is for a *verse* (``*v``).
    - ``I`` is for an *intro* (``*i``).
    """

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    V = "v"
    I = "i"


@dataclass(frozen=True)
class SectionMark:
    """
    ``*A``, ``*B``, ``*C``, ``*D``, ``*v``, ``*i`` – rehearsal section label.

    Attributes:
        kind: Which section this mark refers to.
    """

    kind: SectionKind


@dataclass(frozen=True)
class TimeSignature:
    """
    ``T44``, ``T34``, ``T54``, ``T64``, ``T22``, ``T32``, ``T68``, ``T98``,
    ``T128`` – change of time signature.

    The format encodes time signature as ``T`` followed by the numerator
    digits and then the denominator digit (``4`` or ``8``).  For example,
    ``T128`` encodes 12/8 (numerator ``12``, denominator ``8``).

    Attributes:
        numerator:   Beats per measure (e.g. 3 for 3/4).
        denominator: Beat unit (4 for quarter notes, 8 for eighth notes).

    Examples::

        TimeSignature.from_token("T44")   # TimeSignature(4,  4)
        TimeSignature.from_token("T34")   # TimeSignature(3,  4)
        TimeSignature.from_token("T128")  # TimeSignature(12, 8)
        TimeSignature(6, 8).to_token()    # "T68"
    """

    numerator: int
    denominator: int

    @classmethod
    def from_token(cls, token: str) -> TimeSignature:
        """
        Parse a wire-format time-signature token into a :class:`TimeSignature`.

        The token must start with ``T``.  The last character is the
        denominator (``4`` or ``8``); everything between ``T`` and the last
        character is the numerator.

        Args:
            token: A string of the form ``"T<numerator><denominator>"``,
                   e.g. ``"T44"``, ``"T34"``, ``"T128"``.

        Returns:
            The corresponding :class:`TimeSignature`.

        Raises:
            :exc:`ValueError`: If the token does not match the expected format.
        """
        if not token.startswith("T") or len(token) < 3:  # noqa: PLR2004
            raise ValueError(f"Invalid time signature token: {token!r}")
        try:
            denominator = int(token[-1])
            numerator = int(token[1:-1])
        except ValueError as exc:
            raise ValueError(f"Invalid time signature token: {token!r}") from exc
        return cls(numerator, denominator)

    def to_token(self) -> str:
        """
        Serialise this :class:`TimeSignature` back to its wire-format token.

        Returns:
            A string of the form ``"T<numerator><denominator>"``,
            e.g. ``"T44"`` or ``"T128"``.
        """
        return f"T{self.numerator}{self.denominator}"


@dataclass(frozen=True)
class Ending:
    """
    ``N1``, ``N2``, ``N3`` – numbered repeat ending bracket.

    Attributes:
        number: Which ending this is (1, 2, or 3).

    Examples::

        Ending.from_token("N1")  # Ending(1)
        Ending(2).to_token()     # "N2"
    """

    number: Literal[1, 2, 3]

    @classmethod
    def from_token(cls, token: str) -> Ending:
        """
        Parse a wire-format ending token into an :class:`Ending`.

        Args:
            token: One of ``"N1"``, ``"N2"``, ``"N3"``.

        Returns:
            The corresponding :class:`Ending`.

        Raises:
            :exc:`ValueError`: If the token is not a valid ending.
        """
        match token:
            case "N1":
                return cls(1)
            case "N2":
                return cls(2)
            case "N3":
                return cls(3)
            case _:
                raise ValueError(f"Invalid ending token: {token!r}")

    def to_token(self) -> str:
        """
        Serialise this :class:`Ending` back to its wire-format token.

        Returns:
            ``"N1"``, ``"N2"``, or ``"N3"``.
        """
        return f"N{self.number}"


# ── Structural markers ────────────────────────────────────────────────────────


class MarkerKind(StrEnum):
    """
    A single-token structural or layout marker in the progression.

    =============== ======= ================================================
    Member          Symbol  Meaning
    =============== ======= ================================================
    ``CODA``        ``Q``   Coda symbol (𝄌); D.C./D.S. al Coda jump target
    ``SEGNO``       ``S``   Segno symbol (𝄋); D.S. jump target
    ``FERMATA``     ``f``   Fermata over the preceding chord
    ``NO_CHORD``    ``n``   Explicit *no chord* / tacet
    ``REPEAT_BAR``  ``x``   Simile / repeat-previous-bar (𝄎)
    ``BREAK``       ``Y``   Empty spacer; forces a visual gap on the chart
    ``PAUSE``       ``p``   Rest / silence for one beat position
    ``PUSH``        ``,``   Syncopation push (chord anticipated before beat)
    =============== ======= ================================================
    """

    CODA = "Q"
    SEGNO = "S"
    FERMATA = "f"
    NO_CHORD = "n"
    REPEAT_BAR = "x"
    BREAK = "Y"
    PAUSE = "p"
    PUSH = ","


@dataclass(frozen=True)
class Marker:
    """
    A single-token structural or layout marker.

    Consolidating all atomic markers into one node with a :class:`MarkerKind`
    field makes ``match`` / ``case`` dispatch concise::

        match cell:
            case Marker(kind=MarkerKind.CODA):     ...
            case Marker(kind=MarkerKind.NO_CHORD): ...
            case Marker():                         ...  # any other marker

    Attributes:
        kind: Which marker this cell represents.
    """

    kind: MarkerKind


# ── Text annotations ──────────────────────────────────────────────────────────


class NavigationKind(StrEnum):
    """
    Well-known navigation directives that appear as inline text annotations.

    These values are the most common contents of :class:`TextAnnotation` nodes,
    but the format allows arbitrary text so this enum is not exhaustive.
    Use it as a convenience when constructing or pattern-matching known
    navigation directives.

    ============== ============ ================================================
    Member         Text         Meaning
    ============== ============ ================================================
    ``DC``         ``D.C.``     *Da Capo* – jump back to the beginning
    ``DS``         ``D.S.``     *Dal Segno* – jump back to the segno (𝄋)
    ``DC_AL_CODA`` ``D.C. al Coda``  *Da Capo al Coda*
    ``DS_AL_CODA`` ``D.S. al Coda``  *Dal Segno al Coda*
    ``FINE``       ``Fine``     Marks the actual end of the piece
    ============== ============ ================================================
    """

    DC = "D.C."
    DS = "D.S."
    DC_AL_CODA = "D.C. al Coda"
    DS_AL_CODA = "D.S. al Coda"
    FINE = "Fine"


@dataclass(frozen=True)
class TextAnnotation:
    """
    ``<text>`` – an inline text annotation embedded in the progression.

    In the wire format these appear as arbitrary strings enclosed in angle
    brackets, e.g. ``<Fine>``, ``<D.C. al Coda>``, ``<Play 3x>``.
    The :class:`NavigationKind` enum lists the common navigation values, but
    the content is open-ended.

    Attributes:
        text: The annotation text, without the surrounding ``<`` and ``>``.

    Examples::

        TextAnnotation(NavigationKind.FINE)       # <Fine>
        TextAnnotation(NavigationKind.DC_AL_CODA) # <D.C. al Coda>
        TextAnnotation("Play 3x")                 # <Play 3x>
    """

    text: str


# ── Cell union type ───────────────────────────────────────────────────────────

type Cell = Chord | Barline | SectionMark | TimeSignature | Ending | Marker | TextAnnotation
"""
Union of all valid chord-progression cell types.

The seven members cover the full iReal Pro progression language:

- :class:`Chord`          – a chord symbol
- :class:`Barline`        – any bar line or bracket (7 kinds via :class:`BarlineKind`)
- :class:`SectionMark`    – a rehearsal mark (``*A``, ``*B``, …)
- :class:`TimeSignature`  – a time-signature change (``T44``, ``T34``, …)
- :class:`Ending`         – a numbered repeat ending (``N1``, ``N2``, ``N3``)
- :class:`Marker`         – any single-token structural symbol (8 kinds via :class:`MarkerKind`)
- :class:`TextAnnotation` – an inline text annotation (``<Fine>``, ``<D.C.>``, …)

Use ``match`` / ``case`` for exhaustive dispatch::

    def render(cell: Cell) -> str:
        match cell:
            case Chord():           ...
            case Barline():         ...
            case SectionMark():     ...
            case TimeSignature():   ...
            case Ending():          ...
            case Marker():          ...
            case TextAnnotation():  ...

.. note::

    The ``cells`` sequence is intentionally a *flat* list that mirrors the
    wire format directly.  Repeat sections (``{ … }`` with ``N1``/``N2``
    endings) are represented by their constituent :class:`Barline` and
    :class:`Ending` tokens in order.  A future tree-structured AST could
    collapse these into dedicated ``RepeatSection`` nodes for easier
    traversal and analysis, but that would require a two-pass parse and is
    deferred until there is a concrete need.
"""


# ── Key ───────────────────────────────────────────────────────────────────────


class Mode(StrEnum):
    """Tonal mode of the key."""

    MAJOR = "major"
    MINOR = "minor"


@dataclass(frozen=True)
class Key:
    """
    The key of a song.

    In the format the key is encoded as a note name with an optional flat or
    sharp followed by a ``-`` for minor, e.g. ``Bb``, ``D-``, ``F#``.

    Attributes:
        root:        The tonic note.
        accidental:  Optional ♭ or ♯ on the tonic.
        mode:        Major or minor.

    Examples::

        Key(NoteName.C)                                        # C major
        Key(NoteName.B, Accidental.FLAT)                       # B♭ major
        Key(NoteName.D, mode=Mode.MINOR)                       # D minor
        Key(NoteName.F, Accidental.SHARP, Mode.MINOR)          # F♯ minor
    """

    root: NoteName
    accidental: Accidental | None = None
    mode: Mode = Mode.MAJOR


# ── Song ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Song:
    """
    A single lead sheet / chord chart.

    Attributes:
        title:    Song title.
        composer: Composer name, typically ``"LastName FirstName"``.
        style:    Broad genre label, e.g. ``"Medium Swing"``, ``"Bossa Nova"``.
        key:      The key of the song.
        feel:     Sub-style / playback feel string, e.g. ``"Jazz-Swing"``,
                  ``"Pop-Ballad"``.  May be empty.
        bpm:      Playback tempo in beats per minute (0 means "not set").
        cells:    The full chord progression as a flat sequence of cells.

    The ``cells`` sequence is the canonical representation of the progression.
    Bar lines, section marks, repeat signs etc. are interleaved with chords.
    """

    title: str
    composer: str
    style: str
    key: Key
    feel: str
    bpm: int
    cells: tuple[Cell, ...]


# ── Playlist ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Playlist:
    """
    A named collection of songs stored in a single ``.irealb`` file.

    Attributes:
        name:  The playlist name (typically derived from the filename).
        songs: The ordered collection of songs.

    The wire format encodes a playlist as::

        irealb://<song1>===<song2>===…===<songN>

    where each song is a ``=``-delimited field string (10 fields in the
    current format).
    """

    name: str
    songs: tuple[Song, ...]


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    # Notes
    "NoteName",
    "Accidental",
    # Chord
    "Quality",
    "Alteration",
    "ChordSize",
    "Chord",
    # Bar lines
    "BarlineKind",
    "Barline",
    # Section / rehearsal marks
    "SectionKind",
    "SectionMark",
    # Time signature
    "TimeSignature",
    # Repeat endings
    "Ending",
    # Structural markers
    "MarkerKind",
    "Marker",
    # Text annotations
    "NavigationKind",
    "TextAnnotation",
    # Cell union type
    "Cell",
    # Key & song
    "Mode",
    "Key",
    "Song",
    "Playlist",
]
