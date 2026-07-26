# Implementation notes

The first release focuses on the placement engine and an end-to-end interactive
path. It keeps infrastructure replaceable:

- API persistence is in-memory.
- OR-Tools is optional; CP-SAT reports its fallback when unavailable.
- The simulator is deterministic and synchronous.
- Authentication and direct cluster mutation are out of scope.

## Production follow-ups

- Add SQLAlchemy/Alembic persistence and Redis-backed workers.
- Add interval-aware GPU device allocations rather than aggregate free counts.
- Add scenario CRUD and a full event timeline UI.
- Add property-based tests at enterprise fleet scale.
- Add authentication, audit logging, quotas, and deployment observability.
