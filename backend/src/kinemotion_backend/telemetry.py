"""Telemetry configuration for Kinemotion Backend.

Enables OpenTelemetry tracing and logging if OTEL_EXPORTER_OTLP_ENDPOINT is set.
"""

import logging
import os

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def setup_telemetry(app: FastAPI) -> bool:
    """Initialize OpenTelemetry if configured.

    Args:
        app: FastAPI application instance to instrument

    Returns:
        True if telemetry was enabled, False otherwise.
    """
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    enable_gcp = os.getenv("ENABLE_GCP_TRACE", "").lower() == "true"

    if not otlp_endpoint and not enable_gcp:
        logger.info("telemetry_disabled_no_endpoint")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as e:
        logger.warning(
            "telemetry_dependencies_missing",
            error=str(e),
            message="Install opentelemetry dependencies to enable tracing",
        )
        return False

    try:
        logger.info("telemetry_initializing")

        # resource = Resource.create(attributes={
        #     "service.name": "kinemotion-backend",
        #     "service.instance.id": f"kinemotion-{os.getpid()}",
        # })
        # Use default resource detection (env vars like OTEL_SERVICE_NAME)
        resource = Resource.create()

        # Configure Tracer
        tracer_provider = TracerProvider(resource=resource)

        span_processor = None

        if enable_gcp:
            try:
                from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

                gcp_exporter = CloudTraceSpanExporter()
                span_processor = BatchSpanProcessor(gcp_exporter)
                logger.info("telemetry_gcp_exporter_configured")
            except ImportError:
                logger.error(
                    "telemetry_gcp_dependency_missing",
                    message="Install opentelemetry-exporter-gcp-trace",
                )
                return False
        elif otlp_endpoint:
            # OTLP Exporter (defaults to gRPC)
            otlp_exporter = OTLPSpanExporter()
            span_processor = BatchSpanProcessor(otlp_exporter)
            logger.info("telemetry_otlp_exporter_configured", endpoint=otlp_endpoint)

        if span_processor:
            tracer_provider.add_span_processor(span_processor)
            trace.set_tracer_provider(tracer_provider)

            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

            # Instrument Logging
            LoggingInstrumentor().instrument(set_logging_format=True)

            logger.info("telemetry_enabled")
            return True
        else:
            logger.warning("telemetry_no_exporter_configured")
            return False

    except Exception as e:
        logger.error("telemetry_initialization_failed", error=str(e), exc_info=True)
        return False
