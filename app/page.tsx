"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import MCPServerManager from "./components/MCPServerManager";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Gestionnaire MCP */}
          <div className="lg:col-span-1">
            <MCPServerManager 
              onServerConnected={(server) => {
                console.log(`MCP Server connected: ${server.name}`);
              }}
              onServerDisconnected={(serverName) => {
                console.log(`MCP Server disconnected: ${serverName}`);
              }}
            />
          </div>
          
          {/* Chat Interface */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md h-[600px]">
              <CopilotChat
                api="/api/copilotkit"
                placeholder="Ask me anything! I can help with calculations, conversions, scientific analysis, and statistics using MCP servers..."
                showAvatar={true}
                showAvatarInMessages={true}
                showCodeBlockActions={true}
                showCopyButton={true}
                showMarkdownAsHTML={true}
                showStopGenerating={true}
                showSuggestedQuestions={true}
                suggestedQuestions={[
                  // Math questions
                  "What make 5 + 12 ?",
                  "Calculate 4 * 7",
                  "Combien font 2 * 6 ?",
                  
                  // Conversion questions
                  "25°C en Fahrenheit",
                  "100 mètres en pieds",
                  "10 km en miles",
                  
                  // Scientific questions
                  "Racine carrée de 16",
                  "5 puissance 3",
                  "5!",
                  
                  // Statistics questions
                  "Moyenne de 1,2,3,4,5",
                  "Écart-type de 10,20,30",
                  "Statistiques de 1,2,3,4,5,6,7,8,9,10"
                ]}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
