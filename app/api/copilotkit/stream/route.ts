import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

async function waitForResult(threadId: string, runId: string, assistantId: string) {
  const maxAttempts = 60; // ~30s
  const backoffMs = 500;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const waitRes = await fetch(
      `http://127.0.0.1:8123/threads/${threadId}/runs/wait`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assistant_id: assistantId, run_id: runId }),
      }
    );
    if (waitRes.status === 409) {
      await new Promise((r) => setTimeout(r, backoffMs));
      continue;
    }
    if (!waitRes.ok) {
      throw new Error(`wait failed (${waitRes.status})`);
    }
    const data = await waitRes.json();
    const ai = (data?.messages || []).find((m: any) => m?.type === "ai");
    const content: string = ai?.content ?? "";
    return content;
  }
  throw new Error("wait timed out");
}

function streamFromText(content: string): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        if (!content) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content: "" })}\n\n`));
          controller.enqueue(encoder.encode("data: [DONE]\n\n"));
          controller.close();
          return;
        }
        const words = content.split(/(\s+)/);
        for (let i = 0; i < words.length; i++) {
          const chunk = words[i];
          if (!chunk) continue;
          const evt = `data: ${JSON.stringify({ content: chunk })}\n\n`;
          controller.enqueue(encoder.encode(evt));
          await new Promise((r) => setTimeout(r, 20));
        }
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      } catch (e) {
        controller.error(e);
      }
    },
  });
}

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json();
    if (!message || typeof message !== "string") {
      return new Response(JSON.stringify({ error: "Missing 'message'" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const assistantId = "b17669e2-1608-4504-936a-4a88ed3347a7";

    const threadRes = await fetch("http://127.0.0.1:8123/threads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assistant_id: assistantId }),
    });

    if (!threadRes.ok) {
      return new Response(
        JSON.stringify({ error: `Failed to create thread (${threadRes.status})` }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const { thread_id } = await threadRes.json();

    const runRes = await fetch(`http://127.0.0.1:8123/threads/${thread_id}/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assistant_id: assistantId,
        input: { messages: [{ type: "human", content: message }] },
      }),
    });

    if (!runRes.ok) {
      return new Response(
        JSON.stringify({ error: `Failed to run agent (${runRes.status})` }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const { run_id } = await runRes.json();

    const maxAttempts = 15;
    const backoffMs = 300;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const sse = await fetch(
        `http://127.0.0.1:8123/threads/${thread_id}/runs/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ assistant_id: assistantId, run_id }),
        }
      );

      if (sse.status === 409) {
        await new Promise((r) => setTimeout(r, backoffMs));
        continue;
      }

      if (sse.ok && sse.body) {
        return new Response(sse.body, {
          headers: {
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache, no-transform",
            Connection: "keep-alive",
          },
        });
      }

      break;
    }

    const finalText = await waitForResult(thread_id, run_id, assistantId);
    const stream = streamFromText(finalText);
    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
      },
    });
  } catch (err: any) {
    return new Response(
      JSON.stringify({ error: "Internal server error", details: String(err?.message || err) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
