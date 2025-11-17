import os

from posthog import Posthog, new_context, identify_context
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan
from typing import Sequence
from .errors import MissingPosthogCredentialyError


class PosthogSpanExporter(SpanExporter):
    """
    Implementation of an OpenTelemetry-compatible `SpanExporter` to export events to PostHog.
    """

    def __init__(
        self, posthog_api_key: str | None = None, posthog_endpoint: str | None = None
    ):
        """
        Initializes the exporter with the provided PostHog API key and endpoint.

        Args:
            posthog_api_key (str | None): The PostHog API key. If not provided, it will be read from the 'POSTHOG_API_KEY' environment variable.
            posthog_endpoint (str | None): The PostHog endpoint URL. If not provided, it will be read from the 'POSTHOG_ENDPOINT' environment variable.

        Raises:
            MissingPosthogCredentialyError: If neither the API key nor the endpoint are provided or found in the environment variables.
        """
        self.posthog_api_key = posthog_api_key or os.getenv("POSTHOG_API_KEY")
        self.posthog_endpoint = posthog_endpoint or os.getenv("POSTHOG_ENDPOINT")
        if self.posthog_api_key is None or self.posthog_endpoint is None:
            raise MissingPosthogCredentialyError(
                "Either Posthog API key or Posthog Endpoint were not provided and not found within the environment variables"
            )
        self._posthog_client = Posthog(
            self.posthog_api_key,
            host=self.posthog_endpoint,
        )

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Exports a sequence of spans by iterating through each span and its events, capturing event data using the PostHog client.

        Args:
            spans (Sequence[ReadableSpan]): A sequence of ReadableSpan objects to be exported.

        Returns:
            SpanExportResult: The result of the export operation, indicating success or failure.
        """
        for span in spans:
            with new_context():
                identify_context(distinct_id=span.name)
                for event in span.events:
                    if event.attributes is not None:
                        self._posthog_client.capture(
                            event=event.name,
                            properties=dict(event.attributes),
                        )

        return SpanExportResult.SUCCESS

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
