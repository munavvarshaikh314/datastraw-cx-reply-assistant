const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function getConversations() {
  const response = await fetch(API_BASE_URL + "/conversations", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch conversations");
  }

  return response.json();
}

export async function getConversation(id: string) {
  const response = await fetch(
    API_BASE_URL + "/conversations/" + id,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch conversation");
  }

  return response.json();
}

export async function updateConversationStatus(
  id: string,
  conversationStatus: string
) {
  const response = await fetch(
    API_BASE_URL + "/conversations/" + id + "/status",
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status: conversationStatus,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to update conversation status");
  }

  return response.json();
}

export async function generateReply(
  conversationId: string,
  customerMessage: string,
  agentId: string
) {
  const response = await fetch(
    API_BASE_URL + "/conversations/" + conversationId + "/reply",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        customer_message: customerMessage,
        agent_id: agentId,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to generate reply");
  }

  return response.json();
}

export async function updateReply(
  replyId: string,
  editedResponse: string
) {
  const response = await fetch(
    API_BASE_URL + "/conversations/replies/" + replyId,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        edited_response: editedResponse,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to update reply");
  }

  return response.json();
}

export async function approveReply(replyId: string) {
  const response = await fetch(
    API_BASE_URL + "/conversations/replies/" + replyId + "/approve",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error("Failed to approve reply");
  }

  return response.json();
}
