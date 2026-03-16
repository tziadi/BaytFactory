# --- BaytFactory - Smart Home Variant Generator with SAT Solver, Colored Configurator & HA Launcher ---

import streamlit as st
import zipfile
import tempfile
import json
import os
import re
import hashlib
import subprocess
import threading
import time
import webbrowser
import shutil
import sys
import signal
from pathlib import Path
from dotenv import load_dotenv
from sat_interactive import SATFeatureSolver
from annotated_monaco import st_annotated_monaco

# --- Constantes ---
PERSISTENT_DIR = "spl-smarthome-generated-variants"
PERSISTENT_ENV = os.path.join(PERSISTENT_DIR, ".env")
PERSISTENT_CREDENTIALS = os.path.join(PERSISTENT_DIR, "credentials.env")
DEPLOY_STATE_FILE = os.path.join(PERSISTENT_DIR, ".ha_deploy_state.json")
DEFAULT_HA_USER = "baytadmin"
DEFAULT_HA_PASSWORD = "baytadmin1234"

load_dotenv()

def inject_global_styles():
    st.markdown(
        """
        <style>
          :root {
            --bayt-ink: #17324d;
            --bayt-muted: #5d6d7e;
            --bayt-line: #d8e1e8;
            --bayt-surface: #f5f7f4;
            --bayt-card: #fcfdfb;
            --bayt-accent: #c96d44;
            --bayt-accent-soft: #f5dfd3;
            --bayt-good: #2f6b57;
            --bayt-good-soft: #dceee4;
            --bayt-warn: #9c5a1a;
            --bayt-warn-soft: #f7e7d1;
          }

          .stApp {
            background:
              radial-gradient(circle at top right, rgba(201,109,68,0.10), transparent 28%),
              linear-gradient(180deg, #f4f1ea 0%, #eef3ef 100%);
          }

          .bayt-hero {
            padding: 0.9rem 1.2rem 1rem 1.2rem;
            border: 1px solid var(--bayt-line);
            border-radius: 18px;
            background: linear-gradient(145deg, rgba(252,253,251,0.95), rgba(246,249,246,0.95));
            box-shadow: 0 10px 30px rgba(23,50,77,0.07);
            margin-bottom: 1rem;
          }

          .bayt-kicker {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: var(--bayt-accent);
            font-weight: 700;
            margin-bottom: 0.25rem;
          }

          .bayt-title {
            font-size: 2rem;
            line-height: 1.05;
            color: var(--bayt-ink);
            font-weight: 800;
            margin: 0;
          }

          .bayt-subtitle {
            color: var(--bayt-muted);
            margin-top: 0.35rem;
            font-size: 0.98rem;
          }

          .bayt-panel-title {
            color: var(--bayt-ink);
            font-size: 1.05rem;
            font-weight: 800;
            margin-bottom: 0.65rem;
            letter-spacing: 0.01em;
          }

          .bayt-panel-note {
            color: var(--bayt-muted);
            font-size: 0.84rem;
            margin-bottom: 0.85rem;
          }

          div[data-testid="stTabs"] div[role="tablist"] {
            gap: 0.55rem;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(216,225,232,0.92);
            border-radius: 16px;
            padding: 0.35rem;
            margin: 0.35rem 0 1rem 0;
            box-shadow: 0 10px 20px rgba(23,50,77,0.04);
          }

          div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] {
            height: 2.6rem;
            padding: 0 1rem;
            border-radius: 12px;
            border: 1px solid transparent;
            background: transparent;
            color: var(--bayt-muted);
            font-weight: 700;
            font-size: 0.9rem;
            transition: background 120ms ease, color 120ms ease, border-color 120ms ease, transform 120ms ease;
          }

          div[data-testid="stTabs"] div[role="tablist"] button[role="tab"]:hover {
            color: var(--bayt-ink);
            background: rgba(255,255,255,0.84);
            border-color: rgba(216,225,232,0.92);
          }

          div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"] {
            background: linear-gradient(180deg, rgba(201,109,68,0.16), rgba(201,109,68,0.10));
            border-color: rgba(201,109,68,0.28);
            color: var(--bayt-ink);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.78);
          }

          div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] p {
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.01em;
          }

          div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"] p {
            color: var(--bayt-ink);
          }

          div[data-testid="stTabs"] div[role="tablist"] button[role="tab"]::after {
            display: none !important;
          }

          .bayt-summary {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
            margin: 0.4rem 0 0.95rem 0;
          }

          .bayt-summary-card {
            background: var(--bayt-card);
            border: 1px solid var(--bayt-line);
            border-radius: 14px;
            padding: 0.7rem 0.8rem;
          }

          .bayt-summary-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--bayt-muted);
          }

          .bayt-summary-value {
            margin-top: 0.2rem;
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--bayt-ink);
          }

          .bayt-summary-value.good {
            color: var(--bayt-good);
          }

          .bayt-config-shell {
            border: 1px solid var(--bayt-line);
            border-radius: 20px;
            background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(247,250,248,0.92));
            padding: 0.95rem;
            box-shadow: 0 12px 24px rgba(23,50,77,0.05);
          }

          .bayt-config-hero {
            border: 1px solid rgba(216,225,232,0.95);
            border-radius: 16px;
            background: rgba(255,255,255,0.92);
            padding: 0.85rem 0.9rem;
            margin-bottom: 0.85rem;
          }

          .bayt-config-hero-title {
            color: var(--bayt-ink);
            font-size: 1.02rem;
            font-weight: 800;
            margin-bottom: 0.18rem;
          }

          .bayt-config-hero-note {
            color: var(--bayt-muted);
            font-size: 0.78rem;
          }

          .bayt-config-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border: 1px solid rgba(216,225,232,0.72);
            border-radius: 10px;
            background: rgba(255,255,255,0.74);
            padding: 0.38rem 0.5rem;
            margin-bottom: 0.28rem;
            min-width: 0;
          }

          .bayt-config-row.active {
            border-color: rgba(201,109,68,0.34);
            background: linear-gradient(90deg, rgba(201,109,68,0.10), rgba(201,109,68,0.03) 22%, rgba(255,255,255,0.86) 66%);
            box-shadow: inset 3px 0 0 var(--bayt-accent);
          }

          .bayt-config-row.locked {
            background: linear-gradient(180deg, rgba(243,246,248,0.92), rgba(238,242,245,0.86));
            border-color: rgba(207,216,224,0.95);
            opacity: 0.9;
          }

          .bayt-config-name {
            color: var(--bayt-ink);
            font-weight: 760;
            font-size: 0.84rem;
            line-height: 1.16;
            white-space: normal;
            overflow-wrap: anywhere;
          }

          .bayt-config-key {
            color: var(--bayt-muted);
            font-size: 0.7rem;
            margin-top: 0.14rem;
            letter-spacing: 0.01em;
          }

          .bayt-config-main {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            min-width: 0;
            flex: 1 1 auto;
          }

          .bayt-config-level {
            display: inline-flex;
            align-items: stretch;
            flex: 0 0 auto;
            height: 24px;
            min-width: 0;
            position: relative;
          }

          .bayt-config-level::after {
            content: "";
            width: 100%;
            border-radius: 10px;
            background: linear-gradient(
              90deg,
              transparent calc(100% - 2px),
              rgba(23,50,77,0.12) calc(100% - 2px)
            );
          }

          .bayt-config-feature-bar {
            display: inline-flex;
            width: 4px;
            height: 1.45rem;
            border-radius: 999px;
            flex: 0 0 auto;
            box-shadow: inset 0 0 0 1px rgba(23,50,77,0.08);
          }

          .bayt-config-lock {
            color: #8a99a8;
            font-size: 0.82rem;
            line-height: 1;
            margin-left: auto;
            flex: 0 0 auto;
          }


          .bayt-config-toolbar {
            margin-bottom: 0.75rem;
          }

          .bayt-config-group {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.8rem;
            padding: 0.2rem 0.1rem 0.5rem 0.1rem;
            margin: 0.9rem 0 0.3rem 0;
            border-bottom: 1px solid rgba(216,225,232,0.78);
          }

          .bayt-config-group:first-of-type {
            margin-top: 0.15rem;
          }

          .bayt-config-group-title {
            color: var(--bayt-ink);
            font-size: 0.86rem;
            font-weight: 800;
          }

          .bayt-config-group-meta {
            color: var(--bayt-muted);
            font-size: 0.74rem;
            white-space: nowrap;
          }

          .bayt-config-insight {
            border: 1px solid var(--bayt-line);
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(246,249,246,0.92));
            padding: 0.8rem 0.85rem;
            margin-top: 0.9rem;
          }

          .bayt-config-insight-title {
            color: var(--bayt-ink);
            font-size: 0.9rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
          }

          .bayt-config-insight-note {
            color: var(--bayt-muted);
            font-size: 0.75rem;
            margin-bottom: 0.65rem;
          }

          .bayt-config-mini-stats {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
            margin-bottom: 0.85rem;
          }

          .bayt-config-mini-stat {
            border: 1px solid rgba(216,225,232,0.92);
            border-radius: 14px;
            background: rgba(255,255,255,0.92);
            padding: 0.7rem 0.8rem;
          }

          .bayt-config-mini-stat .label {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--bayt-muted);
          }

          .bayt-config-mini-stat .value {
            margin-top: 0.18rem;
            font-size: 1.05rem;
            font-weight: 800;
            color: var(--bayt-ink);
          }

          .bayt-runtime-shell {
            margin-top: 1.25rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(216,225,232,0.95);
          }

          .bayt-runtime-panel {
            border: 1px solid var(--bayt-line);
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(246,249,246,0.92));
            padding: 0.95rem;
            box-shadow: 0 10px 22px rgba(23,50,77,0.04);
            text-align: center;
          }

          .bayt-runtime-title {
            color: var(--bayt-ink);
            font-size: 1.14rem;
            font-weight: 800;
            margin-bottom: 0.22rem;
          }

          .bayt-runtime-note {
            color: var(--bayt-muted);
            font-size: 0.82rem;
            margin-bottom: 0.95rem;
          }

          .bayt-feature-label {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            min-height: 34px;
          }

          .bayt-feature-name {
            color: var(--bayt-ink);
            font-weight: 650;
            line-height: 1.1;
          }

          .bayt-feature-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 12px;
            width: 12px;
            border-radius: 999px;
            border: 1px solid rgba(23,50,77,0.12);
            flex: 0 0 auto;
          }

          .bayt-meta {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 0.16rem 0.5rem;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            border: 1px solid var(--bayt-line);
            color: var(--bayt-muted);
            background: rgba(255,255,255,0.72);
          }

          .bayt-meta.required {
            background: var(--bayt-accent-soft);
            color: #8a4a23;
            border-color: #ebc4af;
          }

          .bayt-meta.group {
            background: #e2ebf5;
            color: #38516b;
            border-color: #c9d7e6;
          }

          .bayt-meta.manual {
            background: var(--bayt-good-soft);
            color: var(--bayt-good);
            border-color: #bfd9ca;
          }

          .bayt-meta.inferred {
            background: #f1ebd9;
            color: #7b6231;
            border-color: #dece9f;
          }

          .bayt-meta.excludes {
            background: #f7e1df;
            color: #8f3c33;
            border-color: #ebc2bc;
          }

          .bayt-branch-title {
            color: var(--bayt-ink);
            font-weight: 750;
          }

          .bayt-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 0.55rem;
          }

          .bayt-chip {
            padding: 0.26rem 0.58rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            border: 1px solid var(--bayt-line);
            background: rgba(255,255,255,0.76);
            color: var(--bayt-ink);
          }

          .bayt-chip.requires {
            background: #e4edf8;
            border-color: #cbd9e6;
            color: #31547a;
          }

          .bayt-chip.excludes {
            background: #f7e1df;
            border-color: #ebc2bc;
            color: #8f3c33;
          }

          .bayt-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.45rem 0 0.75rem 0;
          }

          .bayt-legend-item {
            display: inline-flex;
            align-items: center;
            gap: 0.42rem;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.78);
            border: 1px solid var(--bayt-line);
            color: var(--bayt-muted);
            font-size: 0.72rem;
            font-weight: 700;
          }

          .bayt-legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            display: inline-block;
          }

          .bayt-tabbar {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin: 0.5rem 0 0.85rem 0;
          }

          .bayt-tab {
            padding: 0.36rem 0.62rem;
            border-radius: 10px;
            border: 1px solid var(--bayt-line);
            background: rgba(255,255,255,0.8);
            color: var(--bayt-ink);
            font-size: 0.74rem;
            font-weight: 700;
          }

          .bayt-tab.active {
            background: #17324d;
            color: #ffffff;
            border-color: #17324d;
          }

          .bayt-code-shell {
            border: 1px solid var(--bayt-line);
            border-radius: 18px;
            background: rgba(252, 253, 251, 0.86);
            box-shadow: 0 12px 28px rgba(23,50,77,0.06);
            padding: 0.8rem;
          }

          .bayt-code-sidebar {
            border: 1px solid var(--bayt-line);
            border-radius: 16px;
            background: rgba(255,255,255,0.75);
            padding: 0.8rem;
          }

          .bayt-code-toolbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            margin-bottom: 0.7rem;
          }

          .bayt-code-access {
            border: 1px solid rgba(216,225,232,0.92);
            border-radius: 16px;
            background: rgba(255,255,255,0.82);
            padding: 0.85rem 0.9rem;
            margin-bottom: 0.9rem;
          }

          .bayt-code-access-title {
            color: var(--bayt-ink);
            font-size: 0.92rem;
            font-weight: 800;
            margin-bottom: 0.18rem;
          }

          .bayt-code-access-note {
            color: var(--bayt-muted);
            font-size: 0.77rem;
            margin-bottom: 0.75rem;
          }

          .bayt-code-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.22rem 0.6rem;
            font-size: 0.72rem;
            font-weight: 700;
            border: 1px solid var(--bayt-line);
            color: var(--bayt-muted);
            background: rgba(255,255,255,0.85);
          }

          .bayt-code-meta {
            color: var(--bayt-muted);
            font-size: 0.78rem;
            margin-bottom: 0.7rem;
          }

          .bayt-code-editor {
            border: 1px solid var(--bayt-line);
            border-radius: 16px;
            background: rgba(255,255,255,0.68);
            padding: 0.8rem;
          }

          .bayt-code-empty {
            border: 1px dashed var(--bayt-line);
            border-radius: 16px;
            padding: 1.8rem 1rem;
            text-align: center;
            color: var(--bayt-muted);
            background: rgba(255,255,255,0.55);
          }

          .bayt-annotation-lane {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-bottom: 0.85rem;
          }

          .bayt-annotation-card {
            min-width: 220px;
            max-width: 320px;
            border: 1px solid var(--bayt-line);
            border-radius: 12px;
            padding: 0.55rem 0.65rem;
            background: rgba(255,255,255,0.92);
          }

          .bayt-annotation-rule {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            color: var(--bayt-ink);
            font-weight: 700;
            font-size: 0.8rem;
            line-height: 1.25;
            word-break: break-word;
          }

          .bayt-annotation-meta {
            margin-top: 0.28rem;
            color: var(--bayt-muted);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
          }

          .bayt-annotation-swatch {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            flex: 0 0 auto;
          }

          .bayt-annotation-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-top: 0.45rem;
          }

          .bayt-annotation-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.18rem 0.5rem;
            font-size: 0.68rem;
            font-weight: 800;
            color: #17324d;
            border: 1px solid rgba(23,50,77,0.08);
          }

          .bayt-annotation-chip.unknown,
          .bayt-unknown-chip {
            background: #f5dfbf;
            color: #8c5212;
            border: 1px solid #e4bb78;
          }

          .bayt-unknown-callout {
            margin-bottom: 0.75rem;
            padding: 0.6rem 0.7rem;
            border-radius: 12px;
            border: 1px solid #e4bb78;
            background: #fff7e8;
            color: #8c5212;
            font-size: 0.82rem;
          }

          .bayt-unknown-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.16rem 0.5rem;
            font-size: 0.7rem;
            font-weight: 800;
            margin-left: 0.35rem;
          }

          button[kind="tertiary"] {
            justify-content: flex-start !important;
            text-align: left !important;
            border: 1px solid transparent !important;
            border-radius: 8px !important;
            padding: 0.18rem 0.5rem !important;
            min-height: 1.9rem !important;
            color: var(--bayt-ink) !important;
          }

          button[kind="tertiary"]:hover {
            background: rgba(23,50,77,0.06) !important;
            border-color: rgba(23,50,77,0.08) !important;
          }

          button[kind="secondary"] {
            border-radius: 0 !important;
            border: none !important;
            background: transparent !important;
            color: var(--bayt-ink) !important;
            font-weight: 700 !important;
            min-height: 1.2rem !important;
            min-width: 1.2rem !important;
            padding: 0 !important;
            box-shadow: none !important;
          }

          button[kind="secondary"] span[data-testid="stIconMaterial"] {
            font-size: 0.9rem !important;
            line-height: 1 !important;
          }

          button[kind="secondary"]:hover {
            background: transparent !important;
            color: var(--bayt-accent) !important;
          }

          .bayt-file-active-marker {
            height: 2px;
            border-radius: 999px;
            background: var(--bayt-accent);
            margin: -0.05rem 0 0.2rem 0.25rem;
            width: 78%;
          }

          .bayt-fm-shell {
            border: 1px solid var(--bayt-line);
            border-radius: 20px;
            background: rgba(252,253,251,0.86);
            box-shadow: 0 12px 26px rgba(23,50,77,0.06);
            padding: 0.95rem;
          }

          .bayt-fm-header {
            display: grid;
            grid-template-columns: 1.8fr 1fr 1fr 1fr;
            gap: 0.65rem;
            margin-bottom: 0.9rem;
          }

          .bayt-fm-stat {
            border: 1px solid var(--bayt-line);
            border-radius: 14px;
            background: rgba(255,255,255,0.88);
            padding: 0.72rem 0.8rem;
          }

          .bayt-fm-stat .label {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--bayt-muted);
          }

          .bayt-fm-stat .value {
            margin-top: 0.22rem;
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--bayt-ink);
          }

          .bayt-fm-panel {
            border: 1px solid var(--bayt-line);
            border-radius: 18px;
            background: rgba(255,255,255,0.8);
            padding: 0.85rem;
            height: 100%;
          }

          .bayt-fm-tree-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            padding: 0.38rem 0.5rem;
            border-radius: 10px;
            border: 1px solid rgba(216,225,232,0.72);
            background: rgba(255,255,255,0.72);
            margin-bottom: 0.3rem;
          }

          .bayt-fm-tree-row.active {
            background: #17324d;
            border-color: #17324d;
          }

          .bayt-fm-tree-main {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            min-width: 0;
            flex: 1 1 auto;
          }

          .bayt-fm-tree-main > div {
            min-width: 0;
            flex: 1 1 auto;
          }

          .bayt-fm-indent {
            display: inline-flex;
            align-items: stretch;
            flex: 0 0 auto;
            height: 26px;
            position: relative;
          }

          .bayt-fm-indent::after {
            content: "";
            width: 100%;
            border-radius: 10px;
            background: linear-gradient(
              90deg,
              rgba(23,50,77,0.10) 0 2px,
              transparent 2px 100%
            );
          }

          .bayt-fm-tree-row.active .bayt-fm-indent::after {
            background: linear-gradient(
              90deg,
              rgba(255,255,255,0.22) 0 2px,
              transparent 2px 100%
            );
          }

          .bayt-fm-tree-name {
            color: var(--bayt-ink);
            font-weight: 750;
            font-size: 0.84rem;
            white-space: normal;
            overflow-wrap: anywhere;
            line-height: 1.15;
          }

          .bayt-fm-tree-row.active .bayt-fm-tree-name,
          .bayt-fm-tree-row.active .bayt-fm-tree-key {
            color: #fff;
          }

          .bayt-fm-tree-key {
            color: var(--bayt-muted);
            font-size: 0.7rem;
          }

          .bayt-fm-tree-actions {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            flex: 0 0 auto;
          }

          .bayt-fm-card-title {
            color: var(--bayt-ink);
            font-weight: 800;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
          }

          .bayt-fm-subtle {
            color: var(--bayt-muted);
            font-size: 0.78rem;
          }

          .bayt-fm-constraint-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 0.5rem;
            align-items: center;
            padding: 0.45rem 0;
            border-bottom: 1px solid rgba(216,225,232,0.7);
          }

          .bayt-fm-constraint-row:last-child {
            border-bottom: none;
          }

          .bayt-fm-feature-hero {
            border: 1px solid var(--bayt-line);
            border-radius: 16px;
            background: linear-gradient(145deg, rgba(255,255,255,0.96), rgba(246,249,246,0.92));
            padding: 0.85rem 0.95rem;
            margin-bottom: 0.85rem;
            position: relative;
            overflow: hidden;
          }

          .bayt-fm-feature-hero::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 6px;
            background: var(--bayt-accent);
          }

          .bayt-fm-feature-kicker {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--bayt-accent);
            font-weight: 800;
            margin-bottom: 0.22rem;
          }

          .bayt-fm-feature-name {
            color: var(--bayt-ink);
            font-size: 1.2rem;
            line-height: 1.08;
            font-weight: 800;
            margin: 0;
          }

          .bayt-fm-feature-key {
            color: var(--bayt-muted);
            font-size: 0.82rem;
            margin-top: 0.25rem;
          }

          .bayt-fm-feature-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 0.7rem;
          }

          .bayt-fm-feature-tag {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.22rem 0.55rem;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            border: 1px solid var(--bayt-line);
            color: var(--bayt-ink);
            background: rgba(255,255,255,0.9);
          }

          .bayt-fm-feature-tag.required {
            background: var(--bayt-accent-soft);
            color: #8a4a23;
            border-color: #ebc4af;
          }

          .bayt-fm-feature-tag.group {
            background: #e2ebf5;
            color: #38516b;
            border-color: #c9d7e6;
          }

          .bayt-fm-section {
            border-top: 1px solid rgba(216,225,232,0.75);
            padding-top: 0.85rem;
            margin-top: 0.85rem;
          }

          .bayt-fm-section:first-of-type {
            border-top: none;
            padding-top: 0;
            margin-top: 0;
          }

          .bayt-fm-section-title {
            color: var(--bayt-ink);
            font-size: 0.9rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
          }

          .bayt-fm-section-note {
            color: var(--bayt-muted);
            font-size: 0.76rem;
            margin-bottom: 0.7rem;
          }

          .bayt-fm-section-surface {
            border: 1px solid rgba(216,225,232,0.92);
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(248,250,249,0.94));
            padding: 0.85rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.92), 0 8px 18px rgba(23,50,77,0.03);
          }

          .bayt-fm-danger {
            border: 1px solid #ebc2bc;
            border-radius: 16px;
            background: #fff6f5;
            padding: 0.8rem 0.9rem;
            margin-top: 0.9rem;
          }

          .bayt-fm-danger-title {
            color: #8f3c33;
            font-size: 0.84rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
          }

          .bayt-fm-danger-note {
            color: #8f5a52;
            font-size: 0.75rem;
            margin-bottom: 0.65rem;
          }

          div[data-testid="stTextInput"] label,
          div[data-testid="stSelectbox"] label,
          div[data-testid="stCheckbox"] label {
            color: var(--bayt-ink) !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em;
          }

          div[data-testid="stTextInput"] [data-baseweb="input"],
          div[data-testid="stSelectbox"] [data-baseweb="select"],
          div[data-testid="stMultiSelect"] [data-baseweb="select"] {
            border-radius: 14px !important;
            border: 1.5px solid #c9d6e3 !important;
            background: rgba(255,255,255,0.96) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.85), 0 1px 3px rgba(23,50,77,0.04) !important;
            transition: border-color 120ms ease, box-shadow 120ms ease, background 120ms ease;
          }

          div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
          div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
          div[data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within {
            border-color: #c96d44 !important;
            box-shadow: 0 0 0 3px rgba(201,109,68,0.14) !important;
            background: #ffffff !important;
          }

          div[data-testid="stTextInput"] input,
          div[data-testid="stSelectbox"] input {
            color: var(--bayt-ink) !important;
            font-weight: 600 !important;
          }

          div[data-testid="stTextInput"] input::placeholder {
            color: #8a99a8 !important;
            font-weight: 500 !important;
          }

          div[data-testid="stCheckbox"] {
            padding: 0.1rem 0;
            border-radius: 0;
            background: transparent;
            border: none;
            min-height: 1.2rem;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"] {
            display: flex;
            align-items: center;
            justify-content: center;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
            width: 1.05rem !important;
            height: 1.05rem !important;
            border-radius: 999px !important;
            border: 1.6px solid #c4d0dc !important;
            background: #ffffff !important;
            box-shadow: 0 1px 2px rgba(23,50,77,0.06) !important;
            transition: border-color 120ms ease, box-shadow 120ms ease, background 120ms ease, transform 120ms ease !important;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"]:hover > div:first-child {
            border-color: #c96d44 !important;
            box-shadow: 0 0 0 3px rgba(201,109,68,0.10) !important;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"][aria-checked="true"] > div:first-child {
            background: linear-gradient(180deg, #c96d44, #b85e36) !important;
            border-color: #b85e36 !important;
            box-shadow: 0 0 0 3px rgba(201,109,68,0.12) !important;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"] svg {
            width: 0.66rem !important;
            height: 0.66rem !important;
            color: #ffffff !important;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"][aria-disabled="true"] {
            opacity: 1 !important;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"][aria-disabled="true"] > div:first-child {
            background: #e9eef2 !important;
            border-color: #cfd8e0 !important;
            box-shadow: none !important;
          }

          div[data-testid="stCheckbox"] [data-baseweb="checkbox"][aria-disabled="true"] svg {
            color: #9aabb9 !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- Utils ---
def load_fm(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("features", [None])[0], data.get("constraints", [])

def save_fm(path, root, constraints):
    payload = {
        "features": [root],
        "constraints": constraints,
    }
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

def detect_project_context(base_dir):
    base_path = Path(base_dir)
    if not base_path.exists() or not base_path.is_dir():
        return None, None

    fm_candidates = [
        f for f in base_path.rglob("*.fm.json")
        if "__MACOSX" not in str(f) and ".git" not in f.parts
    ]
    fm_path = str(fm_candidates[0]) if fm_candidates else None
    if not fm_path:
        return None, None

    possible_dirs = [d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('__MACOS')]
    core_path = None
    for d in possible_dirs:
        if any(p.suffix in [".py", ".js", ".java", ".c", ".cpp", ".yaml", ".yml"] for p in d.rglob("*")):
            core_path = d
            break
    if not core_path:
        core_path = base_path

    return fm_path, str(core_path)

def flatten_features(node):
    result = [node.get("key")]
    for child in node.get("children", []):
        result += flatten_features(child)
    return result

def add_ancestor_features(root, selected_features):
    selected = set(selected_features)

    def walk(node, ancestors):
        key = node.get("key")
        if key in selected:
            selected.update(ancestors)
        for child in node.get("children", []):
            walk(child, ancestors + [key])

    walk(root, [])
    return sorted(selected)

def generate_color_map(features):
    color_map = {}
    for feat in sorted(features):
        h = hashlib.md5(feat.encode('utf-8')).digest()
        r, g, b = h[0], h[1], h[2]
        r = int((r + 255) / 2)
        g = int((g + 255) / 2)
        b = int((b + 255) / 2)
        color_map[feat] = f"#{r:02x}{g:02x}{b:02x}"
    return color_map

def count_selected_descendants(node, selected_features):
    total = 1 if node.get("key") in selected_features else 0
    for child in node.get("children", []):
        total += count_selected_descendants(child, selected_features)
    return total

def subtree_matches(node, query):
    if not query:
        return True
    q = query.lower()
    if q in node.get("key", "").lower() or q in node.get("name", node.get("key", "")).lower():
        return True
    return any(subtree_matches(child, query) for child in node.get("children", []))

def collect_branch_stats(node, manual_selected, completed_selected):
    visible = add_ancestor_features(node, [f for f in completed_selected if f in flatten_features(node)])
    manual_count = len([f for f in manual_selected if f in flatten_features(node)])
    return manual_count, len(visible)

def find_feature_node(node, feature_key, ancestors=None):
    ancestors = ancestors or []
    if node.get("key") == feature_key:
        return node, ancestors
    for child in node.get("children", []):
        found = find_feature_node(child, feature_key, ancestors + [node.get("key")])
        if found:
            return found
    return None

def list_feature_nodes(node, level=0, parent=None):
    rows = [{
        "key": node.get("key"),
        "name": node.get("name", node.get("key")),
        "level": level,
        "parent": parent,
        "mandatory": bool(node.get("mandatory")),
        "group": node.get("group"),
    }]
    for child in node.get("children", []):
        rows.extend(list_feature_nodes(child, level + 1, node.get("key")))
    return rows

def clone_feature_model(root, constraints):
    return json.loads(json.dumps(root)), json.loads(json.dumps(constraints))

def update_feature_node(node, feature_key, updates):
    if node.get("key") == feature_key:
        node.update(updates)
        return True
    for child in node.get("children", []):
        if update_feature_node(child, feature_key, updates):
            return True
    return False

def add_child_feature(node, parent_key, child):
    if node.get("key") == parent_key:
        node.setdefault("children", []).append(child)
        return True
    for child_node in node.get("children", []):
        if add_child_feature(child_node, parent_key, child):
            return True
    return False

def delete_feature_node(node, feature_key):
    children = node.get("children", [])
    for index, child in enumerate(children):
        if child.get("key") == feature_key:
            del children[index]
            return True
        if delete_feature_node(child, feature_key):
            return True
    return False

def rename_feature_references(constraints, old_key, new_key):
    for constraint in constraints:
        if constraint.get("if") == old_key:
            constraint["if"] = new_key
        if constraint.get("source") == old_key:
            constraint["source"] = new_key
        if constraint.get("target") == old_key:
            constraint["target"] = new_key
        if "requires" in constraint:
            constraint["requires"] = [new_key if value == old_key else value for value in constraint["requires"]]
        if "excludes" in constraint:
            constraint["excludes"] = [new_key if value == old_key else value for value in constraint["excludes"]]

def delete_feature_references(constraints, feature_key):
    filtered = []
    for constraint in constraints:
        referenced = {constraint.get("if"), constraint.get("source"), constraint.get("target")}
        referenced.update(constraint.get("requires", []))
        referenced.update(constraint.get("excludes", []))
        if feature_key not in referenced:
            filtered.append(constraint)
    return filtered

def validate_feature_model(root, constraints):
    issues = []
    nodes = list_feature_nodes(root)
    keys = [node["key"] for node in nodes]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        issues.append("Duplicate feature keys: " + ", ".join(duplicates))

    key_set = set(keys)
    for node in nodes:
        if not node["key"]:
            issues.append("A feature is missing its key.")
        if node["group"] not in {None, "", "xor", "or"}:
            issues.append(f"Feature `{node['key']}` has an invalid group `{node['group']}`.")

    for constraint in constraints:
        relation = constraint.get("type")
        source = constraint.get("if") or constraint.get("source")
        targets = []
        if relation in {"requires", "excludes"}:
            targets.extend([constraint.get("target")])
        targets.extend(constraint.get("requires", []))
        targets.extend(constraint.get("excludes", []))
        if source and source not in key_set:
            issues.append(f"Constraint references unknown source `{source}`.")
        for target in filter(None, targets):
            if target not in key_set:
                issues.append(f"Constraint references unknown target `{target}`.")
    return list(dict.fromkeys(issues))

def render_fm_tree_sidebar(node_rows, selected_feature, color_map, root_key, constraints, search_query=""):
    q = search_query.strip().lower()
    for row in node_rows:
        name = row["name"]
        key = row["key"]
        if q and q not in name.lower() and q not in key.lower():
            continue
        active = key == selected_feature
        chips = []
        if row["mandatory"]:
            chips.append("<span class='bayt-meta required'>MANDATORY</span>")
        if row["group"] in {"xor", "or"}:
            chips.append(f"<span class='bayt-meta group'>{row['group'].upper()}</span>")
        row_cols = st.columns([8.8, 1.3], gap="small", vertical_alignment="center")
        with row_cols[0]:
            st.markdown(
                f"""
                <div class="bayt-fm-tree-row {'active' if active else ''}">
                  <div class="bayt-fm-tree-main" style="padding-left:{row['level'] * 14}px">
                    <span class="bayt-feature-badge" style="background:{color_map.get(key, '#d8e1e8')}"></span>
                    <div>
                      <div class="bayt-fm-tree-name">{name}</div>
                      <div class="bayt-fm-tree-key">{key}</div>
                    </div>
                  </div>
                  <div class="bayt-fm-tree-actions">
                    {''.join(chips)}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with row_cols[1]:
            if st.button(" ", key=f"fm_tree_select::{key}", type="secondary", icon=":material/edit:", use_container_width=False):
                st.session_state.focused_feature = key
                st.rerun()

def collect_feature_constraints(feature_key, constraints):
    results = []
    for constraint in constraints:
        src = constraint.get("if") or constraint.get("source")
        targets = []
        relation = None
        if "requires" in constraint:
            targets.extend(constraint.get("requires", []))
            relation = "requires"
        if "excludes" in constraint:
            targets.extend(constraint.get("excludes", []))
            relation = "excludes" if relation is None else relation
        if constraint.get("type") in {"requires", "excludes"}:
            targets.append(constraint.get("target"))
            relation = constraint.get("type")

        if src == feature_key:
            for tgt in filter(None, targets):
                results.append((relation or "relates", tgt, "outgoing"))
        elif feature_key in targets:
            results.append((relation or "relates", src, "incoming"))
    return results

def collect_solver_insights(selected_manual, selected_completed, constraints):
    manual = set(selected_manual)
    completed = set(selected_completed)
    inferred = sorted(completed - manual)
    blocked = []

    for constraint in constraints:
        source = constraint.get("if") or constraint.get("source")
        targets = []
        relation = constraint.get("type")
        if "requires" in constraint:
            targets.extend(constraint.get("requires", []))
            relation = "requires"
        if "excludes" in constraint:
            targets.extend(constraint.get("excludes", []))
            relation = "excludes"
        if constraint.get("type") in {"requires", "excludes"} and constraint.get("target"):
            targets.append(constraint.get("target"))

        if relation == "excludes" and source in manual:
            for target in targets:
                if target in manual:
                    blocked.append(f"{source} excludes {target}")

    return inferred, list(dict.fromkeys(blocked))

def collect_inference_reasons(selected_manual, selected_completed, constraints):
    manual = set(selected_manual)
    completed = set(selected_completed)
    inferred = sorted(completed - manual)
    reasons = []

    for feature in inferred:
        feature_reasons = []
        for constraint in constraints:
            source = constraint.get("if") or constraint.get("source")
            targets = []
            relation = constraint.get("type")
            if "requires" in constraint:
                targets.extend(constraint.get("requires", []))
                relation = "requires"
            if constraint.get("type") == "requires" and constraint.get("target"):
                targets.append(constraint.get("target"))

            if relation == "requires" and feature in targets and source in completed:
                qualifier = "manual" if source in manual else "auto"
                feature_reasons.append(f"{source} ({qualifier}) requires {feature}")

        if feature_reasons:
            reasons.append((feature, feature_reasons))

    return reasons

def collect_locked_features(root, constraints, selected_features):
    selected = set(selected_features)
    locked = {}

    def walk(node):
        children = node.get("children", [])
        if node.get("group") == "xor":
            selected_children = [child.get("key") for child in children if child.get("key") in selected]
            if selected_children:
                chosen = selected_children[0]
                for child in children:
                    child_key = child.get("key")
                    if child_key != chosen and child_key not in selected:
                        locked[child_key] = f"Locked by XOR choice `{chosen}`"
        for child in children:
            walk(child)

    walk(root)

    for constraint in constraints:
        source = constraint.get("if") or constraint.get("source")
        targets = []
        relation = constraint.get("type")
        if "excludes" in constraint:
            targets.extend(constraint.get("excludes", []))
            relation = "excludes"
        if constraint.get("type") == "excludes" and constraint.get("target"):
            targets.append(constraint.get("target"))

        if relation == "excludes":
            if source in selected:
                for target in targets:
                    if target not in selected:
                        locked[target] = f"Excluded by `{source}`"
            for target in targets:
                if target in selected and source not in selected:
                    locked[source] = f"Excluded by `{target}`"

    return locked

def render_constraint_chips(constraints):
    if not constraints:
        st.markdown("<div class='bayt-panel-note'>No cross-tree constraints in this model.</div>", unsafe_allow_html=True)
        return

    chunks = []
    for c in constraints:
        src = c.get("if") or c.get("source") or "?"
        if "requires" in c:
            for tgt in c["requires"]:
                chunks.append(f"<span class='bayt-chip requires'>{src} requires {tgt}</span>")
        if "excludes" in c:
            for tgt in c["excludes"]:
                chunks.append(f"<span class='bayt-chip excludes'>{src} excludes {tgt}</span>")
        if c.get("type") == "requires":
            chunks.append(f"<span class='bayt-chip requires'>{src} requires {c.get('target')}</span>")
        if c.get("type") == "excludes":
            chunks.append(f"<span class='bayt-chip excludes'>{src} excludes {c.get('target')}</span>")

    st.markdown("<div class='bayt-chip-row'>" + "".join(chunks) + "</div>", unsafe_allow_html=True)

# --- Expression evaluator for #if[...] ---
def eval_condition(expr, selected):
    expr = expr.replace("&&", " and ").replace("||", " or ").replace("!", " not ")
    reserved = {"and", "or", "not", "True", "False"}
    for f in re.findall(r"[A-Za-z0-9_]+", expr):
        if f in reserved:
            continue
        expr = re.sub(rf"\b{f}\b", str(f in selected), expr)
    try:
        return bool(eval(expr, {"__builtins__": {}}, {}))
    except Exception:
        return False

def extract_guard_expression(line):
    stripped = line.strip()
    if not stripped.startswith("#if["):
        return None

    expr = stripped[len("#if["):]
    expr = expr.replace("] and [", " && ")
    expr = expr.replace("] or [", " || ")
    expr = expr.replace("] && [", " && ")
    expr = expr.replace("] || [", " || ")
    expr = expr.replace("[", "").replace("]", "")
    return expr.strip()

def highlight_features_in_code(code, selected_features, color_map):
    lines = code.splitlines()
    highlighted = []
    stack = []
    for line in lines:
        stripped = line.strip()
        expr = extract_guard_expression(stripped)
        if expr:
            color = "#f0f0f0"
            for f in re.findall(r"[A-Za-z0-9_]+", expr):
                if f in color_map:
                    color = color_map[f]
                    break
            stack.append(expr)
            highlighted.append(f'<div style="background-color: {color}; padding-left: 10px;"><code>{line}</code><br>')
        elif "#endif" in stripped and stack:
            highlighted.append(f'<code>{line}</code></div><br>')
            stack.pop()
        else:
            highlighted.append(f'<code>{line}</code><br>')
    return "\n".join(highlighted)

def collect_code_annotations(code, selected_features, color_map):
    annotations = []
    stack = []
    lines = code.splitlines()
    known_features = set(color_map)

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        expr = extract_guard_expression(stripped)
        if expr:
            features = [
                token for token in re.findall(r"[A-Za-z0-9_]+", expr)
                if token not in {"and", "or", "not", "True", "False"}
            ]
            unknown_features = [feature for feature in features if feature not in known_features]
            color = "#e3a23b" if unknown_features else next((color_map.get(feature) for feature in features if feature in color_map), "#d8e1e8")
            annotation = {
                "expr": expr,
                "start": index,
                "end": index,
                "features": features,
                "unknown_features": unknown_features,
                "color": color,
                "active": eval_condition(expr, selected_features),
                "depth": len(stack),
            }
            annotations.append(annotation)
            stack.append(annotation)
            continue

        if "#endif" in stripped and stack:
            current = stack.pop()
            current["end"] = index

    for annotation in annotations:
        if annotation["end"] < annotation["start"]:
            annotation["end"] = annotation["start"]
    return annotations

def render_annotation_lane(code, selected_features, color_map):
    annotations = collect_code_annotations(code, selected_features, color_map)
    if not annotations:
        st.markdown("<div class='bayt-panel-note'>No `#if[...]` annotations detected in this file.</div>", unsafe_allow_html=True)
        return

    unknown_features = sorted({feature for annotation in annotations for feature in annotation.get("unknown_features", [])})
    if unknown_features:
        st.markdown(
            "<div class='bayt-unknown-callout'>"
            "<strong>Unknown features in code:</strong> "
            + " ".join(f"<span class='bayt-unknown-chip'>{feature}</span>" for feature in unknown_features)
            + "</div>",
            unsafe_allow_html=True,
        )

    cards = []
    for annotation in annotations:
        features = annotation["features"] or ["guard"]
        chips = "".join(
            (
                f"<span class='bayt-annotation-chip unknown'>{feature}</span>"
                if feature in annotation.get("unknown_features", [])
                else f"<span class='bayt-annotation-chip' style='background:{color_map.get(feature, annotation['color'])};'>{feature}</span>"
            )
            for feature in features[:4]
        )
        state = "ACTIVE" if annotation["active"] else "INACTIVE"
        if annotation.get("unknown_features"):
            state += " · UNKNOWN"
        cards.append(
            "<div class='bayt-annotation-card'>"
            f"<div class='bayt-annotation-rule'><span class='bayt-annotation-swatch' style='background:{annotation['color']};'></span>{annotation['expr']}</div>"
            f"<div class='bayt-annotation-meta'>lines {annotation['start']}-{annotation['end']} · depth {annotation['depth']} · {state}</div>"
            f"<div class='bayt-annotation-chips'>{chips}</div>"
            "</div>"
        )

    st.markdown("<div class='bayt-annotation-lane'>" + "".join(cards) + "</div>", unsafe_allow_html=True)

def list_files(directory):
    return sorted([
        str(p.relative_to(directory)) for p in Path(directory).rglob("*")
        if p.is_file() and not p.name.startswith(".") and p.suffix != ".pyc"
    ])

def read_file(file_path):
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

def save_text_file(file_path, content):
    Path(file_path).write_text(content, encoding="utf-8")

def handle_editor_payload(payload, editor_key, active_file, file_choice):
    if payload is None:
        return

    if isinstance(payload, str):
        st.session_state[editor_key] = payload
        return

    if not isinstance(payload, dict):
        return

    value = payload.get("value")
    if value is not None:
        st.session_state[editor_key] = value

    event_id = payload.get("eventId")
    if not event_id:
        return

    action = payload.get("action")
    event_key = f"editor_action::{editor_key}"
    if st.session_state.get(event_key) == event_id:
        return
    st.session_state[event_key] = event_id

    if action == "save":
        try:
            save_text_file(active_file, st.session_state.get(editor_key, ""))
            st.success(f"Saved {file_choice}")
        except Exception as exc:
            st.error(f"Save failed: {exc}")

def is_text_editable(file_path):
    path = Path(file_path)
    if not path.is_file():
        return False
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".db", ".sqlite", ".pyc", ".ico", ".pdf"}:
        return False
    try:
        path.read_text(encoding="utf-8")
        return True
    except Exception:
        return False

def monaco_language(file_path):
    suffix = Path(file_path).suffix.lower()
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".txt": "plaintext",
        ".html": "html",
        ".css": "css",
        ".xml": "xml",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
    }
    return mapping.get(suffix, "plaintext")

def file_icon(path_obj):
    if path_obj.is_dir():
        return "DIR"
    suffix = path_obj.suffix.lower()
    if suffix in {".py"}:
        return "PY"
    if suffix in {".yaml", ".yml"}:
        return "YAML"
    if suffix in {".json"}:
        return "JSON"
    if suffix in {".md"}:
        return "MD"
    if suffix in {".js", ".ts"}:
        return "JS"
    return "FILE"

def render_file_tree(base_dir, current_dir, query="", key_prefix="tree"):
    base_path = Path(current_dir)
    if not base_path.exists():
        return None

    selected = None
    normalized_query = query.strip().lower()
    expanded_key = f"expanded::{key_prefix}"
    if expanded_key not in st.session_state:
        st.session_state[expanded_key] = {""}

    def matches(entry):
        if not normalized_query:
            return True
        rel = str(entry.relative_to(base_path)).lower()
        return normalized_query in entry.name.lower() or normalized_query in rel

    def subtree_has_match(folder):
        if matches(folder):
            return True
        try:
            return any(
                subtree_has_match(child)
                for child in folder.iterdir()
                if not (child.name.startswith(".") and child.name not in {".storage"})
            )
        except Exception:
            return False

    def walk(folder, depth=0):
        nonlocal selected
        entries = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        for entry in entries:
            if entry.name.startswith(".") and entry.name not in {".storage"}:
                continue
            rel = str(entry.relative_to(base_path))
            if entry.is_dir():
                if not subtree_has_match(entry):
                    continue
                is_expanded = rel in st.session_state[expanded_key] or (normalized_query and depth < 2)
                spacer, row = st.columns([max(0.06, 0.07 * depth), 1], gap="small")
                with row:
                    if st.button(
                        f"{'▾' if is_expanded else '▸'} {entry.name}",
                        key=f"{key_prefix}:dir:{rel}",
                        use_container_width=True,
                        type="tertiary",
                        icon=":material/folder:",
                    ):
                        if rel in st.session_state[expanded_key]:
                            st.session_state[expanded_key].remove(rel)
                        else:
                            st.session_state[expanded_key].add(rel)
                        st.rerun()
                if is_expanded:
                    walk(entry, depth + 1)
            else:
                if not matches(entry):
                    continue
                spacer, row = st.columns([max(0.06, 0.07 * (depth + 0.2)), 1], gap="small")
                with row:
                    is_active = rel == st.session_state.get("active_editor_relpath")
                    label = f"{entry.name}{'  *' if file_dirty(rel, current_dir) else ''}"
                    if st.button(
                        label,
                        key=f"{key_prefix}:file:{rel}",
                        use_container_width=True,
                        type="tertiary",
                        icon=":material/description:",
                    ):
                        selected = rel
                    if is_active:
                        st.markdown(
                            "<div class='bayt-file-active-marker'></div>",
                            unsafe_allow_html=True,
                        )

    walk(base_path)
    return selected

def count_project_files(base_dir):
    base_path = Path(base_dir)
    if not base_path.exists():
        return 0
    return sum(
        1 for p in base_path.rglob("*")
        if p.is_file() and not (p.name.startswith(".") and ".storage" not in p.parts)
    )

def ensure_open_file_state():
    if "open_files" not in st.session_state:
        st.session_state.open_files = []
    if "active_editor_relpath" not in st.session_state:
        st.session_state.active_editor_relpath = None

def sync_editor_workspace(current_dir):
    available = set(list_files(current_dir)) if Path(current_dir).exists() else set()
    st.session_state.open_files = [rel for rel in st.session_state.open_files if rel in available]
    if st.session_state.active_editor_relpath not in available:
        st.session_state.active_editor_relpath = None

def open_file_in_editor(rel_path):
    ensure_open_file_state()
    if rel_path not in st.session_state.open_files:
        st.session_state.open_files.append(rel_path)
    st.session_state.active_editor_relpath = rel_path

def close_file_in_editor(rel_path):
    ensure_open_file_state()
    st.session_state.open_files = [p for p in st.session_state.open_files if p != rel_path]
    if st.session_state.active_editor_relpath == rel_path:
        st.session_state.active_editor_relpath = st.session_state.open_files[-1] if st.session_state.open_files else None

def file_dirty(rel_path, current_dir):
    source_name = "core" if "generated-variants" not in str(current_dir) else "derived"
    editor_key = f"editor::{source_name}::{rel_path}"
    path = Path(current_dir) / rel_path
    if not path.exists() or editor_key not in st.session_state:
        return False
    try:
        return st.session_state[editor_key] != path.read_text(encoding="utf-8")
    except Exception:
        return False

def create_new_file(base_dir, rel_path):
    target = Path(base_dir) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text("", encoding="utf-8")
    return str(target)

def rename_path(base_dir, old_rel_path, new_rel_path):
    source = Path(base_dir) / old_rel_path
    target = Path(base_dir) / new_rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    source.rename(target)
    return str(target)

def delete_path(base_dir, rel_path):
    target = Path(base_dir) / rel_path
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()

def diagnose_configuration(root, constraints, selected_features):
    selected = set(selected_features)
    issues = []

    def walk(node):
        parent_key = node["key"]
        children = node.get("children", [])
        chosen_children = [child["key"] for child in children if child["key"] in selected]

        if parent_key in selected:
            for child in children:
                if child.get("mandatory") and child["key"] not in selected:
                    issues.append(f"`{parent_key}` requires mandatory child `{child['key']}`.")

            group = node.get("group")
            if group == "xor":
                if len(chosen_children) == 0:
                    issues.append(f"`{parent_key}` requires exactly one child in XOR group: {', '.join(child['key'] for child in children)}.")
                elif len(chosen_children) > 1:
                    issues.append(f"`{parent_key}` allows only one XOR child, but got: {', '.join(chosen_children)}.")
            elif group == "or" and len(chosen_children) == 0:
                issues.append(f"`{parent_key}` requires at least one child in OR group: {', '.join(child['key'] for child in children)}.")

        for child in children:
            walk(child)

    walk(root)

    for constraint in constraints:
        if "type" in constraint:
            source = constraint.get("source")
            target = constraint.get("target")
            ctype = constraint.get("type")
            if ctype == "requires" and source in selected and target not in selected:
                issues.append(f"`{source}` requires `{target}`.")
            if ctype == "excludes" and source in selected and target in selected:
                issues.append(f"`{source}` excludes `{target}`.")
            continue

        source = constraint.get("if")
        if source not in selected:
            continue
        for target in constraint.get("requires", []):
            if target not in selected:
                issues.append(f"`{source}` requires `{target}`.")
        for target in constraint.get("excludes", []):
            if target in selected:
                issues.append(f"`{source}` excludes `{target}`.")

    # Keep order stable but remove duplicates.
    return list(dict.fromkeys(issues))

def explain_failure(root, constraints, solver, selected_features):
    if not selected_features:
        return "No features selected."

    issues = diagnose_configuration(root, constraints, selected_features)
    if issues:
        preview = issues[:4]
        suffix = " ..." if len(issues) > 4 else ""
        return "Invalid configuration: " + " ".join(preview) + suffix

    assumptions = [solver._get_var(f) for f in selected_features if f in solver.var_map]
    if not solver.solver.solve(assumptions=assumptions):
        return "Invalid configuration: the SAT model found an unresolved conflict."
    return None

def generate_variant(selected, core_dir, variant_name):
    out_dir = os.path.join(PERSISTENT_DIR, variant_name)
    os.makedirs(out_dir, exist_ok=True)
    for file in Path(core_dir).rglob("*"):
        if file.is_dir():
            continue
        rel = file.relative_to(core_dir)
        if rel.name == ".env":
            continue
        dest_file = Path(out_dir) / rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(file, dest_file)
            continue
        except Exception:
            continue
        lines = text.splitlines(keepends=True)
        output = []
        stack = []
        include = True
        for line in lines:
            stripped = line.strip()
            expr = extract_guard_expression(stripped)
            if expr:
                cond = eval_condition(expr, selected)
                stack.append((include, cond))
                include = include and cond
                continue
            if "#endif" in stripped and stack:
                include, _ = stack.pop()
                continue
            if include:
                output.append(line)
        with open(dest_file, "w", encoding="utf-8") as f:
            f.writelines(output)
    return out_dir

def collect_social_rules(node):
    rules = []
    def visit(n):
        for rel in n.get("relations", []):
            rules.append({
                "source": n["key"],
                "type": rel["type"],
                "target": rel["target"],
                "policies": rel.get("policies", [])
            })
        for child in n.get("children", []):
            visit(child)
    visit(node)
    return rules

def save_social_rules(rules, out_dir):
    with open(os.path.join(out_dir, "social_rules.json"), "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

def load_ha_credentials():
    creds = {
        "username": os.getenv("BAYTFACTORY_HA_USER") or os.getenv("BAYT_HASS_USER"),
        "password": os.getenv("BAYTFACTORY_HA_PASSWORD") or os.getenv("BAYT_HASS_PASS"),
    }
    if Path(PERSISTENT_CREDENTIALS).exists():
        for line in Path(PERSISTENT_CREDENTIALS).read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in {"BAYTFACTORY_HA_USER", "BAYT_HASS_USER"} and not creds["username"]:
                creds["username"] = value
            if key in {"BAYTFACTORY_HA_PASSWORD", "BAYT_HASS_PASS"} and not creds["password"]:
                creds["password"] = value

    creds["username"] = creds["username"] or DEFAULT_HA_USER
    creds["password"] = creds["password"] or DEFAULT_HA_PASSWORD
    return creds

def get_home_assistant_user_id(variant_path, username):
    auth_file = Path(variant_path) / ".storage" / "auth"
    provider_file = Path(variant_path) / ".storage" / "auth_provider.homeassistant"
    if not auth_file.exists() or not provider_file.exists():
        return None

    try:
        auth_data = json.loads(auth_file.read_text(encoding="utf-8"))
        provider_data = json.loads(provider_file.read_text(encoding="utf-8"))
    except Exception:
        return None

    provider_users = {
        user.get("id"): user.get("username")
        for user in provider_data.get("data", {}).get("users", [])
    }
    for user in auth_data.get("data", {}).get("users", []):
        if provider_users.get(user.get("auth_provider_id")) == username:
            return user.get("id")
    return None

def ensure_homeassistant_auth_provider(variant_path):
    config_path = Path(variant_path) / "configuration.yaml"
    if not config_path.exists():
        return

    text = config_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    homeassistant_idx = next((i for i, line in enumerate(lines) if line.strip() == "homeassistant:"), None)
    if homeassistant_idx is None:
        return

    auth_idx = next((i for i, line in enumerate(lines) if line.strip() == "auth_providers:"), None)
    if auth_idx is not None:
        end_idx = len(lines)
        for i in range(auth_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() and not line.startswith((" ", "\t")):
                end_idx = i
                break
        del lines[auth_idx:end_idx]

    insert_at = len(lines)
    for i in range(homeassistant_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith((" ", "\t")):
            insert_at = i
            break

    auth_block = [
        "  auth_providers:",
        "    - type: homeassistant",
        "",
    ]
    lines[insert_at:insert_at] = auth_block
    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def ensure_default_lovelace(variant_path):
    variant = Path(variant_path)
    ui = variant / "ui-lovelace.yaml"
    ll = variant / "lovelace_spl.yaml"
    if ui.exists():
        return
    if ll.exists():
        shutil.copyfile(ll, ui)
    else:
        ui.write_text("title: BaytFactory (auto)\nviews: []\n", encoding="utf-8")

def create_default_user(variant_path):
    creds = load_ha_credentials()
    username = creds["username"]
    password = creds["password"]

    venv_python = os.path.join(PERSISTENT_ENV, "bin", "python3")
    if not os.path.exists(venv_python):
        print("⚠️ Shared Home Assistant venv not found.")
        return

    try:
        result = subprocess.run(
            [
                venv_python, "-m", "homeassistant", "--script", "auth",
                "--config", variant_path, "validate", username, password
            ],
            text=True,
            capture_output=True,
            check=False
        )
        if result.returncode != 0 or "Auth valid" not in result.stdout:
            bootstrap = subprocess.run(
                [
                    venv_python,
                    os.path.join(os.getcwd(), "ha_bootstrap_user.py"),
                    "--config",
                    variant_path,
                    "--username",
                    username,
                    "--password",
                    password,
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            user_id = bootstrap.stdout.strip().splitlines()[-1].strip()
        else:
            user_id = get_home_assistant_user_id(variant_path, username)

        print(f"✅ Default user '{username}' ready.")
        return user_id
    except subprocess.CalledProcessError as e:
        print("⚠️ Failed to create default user:", e)
        if getattr(e, "stdout", None):
            print(e.stdout)
        if getattr(e, "stderr", None):
            print(e.stderr)
        return None

def prepare_variant_for_home_assistant(variant_path):
    ensure_default_lovelace(variant_path)
    ensure_homeassistant_auth_provider(variant_path)
    create_default_user(variant_path)

def home_assistant_access_message():
    creds = load_ha_credentials()
    return (
        "Acces local HA avec compte admin par defaut. "
        f"Identifiants: `{creds['username']}` / `{creds['password']}`."
    )

def get_home_assistant_port():
    forced = os.getenv("BAYTFACTORY_HA_PORT")
    if forced:
        try:
            return int(forced)
        except ValueError as exc:
            raise RuntimeError(f"Invalid BAYTFACTORY_HA_PORT value: {forced}") from exc

    return 8125

def load_deploy_state():
    path = Path(DEPLOY_STATE_FILE)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_deploy_state(state):
    Path(DEPLOY_STATE_FILE).write_text(json.dumps(state, indent=2), encoding="utf-8")

def stop_previous_home_assistant():
    state = load_deploy_state()
    pid = state.get("pid")
    if not pid:
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except Exception as exc:
        st.warning(f"Impossible d'arreter l'ancienne instance HA (pid={pid}) : {exc}")
    finally:
        save_deploy_state({})

def ensure_http_server_port(variant_path, port):
    config_path = Path(variant_path) / "configuration.yaml"
    if not config_path.exists():
        return

    lines = config_path.read_text(encoding="utf-8").splitlines()
    http_idx = next((i for i, line in enumerate(lines) if line.strip() == "http:"), None)
    if http_idx is None:
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith((" ", "\t")) and line.strip() != "homeassistant:":
                insert_at = i
                break
        lines[insert_at:insert_at] = ["http:", f"  server_port: {port}", ""]
    else:
        next_top = len(lines)
        for i in range(http_idx + 1, len(lines)):
            if lines[i].strip() and not lines[i].startswith((" ", "\t")):
                next_top = i
                break
        port_idx = next((i for i in range(http_idx + 1, next_top) if lines[i].strip().startswith("server_port:")), None)
        if port_idx is None:
            lines.insert(http_idx + 1, f"  server_port: {port}")
        else:
            lines[port_idx] = f"  server_port: {port}"

    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def disable_legacy_mqtt_block(variant_path):
    config_path = Path(variant_path) / "configuration.yaml"
    if not config_path.exists():
        return

    lines = config_path.read_text(encoding="utf-8").splitlines()
    mqtt_idx = next((i for i, line in enumerate(lines) if line.strip() == "mqtt:"), None)
    if mqtt_idx is None:
        return

    end_idx = len(lines)
    for i in range(mqtt_idx + 1, len(lines)):
        if lines[i].strip() and not lines[i].startswith((" ", "\t")):
            end_idx = i
            break

    replacement = [
        "# MQTT block disabled by BaytFactory for compatibility with current Home Assistant",
        "# Configure MQTT via HA UI/config entries if needed.",
        "",
    ]
    lines[mqtt_idx:end_idx] = replacement
    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_home_assistant(variant_path):
    base_dir = os.path.dirname(variant_path)
    hass_exec = os.path.join(base_dir, ".env", "bin", "hass")

    if not os.path.exists(hass_exec):
        st.error(f"⚠️ Impossible de trouver hass à l'emplacement attendu : {hass_exec}")
        return

    stop_previous_home_assistant()
    port = get_home_assistant_port()
    ensure_http_server_port(variant_path, port)
    disable_legacy_mqtt_block(variant_path)
    process = subprocess.Popen([hass_exec, "-c", variant_path])
    save_deploy_state({
        "pid": process.pid,
        "port": port,
        "variant_path": variant_path,
    })
    st.info(f"🚀 Home Assistant demarre avec le variant : {variant_path}")
    st.info(f"URL locale HA: http://localhost:{port}")
    st.info(home_assistant_access_message())

    def open_browser():
        time.sleep(5)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

def auto_initialize_variant(variant_dir: str, username: str, password: str):
    """Post-derivation: Lovelace de secours + création d'un admin HA dans ce dossier."""
    from pathlib import Path
    import shutil, subprocess

    variant = Path(variant_dir)
    variant.mkdir(parents=True, exist_ok=True)

    # --- 1) Lovelace: si pas de ui-lovelace.yaml, on essaye de copier lovelace_spl.yaml sinon on met un fallback
    ui = variant / "ui-lovelace.yaml"
    ll = variant / "lovelace_spl.yaml"
    if not ui.exists():
        if ll.exists():
            try:
                shutil.copyfile(ll, ui)
            except Exception as e:
                st.warning(f"Impossible de copier lovelace_spl.yaml -> ui-lovelace.yaml : {e}")
        if not ui.exists():
            # fallback minimal
            ui.write_text("title: BaytFactory (auto)\nviews: []\n", encoding="utf-8")

    # --- 2) Créer un admin si l’auth n’existe pas encore
    auth_file = variant / ".storage" / "auth"
    if auth_file.exists():
        return  # rien à faire : déjà initialisé

    # quel Python pour exécuter "python -m homeassistant" ?
    base_dir = variant.parent  # = PERSISTENT_DIR dans ton code
    py_exec = os.path.join(base_dir, ".env", "bin", "python")
    if not os.path.exists(py_exec):
        py_exec = shutil.which("python3") or shutil.which("python") or sys.executable

    cmd = [py_exec, "-m", "homeassistant", "--script", "auth", "-c", str(variant), "add", username, "--admin"]

    try:
        # Le script demande le mot de passe 2x sur stdin
        subprocess.run(cmd, input=f"{password}\n{password}\n", text=True, check=False)
    except Exception as e:
        st.warning(f"Création auto de l'admin HA non effectuée : {e}")

# --- Feature Model Rendering with D3.js ---
def render_fm_d3(root, constraints):
    fm_data = {"root": root, "constraints": constraints}
    fm_json = json.dumps(fm_data)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://d3js.org/d3.v7.min.js"></script>
      <style>
        body {{ margin: 0; background: transparent; font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, sans-serif; }}
        .link {{ fill: none; stroke: #afbcc9; stroke-opacity: 0.95; stroke-width: 1.8px; }}
        .node-card {{ fill: #fcfdfb; stroke: #d6dee5; stroke-width: 1.2px; rx: 16; ry: 16; filter: drop-shadow(0 6px 12px rgba(23,50,77,0.08)); }}
        .node-card.root {{ fill: #17324d; stroke: #17324d; }}
        .node-card.group-xor {{ fill: #f8e7e2; stroke: #e5bdb1; }}
        .node-card.group-or {{ fill: #e5eef6; stroke: #c7d6e6; }}
        .node-dot {{ stroke: #ffffff; stroke-width: 2px; }}
        .node-title {{ font-size: 13px; font-weight: 700; fill: #17324d; }}
        .node-title.root {{ fill: #ffffff; }}
        .node-meta {{ font-size: 10px; font-weight: 700; letter-spacing: 0.06em; fill: #637487; }}
        .node-meta.root {{ fill: rgba(255,255,255,0.72); }}
      </style>
    </head>
    <body>
      <svg id="fm_svg" width="100%" height="860"></svg>
      <script>
        var data = {fm_json};
        var svg = d3.select("#fm_svg"), g = svg.append("g");
        var zoom = d3.zoom().scaleExtent([0.5, 3]).on("zoom", function(event) {{ g.attr("transform", event.transform); }});
        svg.call(zoom);

        var root = d3.hierarchy(data.root, d => d.children);
        var treeLayout = d3.tree().nodeSize([210, 96]);
        treeLayout(root);

        g.selectAll(".link").data(root.links()).enter()
          .append("path").attr("class", "link")
          .attr("d", d3.linkVertical().x(d => d.x).y(d => d.y));

        var node = g.selectAll(".node")
          .data(root.descendants()).enter()
          .append("g")
          .attr("class", "node")
          .attr("transform", d => "translate(" + d.x + "," + d.y + ")");

        node.append("rect")
          .attr("class", d => {{
            const classes = ["node-card"];
            if (d.depth === 0) classes.push("root");
            if (d.data.group === "xor") classes.push("group-xor");
            if (d.data.group === "or") classes.push("group-or");
            return classes.join(" ");
          }})
          .attr("x", -10)
          .attr("y", -24)
          .attr("width", 178)
          .attr("height", 48);

        node.append("circle")
          .attr("class", "node-dot")
          .attr("cx", 10)
          .attr("cy", 0)
          .attr("r", 7)
          .attr("fill", d => d.depth === 0 ? "#f0c7b5" : (d.data.mandatory ? "#c96d44" : "#90a3b5"));

        node.append("text")
          .attr("class", d => d.depth === 0 ? "node-title root" : "node-title")
          .attr("x", 25)
          .attr("y", -2)
          .text(d => d.data.name || d.data.key);

        node.append("text")
          .attr("class", d => d.depth === 0 ? "node-meta root" : "node-meta")
          .attr("x", 25)
          .attr("y", 14)
          .text(d => {{
            const meta = [];
            if (d.data.mandatory) meta.push("MANDATORY");
            if (d.data.group) meta.push(d.data.group.toUpperCase());
            if (!meta.length) meta.push("OPTIONAL");
            return meta.join(" • ");
          }});

        svg.call(zoom.transform, d3.zoomIdentity.translate(180, 70));
      </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=880, scrolling=True)

# --- UI Config ---
st.set_page_config(layout='wide')
inject_global_styles()
st.image("logo.png", width=200)
st.markdown(
    """
    <div class="bayt-hero">
      <div class="bayt-kicker">Smart Home Product Line Engineering</div>
      <h1 class="bayt-title">BaytFactory Variant Studio</h1>
      <div class="bayt-subtitle">
        Configure features, inspect variability, derive a runnable variant, and validate it in Home Assistant.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

source_mode = st.radio("Project Source", ["Workspace folder", "ZIP upload"], horizontal=True)
default_workspace = os.getcwd()
project_path = None
fm_path = None
core_path = None

if source_mode == "Workspace folder":
    local_project_dir = st.text_input("Project folder", value=default_workspace)
    if local_project_dir:
        project_path = local_project_dir
        fm_path, core_path = detect_project_context(local_project_dir)
        if not fm_path:
            st.info("Select a local folder that contains a `*.fm.json` file and source files.")
else:
    uploaded = st.file_uploader('📦 Upload ZIP with source code + `.fm.json`', type='zip')
    if uploaded:
        tmpdir = tempfile.mkdtemp()
        with open(os.path.join(tmpdir, 'project.zip'), 'wb') as f:
            f.write(uploaded.read())
        with zipfile.ZipFile(os.path.join(tmpdir, 'project.zip'), 'r') as zipf:
            zipf.extractall(tmpdir)
        project_path = tmpdir
        fm_path, core_path = detect_project_context(tmpdir)

if fm_path and core_path:
        os.makedirs(PERSISTENT_DIR, exist_ok=True)
        loaded_root, loaded_constraints = load_fm(fm_path)
        fm_state_key = f"fm_editor::{fm_path}"
        if st.session_state.get("fm_editor_source") != fm_state_key:
            editor_root, editor_constraints = clone_feature_model(loaded_root, loaded_constraints)
            st.session_state.fm_editor_source = fm_state_key
            st.session_state.fm_editor_root = editor_root
            st.session_state.fm_editor_constraints = editor_constraints
            st.session_state.manual_selected = []
            st.session_state.selected = []
            st.session_state.rendered_selected = []
            st.session_state.rendered_auto_selected = []
        root = st.session_state.fm_editor_root
        constraints = st.session_state.fm_editor_constraints
        all_social_rules = collect_social_rules(root)
        solver = SATFeatureSolver(root, constraints)

        if 'selected' not in st.session_state:
            st.session_state.selected = []
        if 'manual_selected' not in st.session_state:
            st.session_state.manual_selected = []
        if 'source' not in st.session_state:
            st.session_state.source = 'core'
        if 'focused_feature' not in st.session_state:
            st.session_state.focused_feature = root.get("key")
        if st.session_state.focused_feature not in flatten_features(root):
            st.session_state.focused_feature = root.get("key")

        all_features = flatten_features(root) or []
        st.session_state.manual_selected = [feature for feature in st.session_state.manual_selected if feature in all_features]
        color_map = generate_color_map(all_features)

        model_tab, configure_tab, code_tab = st.tabs(["Feature Model (FM)", "Variant Derivation", "Code Explorer"])

        with model_tab:
            preview_tab, editor_tab = st.tabs(["FM Preview", "FM Editor"])

            with preview_tab:
                st.markdown("<div class='bayt-panel-title'>Feature Model</div>", unsafe_allow_html=True)
                st.markdown(
                    """
                    <div class='bayt-legend'>
                      <span class='bayt-legend-item'><span class='bayt-legend-dot' style='background:#17324d'></span>Root</span>
                      <span class='bayt-legend-item'><span class='bayt-legend-dot' style='background:#c96d44'></span>Mandatory</span>
                      <span class='bayt-legend-item'><span class='bayt-legend-dot' style='background:#90a3b5'></span>Optional</span>
                      <span class='bayt-legend-item'>XOR and OR groups are highlighted on their parent nodes</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                render_fm_d3(root, constraints)

                st.markdown("<div class='bayt-panel-title'>Constraints</div>", unsafe_allow_html=True)
                render_constraint_chips(constraints)

            with editor_tab:
                fm_issues = validate_feature_model(root, constraints)
                node_rows = list_feature_nodes(root)
                node_lookup = {row["key"]: row for row in node_rows}
                feature_options = [row["key"] for row in node_rows]
                selected_feature = st.session_state.focused_feature if st.session_state.focused_feature in feature_options else root.get("key")
                selected_node, selected_ancestors = find_feature_node(root, selected_feature)
                selected_node = selected_node or root

                st.markdown("<div class='bayt-fm-shell'>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class='bayt-fm-header'>
                      <div class='bayt-fm-stat'>
                        <div class='label'>Model</div>
                        <div class='value'>{Path(fm_path).name}</div>
                      </div>
                      <div class='bayt-fm-stat'>
                        <div class='label'>Features</div>
                        <div class='value'>{len(feature_options)}</div>
                      </div>
                      <div class='bayt-fm-stat'>
                        <div class='label'>Constraints</div>
                        <div class='value'>{len(constraints)}</div>
                      </div>
                      <div class='bayt-fm-stat'>
                        <div class='label'>Status</div>
                        <div class='value'>{'Issues' if fm_issues else 'Clean'}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                editor_actions = st.columns([1, 1, 2.4, 1.2])
                if editor_actions[0].button("Save Model", key="fm_save", use_container_width=True, type="primary"):
                    save_fm(fm_path, root, constraints)
                    st.success(f"Saved {Path(fm_path).name}")
                if editor_actions[1].button("Reset Draft", key="fm_reset", use_container_width=True):
                    reset_root, reset_constraints = clone_feature_model(loaded_root, loaded_constraints)
                    st.session_state.fm_editor_root = reset_root
                    st.session_state.fm_editor_constraints = reset_constraints
                    st.session_state.focused_feature = reset_root.get("key")
                    st.rerun()
                if fm_issues:
                    editor_actions[3].error(f"{len(fm_issues)} issues")
                else:
                    editor_actions[3].success("Valid")

                editor_tree_col, editor_props_col = st.columns([1.05, 1.95], gap="large")
                node_rows = list_feature_nodes(root)

                with editor_tree_col:
                    st.markdown("<div class='bayt-fm-panel'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-card-title'>Feature Tree</div>", unsafe_allow_html=True)
                    tree_search = st.text_input("Search features", value="", placeholder="Search by key or label", key="fm_tree_search")
                    toolbar = st.columns([1, 1])
                    with toolbar[0].popover("New Child", use_container_width=True):
                        new_child_key = st.text_input("Child key", key="fm_add_child_key", placeholder="NewFeature")
                        new_child_name = st.text_input("Child label", key="fm_add_child_name", placeholder="New Feature")
                        add_cols = st.columns(2)
                        new_child_mandatory = add_cols[0].checkbox("Mandatory", key="fm_add_child_mandatory")
                        new_child_group = add_cols[1].selectbox("Group", ["", "xor", "or"], key="fm_add_child_group")
                        if st.button("Add Child", key="fm_add_child_submit", use_container_width=True, type="primary"):
                            if new_child_key.strip():
                                child_payload = {
                                    "key": new_child_key.strip(),
                                    "name": new_child_name.strip() or new_child_key.strip(),
                                    "mandatory": new_child_mandatory,
                                    "children": [],
                                }
                                if new_child_group:
                                    child_payload["group"] = new_child_group
                                add_child_feature(root, selected_feature, child_payload)
                                st.session_state.focused_feature = child_payload["key"]
                                st.rerun()
                    toolbar[1].markdown("")
                    render_fm_tree_sidebar(node_rows, selected_feature, color_map, root.get("key"), constraints, tree_search)
                    st.markdown("</div>", unsafe_allow_html=True)

                with editor_props_col:
                    hero_tags = [
                        "<span class='bayt-fm-feature-tag'>FEATURE</span>",
                        ("<span class='bayt-fm-feature-tag required'>MANDATORY</span>" if selected_node.get("mandatory") else "<span class='bayt-fm-feature-tag'>OPTIONAL</span>"),
                    ]
                    if selected_node.get("group") in {"xor", "or"}:
                        hero_tags.append(f"<span class='bayt-fm-feature-tag group'>{selected_node.get('group').upper()} GROUP</span>")
                    if selected_ancestors:
                        hero_tags.append(f"<span class='bayt-fm-feature-tag'>PARENT {selected_ancestors[-1]}</span>")
                    st.markdown("<div class='bayt-fm-panel'>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                        <div class='bayt-fm-feature-hero'>
                          <div class='bayt-fm-feature-kicker'>Feature Editor</div>
                          <h3 class='bayt-fm-feature-name'>{selected_node.get('name', selected_feature)}</h3>
                          <div class='bayt-fm-feature-key'>{selected_feature}</div>
                          <div class='bayt-fm-feature-tags'>{''.join(hero_tags)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown("<div class='bayt-fm-section'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-surface'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-title'>Identity</div>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-note'>Update the feature key and the business label shown across the configurator.</div>", unsafe_allow_html=True)
                    prop_key = st.text_input("Feature key", value=selected_node.get("key", ""), key=f"fm_prop_key::{selected_feature}")
                    prop_name = st.text_input("Feature label", value=selected_node.get("name", selected_feature), key=f"fm_prop_name::{selected_feature}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<div class='bayt-fm-section'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-surface'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-title'>Structure</div>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-note'>Define how this feature behaves in the tree and how children are selected.</div>", unsafe_allow_html=True)
                    prop_cols = st.columns(2)
                    prop_mandatory = prop_cols[0].checkbox("Mandatory", value=bool(selected_node.get("mandatory")), key=f"fm_prop_mandatory::{selected_feature}")
                    prop_group = prop_cols[1].selectbox("Group", ["", "xor", "or"], index=["", "xor", "or"].index(selected_node.get("group", "")) if selected_node.get("group", "") in {"", "xor", "or"} else 0, key=f"fm_prop_group::{selected_feature}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<div class='bayt-fm-section'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-title'>Apply</div>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-note'>Commit the current edits to the in-memory model before saving the FM file.</div>", unsafe_allow_html=True)
                    if st.button("Save Changes", key=f"fm_apply::{selected_feature}", use_container_width=True, type="primary"):
                        old_key = selected_node.get("key")
                        updates = {
                            "key": prop_key.strip() or old_key,
                            "name": prop_name.strip() or prop_key.strip() or old_key,
                            "mandatory": prop_mandatory,
                        }
                        if prop_group:
                            updates["group"] = prop_group
                        else:
                            selected_node.pop("group", None)
                        update_feature_node(root, old_key, updates)
                        if old_key != updates["key"]:
                            rename_feature_references(constraints, old_key, updates["key"])
                            st.session_state.focused_feature = updates["key"]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                    if selected_ancestors:
                        st.markdown("<div class='bayt-fm-subtle'>Ancestors: " + " / ".join(selected_ancestors) + "</div>", unsafe_allow_html=True)

                    st.markdown("<div class='bayt-fm-section'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-surface'>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-title'>Cross-tree Constraints</div>", unsafe_allow_html=True)
                    st.markdown("<div class='bayt-fm-section-note'>Inspect relationships that force or block this feature elsewhere in the model.</div>", unsafe_allow_html=True)
                    existing_constraints = collect_feature_constraints(selected_feature, constraints)
                    if existing_constraints:
                        for idx, (rel, other, direction) in enumerate(existing_constraints):
                            row_cols = st.columns([5, 1])
                            row_cols[0].markdown(f"<div class='bayt-fm-constraint-row'><div><span class='bayt-chip {'requires' if rel == 'requires' else 'excludes' if rel == 'excludes' else ''}'>{direction} {rel} {other}</span></div></div>", unsafe_allow_html=True)
                            if row_cols[1].button("Remove", key=f"fm_delete_constraint::{selected_feature}::{idx}", use_container_width=True):
                                new_constraints = []
                                removed = False
                                for constraint in constraints:
                                    src = constraint.get("if") or constraint.get("source")
                                    targets = constraint.get("requires", []) + constraint.get("excludes", []) + ([constraint.get("target")] if constraint.get("target") else [])
                                    ctype = constraint.get("type") or ("requires" if constraint.get("requires") else "excludes" if constraint.get("excludes") else None)
                                    is_match = (
                                        not removed
                                        and ctype == rel
                                        and ((direction == "outgoing" and src == selected_feature and other in targets) or (direction == "incoming" and src == other and selected_feature in targets))
                                    )
                                    if is_match:
                                        removed = True
                                        continue
                                    new_constraints.append(constraint)
                                st.session_state.fm_editor_constraints = new_constraints
                                st.rerun()
                    else:
                        st.markdown("<div class='bayt-fm-subtle'>No constraints for this feature.</div>", unsafe_allow_html=True)

                    with st.popover("Add Constraint", use_container_width=False):
                        add_constraint_cols = st.columns([2, 1, 2])
                        constraint_direction = add_constraint_cols[0].selectbox("Direction", ["outgoing", "incoming"], key=f"fm_constraint_direction::{selected_feature}")
                        constraint_type = add_constraint_cols[1].selectbox("Relation", ["requires", "excludes"], key=f"fm_constraint_type::{selected_feature}")
                        constraint_target = add_constraint_cols[2].selectbox("Target", [key for key in feature_options if key != selected_feature], key=f"fm_constraint_target::{selected_feature}")
                        if st.button("Create Constraint", key=f"fm_add_constraint::{selected_feature}", use_container_width=True, type="primary"):
                            if constraint_direction == "outgoing":
                                constraints.append({"type": constraint_type, "source": selected_feature, "target": constraint_target})
                            else:
                                constraints.append({"type": constraint_type, "source": constraint_target, "target": selected_feature})
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    if selected_feature != root.get("key"):
                        st.markdown(
                            """
                            <div class='bayt-fm-danger'>
                              <div class='bayt-fm-danger-title'>Danger Zone</div>
                              <div class='bayt-fm-danger-note'>Delete this feature and remove all constraints that reference it.</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Delete Feature", key=f"fm_delete_feature::{selected_feature}", use_container_width=True):
                            delete_feature_node(root, selected_feature)
                            st.session_state.fm_editor_constraints = delete_feature_references(constraints, selected_feature)
                            st.session_state.focused_feature = root.get("key")
                            st.rerun()

                    if fm_issues:
                        st.markdown("<div class='bayt-fm-card-title' style='margin-top:0.9rem;'>Validation</div>", unsafe_allow_html=True)
                        st.markdown("<div class='bayt-chip-row'>" + "".join(f"<span class='bayt-chip excludes'>{issue}</span>" for issue in fm_issues[:6]) + "</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

        with configure_tab:
            st.markdown("<div class='bayt-panel-title'>Configurator</div>", unsafe_allow_html=True)
            st.markdown("<div class='bayt-panel-note'>Select the business options you want. The solver keeps the result minimal and only infers what is strictly required.</div>", unsafe_allow_html=True)
            st.markdown("<div class='bayt-config-shell'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class='bayt-config-hero'>
                  <div class='bayt-config-hero-title'>Configuration Studio</div>
                  <div class='bayt-config-hero-note'>Pick the features you want, inspect what the solver adds, and understand conflicts before generating a variant.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            head_cols = st.columns([1, 1], gap="small")
            variant_name = head_cols[0].text_input("Variant Name", value="variant1")
            search_query = head_cols[1].text_input("Search features", value="", placeholder="Search by feature name or key")
            filter_mode = st.pills("Filter", ["All", "Manual only", "Inferred only", "Selected only"], default="All", key="config_filter", width="stretch")

            rendered_selected = set(st.session_state.get("rendered_selected", st.session_state.selected))
            prior_auto_selected = set(st.session_state.get("rendered_auto_selected", []))
            requested_checked = {
                feature for feature in all_features
                if st.session_state.get(f"chk_{feature}", feature in rendered_selected)
            }
            manual_preview = requested_checked - prior_auto_selected
            completed_preview = solver.complete_model(list(manual_preview))
            resolved_preview = set(completed_preview or [])
            new_checked = set(manual_preview)
            locked_features = collect_locked_features(root, constraints, resolved_preview)
            for feature in all_features:
                st.session_state[f"chk_{feature}"] = feature in resolved_preview if completed_preview is not None else feature in requested_checked

            def render_node(node, level=0):
                if not subtree_matches(node, search_query):
                    return

                key = node.get('key')
                name = node.get('name', key)
                is_manual = key in manual_preview
                is_inferred = key in resolved_preview and key not in manual_preview
                is_selected = key in resolved_preview
                lock_reason = locked_features.get(key)
                is_locked = bool(lock_reason) and not is_selected

                if filter_mode == "Manual only" and not is_manual:
                    return
                if filter_mode == "Inferred only" and not is_inferred:
                    return
                if filter_mode == "Selected only" and not is_selected:
                    return

                cols = st.columns([1.0, 0.56, 0.12], gap="small")

                color = color_map.get(key, '#d8e1e8')
                with cols[0]:
                    line_cols = st.columns([max(level, 0) * 0.2 + 0.08, 0.26, 4.2], gap="small")
                    with line_cols[0]:
                        st.markdown("&nbsp;", unsafe_allow_html=True)
                    with line_cols[1]:
                        checked = st.checkbox(
                            label=f"Select {name}",
                            key=f'chk_{key}',
                            label_visibility="collapsed",
                            disabled=is_locked,
                        )
                    with line_cols[2]:
                        lock_markup = "<span class='bayt-config-lock'>LOCK</span>" if is_locked else ""
                        st.markdown(
                            (
                                f"<div class='bayt-config-row {'active' if is_selected else ''} {'locked' if is_locked else ''}'>"
                                "<div class='bayt-config-main'>"
                                f"<span class='bayt-config-feature-bar' style='background:{color}'></span>"
                                "<div>"
                                f"<div class='bayt-config-name'>{name}</div>"
                                f"<div class='bayt-config-key'>{key}</div>"
                                "</div>"
                                f"{lock_markup}"
                                "</div></div>"
                            ),
                            unsafe_allow_html=True,
                        )

                if cols[2].button(" ", key=f"focus_{key}", icon=":material/open_in_new:", use_container_width=False, type="secondary"):
                    st.session_state.focused_feature = key

                tags = []
                if node.get("mandatory"):
                    tags.append("<span class='bayt-meta required'>MANDATORY</span>")
                if node.get("group") in {"xor", "or"}:
                    tags.append(f"<span class='bayt-meta group'>{node.get('group').upper()}</span>")
                if is_manual:
                    tags.append("<span class='bayt-meta manual'>MANUAL</span>")
                elif is_inferred:
                    tags.append("<span class='bayt-meta inferred'>INFERRED</span>")
                elif is_selected:
                    tags.append("<span class='bayt-meta'>ACTIVE</span>")
                if is_locked:
                    tags.append("<span class='bayt-meta excludes'>LOCKED</span>")
                cols[1].markdown("".join(tags), unsafe_allow_html=True)

                if checked:
                    new_checked.add(key)

                for child in node.get('children', []):
                    render_node(child, level + 1)

            top_branches = root.get("children", [])
            root_manual_count, root_visible_count = collect_branch_stats(root, manual_preview, resolved_preview)
            st.markdown(
                f"""
                <div class='bayt-config-mini-stats'>
                  <div class='bayt-config-mini-stat'><div class='label'>Model Root</div><div class='value'>{root.get('name', root.get('key'))}</div></div>
                  <div class='bayt-config-mini-stat'><div class='label'>Manual Picks</div><div class='value'>{root_manual_count}</div></div>
                  <div class='bayt-config-mini-stat'><div class='label'>Visible After Solve</div><div class='value'>{root_visible_count}</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for branch in top_branches:
                if not subtree_matches(branch, search_query):
                    continue
                branch_manual_count, branch_visible_count = collect_branch_stats(branch, manual_preview, resolved_preview)
                st.markdown(
                    (
                        "<div class='bayt-config-group'>"
                        f"<div class='bayt-config-group-title'>{branch.get('name', branch.get('key'))}</div>"
                        f"<div class='bayt-config-group-meta'>{branch_manual_count} manual · {branch_visible_count} visible after solve</div>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
                render_node(branch, level=1)

            st.session_state.manual_selected = sorted(new_checked)
            completed_model = solver.complete_model(list(st.session_state.manual_selected))
            config_status = "Invalid"
            config_status_class = ""
            resolved_for_ui = list(completed_model or new_checked)
            if completed_model is None:
                st.warning(f"⚠️ {explain_failure(root, constraints, solver, list(new_checked))}")
            else:
                st.session_state.selected = completed_model
                config_status = "Valid"
                config_status_class = "good"
                resolved_for_ui = list(completed_model)
            st.session_state.rendered_selected = list(resolved_for_ui)
            st.session_state.rendered_auto_selected = [feature for feature in resolved_for_ui if feature not in st.session_state.manual_selected]

            display_selected = add_ancestor_features(root, resolved_for_ui)
            inferred_features, blocked_rules = collect_solver_insights(st.session_state.manual_selected, resolved_for_ui, constraints)
            inference_reasons = collect_inference_reasons(st.session_state.manual_selected, resolved_for_ui, constraints)
            st.markdown(
                f"""
                <div class="bayt-summary">
                  <div class="bayt-summary-card">
                    <div class="bayt-summary-label">Manual Picks</div>
                    <div class="bayt-summary-value">{len(new_checked)}</div>
                  </div>
                  <div class="bayt-summary-card">
                    <div class="bayt-summary-label">Visible Features</div>
                    <div class="bayt-summary-value">{len(display_selected)}</div>
                  </div>
                  <div class="bayt-summary-card">
                    <div class="bayt-summary-label">Configuration</div>
                    <div class="bayt-summary-value {config_status_class}">{config_status}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("**Final Selected Features**")
            st.markdown(
                "<div class='bayt-chip-row'>" + "".join(
                    f"<span class='bayt-chip'>{feat}{' · manual' if feat in st.session_state.manual_selected else ' · inferred' if feat in resolved_for_ui else ''}</span>"
                    for feat in display_selected
                ) + "</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class='bayt-config-insight'>
                  <div class='bayt-config-insight-title'>Solver Insight</div>
                  <div class='bayt-config-insight-note'>Understand what was selected manually, what the solver added, and what conflicts remain.</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("**Inferred by solver**")
            if inferred_features:
                st.markdown("<div class='bayt-chip-row'>" + "".join(f"<span class='bayt-chip'>{feat}</span>" for feat in inferred_features) + "</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='bayt-fm-subtle'>No additional features were inferred.</div>", unsafe_allow_html=True)

            if inference_reasons:
                st.markdown("**Why these features were added**")
                for feature, reasons in inference_reasons:
                    st.markdown(
                        "<div class='bayt-chip-row'>"
                        + f"<span class='bayt-chip'>{feature}</span>"
                        + "".join(f"<span class='bayt-chip requires'>{reason}</span>" for reason in reasons)
                        + "</div>",
                        unsafe_allow_html=True,
                    )

            st.markdown("**Conflicts / blocked rules**")
            if blocked_rules:
                st.markdown("<div class='bayt-chip-row'>" + "".join(f"<span class='bayt-chip excludes'>{item}</span>" for item in blocked_rules) + "</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='bayt-fm-subtle'>No excludes conflict detected in the current manual selection.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            focused_feature = st.session_state.focused_feature
            found = find_feature_node(root, focused_feature)
            if found:
                focus_node, focus_ancestors = found
                focus_constraints = collect_feature_constraints(focused_feature, constraints)
                focus_children = [child.get("key") for child in focus_node.get("children", [])]
                focus_name = focus_node.get("name", focused_feature)
                focus_status = "Manual" if focused_feature in st.session_state.manual_selected else "Inferred" if focused_feature in resolved_for_ui else "Idle"
                st.markdown("<div class='bayt-panel-title' style='margin-top:1rem;'>Feature Detail</div>", unsafe_allow_html=True)
                st.markdown(f"**{focus_name}**")
                st.markdown(
                    "<div class='bayt-chip-row'>"
                    + f"<span class='bayt-chip'>{focused_feature}</span>"
                    + f"<span class='bayt-chip'>{focus_status}</span>"
                    + (f"<span class='bayt-chip'>group: {focus_node.get('group')}</span>" if focus_node.get('group') else "")
                    + ("<span class='bayt-chip'>mandatory</span>" if focus_node.get('mandatory') else "<span class='bayt-chip'>optional</span>")
                    + "</div>",
                    unsafe_allow_html=True,
                )
                if focus_ancestors:
                    st.markdown("**Ancestors**")
                    st.markdown("<div class='bayt-chip-row'>" + "".join(f"<span class='bayt-chip'>{a}</span>" for a in focus_ancestors) + "</div>", unsafe_allow_html=True)
                if focus_children:
                    st.markdown("**Children**")
                    st.markdown("<div class='bayt-chip-row'>" + "".join(f"<span class='bayt-chip'>{c}</span>" for c in focus_children) + "</div>", unsafe_allow_html=True)
                if focus_constraints:
                    st.markdown("**Constraints**")
                    st.markdown(
                        "<div class='bayt-chip-row'>"
                        + "".join(
                            f"<span class='bayt-chip {'requires' if rel == 'requires' else 'excludes' if rel == 'excludes' else ''}'>{'from' if direction == 'incoming' else 'to'} {other} ({rel})</span>"
                            for rel, other, direction in focus_constraints
                        )
                        + "</div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """
                <div class='bayt-runtime-shell'>
                  <div class='bayt-runtime-panel'>
                    <div class='bayt-runtime-title'>Variant Runtime</div>
                    <div class='bayt-runtime-note'>Finalize the current configuration, generate the derived variant, then launch it in Home Assistant from the same workflow.</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            runtime_cols = st.columns([1, 1, 1], gap="small")
            runtime_cols[0].markdown(
                f"<div class='bayt-summary-card'><div class='bayt-summary-label'>Variant</div><div class='bayt-summary-value'>{variant_name}</div></div>",
                unsafe_allow_html=True,
            )
            runtime_cols[1].markdown(
                f"<div class='bayt-summary-card'><div class='bayt-summary-label'>Manual Picks</div><div class='bayt-summary-value'>{len(st.session_state.manual_selected)}</div></div>",
                unsafe_allow_html=True,
            )
            runtime_cols[2].markdown(
                f"<div class='bayt-summary-card'><div class='bayt-summary-label'>Resolved Features</div><div class='bayt-summary-value'>{len(st.session_state.selected)}</div></div>",
                unsafe_allow_html=True,
            )

            if st.session_state.selected:
                st.markdown("**Ready to build**")
                st.markdown(
                    "<div class='bayt-chip-row'>" + "".join(
                        f"<span class='bayt-chip'>{feat}{' · manual' if feat in st.session_state.manual_selected else ' · inferred'}</span>"
                        for feat in add_ancestor_features(root, st.session_state.selected)
                    ) + "</div>",
                    unsafe_allow_html=True,
                )

            action_cols = st.columns([1, 1, 2.2], gap="small")
            if action_cols[0].button('Generate Variant', key="config_generate", use_container_width=True, type="primary"):
                if solver.is_valid(st.session_state.selected):
                    variant_dir = generate_variant(st.session_state.selected, core_path, variant_name)
                    prepare_variant_for_home_assistant(variant_dir)
                    save_social_rules(all_social_rules, variant_dir)
                    st.session_state.variant_name = variant_name
                    st.success(f"Variant generated in {variant_dir}")
                    st.info(home_assistant_access_message())
                else:
                    st.error("Invalid feature selection.")

            variant_ready = "variant_name" in st.session_state
            if action_cols[1].button('Deploy on Home Assistant', key="config_deploy", use_container_width=True, type="primary", disabled=not variant_ready):
                run_home_assistant(os.path.join(PERSISTENT_DIR, st.session_state.variant_name))

            if variant_ready:
                action_cols[2].markdown(
                    f"<div class='bayt-fm-subtle'>Current variant folder: {os.path.join(PERSISTENT_DIR, st.session_state.variant_name)}</div>",
                    unsafe_allow_html=True,
                )
            else:
                action_cols[2].markdown(
                    "<div class='bayt-fm-subtle'>Generate a variant first to enable deployment.</div>",
                    unsafe_allow_html=True,
                )

        with code_tab:
            st.markdown("<div class='bayt-panel-title'>Source Code Viewer</div>", unsafe_allow_html=True)
            st.markdown("<div class='bayt-panel-note'>Open one project folder, browse its files from a clean explorer, and edit the active file in Monaco.</div>", unsafe_allow_html=True)
            ensure_open_file_state()
            st.markdown("<div class='bayt-code-shell'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class='bayt-code-access'>
                  <div class='bayt-code-access-title'>Workspace Access</div>
                  <div class='bayt-code-access-note'>Switch between the original project, a generated variant, or any local folder you want to inspect in Monaco.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            variant_candidates = sorted(
                [p.name for p in Path(PERSISTENT_DIR).iterdir() if p.is_dir() and not p.name.startswith(".")] if Path(PERSISTENT_DIR).exists() else []
            )
            if st.session_state.get("source") not in {"project", "variant", "folder"}:
                st.session_state.source = "project"
            if "code_variant_target" not in st.session_state:
                st.session_state.code_variant_target = st.session_state.get("variant_name") or (variant_candidates[0] if variant_candidates else "")
            if "code_folder_target" not in st.session_state:
                st.session_state.code_folder_target = str(core_path)

            access_cols = st.columns([1.1, 1.35, 1.55], gap="small")
            if access_cols[0].button("Project Workspace", key="code_open_project", icon=":material/folder_open:", use_container_width=True, type="primary"):
                st.session_state.source = "project"
                st.session_state.code_folder_target = str(core_path)
                st.rerun()

            selected_variant = access_cols[1].selectbox(
                "Generated variants",
                variant_candidates or [""],
                index=(variant_candidates.index(st.session_state.code_variant_target) if st.session_state.code_variant_target in variant_candidates else 0) if variant_candidates else 0,
                key="code_variant_select",
                disabled=not variant_candidates,
            )
            if selected_variant:
                st.session_state.code_variant_target = selected_variant
            if access_cols[1].button("Open Selected Variant", key="code_open_variant", icon=":material/deployed_code:", use_container_width=True, type="primary", disabled=not variant_candidates):
                st.session_state.source = "variant"
                st.rerun()

            folder_cols = st.columns([2.2, 1], gap="small")
            st.session_state.code_folder_target = folder_cols[0].text_input(
                "Open folder path",
                value=st.session_state.code_folder_target,
                placeholder=str(core_path),
                key="code_folder_input",
            )
            if folder_cols[1].button("Open Folder", key="code_open_folder", icon=":material/drive_folder_upload:", use_container_width=True, type="primary"):
                folder_candidate = Path(st.session_state.code_folder_target)
                if folder_candidate.exists() and folder_candidate.is_dir():
                    st.session_state.source = "folder"
                    st.rerun()
                else:
                    st.error("Folder does not exist.")

            if st.session_state.source == "variant" and st.session_state.code_variant_target:
                current_dir = os.path.join(PERSISTENT_DIR, st.session_state.code_variant_target)
            elif st.session_state.source == "folder":
                current_dir = st.session_state.code_folder_target
            else:
                current_dir = core_path
            sync_editor_workspace(current_dir)
            tree_col, editor_col = st.columns([1.05, 2.8], gap="large")

            with tree_col:
                st.markdown("<div class='bayt-code-sidebar'>", unsafe_allow_html=True)
                meta_cols = st.columns([2.2, 1])
                with meta_cols[0]:
                    workspace_label = "Project" if st.session_state.source == "project" else "Variant" if st.session_state.source == "variant" else "Folder"
                    st.markdown(f"<div class='bayt-code-badge'>{workspace_label}: {Path(current_dir).name}</div>", unsafe_allow_html=True)
                with meta_cols[1]:
                    st.markdown(f"<div class='bayt-code-badge'>{count_project_files(current_dir)} files</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='bayt-code-meta'>{current_dir}</div>", unsafe_allow_html=True)

                file_search = st.text_input("Search files", value="", placeholder="app, yaml, thermostat...", key=f"file_search::{st.session_state.source}::{Path(current_dir).name}")

                with st.expander("Workspace actions", expanded=False):
                    new_file_rel = st.text_input("New file", value="", placeholder="src/new_module.py")
                    if st.button("Create File", use_container_width=True, key=f"create::{st.session_state.source}::{Path(current_dir).name}", icon=":material/note_add:", type="primary"):
                        if new_file_rel.strip():
                            try:
                                create_new_file(current_dir, new_file_rel.strip())
                                open_file_in_editor(new_file_rel.strip())
                                st.success(f"Created {new_file_rel.strip()}")
                            except Exception as exc:
                                st.error(f"Create failed: {exc}")

                    current_rel = st.session_state.active_editor_relpath or ""
                    rename_rel = st.text_input("Rename active file", value=current_rel, placeholder="src/renamed.py", key=f"rename_input::{st.session_state.source}")
                    rename_cols = st.columns(2)
                    if rename_cols[0].button("Rename File", use_container_width=True, disabled=not current_rel, key=f"rename::{st.session_state.source}::{Path(current_dir).name}", icon=":material/edit_document:"):
                        try:
                            rename_path(current_dir, current_rel, rename_rel)
                            close_file_in_editor(current_rel)
                            open_file_in_editor(rename_rel)
                            st.success(f"Renamed to {rename_rel}")
                        except Exception as exc:
                            st.error(f"Rename failed: {exc}")
                    if rename_cols[1].button("Delete File", use_container_width=True, disabled=not current_rel, key=f"delete::{st.session_state.source}::{Path(current_dir).name}", icon=":material/delete:"):
                        try:
                            delete_path(current_dir, current_rel)
                            close_file_in_editor(current_rel)
                            st.success(f"Deleted {current_rel}")
                        except Exception as exc:
                            st.error(f"Delete failed: {exc}")

                tree_selection = render_file_tree(project_path, current_dir, query=file_search, key_prefix=f"tree::{st.session_state.source}::{Path(current_dir).name}")
                if tree_selection:
                    open_file_in_editor(tree_selection)
                st.markdown("</div>", unsafe_allow_html=True)

            with editor_col:
                file_choice = st.session_state.active_editor_relpath
                if not file_choice:
                    available_files = list_files(current_dir)
                    if available_files:
                        file_choice = available_files[0]
                        open_file_in_editor(file_choice)

                st.markdown("<div class='bayt-code-editor'>", unsafe_allow_html=True)
                if st.session_state.open_files:
                    selected_tab = st.segmented_control(
                        "Open files",
                        st.session_state.open_files,
                        default=st.session_state.active_editor_relpath,
                        key=f"open_files_tabs::{st.session_state.source}",
                        format_func=lambda rel: f"{Path(rel).name}{' *' if file_dirty(rel, current_dir) else ''}",
                        label_visibility="collapsed",
                        width="stretch",
                    )
                    if selected_tab:
                        st.session_state.active_editor_relpath = selected_tab
                    if st.session_state.active_editor_relpath:
                        toolbar_cols = st.columns([1, 1.2, 4])
                        if toolbar_cols[0].button("Save", key=f"toolbar-save::{st.session_state.source}", icon=":material/save:", use_container_width=True, type="primary"):
                            active_rel = st.session_state.active_editor_relpath
                            active_path = os.path.join(current_dir, active_rel)
                            editor_key = f"editor::{st.session_state.source}::{active_rel}"
                            if is_text_editable(active_path):
                                try:
                                    save_text_file(active_path, st.session_state.get(editor_key, ""))
                                    st.success(f"Saved {active_rel}")
                                except Exception as exc:
                                    st.error(f"Save failed: {exc}")
                        if toolbar_cols[1].button("Close", key=f"close_active_file::{st.session_state.source}", icon=":material/close:", use_container_width=True):
                            close_file_in_editor(st.session_state.active_editor_relpath)
                    file_choice = st.session_state.active_editor_relpath

                if file_choice:
                    active_file = os.path.join(current_dir, file_choice)
                    editor_key = f"editor::{st.session_state.source}::{file_choice}"
                    editable = is_text_editable(active_file)
                    st.caption(active_file)
                    if editable and st.session_state.get("active_editor_file") != active_file:
                        file_content = read_file(active_file)
                        st.session_state["active_editor_file"] = active_file
                        st.session_state[editor_key] = file_content

                    if editable:
                        st.markdown("<div class='bayt-panel-note'>SPL annotations detected in the active file.</div>", unsafe_allow_html=True)
                        code_value = st.session_state.get(editor_key, "")
                        annotations = collect_code_annotations(code_value, st.session_state.get("selected", []), color_map)
                        render_annotation_lane(code_value, st.session_state.get("selected", []), color_map)
                        updated_value = st_annotated_monaco(
                            value=code_value,
                            language=monaco_language(active_file),
                            theme="vs-light",
                            height=620,
                            annotations=annotations,
                            features=sorted(all_features),
                            path=file_choice,
                            key=f"annotated_monaco::{st.session_state.source}::{file_choice}",
                        )
                        handle_editor_payload(updated_value, editor_key, active_file, file_choice)

                        with st.expander("Raw annotated preview", expanded=False):
                            html_code = highlight_features_in_code(st.session_state[editor_key], st.session_state.get("selected", []), color_map)
                            st.markdown(f"<div style='font-family: monospace; font-size: 16px;'>{html_code}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("This file is not UTF-8 text editable in Monaco. Use the explorer for text sources only.")
                else:
                    st.markdown("<div class='bayt-code-empty'>Select a file from the explorer to start editing.</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

elif source_mode == "ZIP upload" and 'uploaded' in locals() and uploaded:
    st.error("❌ ZIP must contain `.fm.json` and source code.")
