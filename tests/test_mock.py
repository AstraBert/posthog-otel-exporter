import os
import pytest

from unittest.mock import Mock, patch
from typing import Sequence
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan, Event
from posthog_otel_exporter.exporter import PosthogSpanExporter
from posthog_otel_exporter.errors import MissingPosthogCredentialyError

CAPTURED_EVENTS = []
IDENTIFIED_CONTEXTS = []


def mock_identify_context(*args, **kwargs) -> None:
    if "distinct_id" in kwargs:
        IDENTIFIED_CONTEXTS.append(kwargs["distinct_id"])
    return


def mock_capture(*args, **kwargs) -> str | None:
    if "event" in kwargs:
        CAPTURED_EVENTS.append(kwargs["event"])
    return "success"


def test_span_exporter_init() -> None:
    os.environ["POSTHOG_API_KEY"] = "this-is-a-key"
    os.environ["POSTHOG_ENDPOINT"] = "https://test.posthog.com"
    try:
        PosthogSpanExporter()
        success = True
    except Exception:
        success = False
    assert success
    del os.environ["POSTHOG_API_KEY"]
    del os.environ["POSTHOG_ENDPOINT"]
    with pytest.raises(MissingPosthogCredentialyError):
        PosthogSpanExporter()


@pytest.fixture()
def spans() -> Sequence[ReadableSpan]:
    return [
        ReadableSpan(
            name="span-1", events=[Event(name="helloWorld", attributes={"duration": 1})]
        ),
        ReadableSpan(
            name="span-2", events=[Event(name="byeMars", attributes={"duration": 3})]
        ),
        ReadableSpan(
            name="span-3",
            events=[
                Event(name="nigthVenus", attributes={"duration": 4}),
                Event(name="morningJupyter", attributes={"duration": 2}),
            ],
        ),
    ]


@patch("posthog_otel_exporter.exporter.Posthog")
@patch("posthog_otel_exporter.exporter.identify_context")
@patch("posthog_otel_exporter.exporter.new_context")
def test_span_exporter(
    mock_new_context: Mock,
    mock_identify: Mock,
    mock_posthog_class: Mock,
    spans: Sequence[ReadableSpan],
) -> None:
    mock_posthog_instance = Mock()
    mock_posthog_instance.capture = Mock(side_effect=mock_capture)
    mock_posthog_class.return_value = mock_posthog_instance

    mock_context = Mock()
    mock_context.__enter__ = Mock(return_value=None)
    mock_context.__exit__ = Mock(return_value=None)
    mock_new_context.return_value = mock_context

    mock_identify.side_effect = mock_identify_context

    exporter = PosthogSpanExporter("not-an-api-key", "https://test.posthog.com")
    res = exporter.export(spans=spans)

    mock_new_context.assert_called()
    mock_identify.assert_called()
    mock_posthog_instance.capture.assert_called()
    assert res == SpanExportResult.SUCCESS
    assert [span.name for span in spans] == IDENTIFIED_CONTEXTS
    event_names = []
    for span in spans:
        for event in span.events:
            event_names.append(event.name)
    assert event_names == CAPTURED_EVENTS
