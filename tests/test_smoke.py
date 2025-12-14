def test_smoke():
    assert True


def test_imports():
    import pypdf  # noqa: F401
    import yaml  # noqa: F401

    assert hasattr(pypdf, "PdfReader")
    assert hasattr(pypdf, "PdfWriter")
