---
description: Manage optional nonblocking verification warnings and explicit task bindings.
---
# Verification warnings

Manage only this optional warning feature. Warnings never block tools and do not replace completion checks. Native notification visibility is unverified.

For on/off/status run:
`python3 ~/.config/mrcall-ai-kit/verification-warnings/register.py claude ACTION`

For an explicit task run:
`python3 ~/.config/mrcall-ai-kit/verification-warnings/verification_warnings.py check --repo PATH --task ID`

Bind only an actual available native session ID:
`python3 ~/.config/mrcall-ai-kit/verification-warnings/verification_warnings.py bind --runtime claude --session SESSION --repo PATH --task ID`

Unbind with `unbind --runtime claude --session SESSION`. Never guess session IDs or select the newest task. Without a binding hooks stay silent. Off removes this feature's registrations and bindings only. Codex registration requires trust confirmation in /hooks; native trust is unverified.
