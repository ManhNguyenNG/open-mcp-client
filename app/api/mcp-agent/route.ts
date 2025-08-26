import { NextRequest, NextResponse } from "next/server";

// Endpoint pour communiquer avec l'agent MCP
export async function POST(req: NextRequest) {
  try {
    const { message, serverName } = await req.json();

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Utiliser l'agent existant au lieu d'en créer un nouveau
    const assistantId = "6f4cc99e-29fe-4da9-97f3-86590cbe6114";

    // Créer un thread
    const threadResponse = await fetch('http://127.0.0.1:8123/threads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        assistant_id: assistantId
      }),
    });

    if (!threadResponse.ok) {
      throw new Error('Failed to create thread');
    }

    const threadData = await threadResponse.json();
    const threadId = threadData.thread_id;

    // Exécuter l'agent avec le message
    const runResponse = await fetch(`http://127.0.0.1:8123/threads/${threadId}/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        assistant_id: assistantId,
        input: {
          messages: [
            {
              type: "human",
              content: message
            }
          ]
        }
      }),
    });

    if (!runResponse.ok) {
      throw new Error('Failed to run agent');
    }

    const runData = await runResponse.json();
    const runId = runData.run_id;

    // Attendre le résultat
    let resultData = null;
    let attempts = 0;
    const maxAttempts = 10;

    while (attempts < maxAttempts) {
      try {
        const waitResponse = await fetch(`http://127.0.0.1:8123/threads/${threadId}/runs/wait`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            run_id: runId,
            assistant_id: assistantId
          }),
        });

        if (waitResponse.ok) {
          resultData = await waitResponse.json();
          break;
        } else {
          await new Promise(resolve => setTimeout(resolve, 1000));
          attempts++;
        }
      } catch (error) {
        attempts++;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    if (!resultData) {
      throw new Error('Failed to get agent response');
    }

    // Extraire la réponse de l'agent
    const aiMessage = resultData.messages?.find((msg: any) => msg.type === "ai");
    const response = aiMessage?.content || "No response from agent";

    return NextResponse.json({
      success: true,
      message: response,
      serverName,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error communicating with MCP agent:', error);
    return NextResponse.json(
      { 
        error: 'Failed to communicate with MCP agent',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

// Endpoint pour obtenir le statut de l'agent MCP
export async function GET() {
  try {
    // Vérifier si le serveur LangGraph est accessible
    const response = await fetch('http://127.0.0.1:8123/docs');
    
    if (response.ok) {
      return NextResponse.json({
        status: 'available',
        message: 'MCP Agent is running and ready',
        assistantId: '6f4cc99e-29fe-4da9-97f3-86590cbe6114',
        timestamp: new Date().toISOString()
      });
    } else {
      return NextResponse.json({
        status: 'unavailable',
        message: 'MCP Agent is not available',
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Failed to check MCP Agent status',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    });
  }
}
