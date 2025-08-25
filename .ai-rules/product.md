---
title: Product Vision
description: "Defines the project's core purpose, target users, and main features."
inclusion: always
---

# Product Vision - Open MCP Client

## Core Purpose
Open MCP Client est une application web open-source qui permet aux utilisateurs d'interagir avec des agents IA via le protocole MCP (Model Context Protocol). L'application combine une interface utilisateur moderne avec des capacités de traitement de données avancées.

## Target Users
- **Développeurs** : Qui souhaitent tester et intégrer des services MCP
- **Analystes de données** : Qui ont besoin d'assistance pour manipuler des données via des feuilles de calcul
- **Utilisateurs techniques** : Qui veulent interagir avec des agents IA via une interface intuitive
- **Équipes de développement** : Qui cherchent à comprendre et implémenter le protocole MCP

## Main Features

### 1. Interface de Chat IA
- Assistant conversationnel intégré avec CopilotKit
- Support des instructions personnalisées pour guider l'agent
- Interface responsive avec sidebar fixe sur desktop et toggle sur mobile

### 2. Configuration MCP Dynamique
- Interface de configuration pour connecter des services MCP
- Support de multiples types de transport (stdio, SSE)
- Configuration en temps réel sans redémarrage
- Sauvegarde locale des configurations

### 3. Traitement de Données
- Rendu de feuilles de calcul interactives
- Support de formules Excel complètes
- Prévisualisation des changements avant application
- Manipulation de données via l'agent IA

### 4. Architecture Modulaire
- Frontend Next.js avec TypeScript
- Backend agent Python avec LangGraph
- Communication via protocole MCP
- Monitoring avec LangSmith

## Key Value Propositions
- **Simplicité** : Interface intuitive pour configurer et utiliser des services MCP
- **Flexibilité** : Support de multiples types de services et protocoles
- **Productivité** : Intégration directe entre IA et outils de données
- **Observabilité** : Monitoring complet des interactions via LangSmith
- **Open Source** : Code accessible et modifiable par la communauté

## Success Metrics
- Nombre d'utilisateurs configurant des services MCP
- Temps de configuration d'un nouveau service
- Qualité des interactions avec l'agent IA
- Adoption par la communauté open source
