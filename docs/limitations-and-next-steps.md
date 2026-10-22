# Limitations and Next Steps

## Current limitations
- Synthetic data and labels only.
- Simplified velocity calculation in the API demonstration.
- Local JSON rule registry; no concurrent update protection.
- No authentication, authorisation or production security.
- No external fraud platform integration.
- No real-world calibration or validated loss estimates.
- The SQL examples include a warehouse-style `QUALIFY` example; use the provided note/CTE alternative for PostgreSQL.

## Next iteration
1. Add PostgreSQL persistence and migrations.
2. Add robust event-time velocity aggregation.
3. Add role-based rule approvals and immutable audit events.
4. Add time-based train/test separation and independently generated fraud scenarios.
5. Add threshold optimisation against explicit fraud-loss and customer-friction costs.
6. Add monitoring for data drift and rule performance decay.
7. Add a challenger anomaly model and compare it to the rules baseline.
