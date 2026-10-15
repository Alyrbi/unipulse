// State store
let postsState = [];

// DOM references
const postForm = document.getElementById("post-form");
const postTitle = document.getElementById("post-title");
const authorName = document.getElementById("author-name");
const authorId = document.getElementById("author-id");
const postAudience = document.getElementById("post-audience");
const communityId = document.getElementById("community-id");
const postContent = document.getElementById("post-content");
const requestAi = document.getElementById("request-ai");
const btnPreviewAi = document.getElementById("btn-preview-ai");
const aiPreviewBox = document.getElementById("ai-preview-box");
const aiPreviewText = document.getElementById("ai-preview-text");
const aiPreviewTags = document.getElementById("ai-preview-tags");
const aiPreviewEventInfo = document.getElementById("ai-preview-event-info");
const acceptAiSummary = document.getElementById("accept-ai-summary");
const filterAudience = document.getElementById("filter-audience");
const feedStatus = document.getElementById("feed-status");
const postList = document.getElementById("post-list");
const currentUserRole = document.getElementById("current-user-role");

// Helper to get active role
function getActiveRole() {
  return currentUserRole ? currentUserRole.value : "student";
}

// Fetch posts
async function fetchPosts() {
  feedStatus.textContent = "Loading posts...";
  feedStatus.style.display = "block";

  const audience = filterAudience.value;
  const url = audience ? `/api/posts?audience=${encodeURIComponent(audience)}` : "/api/posts";

  try {
    const response = await fetch(url, {
      headers: {
        "X-Mock-Role": getActiveRole(),
      },
    });
    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }
    const data = await response.json();
    postsState = data.items || [];
    renderPosts();
  } catch (err) {
    feedStatus.textContent = `Failed to load posts: ${err.message}`;
  }
}

// Render DOM
function renderPosts() {
  postList.innerHTML = "";

  if (postsState.length === 0) {
    feedStatus.textContent = "No posts found for this view.";
    feedStatus.style.display = "block";
    return;
  }

  feedStatus.style.display = "none";

  postsState.forEach((post) => {
    const card = document.createElement("article");
    card.className = "post-item";

    // Card header
    const header = document.createElement("div");
    header.className = "post-item-header";

    const title = document.createElement("h3");
    title.className = "post-title";
    title.textContent = post.title;

    const badge = document.createElement("span");
    badge.className = "badge-audience";
    badge.textContent = post.audience.replace("_", " ");

    header.appendChild(title);
    header.appendChild(badge);
    card.appendChild(header);

    // Meta details
    const meta = document.createElement("div");
    meta.className = "post-meta";
    const dateFormatted = new Date(post.created_at).toLocaleString();
    const commDisplay = post.community_id ? `Space: ${post.community_id}` : "General Space";
    meta.textContent = `By ${post.author_name} • ${commDisplay} • ${dateFormatted}`;
    card.appendChild(meta);

    // Content body
    const body = document.createElement("div");
    body.className = "post-body";
    body.textContent = post.content;
    card.appendChild(body);

    // Event box
    if (post.event_detail && post.event_detail.is_event) {
      const evtBox = document.createElement("div");
      evtBox.className = "event-box";
      const locText = post.event_detail.event_location || "Campus Venue TBA";
      const dateText = post.event_detail.event_date ? new Date(post.event_detail.event_date).toLocaleString() : "Date TBA";
      evtBox.textContent = `Event: ${locText} | Time: ${dateText}`;
      card.appendChild(evtBox);
    }

    // AI summary
    if (post.ai_summary) {
      const aiBox = document.createElement("div");
      aiBox.className = "ai-badge-box";

      const aiTitle = document.createElement("div");
      aiTitle.className = "ai-badge-title";
      aiTitle.textContent = "PulseDigest AI Summary";

      const aiText = document.createElement("div");
      aiText.className = "ai-badge-summary";
      aiText.textContent = post.ai_summary;

      aiBox.appendChild(aiTitle);
      aiBox.appendChild(aiText);
      card.appendChild(aiBox);
    }

    // Tag pills
    if (post.tags && post.tags.length > 0) {
      const tagsBox = document.createElement("div");
      tagsBox.className = "tags-container";
      post.tags.forEach((t) => {
        const pill = document.createElement("span");
        pill.className = "tag-pill";
        pill.textContent = `#${t}`;
        tagsBox.appendChild(pill);
      });
      card.appendChild(tagsBox);
    }

    // Oral Defense Demo Button: Test GET /api/posts/{id} with current role
    const actionRow = document.createElement("div");
    actionRow.style.marginTop = "8px";
    actionRow.style.display = "flex";
    actionRow.style.justifyContent = "flex-end";

    const inspectBtn = document.createElement("button");
    inspectBtn.type = "button";
    inspectBtn.className = "btn btn-secondary";
    inspectBtn.style.padding = "3px 8px";
    inspectBtn.style.fontSize = "0.8em";
    inspectBtn.textContent = `Verify Audience Access (ID: ${post.id})`;
    inspectBtn.addEventListener("click", async () => {
      const activeRole = getActiveRole();
      try {
        const res = await fetch(`/api/posts/${post.id}`, {
          headers: {
            "X-Mock-Role": activeRole,
          },
        });
        if (res.status === 403) {
          const errData = await res.json();
          alert(`[403 FORBIDDEN]\nRole "${activeRole}" rejected by server-side query scoping!\nCode: ${errData.detail?.error_code || "FORBIDDEN"}\nMessage: ${errData.detail?.message || "Access denied"}`);
        } else if (!res.ok) {
          alert(`[HTTP ${res.status}] ${res.statusText}`);
        } else {
          const data = await res.json();
          alert(`[200 OK]\nAudience verification passed for role "${activeRole}".\nPost: "${data.title}" (Audience: ${data.audience})`);
        }
      } catch (e) {
        alert(`Request failed: ${e.message}`);
      }
    });

    actionRow.appendChild(inspectBtn);
    card.appendChild(actionRow);

    postList.appendChild(card);
  });
}

// Form submit
postForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Satisfy FR-AI-02: Only attach AI summary if author explicitly reviewed & accepted it
  const shouldAttachAi = acceptAiSummary ? acceptAiSummary.checked : false;

  const rawCommId = communityId.value.trim();
  const payload = {
    title: postTitle.value.trim(),
    content: postContent.value.trim(),
    author_name: authorName.value.trim(),
    author_id: authorId.value.trim(),
    audience: postAudience.value,
    community_id: rawCommId.length > 0 ? rawCommId : null,
    request_ai_summary: shouldAttachAi,
    tags: [],
  };

  try {
    const res = await fetch("/api/posts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Mock-Role": getActiveRole(),
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail ? JSON.stringify(errorData.detail) : "Creation failed");
    }

    // Reset inputs
    postTitle.value = "";
    postContent.value = "";
    aiPreviewBox.style.display = "none";
    if (acceptAiSummary) acceptAiSummary.checked = false;
    if (requestAi) requestAi.checked = false;

    // Refresh feed
    await fetchPosts();
  } catch (err) {
    alert(`Error creating post: ${err.message}`);
  }
});

// AI preview
btnPreviewAi.addEventListener("click", async () => {
  const text = postContent.value.trim();
  if (text.length < 10) {
    alert("Please enter at least 10 characters in the content field to generate a preview.");
    return;
  }

  try {
    const res = await fetch("/api/posts/ai/preview", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Mock-Role": getActiveRole(),
      },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) throw new Error("AI preview failed");

    const data = await res.json();
    aiPreviewText.textContent = data.summary;

    // Render suggested date & location in demo UI
    if (aiPreviewEventInfo) {
      if (data.detected_event) {
        const dateStr = data.suggested_date ? new Date(data.suggested_date).toLocaleString() : "Date: TBD";
        const locStr = data.suggested_location || "Venue: TBD";
        aiPreviewEventInfo.textContent = `Detected Event -> Location: ${locStr} | Date: ${dateStr}`;
        aiPreviewEventInfo.style.color = "#000000";
      } else {
        aiPreviewEventInfo.textContent = "No campus event schedule detected in text.";
        aiPreviewEventInfo.style.color = "#555555";
      }
      if (data.is_fallback) {
        aiPreviewEventInfo.textContent += " (Circuit Breaker Tripped: Extractive Fallback Mode)";
      }
    }

    // Render tags
    aiPreviewTags.innerHTML = "";
    data.suggested_tags.forEach((tag) => {
      const pill = document.createElement("span");
      pill.className = "tag-pill";
      pill.textContent = `#${tag}`;
      aiPreviewTags.appendChild(pill);
    });

    aiPreviewBox.style.display = "block";
  } catch (err) {
    alert(`Could not fetch AI preview: ${err.message}`);
  }
});

// Role switcher change
if (currentUserRole) {
  currentUserRole.addEventListener("change", () => {
    fetchPosts();
  });
}

// Filter change
filterAudience.addEventListener("change", fetchPosts);

// Init load
fetchPosts();
