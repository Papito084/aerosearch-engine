"""Unit tests for Porter Stemmer algorithm."""

from aerosearch.core.text.stemmer import PorterStemmer


def test_stemmer_plurals_and_endings() -> None:
    stemmer = PorterStemmer()
    assert stemmer.stem("caresses") == "caress"
    assert stemmer.stem("ponies") == "poni"
    assert stemmer.stem("ties") == "ti"
    assert stemmer.stem("cats") == "cat"


def test_stemmer_step1b() -> None:
    stemmer = PorterStemmer()
    assert stemmer.stem("feed") == "feed"
    assert stemmer.stem("agreed") == "agre"
    assert stemmer.stem("motoring") == "motor"
    assert stemmer.stem("sing") == "sing"


def test_stemmer_step2_to_step5() -> None:
    stemmer = PorterStemmer()
    assert stemmer.stem("relational") == "relat"
    assert stemmer.stem("conditional") == "condit"
    assert stemmer.stem("rational") == "ration"
    assert stemmer.stem("valency") == "valenc"
    assert stemmer.stem("hesitancy") == "hesit"
    assert stemmer.stem("digitizer") == "digit"
    assert stemmer.stem("allowance") == "allow"
    assert stemmer.stem("inference") == "infer"
    assert stemmer.stem("airliner") == "airlin"
    assert stemmer.stem("probate") == "probat"
    assert stemmer.stem("rate") == "rate"
    assert stemmer.stem("cease") == "ceas"


def test_stemmer_short_words() -> None:
    stemmer = PorterStemmer()
    assert stemmer.stem("a") == "a"
    assert stemmer.stem("to") == "to"
    assert stemmer.stem("in") == "in"
