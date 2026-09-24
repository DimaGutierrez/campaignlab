# Security

This is a single-workspace prototype, not a managed analytics service. API keys give broad access and must remain private. Do not submit real customer data to a public demonstration.

Please use GitHub private vulnerability reporting if enabled. Do not include exploit credentials or private customer records in public issues. If private reporting is not available, open an issue requesting a private contact without technical vulnerability details.

Keep the default loopback binding for local demos. Before hosting publicly, use HTTPS, rate and request-size limits, independent random keys, backups and a retention policy. The ingestion key belongs only in your backend. The admin key is kept in browser memory; reload or disconnect to clear it. Infrastructure logs may collect data beyond this application database.
