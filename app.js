const count = document.querySelector("#count");
let value = 0;

document.querySelector("#increment").addEventListener("click", () => {
  value += 2;
  count.textContent = String(value);
});

document.querySelector("#reset").addEventListener("click", () => {
  value = 0;
  count.textContent = String(value);
});

async function loadGitState() {
  try {
    const response = await fetch("/api/git", { cache: "no-store" });
    if (!response.ok) throw new Error("Cannot read Git state");
    const state = await response.json();
    document.querySelector("#branch").textContent = state.branch;
    document.querySelector("#head").textContent = state.head || "尚无提交";
    document.querySelector("#subject").textContent = state.subject || "尚无提交";
    document.querySelector("#worktree").textContent = state.dirty
      ? "有未提交改动（网页内容可能与 HEAD 不同）"
      : "干净（网页内容与 HEAD 一致）";
  } catch {
    for (const id of ["branch", "head", "subject", "worktree"]) {
      document.getElementById(id).textContent = "不可用";
    }
    document.querySelector("#git-note").textContent =
      "无法读取 Git 状态。请使用 python3 server.py 启动，并通过本地地址访问。";
  }
}

loadGitState();
