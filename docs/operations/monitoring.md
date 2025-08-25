# Monitoring avec LangSmith

## Vue d'ensemble

LangSmith est intégré dans Open MCP Client pour fournir un monitoring complet et une observabilité des agents IA. Cette intégration permet de tracer, analyser et optimiser les performances des interactions avec les modèles LLM.

## Configuration

### Variables d'Environnement

```env
# LangSmith API Key (requis pour le monitoring)
LANGSMITH_API_KEY=lsv2-your-langsmith-api-key

# Configuration optionnelle
LANGSMITH_PROJECT=open-mcp-client
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING_V2=true
```

### Configuration Frontend

Dans `app/api/copilotkit/route.ts` :

```typescript
const runtime = new CopilotRuntime({
  remoteEndpoints: [
    langGraphPlatformEndpoint({
      deploymentUrl: `${process.env.AGENT_DEPLOYMENT_URL || 'http://localhost:8123'}`,
      langsmithApiKey: process.env.LANGSMITH_API_KEY, // Monitoring activé
      agents: [
        {
          name: 'sample_agent',
          description: 'A helpful LLM agent.',
        }
      ]
    }),
  ],
});
```

### Configuration Backend

Dans `agent/sample_agent/agent.py`, LangSmith est automatiquement activé via LangChain :

```python
from langchain_openai import ChatOpenAI

# LangSmith est automatiquement configuré via les variables d'environnement
model = ChatOpenAI(model="gpt-4o")
```

## Fonctionnalités de Monitoring

### 1. Traçabilité des Exécutions

#### Traces d'Agent
- **Exécutions complètes** : Toutes les interactions avec l'agent
- **Chaînes de raisonnement** : Étapes de pensée de l'agent
- **Appels d'outils** : Utilisation des services MCP
- **Temps de réponse** : Métriques de performance

#### Métriques Collectées
- **Latence** : Temps de réponse des modèles LLM
- **Tokens** : Nombre de tokens utilisés
- **Coûts** : Estimation des coûts API
- **Erreurs** : Erreurs et exceptions

### 2. Dashboard LangSmith

#### Vue d'ensemble
- **Traces récentes** : Dernières exécutions
- **Métriques globales** : Performance générale
- **Erreurs** : Problèmes détectés
- **Utilisation** : Statistiques d'usage

#### Analyse Détaillée
- **Traces individuelles** : Analyse pas à pas
- **Comparaison** : Comparaison entre exécutions
- **Debugging** : Identification des problèmes
- **Optimisation** : Suggestions d'amélioration

### 3. Alertes et Notifications

#### Métriques Surveillées
- **Taux d'erreur** : > 5% d'erreurs
- **Latence élevée** : > 10 secondes de réponse
- **Coûts excessifs** : Dépassement de budget
- **Disponibilité** : Service indisponible

#### Configuration d'Alertes
```yaml
# Exemple de configuration d'alertes
alerts:
  error_rate:
    threshold: 0.05
    window: 1h
    notification: email
  
  latency:
    threshold: 10s
    window: 5m
    notification: slack
```

## Utilisation du Dashboard

### 1. Accès au Dashboard

1. **Connexion** : Se connecter à [LangSmith](https://smith.langchain.com)
2. **Projet** : Sélectionner le projet "open-mcp-client"
3. **Navigation** : Explorer les différentes sections

### 2. Analyse des Traces

#### Vue Liste
- **Filtrer** : Par date, agent, statut
- **Rechercher** : Par contenu ou métadonnées
- **Trier** : Par temps, coût, performance

#### Vue Détaillée
- **Input/Output** : Messages d'entrée et de sortie
- **Étapes** : Chaîne de raisonnement
- **Outils** : Appels aux services MCP
- **Métriques** : Performance détaillée

### 3. Optimisation

#### Identification des Problèmes
- **Erreurs fréquentes** : Patterns d'erreurs
- **Latence élevée** : Goulots d'étranglement
- **Coûts excessifs** : Utilisation inefficace

#### Améliorations
- **Prompt engineering** : Optimisation des prompts
- **Configuration** : Ajustement des paramètres
- **Architecture** : Amélioration du flux

## Intégration avec l'Application

### 1. Traçage Automatique

#### Frontend
- **Requêtes API** : Traçage des appels CopilotKit
- **Interactions utilisateur** : Actions et réponses
- **Erreurs client** : Problèmes d'interface

#### Backend
- **Exécutions d'agent** : Traçage LangGraph
- **Appels MCP** : Communication avec services
- **Modèles LLM** : Interactions OpenAI

### 2. Métadonnées Personnalisées

#### Ajout de Context
```python
# Dans agent.py
config = RunnableConfig(
    metadata={
        "user_id": "user123",
        "session_id": "session456",
        "feature": "spreadsheet_processing"
    }
)
```

#### Filtrage et Recherche
- **Par utilisateur** : Traces spécifiques
- **Par session** : Interactions de session
- **Par fonctionnalité** : Usage par feature

## Bonnes Pratiques

### 1. Configuration

#### Variables d'Environnement
- **Sécurité** : Ne jamais commiter les clés API
- **Environnements** : Différentes clés pour dev/prod
- **Rotation** : Rotation régulière des clés

#### Projets
- **Séparation** : Projets distincts par environnement
- **Organisation** : Structure logique des projets
- **Permissions** : Gestion des accès

### 2. Monitoring

#### Métriques Clés
- **Taux de succès** : > 95%
- **Latence moyenne** : < 3 secondes
- **Coût par requête** : < $0.10
- **Disponibilité** : > 99.9%

#### Alertes
- **Seuils appropriés** : Basés sur l'usage réel
- **Notifications** : Canaux appropriés
- **Escalade** : Processus d'escalade

### 3. Optimisation

#### Analyse Régulière
- **Rapports hebdomadaires** : Performance générale
- **Revues mensuelles** : Tendances et optimisations
- **Audits trimestriels** : Architecture et coûts

#### Actions Correctives
- **Prompt optimization** : Amélioration des prompts
- **Configuration tuning** : Ajustement des paramètres
- **Architecture review** : Optimisation du flux

## Dépannage

### Problèmes Courants

#### 1. Traces Manquantes
```
Aucune trace visible dans LangSmith
```
**Solutions :**
- Vérifier la clé API LangSmith
- Vérifier la configuration du projet
- Vérifier les variables d'environnement

#### 2. Latence Élevée
```
Temps de réponse > 10 secondes
```
**Solutions :**
- Analyser les traces pour identifier les goulots
- Optimiser les prompts
- Vérifier la configuration des modèles

#### 3. Erreurs Fréquentes
```
Taux d'erreur > 5%
```
**Solutions :**
- Examiner les traces d'erreur
- Vérifier la configuration MCP
- Tester les services externes

### Support

#### Documentation
- [LangSmith Docs](https://docs.smith.langchain.com)
- [LangChain Tracing](https://python.langchain.com/docs/langsmith)
- [API Reference](https://api.smith.langchain.com)

#### Communauté
- [Discord LangChain](https://discord.gg/langchain)
- [GitHub Issues](https://github.com/langchain-ai/langsmith)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/langsmith)
