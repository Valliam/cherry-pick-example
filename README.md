# Cherry-pick example

一个演示 Git cherry-pick 的小网页：`feature` 包含多个功能提交，`main` 只接收其中的 bug 修复。

## 本地预览

需要 Python 3 和 Git，不需要安装依赖：

```sh
python3 server.py
```

打开 <http://127.0.0.1:8000>。如果端口被占用，可以运行 `python3 server.py --port 8001`。

切换分支、修改文件或提交之后刷新页面。服务器直接读取当前工作区文件和 Git 元数据，无需重启。

- Git 状态显示实际分支、HEAD、最新提交标题及是否有未提交改动。
- 内容列表显示当前版本包含的 Base、Commit A/B/C，不代表完整 Git 历史。
- 点击 `+1`：初始版本实际增加 2；Bugfix A 将其修正为增加 1。
- 有未提交改动时，网页可能与 HEAD 对应的提交内容不同；页面会明确提示。

## 静态构建与 GitHub Pages

```sh
python3 build.py
python3 -m http.server 8001 --bind 127.0.0.1
```

打开 <http://127.0.0.1:8001/dist/>，验证网页可以在子路径下加载。
构建生成 `dist/index.html`、`dist/app.js` 和 `dist/git-state.json`。
`dist/` 不提交到 Git；线上版本信息来自构建时的实际 checkout。
本地构建包含未提交改动时会明确提示；CI 构建要求工作区干净。

GitHub Actions 的 `Pages` 工作流在分支 push、指向 main 的 PR，以及手动运行时检查语法并构建。
PR 只检查和构建；PR 的 SHA 可能是 GitHub 生成的测试合并提交，来源分支单独记录。
部署仅允许 main，或仓库变量 `PAGES_BOOTSTRAP_BRANCH` 指定的初始化分支。

首次上线前需要在仓库设置中：

1. 将 Pages 发布源设为 GitHub Actions，跳过创建模板工作流。
2. 将仓库变量 `PAGES_BOOTSTRAP_BRANCH` 设置为 `chore/setup-cicd`。
3. 将 `github-pages` 环境的部署分支设置为 Selected branches and tags，允许
   `main` 和 `chore/setup-cicd` 两个 Branch 规则。
4. 推送初始化分支，完成实际部署和线上验收。
5. 验收后删除该变量和初始化分支的环境规则，再快进合入 main 并推送。

初始化分支会发布到仓库同一个 Pages 地址。后续 main 推送自动更新该地址。
关闭初始化分支后，feature 的 CI 仍运行，但不会覆盖正式网站。
CI 暂不把计数器的增量固定为 1 或 2，保留演示 bug 至 Bugfix A。

## 计划中的历史

以下是待执行方案。所有 commit（包括 cherry-pick 产生的新 commit）均需确认后执行。

| 步骤 | 分支 | 提交标题 | 改动 |
| --- | --- | --- | --- |
| 1 | main | `chore: create base demo` | 初始网页、Git 状态读取、带 bug 的计数器和说明 |
| 2 | chore/setup-cicd | `ci: add GitHub Pages deployment` | 构建和部署；验收后快进合入 main |
| 3 | feature | `feat: add Commit A` | 只向 `index.html` 的内容列表添加 Commit A |
| 4 | feature | `feat: add Commit B` | 只向同一列表添加 Commit B |
| 5 | feature | `feat: add Commit C` | 只向同一列表添加 Commit C |
| 6 | feature | `fix: increment counter by one (Bugfix A)` | 只把 `app.js` 中的 `value += 2` 改为 `value += 1` |
| 7 | main | cherry-pick 步骤 6 | 仅应用修复，并用 `-x` 记录来源提交 |

最终期望的历史（字母为示意名称，实际 SHA 由 Git 生成）：

```text
Base --- CI/CD ---+--- A --- B --- C --- F  (feature)
                 |
                 +--- F'                  (main)
```

如果 CI/CD 调试需要追加提交，保留真实记录并相应更新说明。
`F` 是 Bugfix A。`F'` 是 cherry-pick 创建的新提交，父提交为 CI/CD 共同基点，SHA 与 F 不同。
`main` 的历史不包含 A、B、C，也没有合并提交。

| 版本 | 页面内容列表 | 点击 +1 |
| --- | --- | --- |
| Base 或 CI/CD | Base | 实际 +2 |
| feature 的 A/B/C | Base，加上已提交的 A/B/C | 实际 +2 |
| feature 的 F | Base、Commit A、Commit B、Commit C | 实际 +1 |
| main 的 F' | Base | 实际 +1 |

## 执行与核对方式

CI/CD 验收并快进合入 main 后，从该共同基点建立 feature：

```sh
git switch -c feature
```

逐次准备、确认并创建 A、B、C、Bugfix A。完成 Bugfix A 后，先用 `git rev-parse HEAD`
记录完整 SHA；切回 main 后，使用该 SHA 执行下面的 cherry-pick（此操作会创建提交，需要先确认）：

```sh
git switch main
git cherry-pick -x <Bugfix-A-SHA>
```

`-x` 会在新提交的信息中加入 `(cherry picked from commit ...)`，保留来源线索。
Git 的提交图只展示父子关系，不会额外绘制一条从 F 到 F' 的 cherry-pick 连线。
通过图中的分叉和新提交信息中的来源 SHA，一起核对这个过程：

```sh
git log --graph --oneline --decorate --all
git show --format=fuller main
git diff main feature -- index.html app.js
```

预期最后的 diff 只有 Commit A/B/C 的列表项差异，`app.js` 没有差异。

## 为什么把修复放在 feature 上？

这是为了演示一种常见情况：开发功能时修复了一个旧 bug，但主分支暂时不需要这些功能。
cherry-pick 可以把独立的修复移植回主分支。

单独建立 bugfix 分支同样合理。若修复一开始就明确要进入主分支，可以从 main 或包含该 bug
的合适共同基点建立 bugfix 分支，修复后合入 main，再同步到 feature。

这个示例要求 bug 在 Base 中就存在，且修复不依赖 A/B/C。若 bug 是新功能引入的，main 没有
对应代码，把修复单独移植过去可能没有意义，也可能冲突。这里让功能只改 HTML 列表、修复只改
计数逻辑，使得最后一个提交可以独立应用。
