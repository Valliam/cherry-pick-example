const count = document.querySelector("#count");
let value = 0;

document.querySelector("#increment").addEventListener("click", () => {
  value += 1;
  count.textContent = String(value);
});

document.querySelector("#reset").addEventListener("click", () => {
  value = 0;
  count.textContent = String(value);
});

async function loadGitState() {
  try {
    const url = document.querySelector('meta[name="git-state-url"]').content;
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error("Cannot read Git state");
    const state = await response.json();
    document.querySelector("#branch").textContent = state.branch;
    document.querySelector("#head").textContent = state.head || "尚无提交";
    document.querySelector("#subject").textContent = state.subject || "尚无提交";
    if (state.mode === "deployment") {
      document.querySelector("#git-heading").textContent = "构建版本";
      document.querySelector("#state-label").textContent = "构建状态";
      document.querySelector("#worktree").textContent = state.dirty
        ? "本地构建预览：包含未提交改动，内容可能与上述 SHA 不同"
        : "内容来自上述提交";
      document.querySelector("#git-note").textContent =
        "版本信息在构建时生成；线上内容随下一次部署更新。";
    } else {
      document.querySelector("#worktree").textContent = state.dirty
        ? "有未提交改动（网页内容可能与 HEAD 不同）"
        : "干净（网页内容与 HEAD 一致）";
    }
  } catch {
    for (const id of ["branch", "head", "subject", "worktree"]) {
      document.getElementById(id).textContent = "不可用";
    }
    document.querySelector("#git-note").textContent =
      "无法读取版本信息。本地请使用 python3 server.py；静态站点请检查 git-state.json 是否已发布。";
  }
}

loadGitState();
