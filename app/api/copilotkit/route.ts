import { NextRequest, NextResponse } from "next/server";

// GraphQL endpoint for CopilotKit
export const POST = async (req: NextRequest) => {
  try {
    const body = await req.json();
    console.log('Received GraphQL request:', body.operationName);
    
    const { operationName, query, variables } = body;
    
    switch (operationName) {
      case 'availableAgents':
        return NextResponse.json({
          data: {
            availableAgents: {
              agents: [
                {
                  name: "sample_agent",
                  id: "sample_agent",
                  description: "LangGraph agent with MCP integration",
                  __typename: "Agent"
                }
              ],
              __typename: "AvailableAgents"
            }
          }
        });
        
      case 'loadAgentState':
        return NextResponse.json({
          data: {
            loadAgentState: {
              threadId: variables.data.threadId,
              threadExists: true,
              state: "{}",
              messages: [],
              __typename: "LoadAgentState"
            }
          }
        });
        
      case 'generateCopilotResponse':
        // Handle the actual chat request
        const messages = variables.data.messages || [];
        const userMessage = [...messages].reverse().find((msg: any) => msg.textMessage?.role === 'user');
        
        console.log('DEBUG: Received messages:', JSON.stringify(messages, null, 2));
        console.log('DEBUG: User message found:', userMessage);
        
        if (userMessage) {
          const userContent = userMessage.textMessage.content;
          console.log('DEBUG: User content:', userContent);
          
          // Generate response using our LangGraph agent
          const response = await generateResponse(userContent);
          console.log('DEBUG: Generated response:', response);
          
          return NextResponse.json({
            data: {
              generateCopilotResponse: {
                threadId: variables.data.threadId,
                runId: "test-run-id",
                extensions: {
                  openaiAssistantAPI: {
                    runId: "test-run-id",
                    threadId: variables.data.threadId,
                    __typename: "OpenAIAssistantAPI"
                  },
                  __typename: "Extensions"
                },
                status: {
                  code: "SUCCESS",
                  __typename: "SuccessResponseStatus"
                },
                messages: [
                  {
                    id: "response-message-id",
                    createdAt: new Date().toISOString(),
                    status: {
                      code: "SUCCESS",
                      __typename: "SuccessMessageStatus"
                    },
                    content: [response], // Wrap content in array
                    role: "assistant",
                    parentMessageId: null,
                    __typename: "TextMessageOutput"
                  }
                ],
                metaEvents: [],
                __typename: "CopilotResponse"
              }
            }
          });
        }
        
        return NextResponse.json({
          data: {
            generateCopilotResponse: {
              threadId: variables.data.threadId,
              runId: "test-run-id",
              extensions: {},
              status: {
                code: "SUCCESS",
                __typename: "SuccessResponseStatus"
              },
              messages: [],
              metaEvents: [],
              __typename: "CopilotResponse"
            }
          }
        });
        
      default:
        console.error('Unknown operation:', operationName);
        return NextResponse.json(
          { error: `Unknown operation: ${operationName}` },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Error in GraphQL endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
};

// Function to generate response using LangGraph agent
async function generateResponse(userMessage: string): Promise<string> {
  try {
    const assistantId = "b17669e2-1608-4504-936a-4a88ed3347a7";

    // Step 1: Create a thread
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
      console.error('Failed to create thread:', threadResponse.status);
      return "Sorry, I'm having trouble connecting to my backend. Please try again.";
    }

    const threadData = await threadResponse.json();
    const threadId = threadData.thread_id;

    // Step 2: Run the agent
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
              content: userMessage
            }
          ]
        }
      }),
    });

    if (!runResponse.ok) {
      console.error('Failed to run agent:', runResponse.status);
      return "Sorry, I'm having trouble processing your request. Please try again.";
    }

    const runData = await runResponse.json();
    const runId = runData.run_id;

    // Step 3: Wait for the result
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
          console.log(`Attempt ${attempts + 1}: Waiting for result...`);
          await new Promise(resolve => setTimeout(resolve, 1000));
          attempts++;
        }
      } catch (error) {
        console.error(`Attempt ${attempts + 1} failed:`, error);
        attempts++;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    if (!resultData) {
      console.error('Failed to get result after all attempts');
      return "Sorry, I'm taking too long to respond. Please try again.";
    }
    
    // Extract the AI response
    const aiMessage = resultData.messages?.find((msg: any) => msg.type === "ai");
    return aiMessage?.content || "I received your message but couldn't generate a response.";
    
  } catch (error) {
    console.error('Error generating response:', error);
    return "Sorry, I encountered an error while processing your request.";
  }
}

export const GET = async () => {
  return NextResponse.json({ 
    status: 'ok',
    message: 'CopilotKit GraphQL endpoint',
    agent: 'sample_agent',
    url: 'http://127.0.0.1:8123',
    backend_status: 'running'
  });
};