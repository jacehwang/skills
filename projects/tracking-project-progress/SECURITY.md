# Security Policy

## Supported versions

Security fixes are provided for the latest tagged release and the current `main` branch.

## Reporting a vulnerability

Use GitHub's private security vulnerability reporting for this repository. Do not open a public issue for a suspected vulnerability until a fix or coordinated disclosure is available.

Include the affected version, operating system, agent runtime, reproduction steps, impact, and any suggested mitigation. Never include live credentials or unrelated private project data.

## Security boundaries

This project executes local Python scripts and Claude Code hooks with the permissions available to the user's agent process. It intentionally makes no network calls. Users should review Skill and hook source before installation and avoid recording secrets in `.project-board/`.

