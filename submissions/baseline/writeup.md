# Baseline Write-Up

## Summary

This baseline exists to prove the tournament kit works for a fresh clone. It performs a small multi-query retrieval pass, reranks locally, and drafts a short answer from the top evidence chunks.

## Why It Is Weak On Purpose

- it does not explicitly track evidence groups
- it does not run a critique loop
- it does not adapt by task difficulty
- it does not use richer note-taking or verification passes

## Intended Use

Copy this bundle and improve the scaffold behavior while keeping the same fixed tool surface.
