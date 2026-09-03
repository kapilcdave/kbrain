---
title: when2jam
type: project
status: maintained
started: 2025
updated: 2026-09-03
tags: [scheduling, collaboration, nextjs, supabase]
source_repositories:
  - https://github.com/kapilcdave/when2jam
---

# when2jam

## Summary

A lightweight group-availability scheduler built around shareable links rather
than accounts.

## Why I Built It

Scheduling a rehearsal or informal meeting should not require every participant
to create an account or connect a calendar.

## What I Built

The Next.js application creates events covering up to seven days, lets
participants paint availability onto a time grid, and uses Supabase to update a
shared heatmap in real time. The interface supports pointer interaction for
desktop and mobile use.

## What I Learned

Removing sign-in reduces friction but changes the security model: possession of
the event link becomes the practical access boundary. Hosted backends also need
reproducible migrations and recovery instructions because deployments can
outlive their original data projects.

## Current Status

Public project with a documented production build and recovery workflow.

## Sources

- [Live application](https://when2jam.vercel.app)
- [Repository](https://github.com/kapilcdave/when2jam)
