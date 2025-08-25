---
title: Project Structure
description: "Defines the project's file organization, naming conventions, and architectural patterns."
inclusion: always
---

# Project Structure - Open MCP Client

## Overview
Le projet suit une architecture monorepo avec deux composants principaux : un frontend Next.js et un backend Python LangGraph, séparés dans des dossiers distincts.

## Root Structure

```
open-mcp-client/
├── .ai-rules/                    # Fichiers de steering pour IA
├── app/                         # Frontend Next.js (App Router)
├── agent/                       # Backend Python LangGraph
├── lib/                         # Utilitaires partagés
├── public/                      # Assets statiques
├── docs/                        # Documentation du projet
└── Configuration files
```

## Frontend Structure (`app/`)

### Core Files
- `layout.tsx` : Layout principal avec configuration CopilotKit
- `page.tsx` : Page d'accueil avec interface principale
- `globals.css` : Styles globaux Tailwind CSS
- `types.ts` : Types TypeScript partagés
- `instructions.ts` : Instructions pour l'agent IA

### API Routes (`app/api/`)
- `copilotkit/route.ts` : Endpoint principal pour CopilotKit

### Components (`app/components/`)
- `CopilotActionHandler.tsx` : Gestionnaire d'actions CopilotKit
- `MCPConfigForm.tsx` : Formulaire de configuration MCP
- `SpreadsheetRenderer.tsx` : Rendu des feuilles de calcul
- `SingleSpreadsheet.tsx` : Composant de feuille de calcul individuelle
- `ToolCallRenderer.tsx` : Affichage des appels d'outils
- `ExampleConfigs.tsx` : Configurations d'exemple
- `PreviewSpreadsheetChanges.tsx` : Prévisualisation des changements

### Hooks (`app/hooks/`)
- `useLocalStorage.ts` : Hook pour stockage local

### Utils (`app/utils/`)
- `canonicalSpreadsheetData.ts` : Utilitaires pour données de feuille de calcul

## Backend Structure (`agent/`)

### Core Files
- `pyproject.toml` : Configuration Poetry et dépendances
- `langgraph.json` : Configuration LangGraph
- `math_server.py` : Serveur MCP exemple pour calculs

### Agent Module (`agent/sample_agent/`)
- `__init__.py` : Module Python
- `agent.py` : Définition de l'agent LangGraph principal

## Documentation Structure (`docs/`)

### Architecture (`docs/architecture/`)
- `overview.md` : Vue d'ensemble de l'architecture
- `frontend.md` : Architecture frontend détaillée
- `backend.md` : Architecture backend détaillée
- `mcp-integration.md` : Intégration MCP
- `data-flow.md` : Flux de données

### Operations (`docs/operations/`)
- `setup.md` : Guide de configuration
- `deployment.md` : Guide de déploiement
- `monitoring.md` : Monitoring avec LangSmith
- `troubleshooting.md` : Résolution de problèmes

### Features (`docs/features/`)
- `chat-interface/` : Interface de chat
  - `requirements.md`
  - `design.md`
  - `tasks.md`
- `mcp-configuration/` : Configuration MCP
  - `requirements.md`
  - `design.md`
  - `tasks.md`
- `spreadsheet-processing/` : Traitement de feuilles de calcul
  - `requirements.md`
  - `design.md`
  - `tasks.md`

### Schemas (`docs/schemas/`)
- `mcp-config.schema.json` : Schéma de configuration MCP
- `agent-state.schema.json` : Schéma d'état de l'agent
- `spreadsheet-data.schema.json` : Schéma des données de feuille de calcul

## Naming Conventions

### Files
- **React Components** : PascalCase (`MCPConfigForm.tsx`)
- **Hooks** : camelCase avec préfixe `use` (`useLocalStorage.ts`)
- **Utils** : camelCase (`canonicalSpreadsheetData.ts`)
- **Python Modules** : snake_case (`math_server.py`)
- **Python Classes** : PascalCase (`AgentState`)

### Directories
- **Frontend** : kebab-case (`mcp-config-form/`)
- **Backend** : snake_case (`sample_agent/`)
- **Documentation** : kebab-case (`chat-interface/`)

### Variables & Functions
- **TypeScript** : camelCase
- **Python** : snake_case
- **Constants** : UPPER_SNAKE_CASE

## Configuration Files

### Frontend
- `package.json` : Dépendances et scripts Node.js
- `tsconfig.json` : Configuration TypeScript
- `next.config.ts` : Configuration Next.js
- `tailwind.config.js` : Configuration Tailwind CSS
- `eslint.config.mjs` : Configuration ESLint

### Backend
- `pyproject.toml` : Dépendances et configuration Poetry
- `langgraph.json` : Configuration LangGraph
- `.env` : Variables d'environnement

## Development Workflow

### Adding New Components
1. Créer le composant dans `app/components/`
2. Ajouter les types dans `app/types.ts` si nécessaire
3. Importer et utiliser dans `app/page.tsx`

### Adding New MCP Services
1. Créer le serveur MCP dans `agent/`
2. Ajouter la configuration dans `DEFAULT_MCP_CONFIG`
3. Tester via l'interface de configuration

### Adding New Features
1. Créer le dossier dans `docs/features/`
2. Documenter les requirements, design et tasks
3. Implémenter selon la documentation

## Import Patterns

### Frontend
```typescript
// Composants locaux
import { MCPConfigForm } from "./components/MCPConfigForm";

// Utilitaires
import { canonicalSpreadsheetData } from "./utils/canonicalSpreadsheetData";

// Hooks
import { useLocalStorage } from "./hooks/useLocalStorage";
```

### Backend
```python
# Modules locaux
from sample_agent.agent import AgentState

# Dépendances externes
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
```

## State Management

### Frontend
- **CopilotKit State** : État global de l'application
- **Local Storage** : Persistance des configurations MCP
- **React State** : État local des composants

### Backend
- **AgentState** : État de l'agent LangGraph
- **MemorySaver** : Persistance de l'état entre sessions
- **MCP Client** : État des connexions MCP
