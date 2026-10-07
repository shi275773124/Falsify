/* Falsify project-understanding reader — local only, no uploads.
 * All untrusted text is rendered via textContent (no innerHTML for model/user text). */
"use strict";

(function () {
  // ---------- i18n ----------
  var I18N = {
    zh: {
      title: "项目理解 · Falsify",
      subtitle: "阅读一页可追溯的项目理解：它怎样运转、靠什么成立、证据改变了什么、哪些仍未知。本页只在本地运行，不上传任何内容。",
      importTitle: "导入理解产物",
      importHint: "选择 CLI 生成的 understanding.json 文件。文件在你的浏览器中读取，服务器不会访问你的磁盘路径。",
      chooseFile: "选择 understanding.json",
      metaTitle: "关联的原审查",
      metaNote: "以上为关联信息快照，仅表示与原审查的对应关系，不代表本项目已通过权威验证。",
      s1Title: "1 · 它怎样运转",
      s2Title: "2 · 它靠什么成立",
      s3Title: "3 · 这次发现了什么",
      s4Title: "4 · 我的解释与修正",
      s5Title: "5 · 还有什么没弄清",
      srcTitle: "来源快照",
      srcNote: "以下内容为生成时的来源快照，当前磁盘上的文件未复核。你可以重新选择来源文件，与快照比对哈希。",
      expTitle: "导出",
      expNote: "导出在本地完成，不会自动发布。省略原文不等于自动脱敏，解释文字中仍可能含有你的私人信息。",
      expLegend: "导出内容选择",
      optNotes: "包含我的原话 / 笔记 / 答案",
      optTexts: "包含原材料全文",
      btnPreview: "预览导出内容",
      btnJson: "下载 JSON",
      btnMd: "下载 Markdown",
      previewTitle: "导出预览",
      previewNote: "预览显示了将要导出的机制说明、修正建议与推演题；取消勾选即可移除对应内容。",
      refreshNote: "刷新页面会清空未导出的编辑，请先导出再刷新。",
      goalLabel: "目标",
      chainLabel: "最短机制链",
      assumptionsLabel: "承重假设（最多三条）",
      findingsLabel: "发现解释",
      beforeLabel: "审查前的理解",
      beforeMissing: "审查前的理解未记录",
      beforeWho: "我的原话（生成时提供）",
      revisionsLabel: "修正建议",
      noRevisions: "没有修正建议（未提供审查前的理解，或模型未提出）。",
      confirm: "确认",
      retract: "撤销",
      editOwn: "改写后确认",
      editPlaceholder: "用自己的话改写这条认识……",
      confirmedTag: "已确认",
      retractedTag: "已撤销（恢复为建议）",
      pendingTag: "建议（未确认）",
      myWording: "我的改写",
      unknownsLabel: "未知",
      promptsLabel: "推演问题（可选）",
      promptsNote: "推演题是条件变化的思考练习，不代表已实测。",
      answerPlaceholder: "写下你的答案（仅记录为用户表达，不判定对错）……",
      saveAnswer: "记录答案",
      answerSaved: "已记录",
      viewSource: "查看来源",
      srcRole: { subject: "审查文本", receipt: "原审查记录", material: "补充材料，未被本次审查核验", user_before: "审查前的理解" },
      hashMatch: "一致",
      hashDiffers: "变化",
      hashNotGiven: "未提供",
      recheckFile: "重新选择该来源文件",
      withheldTag: "导出时省略了原文：当前内容无法核对。",
      snapshotTag: "来源快照；当前文件未复核",
      errNotJson: "无法解析 JSON：",
      errSchema: "文件不符合 falsify.understanding.v1 结构：",
      errStatus: "该产物的生成状态不是 available：",
      genStatus: "生成状态",
      verdict: "原审查裁决",
      ceiling: "权威上限",
      claimScope: "主张范围",
      receiptHash: "原审查关联哈希",
      scopeLabel: "本次理解范围",
      scopeNotCovered: "未覆盖",
      pvGoal: "目标",
      pvChain: "机制链",
      pvAssumptions: "假设",
      pvFindings: "发现解释",
      pvRevisions: "修正建议",
      pvPrompts: "推演题",
      pvAnswers: "我的答案",
      pvUnknowns: "未知",
      pvIncluded: "将包含",
      pvExcluded: "已按选择移除",
      dialogClose: "关闭"
    },
    en: {
      title: "Project Understanding · Falsify",
      subtitle: "Read one traceable page of project understanding: how it works, what it rests on, what evidence changed, what remains unknown. This page runs locally and uploads nothing.",
      importTitle: "Import understanding artifact",
      importHint: "Choose an understanding.json produced by the CLI. The file is read in your browser; the server never touches your disk paths.",
      chooseFile: "Choose understanding.json",
      metaTitle: "Linked original review",
      metaNote: "Snapshot linkage only; proves association with the original review, not authority validation.",
      s1Title: "1 · How it works",
      s2Title: "2 · What it rests on",
      s3Title: "3 · What this review found",
      s4Title: "4 · My explanation & corrections",
      s5Title: "5 · What is still unclear",
      srcTitle: "Source snapshots",
      srcNote: "Snapshots as of generation time; current files on disk are NOT re-verified. You may re-select a source file to compare its hash.",
      expTitle: "Export",
      expNote: "Export happens locally and never auto-publishes. Withholding source text is not automatic redaction; explanations may still contain private information.",
      expLegend: "Export content options",
      optNotes: "Include my words / notes / answers",
      optTexts: "Include full source texts",
      btnPreview: "Preview export",
      btnJson: "Download JSON",
      btnMd: "Download Markdown",
      previewTitle: "Export preview",
      previewNote: "Preview shows mechanism notes, suggested revisions and reflection prompts to be exported; uncheck to remove.",
      refreshNote: "Reloading clears unsaved edits — export first.",
      goalLabel: "Goal",
      chainLabel: "Shortest mechanism chain",
      assumptionsLabel: "Load-bearing assumptions (max 3)",
      findingsLabel: "Findings explained",
      beforeLabel: "Understanding before review",
      beforeMissing: "No pre-review understanding recorded",
      beforeWho: "My own words (provided at generation)",
      revisionsLabel: "Suggested revisions",
      noRevisions: "No suggested revisions (no pre-review input provided, or model proposed none).",
      confirm: "Confirm",
      retract: "Retract",
      editOwn: "Confirm with my wording",
      editPlaceholder: "Rewrite this item in your own words…",
      confirmedTag: "Confirmed",
      retractedTag: "Retracted (back to suggestion)",
      pendingTag: "Suggestion (pending)",
      myWording: "My wording",
      unknownsLabel: "Unknowns",
      promptsLabel: "Reflection prompts (optional)",
      promptsNote: "Prompts are conditional-change thought experiments, not measured results.",
      answerPlaceholder: "Write your answer (recorded as user expression only; not graded)…",
      saveAnswer: "Record answer",
      answerSaved: "Recorded",
      viewSource: "View source",
      srcRole: { subject: "Reviewed text", receipt: "Original review receipt", material: "Supplementary material, not verified by this review", user_before: "Pre-review understanding" },
      hashMatch: "match",
      hashDiffers: "changed",
      hashNotGiven: "not provided",
      recheckFile: "Re-select this source file",
      withheldTag: "Source text withheld at export: cannot be re-verified now.",
      snapshotTag: "Source snapshot; current file not re-verified",
      errNotJson: "Cannot parse JSON: ",
      errSchema: "File does not match falsify.understanding.v1 structure: ",
      errStatus: "Artifact generation_status is not available: ",
      genStatus: "Generation status",
      verdict: "Original verdict",
      ceiling: "Authority ceiling",
      claimScope: "Claim scope",
      receiptHash: "Receipt linkage hash",
      scopeLabel: "Understanding scope",
      scopeNotCovered: "Not covered",
      pvGoal: "Goal",
      pvChain: "Mechanism chain",
      pvAssumptions: "Assumptions",
      pvFindings: "Findings explained",
      pvRevisions: "Suggested revisions",
      pvPrompts: "Reflection prompts",
      pvAnswers: "My answers",
      pvUnknowns: "Unknowns",
      pvIncluded: "will be included",
      pvExcluded: "removed per selection",
      dialogClose: "Close"
    }
  };

  var LANG = (new URLSearchParams(location.search).get("lang") === "en") ? "en" : "zh";
  function t(key) {
    var v = I18N[LANG][key];
    return (v === undefined) ? key : v;
  }

  var STATUS_LABEL = {
    source_observation: "source_observation · 材料可见",
    claim: "claim · 主张",
    inference: "inference · 推断",
    unknown: "unknown · 未知"
  };
  var STATUS_LABEL_EN = {
    source_observation: "source_observation · visible in material",
    claim: "claim · stated claim",
    inference: "inference · inferred",
    unknown: "unknown · unsupported yet"
  };

  // ---------- tiny DOM helpers (textContent only) ----------
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) { node.className = cls; }
    if (text !== undefined && text !== null) { node.textContent = String(text); }
    return node;
  }
  function clear(node) { while (node.firstChild) { node.removeChild(node.firstChild); } }
  function para(parent, text, cls) { var p = el("p", cls, text); parent.appendChild(p); return p; }

  // ---------- state ----------
  var state = null;          // validated artifact
  var sourceFiles = {};      // id -> {file, bytes_sha256}

  // ---------- artifact validation ----------
  function isNonEmptyStr(v) { return typeof v === "string" && v.length > 0; }

  function validateArtifact(data) {
    var errs = [];
    if (!data || typeof data !== "object" || Array.isArray(data)) { return ["root is not an object"]; }
    if (data.schema_version !== "falsify.understanding.v1") { errs.push("schema_version must be falsify.understanding.v1"); }
    if (["available", "unavailable", "invalid"].indexOf(data.generation_status) < 0) { errs.push("generation_status invalid"); }
    var ac = data.audit_context;
    if (!ac || typeof ac !== "object" || !isNonEmptyStr(ac.receipt_hash)) { errs.push("audit_context.receipt_hash missing"); }
    if (!Array.isArray(data.sources)) { errs.push("sources must be an array"); return errs; }
    if (!data.project_model || typeof data.project_model !== "object") { errs.push("project_model missing"); return errs; }
    if (!Array.isArray(data.unknowns)) { errs.push("unknowns must be an array"); }
    if (!data.user_notes || typeof data.user_notes !== "object") { errs.push("user_notes missing"); }
    if (data.generation_status === "available") {
      var srcIds = {};
      data.sources.forEach(function (s) {
        if (!isNonEmptyStr(s.id)) { errs.push("source without id"); return; }
        if (srcIds[s.id]) { errs.push("duplicate source id " + s.id); }
        srcIds[s.id] = true;
      });
      var texts = {};
      data.sources.forEach(function (s) {
        if (s.content_state === "withheld") { return; }
        texts[s.id] = String(s.text || "").split("\n");
      });
      function checkRefs(where, refs) {
        (refs || []).forEach(function (r, i) {
          if (!r || !srcIds[r.source_id]) { errs.push(where + " ref[" + i + "] unknown source_id"); return; }
          if (texts[r.source_id] === undefined) { return; } // withheld: quote may be omitted
          var lines = texts[r.source_id];
          var s = r.start_line, e = r.end_line;
          if (!(Number.isInteger(s) && Number.isInteger(e) && s >= 1 && e <= lines.length && s <= e)) {
            errs.push(where + " ref[" + i + "] line range invalid");
            return;
          }
          var quoted = lines.slice(s - 1, e).join("\n");
          var q = String(r.quote || "");
          if (q && quoted.indexOf(q) < 0) { errs.push(where + " ref[" + i + "] quote not found in cited range"); }
        });
      }
      function checkExplained(where, x) {
        if (!x || !isNonEmptyStr(x.text)) { errs.push(where + " missing text"); return; }
        if (["source_observation", "claim", "inference", "unknown"].indexOf(x.epistemic_status) < 0) { errs.push(where + " bad epistemic_status"); }
        checkRefs(where, x.refs);
      }
      var pm = data.project_model;
      if (pm.goal) { checkExplained("project_model.goal", pm.goal); }
      (pm.mechanism_chain || []).forEach(function (m, i) { checkExplained("mechanism_chain[" + i + "]", m); });
      (pm.assumptions || []).forEach(function (a, i) {
        if (!isNonEmptyStr(a.text)) { errs.push("assumption[" + i + "] missing text"); }
        checkRefs("assumption[" + i + "]", a.refs);
      });
      (data.findings_explained || []).forEach(function (f, i) {
        if (!Number.isInteger(f.finding_index)) { errs.push("findings_explained[" + i + "] missing finding_index"); }
        if (!isNonEmptyStr(f.text)) { errs.push("findings_explained[" + i + "] missing text"); }
        checkRefs("findings_explained[" + i + "]", f.refs);
      });
    }
    return errs;
  }

  // ---------- sha256 (async) ----------
  async function sha256Hex(bytes) {
    var digest = await crypto.subtle.digest("SHA-256", bytes);
    return Array.prototype.map.call(new Uint8Array(digest), function (b) {
      return b.toString(16).padStart(2, "0");
    }).join("");
  }

  // ---------- rendering ----------
  function statusLabel(st) {
    var m = (LANG === "en") ? STATUS_LABEL_EN : STATUS_LABEL;
    return m[st] || st;
  }

  function badge(st) {
    return el("span", "badge " + st, st);
  }

  function refButtons(parent, refs) {
    if (!refs || !refs.length) { return; }
    var ul = el("ul", "refs");
    refs.forEach(function (r) {
      var li = el("li");
      var btn = el("button", null, "«" + r.quote + "» " + r.source_id + ":" + r.start_line + (r.end_line !== r.start_line ? "-" + r.end_line : ""));
      btn.setAttribute("aria-label", t("viewSource"));
      btn.addEventListener("click", function () { openSource(r.source_id, r.start_line, r.end_line); });
      li.appendChild(btn);
      ul.appendChild(li);
    });
    parent.appendChild(ul);
  }

  function explainedItem(x, opts) {
    var it = el("div", "item " + (x.epistemic_status || ""));
    var head = el("div");
    head.appendChild(badge(x.epistemic_status));
    var lbl = el("span", "sr-only", statusLabel(x.epistemic_status));
    lbl.style.fontSize = "0.75rem"; lbl.style.color = "var(--muted)";
    head.appendChild(lbl);
    it.appendChild(head);
    para(it, x.text, "txt");
    if (opts && opts.ifWrong && x.if_wrong) { para(it, (LANG === "en" ? "If wrong: " : "若不成立：") + x.if_wrong, "note"); }
    refButtons(it, x.refs);
    return it;
  }

  function assumptionItem(a) {
    var it = el("div", "item");
    para(it, a.text, "txt");
    if (a.if_wrong) { para(it, (LANG === "en" ? "If wrong: " : "若不成立：") + a.if_wrong, "note"); }
    refButtons(it, a.refs);
    return it;
  }

  var srcDialog = null;

  function openSource(sourceId, startLine, endLine) {
    var src = null;
    state.sources.forEach(function (s) { if (s.id === sourceId) { src = s; } });
    if (!src) { return; }
    if (srcDialog) { srcDialog.remove(); }
    srcDialog = el("dialog");
    srcDialog.className = "srcdialog";
    var title = el("h3", null, sourceId + " · " + (t("srcRole")[src.role] || src.role));
    srcDialog.appendChild(title);
    var note = para(srcDialog, t("snapshotTag"), "note");
    if (src.content_state === "withheld") {
      para(srcDialog, t("withheldTag"), "error");
    } else {
      var pre = el("pre", "srctext");
      var lines = String(src.text || "").split("\n");
      lines.forEach(function (line, idx) {
        var n = idx + 1;
        var row = el("span", null, String(n).padStart(4, " ") + " | " + line + "\n");
        if (n >= startLine && n <= endLine) { row.className = "hl"; }
        pre.appendChild(row);
      });
      srcDialog.appendChild(pre);
    }
    var close = el("button", null, t("dialogClose"));
    close.addEventListener("click", function () { srcDialog.close(); });
    srcDialog.appendChild(close);
    document.body.appendChild(srcDialog);
    srcDialog.addEventListener("close", function () { srcDialog.remove(); srcDialog = null; });
    srcDialog.showModal();
  }

  function renderMeta() {
    var ac = state.audit_context;
    var dl = document.getElementById("meta-list");
    clear(dl);
    function row(k, v) {
      dl.appendChild(el("dt", null, t(k)));
      dl.appendChild(el("dd", null, v));
    }
    row("verdict", ac.verdict);
    row("ceiling", ac.authority_ceiling == null ? "—" : ac.authority_ceiling);
    row("claimScope", ac.claim_scope == null ? "—" : ac.claim_scope);
    row("receiptHash", ac.receipt_hash);
    row("genStatus", state.generation_status);
    var scopeBox = document.getElementById("scope-box");
    clear(scopeBox);
    var sc = state.scope || {};
    var h = el("h3", null, t("scopeLabel"));
    scopeBox.appendChild(h);
    (sc.inputs || []).forEach(function (s) { para(scopeBox, "· " + s); });
    if (sc.not_covered && sc.not_covered.length) {
      scopeBox.appendChild(el("h3", null, t("scopeNotCovered")));
      (sc.not_covered || []).forEach(function (s) { para(scopeBox, "· " + s, "note"); });
    }
    if (sc.note) { para(scopeBox, sc.note, "note"); }
  }

  function renderModel() {
    var pm = state.project_model;
    var goalBox = document.getElementById("sec-goal");
    clear(goalBox);
    goalBox.appendChild(el("h3", null, t("goalLabel")));
    if (pm.goal) { goalBox.appendChild(explainedItem(pm.goal)); }

    var chainBox = document.getElementById("sec-chain");
    clear(chainBox);
    chainBox.appendChild(el("h3", null, t("chainLabel")));
    (pm.mechanism_chain || []).forEach(function (m, i) {
      var wrap = el("div");
      wrap.appendChild(el("span", "badge", String(i + 1)));
      wrap.appendChild(explainedItem(m));
      chainBox.appendChild(wrap);
    });

    var aBox = document.getElementById("sec-assumptions");
    clear(aBox);
    aBox.appendChild(el("h3", null, t("assumptionsLabel")));
    (pm.assumptions || []).forEach(function (a) { aBox.appendChild(assumptionItem(a)); });
  }

  function renderFindings() {
    var box = document.getElementById("sec-findings");
    clear(box);
    box.appendChild(el("h3", null, t("findingsLabel")));
    (state.findings_explained || []).forEach(function (f) {
      var it = el("div", "item " + (f.epistemic_status || ""));
      var head = el("div");
      head.appendChild(el("span", "badge", "#" + f.finding_index));
      if (f.original_severity) { head.appendChild(el("span", "badge", f.original_severity)); }
      if (f.original_cutline) { head.appendChild(el("span", "badge", f.original_cutline)); }
      it.appendChild(head);
      para(it, f.text, "txt");
      refButtons(it, f.refs);
      box.appendChild(it);
    });
  }

  function renderUserSection() {
    var beforeBox = document.getElementById("sec-before");
    clear(beforeBox);
    beforeBox.appendChild(el("h3", null, t("beforeLabel")));
    var un = state.user_notes || {};
    if (un.before_recorded) {
      var box = el("div", "beforebox");
      para(box, t("beforeWho"), "who");
      para(box, un.before_recorded);
      beforeBox.appendChild(box);
    } else {
      para(beforeBox, t("beforeMissing"), "note");
    }

    var revBox = document.getElementById("sec-revisions");
    clear(revBox);
    revBox.appendChild(el("h3", null, t("revisionsLabel")));
    var revs = state.suggested_revisions || [];
    if (!revs.length) { para(revBox, t("noRevisions"), "note"); return; }
    var states = {};
    (un.revision_states || []).forEach(function (r) { states[r.revision_id] = r; });
    revs.forEach(function (r) {
      var st = states[r.id] || { state: "pending" };
      var div = el("div", "rev " + st.state);
      para(div, r.before, "before");
      para(div, "→", "arrow");
      para(div, r.after, "after");
      if (st.user_wording) {
        para(div, t("myWording") + ": " + st.user_wording, "userword");
      }
      var tag = (st.state === "confirmed") ? t("confirmedTag") : (st.state === "retracted") ? t("retractedTag") : t("pendingTag");
      para(div, tag, "note");
      var actions = el("div", "actions");
      if (st.state !== "confirmed") {
        var btnC = el("button", null, t("confirm"));
        btnC.addEventListener("click", function () { setRevisionState(r.id, "confirmed", null); });
        actions.appendChild(btnC);
        var btnE = el("button", null, t("editOwn"));
        btnE.addEventListener("click", function () { enableEdit(div, r); });
        actions.appendChild(btnE);
      } else {
        var btnR = el("button", null, t("retract"));
        btnR.addEventListener("click", function () { setRevisionState(r.id, "retracted", null); });
        actions.appendChild(btnR);
      }
      div.appendChild(actions);
      revBox.appendChild(div);
    });
  }

  function enableEdit(div, r) {
    var ta = el("textarea", "ansbox");
    ta.placeholder = t("editPlaceholder");
    div.appendChild(ta);
    var save = el("button", "primary", t("editOwn"));
    save.addEventListener("click", function () {
      var wording = ta.value.trim();
      if (!wording) { return; }
      setRevisionState(r.id, "confirmed", wording);
    });
    div.appendChild(save);
    ta.focus();
  }

  function setRevisionState(revId, st, wording) {
    var list = state.user_notes.revision_states || [];
    var found = false;
    list.forEach(function (r) {
      if (r.revision_id === revId) {
        r.state = st; r.changed_at = new Date().toISOString();
        r.user_wording = (st === "confirmed" && wording) ? wording : undefined;
        found = true;
      }
    });
    if (!found) {
      list.push({ revision_id: revId, state: st, changed_at: new Date().toISOString(), user_wording: wording || undefined });
    }
    state.user_notes.revision_states = list;
    renderUserSection();
  }

  function renderUnknowns() {
    var box = document.getElementById("sec-unknowns");
    clear(box);
    box.appendChild(el("h3", null, t("unknownsLabel")));
    (state.unknowns || []).forEach(function (u) {
      var it = el("div", "item unknown");
      it.appendChild(el("span", "badge unknown", u.kind));
      para(it, u.text, "txt");
      if (u.impact) { para(it, (LANG === "en" ? "Affects: " : "影响：") + u.impact, "note"); }
      if (u.next_evidence) { para(it, (LANG === "en" ? "Next evidence: " : "下一条证据：") + u.next_evidence, "note"); }
      box.appendChild(it);
    });
  }

  function renderPrompts() {
    var box = document.getElementById("sec-prompts");
    clear(box);
    var prompts = state.reflection_prompts || [];
    if (!prompts.length) { return; }
    box.appendChild(el("h3", null, t("promptsLabel")));
    para(box, t("promptsNote"), "note");
    var answers = {};
    ((state.user_notes || {}).answers || []).forEach(function (a) { answers[a.prompt_id] = a; });
    prompts.forEach(function (p) {
      var it = el("div", "item");
      para(it, p.question, "txt");
      var ta = el("textarea", "ansbox");
      ta.placeholder = t("answerPlaceholder");
      ta.value = (answers[p.id] && answers[p.id].answer) || "";
      it.appendChild(ta);
      var btn = el("button", null, t("saveAnswer"));
      var saved = el("span", "anssaved", " ");
      btn.addEventListener("click", function () {
        var val = ta.value.trim();
        if (!val) { return; }
        recordAnswer(p.id, val);
        saved.textContent = "✓ " + t("answerSaved");
      });
      var row = el("div");
      row.appendChild(btn); row.appendChild(saved);
      it.appendChild(row);
      box.appendChild(it);
    });
  }

  function recordAnswer(promptId, val) {
    var un = state.user_notes;
    un.answers = un.answers || [];
    var found = false;
    un.answers.forEach(function (a) {
      if (a.prompt_id === promptId) { a.answer = val; a.recorded_at = new Date().toISOString(); found = true; }
    });
    if (!found) { un.answers.push({ prompt_id: promptId, answer: val, recorded_at: new Date().toISOString() }); }
  }

  function renderSources() {
    var box = document.getElementById("sec-sources");
    clear(box);
    state.sources.forEach(function (s) {
      var det = el("details", "srcbox");
      var sum = el("summary", null, s.id + " · " + (t("srcRole")[s.role] || s.role) + (s.origin_path ? " · " + s.origin_path : ""));
      det.appendChild(sum);
      var body = el("div", "srcbody");
      var hashRow = el("p", "hashrow");
      hashRow.appendChild(document.createTextNode("bytes_sha256: " + s.bytes_sha256 + " · "));
      var state_ = el("span", null, t("snapshotTag"));
      hashRow.appendChild(state_);
      body.appendChild(hashRow);
      if (s.content_state === "withheld") {
        para(body, t("withheldTag"), "error");
      } else {
        var pre = el("pre", "srctext");
        String(s.text || "").split("\n").forEach(function (line, idx) {
          pre.appendChild(el("span", null, String(idx + 1).padStart(4, " ") + " | " + line + "\n"));
        });
        body.appendChild(pre);
      }
      var fileRow = el("div");
      var pick = el("button", null, t("recheckFile"));
      var result = el("span", "hashrow");
      pick.addEventListener("click", function () {
        var input = document.createElement("input");
        input.type = "file";
        input.addEventListener("change", async function () {
          var f = input.files && input.files[0];
          if (!f) { return; }
          var buf = await f.arrayBuffer();
          var h = await sha256Hex(buf);
          sourceFiles[s.id] = { file: f.name, bytes_sha256: h };
          clear(result);
          if (h === s.bytes_sha256) {
            var m = el("span", "match", "✓ " + f.name + " · " + t("hashMatch"));
            result.appendChild(m);
          } else {
            var d = el("span", "differs", "✗ " + f.name + " · " + t("hashDiffers"));
            result.appendChild(d);
          }
        });
        input.click();
      });
      fileRow.appendChild(pick);
      fileRow.appendChild(result);
      body.appendChild(fileRow);
      det.appendChild(body);
      box.appendChild(det);
    });
  }

  // ---------- export ----------
  function buildExport(includeNotes, includeTexts) {
    var out = JSON.parse(JSON.stringify(state));
    if (!includeTexts) {
      out.sources.forEach(function (s) {
        if (s.role === "receipt") { return; } // keep receipt text: it is the review snapshot
        s.content_state = "withheld";
        delete s.text;
        s.text = "";
        s.text_sha256 = "";
      });
      stripQuotesUnableToVerify(out);
    }
    if (!includeNotes) {
      var un = out.user_notes || {};
      un.before_recorded = null;
      un.answers = [];
      un.revision_states = (un.revision_states || []).filter(function (r) { return false; });
      // remove suggested revisions that quote the user's before text
      out.suggested_revisions = (out.suggested_revisions || []).filter(function (r) { return false; });
    }
    return out;
  }

  function stripQuotesUnableToVerify(obj) {
    function walk(node) {
      if (Array.isArray(node)) { node.forEach(walk); return; }
      if (!node || typeof node !== "object") { return; }
      (node.refs || []).forEach(function (r) {
        var src = null;
        out: for (var i = 0; i < (state.sources || []).length; i++) {
          if (state.sources[i].id === r.source_id && state.sources[i].content_state === "withheld") { src = state.sources[i]; break out; }
        }
        if (src) { r.quote = ""; }
      });
      Object.keys(node).forEach(function (k) {
        var v = node[k];
        if (v && typeof v === "object") { walk(v); }
        if (k === "basis_refs" && Array.isArray(v)) {
          v.forEach(function (r) {
            for (var i = 0; i < (state.sources || []).length; i++) {
              if (state.sources[i].id === r.source_id && state.sources[i].content_state === "withheld") { r.quote = ""; }
            }
          });
        }
      });
    }
    walk(obj);
  }

  function renderMarkdown(data) {
    var L = [];
    L.push("# " + t("title"));
    L.push("");
    L.push("- " + t("verdict") + ": " + (data.audit_context || {}).verdict);
    L.push("- " + t("receiptHash") + ": " + (data.audit_context || {}).receipt_hash);
    L.push("");
    var pm = data.project_model || {};
    L.push("## " + t("s1Title"));
    if (pm.goal) { L.push("- " + t("goalLabel") + ": " + pm.goal.text + " (" + pm.goal.epistemic_status + ")"); }
    (pm.mechanism_chain || []).forEach(function (m, i) {
      L.push("- " + (i + 1) + ". " + m.text + " (" + m.epistemic_status + ")");
    });
    L.push("");
    L.push("## " + t("s2Title"));
    (pm.assumptions || []).forEach(function (a) { L.push("- " + a.text); });
    L.push("");
    L.push("## " + t("s3Title"));
    (data.findings_explained || []).forEach(function (f) {
      L.push("- [#" + f.finding_index + "] " + f.text + " (" + f.epistemic_status + ")");
    });
    L.push("");
    L.push("## " + t("s5Title"));
    (data.unknowns || []).forEach(function (u) { L.push("- (" + u.kind + ") " + u.text); });
    L.push("");
    var un = data.user_notes || {};
    if (un.before_recorded) {
      L.push("## " + t("s4Title"));
      L.push("- " + t("beforeLabel") + ": " + un.before_recorded);
      (un.revision_states || []).forEach(function (r) {
        L.push("- " + r.revision_id + ": " + r.state + (r.user_wording ? " — " + r.user_wording : ""));
      });
    }
    (un.answers || []).forEach(function (a) { L.push("- " + a.prompt_id + ": " + a.answer); });
    L.push("");
    var prompts = data.reflection_prompts || [];
    if (prompts.length) {
      L.push("## " + t("promptsLabel"));
      prompts.forEach(function (p) { L.push("- " + p.question); });
    }
    return L.join("\n");
  }

  function download(name, content, type) {
    var blob = new Blob([content], { type: type + ";charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  function previewExport() {
    var includeNotes = document.getElementById("opt-include-notes").checked;
    var includeTexts = document.getElementById("opt-include-texts").checked;
    var data = buildExport(includeNotes, includeTexts);
    var box = document.getElementById("preview-body");
    clear(box);
    var pm = data.project_model || {};
    function item(label, arr, extractor) {
      var row = el("div", "pv-item");
      row.appendChild(el("span", "pv-t", label + " — "));
      var n = (arr || []).length;
      row.appendChild(document.createTextNode(n ? n + " " + t("pvIncluded") : t("pvExcluded")));
      box.appendChild(row);
    }
    item(t("pvGoal"), pm.goal ? [pm.goal] : [], null);
    item(t("pvChain"), pm.mechanism_chain, null);
    item(t("pvAssumptions"), pm.assumptions, null);
    item(t("pvFindings"), data.findings_explained, null);
    item(t("pvRevisions"), includeNotes ? (data.suggested_revisions || []) : [], null);
    item(t("pvPrompts"), data.reflection_prompts || [], null);
    item(t("pvAnswers"), includeNotes ? ((data.user_notes || {}).answers || []) : [], null);
    item(t("pvUnknowns"), data.unknowns, null);
    document.getElementById("preview-area").hidden = false;
    document.getElementById("btn-export-json").disabled = false;
    document.getElementById("btn-export-md").disabled = false;
  }

  // ---------- import ----------
  function onFile(e) {
    var f = e.target.files && e.target.files[0];
    if (!f) { return; }
    var reader = new FileReader();
    reader.onload = function () {
      var errBox = document.getElementById("import-error");
      var data;
      try {
        data = JSON.parse(String(reader.result));
      } catch (err) {
        errBox.textContent = t("errNotJson") + err.message;
        errBox.hidden = false;
        return;
      }
      var errs = validateArtifact(data);
      if (errs.length) {
        errBox.textContent = t("errSchema") + "\n" + errs.slice(0, 6).join("\n");
        errBox.hidden = false;
        return;
      }
      if (data.generation_status !== "available") {
        errBox.textContent = t("errStatus") + data.generation_status + (data.failure_reason ? "\n" + data.failure_reason : "");
        errBox.hidden = false;
        return;
      }
      errBox.hidden = true;
      state = data;
      sourceFiles = {};
      var sum = document.getElementById("imported-summary");
      sum.textContent = "✓ " + f.name;
      sum.hidden = false;
      document.getElementById("reader").hidden = false;
      renderAll();
    };
    reader.readAsText(f, "utf-8");
  }

  function renderAll() {
    renderMeta(); renderModel(); renderFindings(); renderUserSection();
    renderUnknowns(); renderPrompts(); renderSources();
  }

  // ---------- i18n application & boot ----------
  function applyI18n() {
    var nodes = document.querySelectorAll("[data-i18n]");
    var i;
    for (i = 0; i < nodes.length; i++) {
      var key = nodes[i].getAttribute("data-i18n");
      var v = I18N[LANG][key];
      if (v !== undefined) { nodes[i].textContent = v; }
    }
    document.documentElement.lang = (LANG === "en") ? "en" : "zh-CN";
    var links = document.querySelectorAll("[data-i18n-attr-href]");
    for (i = 0; i < links.length; i++) {
      var k2 = links[i].getAttribute("data-i18n-attr-href");
      var v2 = I18N[LANG][k2];
      if (v2 !== undefined) { links[i].setAttribute("href", v2); }
    }
  }
  I18N.zh.hrefZh = "?lang=zh"; I18N.zh.hrefEn = "?lang=en";
  I18N.en.hrefZh = "?lang=zh"; I18N.en.hrefEn = "?lang=en";

  applyI18n();
  document.getElementById("file-input").addEventListener("change", onFile);
  document.getElementById("btn-preview").addEventListener("click", previewExport);
  document.getElementById("btn-export-json").addEventListener("click", function () {
    var data = buildExport(document.getElementById("opt-include-notes").checked, document.getElementById("opt-include-texts").checked);
    download("understanding-export.json", JSON.stringify(data, null, 2), "application/json");
  });
  document.getElementById("btn-export-md").addEventListener("click", function () {
    var data = buildExport(document.getElementById("opt-include-notes").checked, document.getElementById("opt-include-texts").checked);
    download("understanding-export.md", renderMarkdown(data), "text/markdown");
  });
})();
