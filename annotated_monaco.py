from pathlib import Path

import streamlit.components.v1 as components


_COMPONENT = components.declare_component(
    "annotated_monaco",
    path=str((Path(__file__).parent / "components" / "annotated_monaco").resolve()),
)


def st_annotated_monaco(
    value="",
    language="plaintext",
    height=620,
    annotations=None,
    features=None,
    path="file.txt",
    theme="vs-light",
    key=None,
):
    return _COMPONENT(
        value=value,
        language=language,
        height=height,
        annotations=annotations or [],
        features=features or [],
        path=path,
        theme=theme,
        key=key,
        default=value,
    )
