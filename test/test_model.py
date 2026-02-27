"""
Tests for the data model (pyrealpro_format.model).

These are unit tests that verify the model types behave correctly:
immutability, equality, hashing, and structural properties.
Property-based tests (Hypothesis) will be added once the serializer exists.
"""

import pytest
from typing import assert_never
from pyrealpro_format.model import (
    Accidental,
    Alteration,
    Barline,
    BarlineKind,
    Chord,
    ChordSize,
    Ending,
    Key,
    Marker,
    MarkerKind,
    Mode,
    NavigationKind,
    NoteName,
    Playlist,
    Quality,
    SectionKind,
    SectionMark,
    Song,
    TextAnnotation,
    TimeSignature,
)

# ── Chord ─────────────────────────────────────────────────────────────────────


class TestChord:
    def test_plain_major_triad(self) -> None:
        c = Chord(NoteName.C)
        assert c.root == NoteName.C
        assert c.accidental is None
        assert c.quality == Quality.MAJOR
        assert c.major_seventh is False
        assert c.extension is None
        assert c.alterations == ()
        assert c.sub_chord is None
        assert c.bass_note is None
        assert c.bass_accidental is None
        assert c.size == ChordSize.NORMAL

    def test_minor_seventh(self) -> None:
        # A-7
        chord = Chord(NoteName.A, quality=Quality.MINOR, extension=7)
        assert chord.quality == Quality.MINOR
        assert chord.extension == 7

    def test_major_seventh(self) -> None:
        # C^7 – same Quality.MAJOR triad, but major_seventh=True
        chord = Chord(NoteName.C, major_seventh=True, extension=7)
        assert chord.quality == Quality.MAJOR
        assert chord.major_seventh is True
        assert chord.extension == 7

    def test_minor_major_seventh(self) -> None:
        # A-^7 – minor triad with major seventh
        chord = Chord(
            NoteName.A, quality=Quality.MINOR, major_seventh=True, extension=7
        )
        assert chord.quality == Quality.MINOR
        assert chord.major_seventh is True

    def test_half_diminished_seventh(self) -> None:
        # Bh7
        chord = Chord(NoteName.B, quality=Quality.HALF_DIM, extension=7)
        assert chord.quality == Quality.HALF_DIM

    def test_altered_dominant(self) -> None:
        # G7#5
        chord = Chord(
            NoteName.G,
            extension=7,
            alterations=(Alteration.SHARP_5,),
        )
        assert Alteration.SHARP_5 in chord.alterations

    def test_slash_chord(self) -> None:
        # D-/C
        chord = Chord(
            NoteName.D,
            quality=Quality.MINOR,
            bass_note=NoteName.C,
        )
        assert chord.bass_note == NoteName.C
        assert chord.bass_accidental is None

    def test_slash_chord_with_flat_bass(self) -> None:
        # C/Bb
        chord = Chord(
            NoteName.C,
            bass_note=NoteName.B,
            bass_accidental=Accidental.FLAT,
        )
        assert chord.bass_accidental == Accidental.FLAT

    def test_sub_chord(self) -> None:
        # Bb7(A7b9)
        inner = Chord(
            NoteName.A,
            extension=7,
            alterations=(Alteration.FLAT_9,),
        )
        outer = Chord(
            NoteName.B,
            accidental=Accidental.FLAT,
            extension=7,
            sub_chord=inner,
        )
        assert outer.sub_chord is inner
        assert outer.sub_chord is not None
        assert outer.sub_chord.root == NoteName.A

    def test_small_chord(self) -> None:
        # sEh (small half-dim E)
        chord = Chord(NoteName.E, quality=Quality.HALF_DIM, size=ChordSize.SMALL)
        assert chord.size == ChordSize.SMALL

    def test_large_chord(self) -> None:
        chord = Chord(NoteName.D, quality=Quality.MINOR, size=ChordSize.LARGE)
        assert chord.size == ChordSize.LARGE

    def test_frozen_immutability(self) -> None:
        chord = Chord(NoteName.C)
        with pytest.raises(Exception):
            chord.root = NoteName.G  # type: ignore[misc]

    def test_equality_and_hashing(self) -> None:
        a = Chord(NoteName.C, quality=Quality.MINOR, extension=7)
        b = Chord(NoteName.C, quality=Quality.MINOR, extension=7)
        assert a == b
        assert hash(a) == hash(b)
        assert len({a, b}) == 1

    def test_inequality(self) -> None:
        a = Chord(NoteName.C, extension=7)
        b = Chord(NoteName.G, extension=7)
        assert a != b


# ── Key ───────────────────────────────────────────────────────────────────────


class TestKey:
    def test_c_major(self) -> None:
        key = Key(NoteName.C)
        assert key.root == NoteName.C
        assert key.accidental is None
        assert key.mode == Mode.MAJOR

    def test_d_minor(self) -> None:
        key = Key(NoteName.D, mode=Mode.MINOR)
        assert key.mode == Mode.MINOR

    def test_b_flat_major(self) -> None:
        key = Key(NoteName.B, Accidental.FLAT)
        assert key.accidental == Accidental.FLAT
        assert key.mode == Mode.MAJOR

    def test_f_sharp_minor(self) -> None:
        key = Key(NoteName.F, Accidental.SHARP, Mode.MINOR)
        assert key.root == NoteName.F
        assert key.accidental == Accidental.SHARP
        assert key.mode == Mode.MINOR

    def test_frozen(self) -> None:
        key = Key(NoteName.C)
        with pytest.raises(Exception):
            key.root = NoteName.D  # type: ignore[misc]

    def test_hashable(self) -> None:
        keys = {Key(NoteName.C), Key(NoteName.C), Key(NoteName.G)}
        assert len(keys) == 2


# ── Barline ───────────────────────────────────────────────────────────────────


class TestBarline:
    def test_all_kinds_constructible(self) -> None:
        for kind in BarlineKind:
            bl = Barline(kind)
            assert bl.kind is kind

    def test_equality_same_kind(self) -> None:
        assert Barline(BarlineKind.SINGLE) == Barline(BarlineKind.SINGLE)

    def test_inequality_different_kind(self) -> None:
        assert Barline(BarlineKind.SINGLE) != Barline(BarlineKind.DOUBLE)

    def test_frozen(self) -> None:
        bl = Barline(BarlineKind.SINGLE)
        with pytest.raises(Exception):
            bl.kind = BarlineKind.FINAL  # type: ignore[misc]

    def test_hashable(self) -> None:
        barlines = {
            Barline(BarlineKind.SINGLE),
            Barline(BarlineKind.SINGLE),
            Barline(BarlineKind.FINAL),
        }
        # Two distinct kinds → two elements after deduplication
        assert len(barlines) == 2

    def test_kind_string_values(self) -> None:
        # StrEnum values match the wire-format tokens
        assert BarlineKind.SINGLE.value == "|"
        assert BarlineKind.DOUBLE.value == "||"
        assert BarlineKind.FINAL.value == "Z"
        assert BarlineKind.REPEAT_OPEN.value == "{"
        assert BarlineKind.REPEAT_CLOSE.value == "}"
        assert BarlineKind.SECTION_OPEN.value == "["
        assert BarlineKind.SECTION_CLOSE.value == "]"

    def test_pattern_matching(self) -> None:
        cell = Barline(BarlineKind.REPEAT_OPEN)
        match cell:
            case Barline(kind=BarlineKind.REPEAT_OPEN):
                matched = True
            case _:
                matched = False
        assert matched


# ── Marker ────────────────────────────────────────────────────────────────────


class TestMarker:
    def test_all_kinds_constructible(self) -> None:
        for kind in MarkerKind:
            m = Marker(kind)
            assert m.kind is kind

    def test_equality_same_kind(self) -> None:
        assert Marker(MarkerKind.CODA) == Marker(MarkerKind.CODA)

    def test_inequality_different_kind(self) -> None:
        assert Marker(MarkerKind.CODA) != Marker(MarkerKind.SEGNO)

    def test_frozen(self) -> None:
        m = Marker(MarkerKind.CODA)
        with pytest.raises(Exception):
            m.kind = MarkerKind.SEGNO  # type: ignore[misc]

    def test_hashable(self) -> None:
        # All 8 kinds produce distinct hashes; two CODA instances deduplicate
        markers = {Marker(k) for k in MarkerKind} | {Marker(MarkerKind.CODA)}
        assert len(markers) == len(MarkerKind)

    def test_kind_string_values(self) -> None:
        # StrEnum values match the wire-format tokens
        assert MarkerKind.CODA.value == "Q"
        assert MarkerKind.SEGNO.value == "S"
        assert MarkerKind.FERMATA.value == "f"
        assert MarkerKind.NO_CHORD.value == "n"
        assert MarkerKind.REPEAT_BAR.value == "x"
        assert MarkerKind.BREAK.value == "Y"
        assert MarkerKind.PAUSE.value == "p"
        assert MarkerKind.PUSH.value == ","

    def test_pattern_matching(self) -> None:
        cell = Marker(MarkerKind.NO_CHORD)
        match cell:
            case Marker(kind=MarkerKind.NO_CHORD):
                matched = True
            case _:
                matched = False
        assert matched


# ── SectionMark ───────────────────────────────────────────────────────────────


class TestSectionMark:
    def test_construction(self) -> None:
        mark = SectionMark(SectionKind.A)
        assert mark.kind == SectionKind.A

    def test_all_kinds(self) -> None:
        for kind in SectionKind:
            assert SectionMark(kind).kind is kind

    def test_inequality(self) -> None:
        assert SectionMark(SectionKind.A) != SectionMark(SectionKind.B)

    def test_kind_string_values(self) -> None:
        assert SectionKind.A.value == "A"
        assert SectionKind.B.value == "B"
        assert SectionKind.V.value == "v"
        assert SectionKind.I.value == "i"


# ── TimeSignature ─────────────────────────────────────────────────────────────────


class TestTimeSignatureAndEnding:
    def test_time_signature_fields(self) -> None:
        ts = TimeSignature(4, 4)
        assert ts.numerator == 4
        assert ts.denominator == 4

    def test_time_signature_inequality(self) -> None:
        assert TimeSignature(3, 4) != TimeSignature(4, 4)

    def test_from_token_quarter_note_denominator(self) -> None:
        assert TimeSignature.from_token("T44") == TimeSignature(4, 4)
        assert TimeSignature.from_token("T34") == TimeSignature(3, 4)
        assert TimeSignature.from_token("T54") == TimeSignature(5, 4)
        assert TimeSignature.from_token("T64") == TimeSignature(6, 4)
        assert TimeSignature.from_token("T22") == TimeSignature(2, 2)
        assert TimeSignature.from_token("T32") == TimeSignature(3, 2)

    def test_from_token_eighth_note_denominator(self) -> None:
        assert TimeSignature.from_token("T68") == TimeSignature(6, 8)
        assert TimeSignature.from_token("T98") == TimeSignature(9, 8)
        assert TimeSignature.from_token("T128") == TimeSignature(12, 8)

    def test_from_token_invalid(self) -> None:
        with pytest.raises(ValueError):
            TimeSignature.from_token("44")  # missing T prefix
        with pytest.raises(ValueError):
            TimeSignature.from_token("T")  # too short
        with pytest.raises(ValueError):
            TimeSignature.from_token("Txx")  # non-numeric

    def test_to_token_roundtrip(self) -> None:
        for token in ("T44", "T34", "T54", "T64", "T22", "T32", "T68", "T98", "T128"):
            assert TimeSignature.from_token(token).to_token() == token

    def test_ending_numbers(self) -> None:
        for n in (1, 2, 3):
            e = Ending(n)
            assert e.number == n

    def test_ending_inequality(self) -> None:
        assert Ending(1) != Ending(2)

    def test_ending_from_token(self) -> None:
        assert Ending.from_token("N1") == Ending(1)
        assert Ending.from_token("N2") == Ending(2)
        assert Ending.from_token("N3") == Ending(3)

    def test_ending_from_token_invalid(self) -> None:
        with pytest.raises(ValueError):
            Ending.from_token("N0")
        with pytest.raises(ValueError):
            Ending.from_token("N4")
        with pytest.raises(ValueError):
            Ending.from_token("1")

    def test_ending_to_token(self) -> None:
        assert Ending(1).to_token() == "N1"
        assert Ending(2).to_token() == "N2"
        assert Ending(3).to_token() == "N3"

    def test_ending_token_roundtrip(self) -> None:
        for token in ("N1", "N2", "N3"):
            assert Ending.from_token(token).to_token() == token


# ── TextAnnotation ───────────────────────────────────────────────────────────────


class TestTextAnnotation:
    def test_free_text(self) -> None:
        ann = TextAnnotation("Play 3x")
        assert ann.text == "Play 3x"

    def test_navigation_kind_as_text(self) -> None:
        # NavigationKind members are StrEnum – usable anywhere a str is accepted
        ann = TextAnnotation(NavigationKind.FINE)
        assert ann.text == "Fine"
        ann2 = TextAnnotation(NavigationKind.DC_AL_CODA)
        assert ann2.text == "D.C. al Coda"

    def test_all_navigation_kinds_constructible(self) -> None:
        for kind in NavigationKind:
            ann = TextAnnotation(kind)
            assert ann.text == kind.value

    def test_navigation_kind_string_values(self) -> None:
        assert NavigationKind.DC.value == "D.C."
        assert NavigationKind.DS.value == "D.S."
        assert NavigationKind.DC_AL_CODA.value == "D.C. al Coda"
        assert NavigationKind.DS_AL_CODA.value == "D.S. al Coda"
        assert NavigationKind.FINE.value == "Fine"

    def test_equality_and_hashing(self) -> None:
        a = TextAnnotation("Fine")
        b = TextAnnotation("Fine")
        assert a == b
        assert hash(a) == hash(b)
        assert len({a, b}) == 1

    def test_frozen(self) -> None:
        ann = TextAnnotation("Fine")
        with pytest.raises(Exception):
            ann.text = "D.C."  # type: ignore[misc]

    def test_pattern_matching(self) -> None:
        cell = TextAnnotation(NavigationKind.DC)
        match cell:
            case TextAnnotation(text="D.C."):
                matched = True
            case _:
                matched = False
        assert matched


# ── Song ──────────────────────────────────────────────────────────────────────


class TestSong:
    def _make_song(self) -> Song:
        return Song(
            title="Autumn Leaves",
            composer="Kosma Joseph",
            style="Medium Swing",
            key=Key(NoteName.G, mode=Mode.MINOR),
            feel="Jazz-Swing",
            bpm=120,
            cells=(
                TimeSignature(4, 4),
                SectionMark(SectionKind.A),
                Barline(BarlineKind.REPEAT_OPEN),
                Chord(NoteName.C, quality=Quality.MINOR, extension=7),
                Barline(BarlineKind.SINGLE),
                Chord(NoteName.F, extension=7),
                Barline(BarlineKind.SINGLE),
                Chord(
                    NoteName.B,
                    accidental=Accidental.FLAT,
                    major_seventh=True,
                    extension=7,
                ),
                Barline(BarlineKind.SINGLE),
                Chord(
                    NoteName.E,
                    accidental=Accidental.FLAT,
                    major_seventh=True,
                    extension=7,
                ),
                Barline(BarlineKind.REPEAT_CLOSE),
                Barline(BarlineKind.FINAL),
            ),
        )

    def test_construction(self) -> None:
        song = self._make_song()
        assert song.title == "Autumn Leaves"
        assert song.key.mode == Mode.MINOR
        assert song.bpm == 120
        assert len(song.cells) == 12

    def test_frozen(self) -> None:
        song = self._make_song()
        with pytest.raises(Exception):
            song.title = "Something else"  # type: ignore[misc]

    def test_cells_are_tuple(self) -> None:
        song = self._make_song()
        assert isinstance(song.cells, tuple)

    def test_exhaustive_cell_match(self) -> None:
        # Every cell in the progression is matched exhaustively via structural
        # pattern matching – proves the Cell union is sufficient at runtime.
        song = self._make_song()
        matched_count = 0
        for cell in song.cells:
            match cell:
                case Chord():
                    matched_count += 1
                case Barline():
                    matched_count += 1
                case SectionMark():
                    matched_count += 1
                case TimeSignature():
                    matched_count += 1
                case Ending():
                    matched_count += 1
                case Marker():
                    matched_count += 1
                case TextAnnotation():
                    matched_count += 1
                case _ as unreachable:
                    assert_never(unreachable)
        assert matched_count == len(song.cells)


# ── Playlist ──────────────────────────────────────────────────────────────────


class TestPlaylist:
    def test_empty_playlist(self) -> None:
        pl = Playlist(name="My Songs", songs=())
        assert pl.name == "My Songs"
        assert len(pl.songs) == 0
