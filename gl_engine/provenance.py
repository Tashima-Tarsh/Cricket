"""Shared evidence contract and conservative transport labeling.

For legacy objects timestamp is labeling time, NOT observation time. Missing
source evidence remains UNVERIFIED; this boundary cannot verify cricket data.
"""
from datetime import datetime, timezone
from typing import Literal, Optional
import json
from pydantic import BaseModel, Field, AliasChoices, model_validator
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class DataProvenance(BaseModel):
    source: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                validation_alias=AliasChoices('timestamp', 'last_updated'))
    verification_status: Literal['VERIFIED', 'UNVERIFIED', 'MODEL_ESTIMATE', 'PRIOR_ONLY', 'SIMULATION', 'EXPERT_ESTIMATE_UNVERIFIED'] = 'UNVERIFIED'
    sample_size: Optional[int] = Field(default=None, ge=0)
    provider_name: Optional[str] = None
    confidence: float = Field(default=0, ge=0, le=1)
    notes: Optional[str] = None

    @property
    def last_updated(self):
        return self.timestamp

    @model_validator(mode='after')
    def evidence_consistency(self):
        if not self.source.strip():
            raise ValueError('Evidence source cannot be blank')
        if self.timestamp.tzinfo is None:
            # Older EdgeForge providers used naive UTC; preserve the instant.
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
        if self.source == 'unavailable' and (self.confidence or self.verification_status == 'VERIFIED'):
            raise ValueError('Unavailable evidence cannot be verified or confident')
        if self.source == 'estimated' and (self.confidence > .6 or self.verification_status == 'VERIFIED'):
            raise ValueError('Estimates cannot claim verified evidence or confidence > 0.6')
        return self


def unverified_provenance():
    return DataProvenance(source='unavailable', notes='Original source and observation time not supplied; timestamp is labeling time.')


ENTITY_KEYS = frozenset({'players', 'roster', 'lineups', 'lineup', 'match', 'matches',
                         'fixture', 'fixtures', 'projections', 'projection', 'captain', 'vice_captain'})


def annotate_payload(value, source, required=True):
    """Copy payload, label entities without changing numeric maps or claiming verification."""
    if isinstance(value, list):
        return [annotate_payload(item, source, required) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: annotate_payload(item, source, key in ENTITY_KEYS)
              for key, item in value.items() if key != 'provenance'}
    is_entity = ('id' in value and 'name' in value) or 'player_id' in value or ('players' in value and 'captain' in value)
    if required or is_entity or 'provenance' in value:
        existing = value.get('provenance')
        if isinstance(existing, (dict, DataProvenance)):
            provenance = DataProvenance.model_validate(existing)
        else:
            provenance = DataProvenance(source=existing if isinstance(existing, str) and existing.strip() else source, notes='Legacy output: source evidence not verified; timestamp is labeling time, not observation time.')
        result['provenance'] = provenance.model_dump(mode='json')
    return result


class ProvenanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        source = f'{request.app.title}:{request.url.path}'
        provenance = DataProvenance(source=source, notes='Transport labeling time; underlying evidence is unverified.')
        response.headers['X-Data-Provenance'] = provenance.model_dump_json()
        # OpenAPI is a protocol schema, not a cricket data response. Do not mutate it.
        if 'application/json' not in response.headers.get('content-type', '') or request.url.path == '/openapi.json':
            return response
        body = b''.join([chunk async for chunk in response.body_iterator])
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict):
                payload = {'data': payload}
            payload = annotate_payload(payload, source)
        except (ValueError, TypeError):
            return JSONResponse(status_code=503, content={
                'detail': 'Response evidence metadata is invalid',
                'provenance': provenance.model_dump(mode='json')})
        headers = dict(response.headers)
        headers.pop('content-length', None)
        headers.pop('etag', None)
        return JSONResponse(payload, status_code=response.status_code, headers=headers, background=response.background)


def install_provenance(app):
    app.add_middleware(ProvenanceMiddleware)

    @app.exception_handler(Exception)
    async def unavailable_response(request, exc):
        return JSONResponse(status_code=503, content={
            'detail': 'Service unavailable; no substitute data was generated',
            'provenance': unverified_provenance().model_dump(mode='json')})
