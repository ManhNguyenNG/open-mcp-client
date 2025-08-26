# Guide de Configuration

## Prérequis

### Système
- **Node.js** : Version 18+ (recommandé 20+)
- **Python** : Version 3.10-3.12
- **pnpm** : Version 10.2.1+
- **Poetry** : Version 1.7.0+

### Comptes et API Keys
- **AWS** : Compte AWS avec accès à Bedrock (requis par défaut)
- **OpenAI** : Compte avec accès aux modèles GPT-4o (optionnel)
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
# OpenAI API Key (optionnel, si vous voulez utiliser OpenAI)
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
# LangSmith API Key (optionnel mais recommandé)
LANGSMITH_API_KEY=lsv2-your-langsmith-api-key

# Configuration AWS Bedrock (requis par défaut)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_SESSION_TOKEN=your-session-token  # Optionnel, pour les rôles temporaires

# Configuration Bedrock (optionnel, valeurs par défaut utilisées)
AWS_REGION=us-east-1  # Par défaut: us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0  # Par défaut

# Paramètres optionnels de tuning
BEDROCK_MAX_TOKENS=1000
BEDROCK_TEMPERATURE=0.7
BEDROCK_TOP_P=0.9
BEDROCK_STOP=stop1,stop2,stop3  # Séquences d'arrêt séparées par des virgules
```

## Configuration AWS Bedrock (Par Défaut)

### Prérequis AWS
- Compte AWS avec accès à Amazon Bedrock
- Permissions IAM pour Bedrock (ex: `AmazonBedrockFullAccess`)
- Modèle Bedrock activé dans votre région

### Variables d'Environnement Bedrock

**Bedrock est maintenant le provider par défaut.** Pour utiliser OpenAI à la place, ajoutez :

```env
# Pour utiliser OpenAI au lieu de Bedrock
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
```

### Modèles Bedrock Supportés

Le projet supporte les modèles Bedrock suivants :
- **Anthropic Claude** : `us.anthropic.claude-sonnet-4-20250514-v1:0` (par défaut)
- **Anthropic Claude 3.5 Sonnet** : `us.anthropic.claude-3-5-sonnet-20241022-v1:0`
- **Anthropic Claude 3 Haiku** : `us.anthropic.claude-3-haiku-20240307-v1:0`
- **Meta Llama 3** : `meta.llama3-8b-instruct-v1:0`
- **Amazon Titan** : `amazon.titan-text-express-v1`

### Configuration des Permissions AWS

Assurez-vous que votre utilisateur/rôle AWS a les permissions suivantes :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        }
    ]
}
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

### 4. Provider LLM
- **Bedrock** : Provider par défaut, vérifier les logs pour confirmer l'utilisation
- **OpenAI** : Vérifier que les réponses arrivent normalement (si explicitement configuré)

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

#### 5. Erreurs Bedrock

**Erreur de permissions :**
```
Access denied. Please check your AWS credentials and permissions.
```
**Solution :** Vérifier les permissions IAM pour Bedrock

**Erreur de throttling :**
```
Request rate exceeded. Please wait a moment and try again.
```
**Solution :** Le système retry automatiquement. Si persistant, réduire la fréquence des requêtes.

**Erreur de région :**
```
Invalid AWS region
```
**Solution :** Vérifier que `AWS_REGION` est une région valide et que Bedrock y est disponible.

**Erreur de modèle :**
```
Invalid Bedrock model ID
```
**Solution :** Vérifier que le modèle est activé dans votre compte AWS et région.

#### 6. Erreurs OpenAI (si utilisé)

**Erreur de clé API :**
```
OpenAI configuration error: Invalid API key
```
**Solution :** Vérifier que `OPENAI_API_KEY` est correcte et que `LLM_PROVIDER=openai` est défini

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

1. **Configurer AWS Bedrock** : Activer Bedrock dans votre compte AWS
2. **Explorer l'interface** : Tester les fonctionnalités de base
3. **Configurer des services MCP** : Ajouter des services personnalisés
4. **Personnaliser l'agent** : Modifier les instructions et comportements
5. **Déployer en production** : Suivre le guide de déploiement
