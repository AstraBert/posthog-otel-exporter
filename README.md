# posthog-otel-exporter

## Overview

`posthog-otel-exporter` is an OpenTelemetry SpanExporter for Python that sends trace events to [PostHog](https://posthog.com/). This allows you to analyze and visualize your application's traces and events in PostHog.

## Installation

```bash
pip install posthog-otel-exporter
```

## Configuration

You need a PostHog project API key and endpoint. These can be provided as arguments or via environment variables:

- `POSTHOG_API_KEY`: Your PostHog project API key
- `POSTHOG_ENDPOINT`: Your PostHog instance endpoint (e.g., `https://app.posthog.com`)

## Usage with OpenTelemetry

Below is an example of how to use `PosthogSpanExporter` with OpenTelemetry's tracing SDK:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from posthog_otel_exporter.exporter import PosthogSpanExporter

# Set up the tracer provider
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure the Posthog exporter (API key and endpoint can also be set via env vars)
exporter = PosthogSpanExporter(
    posthog_api_key="<your-posthog-api-key>",
    posthog_endpoint="<your-posthog-endpoint>"
)

# Add the exporter to the span processor
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Example span
with tracer.start_as_current_span("example-span") as span:
    span.add_event("event-name", {"key": "value"})
```

### Environment Variables

Alternatively, set the following environment variables:

```bash
export POSTHOG_API_KEY="<your-posthog-api-key>"
export POSTHOG_ENDPOINT="<your-posthog-endpoint>"
```

Then initialize the exporter without arguments:

```python
exporter = PosthogSpanExporter()
```

## License and Contributions

This project is distributed under the [MIT License](./LICENSE).

Contributions are welcome and encouraged, and should follow the guidelines in [CONTRIBUTING.md](./CONTRIBUTING.md).

