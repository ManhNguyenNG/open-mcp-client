# Guide de Configuration

## Prérequis

### Système
- **Node.js** : Version 18+ (recommandé 20+)
- **Python** : Version 3.10-3.12
- **pnpm** : Version 10.2.1+
- **Poetry** : Version 1.7.0+

### Comptes et API Keys
- **OpenAI** : Compte avec accès aux modèles GPT-4o
- **LangSmith** : Compte pour le monitoring (optionnel mais recommandé)

## Installation

### 1. Cloner le Repository

```bash
git clone https://github.com/your-org/open-mcp-client.git
cd open-mcp-client
```

### 2. Configuration Frontend

```bash
# Installer les dépendances
pnpm install

# Créer le fichier d'environnement
touch .env
```

Ajouter les variables d'environnement dans `.env` :

```env
# OpenAI API Key (requis)
OPENAI_API_KEY=sk-your-openai-api-key

# LangSmith API Key (optionnel mais recommandé)
LANGSMITH_API_KEY=lsv2-your-langsmith-api-key

# URL du déploiement agent (optionnel, par défaut localhost:8123)
AGENT_DEPLOYMENT_URL=http://localhost:8123
```

### 3. Configuration Backend

```bash
# Aller dans le dossier agent
cd agent

# Installer Poetry si pas déjà installé
pip install poetry

# Installer les dépendances
poetry install

# Créer le fichier d'environnement
touch .env
```

Ajouter les variables d'environnement dans `agent/.env` :

```env
# OpenAI API Key (requis)
OPENAI_API_KEY=sk-your-openai-api-key

# LangSmith API Key (optionnel mais recommandé)
LANGSMITH_API_KEY=lsv2-your-langsmith-api-key
```

## Démarrage

### Option 1 : Démarrage Combiné (Recommandé)

```bash
# Depuis la racine du projet
pnpm run dev
```

Cette commande démarre automatiquement :
- Frontend sur `http://localhost:3000`
- Backend sur `http://localhost:8123`

### Option 2 : Démarrage Séparé

**Terminal 1 - Frontend :**
```bash
pnpm run dev-frontend
```

**Terminal 2 - Backend :**
```bash
pnpm run dev-agent
```

## Vérification

### 1. Frontend
- Ouvrir `http://localhost:3000`
- Vérifier que l'interface se charge correctement
- Tester l'interface de chat

### 2. Backend
- Vérifier que le serveur LangGraph répond sur `http://localhost:8123`
- Consulter les logs pour détecter d'éventuelles erreurs

### 3. Services MCP
- Vérifier que le serveur mathématique fonctionne
- Tester une opération simple via l'interface

## Configuration Avancée

### 1. Services MCP Personnalisés

Créer un nouveau serveur MCP dans `agent/` :

```python
# agent/my_service.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyService")

@mcp.tool()
def my_function(param: str) -> str:
    """Description de la fonction"""
    return f"Processed: {param}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Ajouter la configuration dans l'interface ou dans `DEFAULT_MCP_CONFIG`.

### 2. Variables d'Environnement Supplémentaires

**Pour le développement :**
```env
# Mode debug
NODE_ENV=development
DEBUG=true

# Configuration LangGraph
LANGGRAPH_HOST=localhost
LANGGRAPH_PORT=8123
```

**Pour la production :**
```env
# Configuration de production
NODE_ENV=production
AGENT_DEPLOYMENT_URL=https://your-agent-domain.com
```

### 3. Configuration LangSmith

Pour un monitoring avancé :

```env
# LangSmith configuration
LANGSMITH_PROJECT=open-mcp-client
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING_V2=true
```

## Dépannage

### Problèmes Courants

#### 1. Erreur de Port
```
Error: listen EADDRINUSE: address already in use :::3000
```
**Solution :** Changer le port ou arrêter le processus existant

#### 2. Erreur de Dépendances Python
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution :** Réinstaller les dépendances Poetry
```bash
cd agent
poetry install --sync
```

#### 3. Erreur d'API Key
```
Error: Invalid API key
```
**Solution :** Vérifier les clés API dans les fichiers `.env`

#### 4. Erreur de Connexion MCP
```
Connection refused to MCP service
```
**Solution :** Vérifier la configuration MCP et les chemins des serveurs

### Logs et Debugging

#### Frontend
```bash
# Activer les logs détaillés
DEBUG=true pnpm run dev-frontend
```

#### Backend
```bash
# Logs LangGraph
cd agent
poetry run langgraph dev --host localhost --port 8123 --verbose
```

#### LangSmith
- Consulter le dashboard LangSmith pour les traces
- Vérifier les métriques de performance
- Analyser les erreurs d'exécution

## Prochaines Étapes

1. **Explorer l'interface** : Tester les fonctionnalités de base
2. **Configurer des services MCP** : Ajouter des services personnalisés
3. **Personnaliser l'agent** : Modifier les instructions et comportements
4. **Déployer en production** : Suivre le guide de déploiement
