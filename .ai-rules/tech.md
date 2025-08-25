---
title: Technology Stack
description: "Defines the project's technology stack, dependencies, and development tools."
inclusion: always
---

# Technology Stack - Open MCP Client

## Frontend Stack

### Core Framework
- **Next.js 15.2.0-canary.73** : Framework React avec App Router
- **React 19.0.0** : Bibliothèque UI
- **TypeScript 5** : Typage statique

### UI & Styling
- **Tailwind CSS 4** : Framework CSS utilitaire
- **Tailwind CSS Animate** : Animations CSS
- **Class Variance Authority** : Gestion des variantes de composants
- **Lucide React** : Icônes modernes
- **Heroicons** : Icônes SVG

### State Management & Runtime
- **CopilotKit 1.6.0** : Framework pour intégration IA
  - `@copilotkit/react-core` : Composants React de base
  - `@copilotkit/react-ui` : Composants UI pré-construits
  - `@copilotkit/runtime` : Runtime pour agents IA

### Data Processing
- **React Spreadsheet 0.9.5** : Composant de feuille de calcul
- **Class Validator 0.14.1** : Validation de données

### Development Tools
- **ESLint 9** : Linting JavaScript/TypeScript
- **PostCSS** : Post-processing CSS
- **Concurrently 9.1.2** : Exécution parallèle de scripts

## Backend Stack

### Core Framework
- **Python 3.10-3.12** : Langage principal
- **Poetry** : Gestionnaire de dépendances Python
- **LangGraph 0.3.5** : Framework pour agents conversationnels

### AI & LLM Integration
- **LangChain 0.3.1** : Framework pour applications LLM
- **LangChain OpenAI 0.2.1** : Intégration OpenAI
- **LangChain Anthropic 0.2.1** : Intégration Anthropic
- **LangChain Community 0.3.1** : Extensions communautaires
- **LangChain Core 0.3.25** : Composants de base

### MCP Protocol
- **FastMCP 0.4.1** : Framework pour serveurs MCP
- **LangChain MCP Adapters 0.0.3** : Adaptateurs MCP pour LangChain

### Development & Runtime
- **Uvicorn 0.31.0** : Serveur ASGI
- **LangGraph CLI 0.1.64** : Outils de ligne de commande
- **Python-dotenv 1.0.1** : Gestion des variables d'environnement

## External Services

### AI Services
- **OpenAI API** : Modèles GPT-4o, GPT-4o-mini
- **LangSmith** : Monitoring et observabilité des agents

### Development Environment
- **pnpm 10.2.1** : Gestionnaire de paquets Node.js
- **Git** : Contrôle de version

## Scripts de Développement

### Frontend
```bash
pnpm run dev-frontend    # Démarrage du frontend avec Turbopack
pnpm run build          # Build de production
pnpm run start          # Démarrage en production
pnpm run lint           # Linting du code
```

### Backend
```bash
cd agent
poetry install          # Installation des dépendances
poetry run langgraph dev --host localhost --port 8123 --no-browser
```

### Développement Combiné
```bash
pnpm run dev            # Démarrage frontend + backend en parallèle
pnpm run dev-agent      # Démarrage du backend agent uniquement
```

## Configuration Requise

### Variables d'Environnement
- `OPENAI_API_KEY` : Clé API OpenAI
- `LANGSMITH_API_KEY` : Clé API LangSmith pour monitoring
- `AGENT_DEPLOYMENT_URL` : URL du déploiement agent (optionnel)

### Ports Utilisés
- **3000** : Frontend Next.js
- **8123** : Backend LangGraph

## Architecture Technique

### Communication
- **MCP Protocol** : Communication entre frontend et services externes
- **HTTP/SSE** : Communication entre frontend et backend
- **WebSocket** : Communication temps réel (si nécessaire)

### Data Flow
1. Frontend → API Route → CopilotKit Runtime
2. CopilotKit → LangGraph Platform Endpoint
3. LangGraph → MCP Services via adaptateurs
4. Retour via la même chaîne avec monitoring LangSmith
