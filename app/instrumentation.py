"""
Instrumentation setup for FastAPI application.
Configures OpenTelemetry tracing and logging for distributed observability.
"""

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def setup_tracer(app: FastAPI):
    """
    Set up OpenTelemetry tracing and logging for a FastAPI app.

    Reads configuration from environment variables:
        - OTEL_SERVICE_NAME: Service name for tracing
        - HONEYCOMB_API_KEY: API key for Honeycomb
        - OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint URL

    Configures:
        - Tracer provider and resource
        - OTLP exporter and span processor
        - FastAPI instrumentation
        - Logging instrumentation

    Args:
        app (FastAPI): FastAPI application instance to instrument
    """
    # Read config from environment
    service_name = os.getenv("OTEL_SERVICE_NAME", "library-management-api")
    honeycomb_api_key = os.getenv("HONEYCOMB_API_KEY")
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://api.honeycomb.io/v1/traces")

    # Define resource attributes for the service
    resource = Resource(attributes={SERVICE_NAME: service_name})
    
    # Create a tracer provider with the resource
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Configure OTLP exporter and span processor
    otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint + "/v1/traces",  # make sure it ends with /v1/traces
    headers={"x-honeycomb-team": honeycomb_api_key}
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Instrument FastAPI app for tracing
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument logging
    LoggingInstrumentor().instrument(set_logging_format=True)
