from pathlib import Path

def test_absolute_path_is_importable():
    try:
        from absolute_paths import LUDWIG_ROOT_DIR
        assert str(LUDWIG_ROOT_DIR).endswith('ludwig')

    except ImportError as exc:
        raise Exception(
            "If this error occurs, something is wrong IN CONFTEST.PY - not the "
            "tested function - with adding ludwig's root dir to the path."
        ) from exc
