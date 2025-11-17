import pytest
import os

from typing import Sequence
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan, Event
from posthog_otel_exporter.exporter import PosthogSpanExporter


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


POSTHOG_CREDS_UNAVAILABLE = (
    os.getenv("POSTHOG_API_KEY") is None or os.getenv("POSTHOG_ENDPOINT") is None
)


@pytest.mark.skipif(
    condition=POSTHOG_CREDS_UNAVAILABLE,
    reason="PostHog credentials not available in the current environment",
)
def test_span_exporter(spans: Sequence[ReadableSpan]) -> None:
    exporter = PosthogSpanExporter()
    res = exporter.export(spans=spans)
    assert res == SpanExportResult.SUCCESS
