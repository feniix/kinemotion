"""Telemetry configuration for Kinemotion Backend.

Enables OpenTelemetry tracing and logging if OTEL_EXPORTER_OTLP_ENDPOINT is set.
"""

import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)


def setup_telemetry(app: FastAPI) -> bool:
    """Initialize OpenTelemetry if configured.

    Args:
        app: FastAPI application instance to instrument

    Returns:
        True if telemetry was enabled, False otherwise.
    """
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if not otlp_endpoint:
        logger.info("telemetry_disabled_no_endpoint")
        return False

    logger.info("telemetry_initializing", endpoint=otlp_endpoint)

    # resource = Resource.create(attributes={
    #     "service.name": "kinemotion-backend",
    #     "service.instance.id": f"kinemotion-{os.getpid()}",
    # })
    # Use default resource detection (env vars like OTEL_SERVICE_NAME)
    resource = Resource.create()

    # Configure Tracer
    tracer_provider = TracerProvider(resource=resource)

    # OTLP Exporter (defaults to gRPC)
    # The endpoint env var is handled automatically by the exporter if not passed,
    # but since we check it manually, we can trust the SDK standard env vars too.
    # We just instantiate it.
    otlp_exporter = OTLPSpanExporter()

    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

    # Instrument Logging
    LoggingInstrumentor().instrument(set_logging_format=True)

    logger.info("telemetry_enabled")
    return True
