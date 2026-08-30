"use client";

import { useEffect, useState } from "react";
import {
  getConversations,
  getConversation,
  updateConversationStatus,
  generateReply,
  updateReply,
  approveReply,
} from "../../../lib/api";

type Conversation = {
  id: string;
  brand_id: string;
  customer_id: string;
  status: string;
  created_at: string;
  updated_at: string;
};

type Message = {
  id: string;
  content?: string;
  message?: string;
  text?: string;
  body?: string;
  message_text?: string;
  role?: string;
  sender_type?: string;
  created_at: string;
};

type Reply = {
  id: string;
  conversation_id: string;
  generation_number: number;
  customer_message: string;
  ai_response: string | null;
  edited_response: string | null;
  final_response: string | null;
  status: string;
};

type ConversationDetail = Conversation & {
  customer?: {
    id: string;
    name?: string;
    email?: string;
  };
  messages?: Message[];
  order?: {
    id: string;
    status?: string;
  };
};

const AGENT_ID = "afcf44aa-c4ca-4ec4-a887-a391b7475c86";

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<ConversationDetail | null>(null);
  const [reply, setReply] = useState<Reply | null>(null);
  const [editedReply, setEditedReply] = useState("");
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function loadConversations() {
    try {
      setLoading(true);
      setError("");

      const data = await getConversations();
      setConversations(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load conversations.");
    } finally {
      setLoading(false);
    }
  }

  async function selectConversation(id: string) {
    try {
      setError("");

      const data = await getConversation(id);

      setSelected(data);
      setReply(null);
      setEditedReply("");
    } catch (err) {
      console.error(err);
      setError("Failed to load conversation.");
    }
  }

const handleGenerateReply = async () => {
  if (!selected) {
    console.log("NO SELECTED CONVERSATION");
    return;
  }

  console.log("SELECTED:", selected);
  console.log("MESSAGES:", selected.messages);

  const customerMessage = [...(selected.messages ?? [])]
    .reverse()
    .find(
      (message: any) =>
        message.sender_type?.toLowerCase() === "customer"
    )?.content;

  console.log("CUSTOMER MESSAGE:", customerMessage);

  if (!customerMessage) {
    setError("No customer message found.");
    return;
  }

  try {
    setGenerating(true);
    setError("");

    console.log("CALLING GENERATE REPLY API...");

    const result = await generateReply(
  selected.id,
  customerMessage,
  AGENT_ID
);

console.log("GENERATE RESULT:", result);

setReply(result);

setEditedReply(
  result.ai_response || ""
);

setReply(result);

setEditedReply(
  result.edited_response ||
  result.ai_response ||
  ""
);
  } catch (error) {
    console.error("GENERATE REPLY ERROR:", error);
    setError(
      error instanceof Error
        ? error.message
        : "Failed to generate reply"
    );
  } finally {
    setGenerating(false);
  }
};

  async function handleSaveEdit() {
    if (!reply) return;

    try {
      setSaving(true);
      setError("");

      const result = await updateReply(
        reply.id,
        editedReply
      );

      setReply(result);
      setEditedReply(
        result.edited_response || editedReply
      );
    } catch (err) {
      console.error(err);
      setError("Failed to save reply.");
    } finally {
      setSaving(false);
    }
  }

  async function handleApprove() {
    if (!reply) return;

    try {
      setSaving(true);
      setError("");

      const result = await approveReply(reply.id);

      setReply(result);
      setEditedReply(
        result.final_response ||
        result.edited_response ||
        result.ai_response ||
        ""
      );
    } catch (err) {
      console.error(err);
      setError("Failed to approve reply.");
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(newStatus: string) {
    if (!selected) return;

    try {
      setError("");

      const result = await updateConversationStatus(
        selected.id,
        newStatus
      );

      setSelected(result);

      setConversations((current) =>
        current.map((conversation) =>
          conversation.id === selected.id
            ? {
                ...conversation,
                status: result.status,
                updated_at: result.updated_at,
              }
            : conversation
        )
      );
    } catch (err) {
      console.error(err);
      setError("Failed to update conversation status.");
    }
  }

  useEffect(() => {
    loadConversations();
  }, []);

  return (
    <main className="min-h-screen bg-gray-100">
      <header className="border-b bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              DataStraw
            </h1>

            <p className="text-sm text-gray-500">
              AI Customer Support Workspace
            </p>
          </div>

          <button
            onClick={loadConversations}
            className="rounded-lg border bg-white px-4 py-2 text-sm hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>
      </header>

      {error && (
        <div className="mx-6 mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid min-h-[calc(100vh-81px)] grid-cols-[280px_1fr_300px]">

        {/* LEFT */}
        <aside className="border-r bg-white">
          <div className="border-b px-5 py-4">
            <h2 className="font-semibold text-gray-900">
              Conversations
            </h2>

            <p className="mt-1 text-xs text-gray-500">
              {conversations.length} conversations
            </p>
          </div>

          {loading ? (
            <div className="p-5 text-sm text-gray-500">
              Loading conversations...
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-5 text-sm text-gray-500">
              No conversations found.
            </div>
          ) : (
            conversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() =>
                  selectConversation(conversation.id)
                }
                className={`w-full border-b px-5 py-4 text-left hover:bg-gray-50 ${
                  selected?.id === conversation.id
                    ? "bg-gray-100"
                    : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    Conversation
                  </span>

                  <span className="rounded-full bg-gray-100 px-2 py-1 text-xs capitalize">
                    {conversation.status}
                  </span>
                </div>

                <p className="mt-2 truncate text-xs text-gray-500">
                  {conversation.id}
                </p>
              </button>
            ))
          )}
        </aside>

        {/* CENTER */}
        <section className="flex min-w-0 flex-col">
          {!selected ? (
            <div className="flex flex-1 items-center justify-center text-sm text-gray-500">
              Select a conversation
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between border-b bg-white px-6 py-4">
                <div>
                  <h2 className="font-semibold text-gray-900">
                    Conversation
                  </h2>

                  <p className="mt-1 text-xs text-gray-500">
                    {selected.id}
                  </p>
                </div>

                <select
                  value={selected.status}
                  onChange={(event) =>
                    handleStatusChange(event.target.value)
                  }
                  className="rounded-lg border bg-white px-3 py-2 text-sm"
                >
                  <option value="open">Open</option>
                  <option value="pending">Pending</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto p-6">
                {(selected.messages ?? []).map((message) => {
                  const content =
                    message.content ||
                    message.message ||
                    "";

                  const role =
                    message.role ||
                    message.sender_type ||
                    "customer";

                  const isCustomer =
                    role.toLowerCase() === "customer";

                  return (
                    <div
                      key={message.id}
                      className={`flex ${
                        isCustomer
                          ? "justify-start"
                          : "justify-end"
                      }`}
                    >
                      <div
                        className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                          isCustomer
                            ? "bg-white shadow-sm"
                            : "bg-black text-white"
                        }`}
                      >
                        <p className="mb-1 text-xs font-medium opacity-60">
                          {role}
                        </p>

                        <p className="whitespace-pre-wrap text-sm">
                          {content}
                        </p>
                      </div>
                    </div>
                  );
                })}

                {(selected.messages ?? []).length === 0 && (
                  <div className="text-sm text-gray-500">
                    No messages in this conversation.
                  </div>
                )}
              </div>

              {/* REPLY AREA */}
              <div className="border-t bg-white p-5">
                {!reply ? (
                  <button
                    onClick={handleGenerateReply}
                    disabled={generating}
                    className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {generating
                      ? "Generating AI Reply..."
                      : "Generate AI Reply"}
                  </button>
                ) : (
                  <div>
                    <div className="mb-3 flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">
                        AI Reply
                      </h3>

                      <span className="rounded-full bg-gray-100 px-3 py-1 text-xs capitalize">
                        {reply.status}
                      </span>
                    </div>

                    <textarea
                      value={editedReply}
                      onChange={(event) =>
                        setEditedReply(event.target.value)
                      }
                      disabled={reply.status === "approved"}
                      rows={7}
                      className="w-full resize-none rounded-xl border p-4 text-sm outline-none focus:ring-2 focus:ring-black disabled:bg-gray-100"
                    />

                    {reply.status !== "approved" ? (
  <div className="mt-3 flex gap-2">
    <button
      onClick={handleSaveEdit}
      disabled={saving}
      className="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50 disabled:opacity-50"
    >
      {saving ? "Saving..." : "Save Edit"}
    </button>

    <button
      onClick={handleApprove}
      disabled={saving}
      className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
    >
      {saving ? "Approving..." : "Approve Reply"}
    </button>
  </div>
) : (
  <div className="mt-3">
    <span className="inline-flex rounded-lg bg-green-100 px-4 py-2 text-sm font-medium text-green-700">
      ✓ Reply Approved
    </span>
  </div>
)}
                  </div>
                )}
              </div>
            </>
          )}
        </section>

        {/* RIGHT */}
        <aside className="border-l bg-white">
          <div className="border-b px-5 py-4">
            <h2 className="font-semibold text-gray-900">
              Customer
            </h2>
          </div>

          {!selected ? (
            <div className="p-5 text-sm text-gray-500">
              Select a conversation
            </div>
          ) : (
            <div className="space-y-6 p-5">
              <div>
                <p className="text-xs text-gray-500">
                  Customer ID
                </p>

                <p className="mt-1 break-all text-sm">
                  {selected.customer_id}
                </p>
              </div>

              {selected.customer?.name && (
                <div>
                  <p className="text-xs text-gray-500">
                    Name
                  </p>

                  <p className="mt-1 text-sm">
                    {selected.customer.name}
                  </p>
                </div>
              )}

              {selected.customer?.email && (
                <div>
                  <p className="text-xs text-gray-500">
                    Email
                  </p>

                  <p className="mt-1 break-all text-sm">
                    {selected.customer.email}
                  </p>
                </div>
              )}

              {selected.order && (
                <div className="border-t pt-5">
                  <p className="font-medium text-gray-900">
                    Order
                  </p>

                  <p className="mt-2 break-all text-xs text-gray-500">
                    {selected.order.id}
                  </p>

                  {selected.order.status && (
                    <p className="mt-2 text-sm capitalize">
                      Status: {selected.order.status}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}
