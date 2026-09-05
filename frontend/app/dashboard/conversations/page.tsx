"use client";

import { useEffect, useMemo, useState } from "react";
import {
  approveReply,
  generateReply,
  getConversation,
  getConversations,
  updateConversationStatus,
  updateReply,
} from "../../../lib/api";

type Customer = {
  id: string;
  name: string;
  email?: string | null;
};

type Brand = {
  id: string;
  name: string;
  slug: string;
};

type Order = {
  id: string;
  conversation_id: string;
  order_number: string;
  product_name: string;
  status: string;
  delivery_date?: string | null;
};

type Conversation = {
  id: string;
  brand_id: string;
  customer_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  customer?: Customer | null;
  brand?: Brand | null;
};

type Message = {
  id: string;
  conversation_id?: string;
  content: string;
  sender_type: string;
  created_at: string;
};

type Reply = {
  id: string;
  conversation_id: string;
  generation_number: number;
  customer_message: string;
  retrieved_context?: {
    documents?: unknown[];
    eligibility_verdict?: {
      applicable: boolean;
      eligible: boolean | null;
      reason: string;
      action: string;
      refund_window_days?: number | null;
      days_since_delivery?: number | null;
    };
  };
  ai_response: string | null;
  edited_response: string | null;
  final_response: string | null;
  status: string;
  created_at?: string;
  approved_at?: string | null;
};

type ConversationDetail = Conversation & {
  messages: Message[];
  order?: Order | null;
};

const AGENT_ID = "afcf44aa-c4ca-4ec4-a887-a391b7475c86";

function formatDate(value?: string | null) {
  if (!value) return "Not available";

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function formatDateTime(value?: string | null) {
  if (!value) return "Not available";

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function statusClass(status: string) {
  if (status === "approved" || status === "resolved") {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  if (status === "edited" || status === "pending") {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }

  return "border-sky-200 bg-sky-50 text-sky-700";
}

function latestCustomerMessage(messages: Message[]) {
  return [...messages]
    .reverse()
    .find((message) => message.sender_type?.toLowerCase() === "customer");
}

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<ConversationDetail | null>(null);
  const [reply, setReply] = useState<Reply | null>(null);
  const [editedReply, setEditedReply] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingConversation, setLoadingConversation] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const latestMessage = useMemo(
    () => latestCustomerMessage(selected?.messages ?? []),
    [selected]
  );

  const replyText =
    reply?.final_response || reply?.edited_response || reply?.ai_response || "";
  const isApproved = reply?.status === "approved";

  async function loadConversations() {
    try {
      setLoading(true);
      setError("");

      const data = await getConversations();
      setConversations(data);

      if (!selected && data.length > 0) {
        await selectConversation(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversations.");
    } finally {
      setLoading(false);
    }
  }

  async function selectConversation(id: string) {
    try {
      setLoadingConversation(true);
      setError("");

      const data = await getConversation(id);

      setSelected(data);
      setReply(null);
      setEditedReply("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation.");
    } finally {
      setLoadingConversation(false);
    }
  }

  async function handleGenerateReply() {
    if (!selected || !latestMessage?.content) {
      setError("No latest customer message found.");
      return;
    }

    try {
      setGenerating(true);
      setError("");

      const result = await generateReply(
        selected.id,
        latestMessage.content,
        AGENT_ID
      );

      setReply(result);
      setEditedReply(result.edited_response || result.ai_response || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate reply.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleRegenerateReply() {
    await handleGenerateReply();
  }

  async function handleSaveEdit() {
    if (!reply || isApproved || !editedReply.trim()) return;

    try {
      setSaving(true);
      setError("");

      const result = await updateReply(reply.id, editedReply);

      setReply(result);
      setEditedReply(result.edited_response || editedReply);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save reply.");
    } finally {
      setSaving(false);
    }
  }

  async function handleApprove() {
    if (!reply || isApproved) return;

    try {
      setSaving(true);
      setError("");

      const result = await approveReply(reply.id);

      setReply(result);
      setEditedReply(
        result.final_response || result.edited_response || result.ai_response || ""
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve reply.");
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(newStatus: string) {
    if (!selected) return;

    try {
      setError("");

      const result = await updateConversationStatus(selected.id, newStatus);

      setSelected((current) =>
        current
          ? {
              ...current,
              status: result.status,
              updated_at: result.updated_at,
            }
          : current
      );

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
      setError(
        err instanceof Error ? err.message : "Failed to update conversation status."
      );
    }
  }

  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main className="min-h-screen bg-[#f4f7fb] text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1600px] flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">
              DataStraw CX
            </p>
            <h1 className="mt-1 text-2xl font-semibold text-slate-950">
              Support Reply Workspace
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
              {conversations.length} conversations
            </div>
            <button
              onClick={loadConversations}
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-800 shadow-sm transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading}
            >
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </div>
      </header>

      {error && (
        <div className="mx-auto mt-4 max-w-[1600px] px-4 sm:px-6">
          <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        </div>
      )}

      <div className="mx-auto grid max-w-[1600px] gap-4 px-4 py-4 sm:px-6 xl:grid-cols-[minmax(260px,320px)_minmax(0,1fr)_minmax(300px,360px)]">
        <aside className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm xl:min-h-[calc(100vh-126px)]">
          <div className="border-b border-slate-200 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-900">
              Conversations
            </h2>
          </div>

          <div className="max-h-90 overflow-y-auto xl:max-h-[calc(100vh-174px)]">
            {loading ? (
              <div className="p-4 text-sm text-slate-500">Loading conversations...</div>
            ) : conversations.length === 0 ? (
              <div className="p-4 text-sm text-slate-500">No conversations found.</div>
            ) : (
              conversations.map((conversation) => {
                const active = selected?.id === conversation.id;

                return (
                  <button
                    key={conversation.id}
                    onClick={() => selectConversation(conversation.id)}
                    className={`w-full border-b border-slate-100 px-4 py-4 text-left transition hover:bg-slate-50 ${
                      active ? "bg-teal-50" : "bg-white"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-slate-950">
                          {conversation.customer?.name || "Unknown customer"}
                        </p>
                        <p className="mt-1 truncate text-xs text-slate-500">
                          {conversation.brand?.name || conversation.brand_id}
                        </p>
                      </div>

                      <span
                        className={`shrink-0 rounded-full border px-2 py-1 text-[11px] font-medium capitalize ${statusClass(
                          conversation.status
                        )}`}
                      >
                        {conversation.status}
                      </span>
                    </div>

                    <p className="mt-3 truncate text-xs text-slate-400">
                      Updated {formatDateTime(conversation.updated_at)}
                    </p>
                  </button>
                );
              })
            )}
          </div>
        </aside>

        <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm xl:min-h-[calc(100vh-126px)]">
          {!selected ? (
            <div className="flex h-72 items-center justify-center text-sm text-slate-500">
              Select a conversation
            </div>
          ) : (
            <div className="flex h-full min-h-160 flex-col">
              <div className="border-b border-slate-200 px-5 py-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-lg font-semibold text-slate-950">
                        {selected.customer?.name || "Customer conversation"}
                      </h2>
                      <span
                        className={`rounded-full border px-2 py-1 text-xs font-medium capitalize ${statusClass(
                          selected.status
                        )}`}
                      >
                        {selected.status}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">
                      {selected.brand?.name || "Brand"} conversation history
                    </p>
                  </div>

                  <select
                    value={selected.status}
                    onChange={(event) => handleStatusChange(event.target.value)}
                    className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-800 shadow-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                  >
                    <option value="open">Open</option>
                    <option value="pending">Pending</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </div>

                <div className="mt-4 rounded-md border border-teal-200 bg-teal-50 px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal-700">
                    Latest Customer Message
                  </p>
                  <p className="mt-2 text-sm leading-6 text-slate-800">
                    {latestMessage?.content || "No customer message found."}
                  </p>
                </div>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto bg-slate-50 px-5 py-5">
                {loadingConversation ? (
                  <div className="text-sm text-slate-500">Loading conversation...</div>
                ) : selected.messages.length === 0 ? (
                  <div className="text-sm text-slate-500">
                    No messages in this conversation.
                  </div>
                ) : (
                  selected.messages.map((message) => {
                    const isCustomer =
                      message.sender_type?.toLowerCase() === "customer";

                    return (
                      <div
                        key={message.id}
                        className={`flex ${isCustomer ? "justify-start" : "justify-end"}`}
                      >
                        <div
                          className={`max-w-[78%] rounded-lg border px-4 py-3 shadow-sm ${
                            isCustomer
                              ? "border-slate-200 bg-white text-slate-900"
                              : "border-indigo-700 bg-indigo-700 text-white"
                          }`}
                        >
                          <div className="mb-2 flex items-center justify-between gap-4">
                            <p
                              className={`text-xs font-semibold capitalize ${
                                isCustomer ? "text-slate-500" : "text-indigo-100"
                              }`}
                            >
                              {message.sender_type}
                            </p>
                            <p
                              className={`text-xs ${
                                isCustomer ? "text-slate-400" : "text-indigo-100"
                              }`}
                            >
                              {formatDateTime(message.created_at)}
                            </p>
                          </div>
                          <p className="whitespace-pre-wrap text-sm leading-6">
                            {message.content}
                          </p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              <div className="border-t border-slate-200 bg-white px-5 py-4">
                {!reply ? (
                  <button
                    onClick={handleGenerateReply}
                    disabled={generating || !latestMessage}
                    className="w-full rounded-md bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
                  >
                    {generating ? "Generating AI Reply..." : "Generate AI Reply"}
                  </button>
                ) : (
                  <div className="space-y-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <h3 className="text-base font-semibold text-slate-950">
                          AI Reply
                        </h3>
                        <p className="mt-1 text-sm text-slate-500">
                          Generation {reply.generation_number}
                        </p>
                      </div>
                      <span
                        className={`w-fit rounded-full border px-3 py-1 text-xs font-medium capitalize ${statusClass(
                          reply.status
                        )}`}
                      >
                        Status: {reply.status}
                      </span>
                    </div>

                    <textarea
                      value={isApproved ? replyText : editedReply}
                      onChange={(event) => setEditedReply(event.target.value)}
                      disabled={isApproved}
                      rows={8}
                      className="w-full resize-none rounded-md border border-slate-300 bg-white p-4 text-sm leading-6 text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-100 disabled:border-slate-200 disabled:bg-slate-100"
                    />

                    {!isApproved ? (
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                        <button
                          onClick={handleRegenerateReply}
                          disabled={generating}
                          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-800 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {generating ? "Regenerating..." : "Regenerate Reply"}
                        </button>
                        <button
                          onClick={handleSaveEdit}
                          disabled={saving || !editedReply.trim()}
                          className="rounded-md border border-teal-600 bg-white px-4 py-2 text-sm font-medium text-teal-700 shadow-sm transition hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {saving ? "Saving..." : "Save Edit"}
                        </button>
                        <button
                          onClick={handleApprove}
                          disabled={saving}
                          className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {saving ? "Approving..." : "Approve Reply"}
                        </button>
                      </div>
                    ) : (
                      <div className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">
                        Reply approved and locked.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </section>

        <aside className="space-y-4 xl:min-h-[calc(100vh-126px)]">
          <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-900">Customer</h2>
            </div>
            <div className="space-y-4 px-4 py-4 text-sm">
              <InfoRow label="Name" value={selected?.customer?.name} />
              <InfoRow label="Email" value={selected?.customer?.email} />
              <InfoRow label="Customer ID" value={selected?.customer_id} mono />
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-900">Brand</h2>
            </div>
            <div className="space-y-4 px-4 py-4 text-sm">
              <InfoRow label="Name" value={selected?.brand?.name} />
              <InfoRow label="Slug" value={selected?.brand?.slug} />
              <InfoRow label="Brand ID" value={selected?.brand_id} mono />
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-900">Order</h2>
            </div>
            <div className="space-y-4 px-4 py-4 text-sm">
              <InfoRow label="Order number" value={selected?.order?.order_number} />
              <InfoRow label="Product" value={selected?.order?.product_name} />
              <InfoRow label="Status" value={selected?.order?.status} capitalize />
              <InfoRow
                label="Delivery date"
                value={formatDate(selected?.order?.delivery_date)}
              />
            </div>
          </section>

          {reply && (
            <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 px-4 py-3">
                <h2 className="text-sm font-semibold text-slate-900">
                  Reply Audit
                </h2>
              </div>
              <div className="space-y-4 px-4 py-4 text-sm">
                <InfoRow label="Generation" value={String(reply.generation_number)} />
                <InfoRow label="Created" value={formatDateTime(reply.created_at)} />
                <InfoRow label="Approved" value={formatDateTime(reply.approved_at)} />
                <InfoRow
                  label="Guardrail"
                  value={reply.retrieved_context?.eligibility_verdict?.action}
                />
              </div>
            </section>
          )}
        </aside>
      </div>
    </main>
  );
}

function InfoRow({
  label,
  value,
  mono = false,
  capitalize = false,
}: {
  label: string;
  value?: string | null;
  mono?: boolean;
  capitalize?: boolean;
}) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p
        className={`mt-1 break-words text-slate-900 ${
          mono ? "font-mono text-xs" : ""
        } ${capitalize ? "capitalize" : ""}`}
      >
        {value || "Not available"}
      </p>
    </div>
  );
}
